# jedy_play

`jedy_play` is a ROS package used to bring up and operate **Jedy**.

This repository is maintained with two branches:

- **internal**: runs on the robot body computer (main entrypoint: `new_jedy.launch`)
- **external**: development utilities to run from an external PC (serial + Python scripts)

---

## Internal (robot body) — main launch

### Quick start

```bash
roslaunch jedy_play new_jedy.launch use_camera:=true
```

### What `new_jedy.launch` does

- Includes robot bringup (`jedy_bringup.launch`) and loads controller config
- (Optional) starts rosserial for M5 input
- (Optional) starts D405 camera bringup
- (Optional) starts ReSpeaker
- (Optional) starts a small tone synthesizer node (`tone_player_alsa.py`)

### Important args

- `urdf_path`, `servo_config_path`: override if your URDF/config package differs
- `use_camera` (default: false)
- `use_m5` (default: true), `serial_port`, `serial_baud`
- `use_respeaker` (default: true)
- `use_tone_player` (default: true), `alsa_device` (default: pulse)

### External package dependencies (robot environment)

`new_jedy.launch` expects these packages to be available in the robot environment:

- `jedy_bringup`
- `kxr_humanoid_movebase_ichikura_version2` (URDF/config default)
- `rosserial_python`
- `respeaker_ros`

---
