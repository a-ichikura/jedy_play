#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROS node: tone_player_alsa
# - Subscribe: "tone_sequence" (std_msgs/String)  ex) [{"freq":440,"duration":200}, ...]
# - Synthesize tones with selectable timbre (waveform/ADSR/vibrato/tremolo/harmonics)
# - Play via ALSA/PulseAudio using `aplay`
#
# Global params (private, ~):
#   ~alsa_device:   "pulse" | "plughw:1,0" | "default" ... (default: "pulse")
#   ~channels:      1 or 2 (L=R stereo).    (default: 1)
#   ~sample_rate:   Hz                       (default: 48000)
#   ~gain:          0.0..1.0                (default: 0.6)
#   ~waveform:      "sine|square|triangle|saw|noise" (default: "sine")
#   ~adsr_attack_ms, ~adsr_decay_ms, ~adsr_sustain, ~adsr_release_ms
#   ~vibrato_hz, ~vibrato_cents
#   ~tremolo_hz, ~tremolo_depth
#   ~harmonics:     ex) "1:1.0,2:0.3,3:0.15" (default: "1:1.0")
#   ~gap_ms:        silence between notes    (default: 5)
#   ~preset:        "beep|chime|buzzer|robot|blip"（プリセット適用。個別paramで上書き可）
#   ~write_tempfile:bool (stdin相性が悪いALSA直叩き用の保険。default: false)
#
# Per-note overrides (within JSON array):
#   {"freq":..., "duration":..., "waveform":..., "gain":..., "vibrato_hz":..., "vibrato_cents":...,
#    "tremolo_hz":..., "tremolo_depth":..., "harmonics":[[k,a],...]}
#
import rospy, json, math, io, wave, subprocess, os, random, tempfile
from std_msgs.msg import String
from array import array

# ----------------------- helpers: DSP -----------------------
def wave_sample(phase, kind):
    """Return -1..+1 sample for given phase and waveform kind."""
    # normalize phase into [0, 2π) but avoid heavy modulo each call
    s = math.sin(phase)
    if kind == "sine":
        return s
    if kind == "square":
        return 1.0 if s >= 0.0 else -1.0
    if kind == "triangle":
        # Map phase to saw [-1,1], then abs+scale to triangle in [-1,1]
        # phase/(2π) -> [0,1)
        u = (phase / (2.0 * math.pi)) % 1.0
        return 2.0 * abs(2.0 * u - 1.0) - 1.0
    if kind == "saw":
        u = (phase / (2.0 * math.pi)) % 1.0
        return 2.0 * u - 1.0
    if kind == "noise":
        return 2.0 * random.random() - 1.0
    return s

def clamp(x, lo=-1.0, hi=1.0):
    return hi if x > hi else (lo if x < lo else x)

# ----------------------- main player -----------------------
class TonePlayer(object):
    def __init__(self):
        # audio / synth params
        self.dev      = rospy.get_param("~alsa_device", "pulse")
        self.channels = int(rospy.get_param("~channels", 1))
        self.sr       = int(rospy.get_param("~sample_rate", 48000))
        self.gap_ms   = float(rospy.get_param("~gap_ms", 5.0))
        self.write_tmp= bool(rospy.get_param("~write_tempfile", False))

        # base timbre
        self.waveform = rospy.get_param("~waveform", "sine")
        self.gain     = float(rospy.get_param("~gain", 0.6))
        self.adsr = {
            "a": float(rospy.get_param("~adsr_attack_ms", 5.0)),
            "d": float(rospy.get_param("~adsr_decay_ms", 60.0)),
            "s": float(rospy.get_param("~adsr_sustain", 0.7)),
            "r": float(rospy.get_param("~adsr_release_ms", 80.0)),
        }
        self.vibrato = {
            "hz":    float(rospy.get_param("~vibrato_hz", 0.0)),
            "cents": float(rospy.get_param("~vibrato_cents", 0.0)),
        }
        self.tremolo = {
            "hz":    float(rospy.get_param("~tremolo_hz", 0.0)),
            "depth": float(rospy.get_param("~tremolo_depth", 0.0)),  # 0..1
        }
        self.harmonics = self._parse_harmonics(rospy.get_param("~harmonics", "1:1.0"))

        # optional preset (applied first; individual params override)
        self._apply_preset(rospy.get_param("~preset", "").strip().lower())


        self.transpose_semitones = float(rospy.get_param("~transpose_semitones", 0.0))
        self.pitch_scale = float(rospy.get_param("~pitch_scale", 1.0))

        rospy.loginfo("tone_player_alsa using ALSA device: %s", self.dev)
        rospy.Subscriber("tone_sequence", String, self.cb, queue_size=10)

    # ---------- param helpers ----------
    @staticmethod
    def _parse_harmonics(text):
        """
        "1:1.0,2:0.35,3:0.15" -> [(1,1.0),(2,0.35),(3,0.15)]
        """
        pairs = []
        s = str(text).strip()
        if not s:
            return [(1,1.0)]
        for part in s.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                k,a = part.split(":")
                try:
                    pairs.append((int(k.strip()), float(a.strip())))
                except Exception:
                    pass
        if not pairs:
            pairs = [(1,1.0)]
        return pairs

    def _apply_preset(self, name):
        if not name:
            return
        w = "sine"; adsr={"a":5,"d":50,"s":0.8,"r":30}; vib={"hz":0,"cents":0}; tre={"hz":0,"depth":0}; harms=[(1,1.0)]; g=0.7
        if name == "beep":
            w, adsr, vib, tre, harms, g = \
              "sine", {"a":5,"d":50,"s":0.8,"r":30}, {"hz":0,"cents":0}, {"hz":0,"depth":0}, [(1,1.0)], 0.7
        elif name == "chime":
            w, adsr, vib, tre, harms, g = \
              "triangle", {"a":2,"d":200,"s":0.0,"r":400}, {"hz":0,"cents":0}, {"hz":0,"depth":0}, [(1,1.0),(2,0.35),(3,0.18)], 0.8
        elif name == "buzzer":
            w, adsr, vib, tre, harms, g = \
              "square", {"a":3,"d":70,"s":0.6,"r":60}, {"hz":0,"cents":0}, {"hz":4,"depth":0.05}, [(1,1.0)], 0.6
        elif name == "robot":
            w, adsr, vib, tre, harms, g = \
              "saw", {"a":8,"d":120,"s":0.5,"r":120}, {"hz":6,"cents":18}, {"hz":4,"depth":0.25}, [(1,1.0),(2,0.2)], 0.6
        elif name == "blip":
            w, adsr, vib, tre, harms, g = \
              "square", {"a":1,"d":80,"s":0.0,"r":20}, {"hz":0,"cents":0}, {"hz":0,"depth":0}, [(1,1.0)], 0.6
        else:
            return
        # apply
        self.waveform = w
        self.adsr.update(adsr)
        self.vibrato.update(vib)
        self.tremolo.update(tre)
        self.harmonics = harms
        self.gain = g
        rospy.loginfo("preset '%s' applied", name)

    # ---------- synth ----------
    def _synth_tones(self, tones):
        """
        tones: list of dicts with at least {"freq":Hz, "duration":ms}
        Returns WAV bytes.
        """
        SR = self.sr
        CH = self.channels
        pcm = array('h')

        # precompute silence gap
        gap_n = int(SR * self.gap_ms / 1000.0) * (2 if CH == 2 else 1)

        for t in tones:
            f0 = float(t.get('freq', 440.0))
            dur_ms = int(t.get('duration', 200))
            if dur_ms <= 0:
                continue

            # --- add here in _synth_tones ---
            # per-note 上書きにも対応（無ければ全体設定を使う）
            tp = float(t.get('transpose_semitones', self.transpose_semitones))
            ps = float(t.get('pitch_scale', self.pitch_scale))
            # ここで移調を反映：f0 * 倍率 * 半音シフト
            f0 *= ps * (2.0 ** (tp / 12.0))

            wf = str(t.get('waveform', self.waveform))
            gain   = float(t.get('gain', self.gain))

            vib_hz = float(t.get('vibrato_hz', self.vibrato["hz"]))
            vib_ct = float(t.get('vibrato_cents', self.vibrato["cents"]))

            tre_hz = float(t.get('tremolo_hz', self.tremolo["hz"]))
            tre_dp = float(t.get('tremolo_depth', self.tremolo["depth"]))

            harms = self.harmonics
            if 'harmonics' in t and isinstance(t['harmonics'], list) and t['harmonics']:
                # allow [[k,a], ...] or [[k,a], ...] as list
                try:
                    harms = [(int(p[0]), float(p[1])) for p in t['harmonics']]
                except Exception:
                    pass
            # normalize by total amplitude to reduce clipping
            norm = sum(abs(a) for (_,a) in harms)
            if norm <= 0.0:
                harms = [(1,1.0)]
                norm = 1.0

            A = int(SR * self.adsr["a"] / 1000.0)
            D = int(SR * self.adsr["d"] / 1000.0)
            S = float(self.adsr["s"])
            R = int(SR * self.adsr["r"] / 1000.0)

            N = int(SR * dur_ms / 1000.0)

            phase = 0.0
            # main note
            for i in range(N):
                tsec = i / float(SR)

                # vibrato in cents -> frequency multiplier
                f = f0
                if vib_hz > 0.0 and vib_ct != 0.0:
                    f *= 2.0 ** ((vib_ct * math.sin(2.0 * math.pi * vib_hz * tsec)) / 1200.0)
                phase += 2.0 * math.pi * f / SR

                # base + harmonics
                s = 0.0
                for (k, a) in harms:
                    s += (a / norm) * wave_sample(phase * k, wf)

                # tremolo (amplitude LFO)
                if tre_hz > 0.0 and tre_dp > 0.0:
                    s *= (1.0 - tre_dp) + tre_dp * (0.5 * (1.0 + math.sin(2.0 * math.pi * tre_hz * tsec)))

                # ADS (attack/decay to sustain)
                if i < A:
                    env = (i / float(max(1, A)))                           # 0 -> 1
                elif i < A + D:
                    env = 1.0 - (1.0 - S) * ((i - A) / float(max(1, D)))   # 1 -> S
                else:
                    env = S

                s = clamp(s * env * gain)
                v = int(s * 32767)
                if CH == 2:
                    pcm.append(v); pcm.append(v)
                else:
                    pcm.append(v)

            # release tail: continue phase to avoid click
            for j in range(R):
                tsec = (N + j) / float(SR)
                f = f0
                if vib_hz > 0.0 and vib_ct != 0.0:
                    f *= 2.0 ** ((vib_ct * math.sin(2.0 * math.pi * vib_hz * tsec)) / 1200.0)
                phase += 2.0 * math.pi * f / SR

                s = 0.0
                for (k, a) in harms:
                    s += (a / norm) * wave_sample(phase * k, wf)

                if tre_hz > 0.0 and tre_dp > 0.0:
                    s *= (1.0 - tre_dp) + tre_dp * (0.5 * (1.0 + math.sin(2.0 * math.pi * tre_hz * tsec)))

                # linear release from sustain level to 0
                env = max(0.0, 1.0 - (j / float(max(1, R))))
                s = clamp(s * env * S * gain)
                v = int(s * 32767)
                if CH == 2:
                    pcm.append(v); pcm.append(v)
                else:
                    pcm.append(v)

            # short gap
            if gap_n > 0:
                pcm.extend([0] * gap_n)

        # build WAV (16-bit PCM, mono/stereo)
        bio = io.BytesIO()
        with wave.open(bio, 'wb') as w:
            w.setnchannels(self.channels)
            w.setsampwidth(2)
            w.setframerate(self.sr)
            w.writeframes(pcm.tobytes())
        return bio.getvalue()

    # ---------- audio out ----------
    def _play_wav_bytes(self, data):
        """
        Prefer stdin pipe to aplay. If fails and device!=pulse, fallback to pulse.
        If ~write_tempfile==true, use tempfile path instead of stdin (for ALSA stdin quirk).
        """
        if self.write_tmp:
            # robust path (works even with some UAC1.0+stdin quirks)
            tmp = None
            try:
                f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                f.write(data); f.flush(); f.close()
                tmp = f.name
                rc = subprocess.call(["aplay", "-q", "-D", self.dev, tmp])
                if rc != 0 and self.dev != "pulse":
                    rospy.logwarn("aplay failed on %s, retrying on 'pulse'...", self.dev)
                    subprocess.call(["aplay", "-q", "-D", "pulse", tmp])
            finally:
                if tmp and os.path.exists(tmp):
                    try: os.remove(tmp)
                    except Exception: pass
            return

        # default path (fast): stdin
        try:
            cmd = ["aplay", "-q", "-D", self.dev, "-t", "wav", "-"]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            p.stdin.write(data)
            p.stdin.close()
            rc = p.wait()
            if rc != 0 and self.dev != "pulse":
                rospy.logwarn("aplay failed on %s, retrying on 'pulse'...", self.dev)
                subprocess.run(["aplay", "-q", "-D", "pulse", "-t", "wav", "-"], input=data)
        except Exception as e:
            rospy.logerr("aplay error: %s", e)

    # ---------- ROS callback ----------
    def cb(self, m):
        try:
            tones = json.loads(m.data)
            if not isinstance(tones, list) or not tones:
                rospy.logwarn("tone_sequence: empty or invalid JSON")
                return
        except Exception as e:
            rospy.logwarn("tone_sequence: JSON parse error: %s", e)
            return

        wav = self._synth_tones(tones)
        self._play_wav_bytes(wav)

# ----------------------- main -----------------------
if __name__ == "__main__":
    rospy.init_node("tone_player_alsa")
    TonePlayer()
    rospy.spin()

