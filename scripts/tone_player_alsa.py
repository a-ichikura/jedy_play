#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy, json, math, io, wave, subprocess, os, time
from std_msgs.msg import String
from array import array

SR = 48000
AMP = 0.5  # 0.0-1.0
FADE_MS = 8
GAP_MS = 5

def synth_tones(tones):
    """tones: [{'freq':Hz, 'duration':ms}, ...] -> WAV(bytes)"""
    fade_n = int(SR * FADE_MS / 1000.0)
    gap_n  = int(SR * GAP_MS  / 1000.0)
    pcm = array('h')

    for t in tones:
        f = float(t.get('freq', 440))
        ms = int(t.get('duration', 200))
        n = int(SR * ms / 1000.0)
        for i in range(n):
            s = math.sin(2.0 * math.pi * f * (i / float(SR)))
            # linear fade in/out
            a = AMP
            if i < fade_n: a *= (i / float(fade_n))
            if i > n - fade_n: a *= max(0.0, (n - i) / float(fade_n))
            val = int(max(-1.0, min(1.0, a * s)) * 32767)
            pcm.append(val)
        # short gap (silence)
        pcm.extend([0]*gap_n)

    bio = io.BytesIO()
    with wave.open(bio, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return bio.getvalue()

class TonePlayer:
    def __init__(self):
        self.dev = rospy.get_param("~alsa_device", os.environ.get("ALSA_DEVICE", "pulse"))
        rospy.loginfo("tone_player_alsa using ALSA device: %s", self.dev)
        rospy.Subscriber("tone_sequence", String, self.cb, queue_size=10)

    def play_wav_bytes(self, data):
        # aplay にWAVをパイプ（'-'はstdin）
        cmd = ["aplay", "-q", "-D", self.dev, "-t", "wav"]  # デバイス: pulse/softvol/plughw:1,0 等
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            p.stdin.write(data)
            p.stdin.close()
            p.wait()
        except Exception:
            p.kill()

    def cb(self, m):
        try:
            tones = json.loads(m.data)
            if not isinstance(tones, list) or not tones:
                return
        except Exception:
            rospy.logwarn("invalid tone_sequence JSON")
            return
        wav_bytes = synth_tones(tones)
        self.play_wav_bytes(wav_bytes)

if __name__ == "__main__":
    rospy.init_node("tone_player_alsa")
    TonePlayer()
    rospy.spin()
