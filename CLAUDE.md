# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Real-time audio visualizer built with **pygame**. It captures live microphone/input audio, runs an FFT, and renders reactive visual effects. A **Tkinter** control panel (running in the main thread) lets the user tweak effects, particles, resolution, screen, and sensitivity while the visualizer renders in a background thread.

The code and comments are primarily in **Spanish** — match that when editing.

## Commands

The venv uses **Python 3.13**. Dependency versions in `requirements.txt` are pinned to what has prebuilt wheels for 3.13 (older pins compile from source and fail).

```powershell
# Activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements.txt

# Run the app (opens the pygame window + Tkinter control panel)
python Visualizer2.py
```

`Visualizer2.py` is the entry point — **not** `VisualizerManager.py` or `web_control_panel.py`. There is no build step, no linter config, and no test framework wired up; the `test_*.py` files are ad-hoc standalone scripts, not a pytest suite.

## Architecture

### Threading model
`Visualizer2.py` `__main__` runs the pygame render loop (`Visualizer.start()`) in a **background `Thread`**, and the Tkinter `ControlPanel.root.mainloop()` in the **main thread**. A third daemon thread inside `AudioManager` continuously reads audio into a shared buffer. The control panel mutates `Visualizer` attributes directly (e.g. `visualizer.current_function`, `visualizer.change_mode`, `visualizer.effect_duration`) — there is no message queue or locking, so cross-thread changes are plain attribute writes.

### Effect system (the core extension point)
- All effects subclass `Effects/effect.py` `Effect` and live in `Effects/`.
- **Effects are auto-discovered by reflection**: `Visualizer.__init__` iterates `globals()` for any `Effect` subclass and instantiates it. This means a new effect only becomes active if it is **imported at the top of `Visualizer2.py`** (so it lands in that module's globals). Adding the file alone is not enough.
- Each effect implements `draw(self, audio_data)` and optionally `on_screen_resize(self, width, height)`.
- Effects expose a `self.config` dict; the control panel's Effects tab renders one entry field per config key generically and writes back via `save_config`. Config is persisted to per-effect JSON under `Effects/configs/` (path set as `self.config_file`, loaded via `load_config_from_file`).
- `Visualizer.current_function` is the single active effect. `change_mode` ("static" | "random" | "sequential") controls whether it auto-cycles every `effect_duration` ms through `active_effects` (the user-enabled subset).

### Audio pipeline
`Managers/audio_manager.py` — reads `int16` PCM (`RATE=44100`, `CHUNK=2048`, mono) on its own thread into `latest_audio`. Effects pull raw samples via `get_audio_data()`; frequency-domain effects call `get_frequency_data()` (real FFT magnitudes, positive half). `get_volume()` applies `sensitivity`. Auto-selects the first input device with input channels.

### Other pieces
- `Managers/particle_manager.py` — particle system driven by audio volume, overlaid on effects.
- `Effects/center_image.py` (`CenterImage`) — always-on centered logo/image that pulses; images loaded from `images/`, default `logo2.png`.
- `panel_control.py` (`ControlPanel`) — the real, actively-used Tkinter UI. `control_panel/` (the package with `debug.py`, `effects.py`, etc.) and `web_control_panel.py` (a Flask panel) appear to be alternative/incomplete UIs and are not wired into the entry point.

### Gotchas
- Duplicate method definitions exist (e.g. `Effect.get_config` and `ControlPanel.update`) — the last definition wins; edit the later one.
- `numpy` is 2.x — avoid removed aliases (`np.float`, `np.int`).
- `screen`/resolution changes must go through `Visualizer.onScreenChange()` so `center_image` and the active effect recompute their center coordinates.
