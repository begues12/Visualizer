import os
import json
import threading
import webbrowser

import numpy as np
import psutil
import pygame
from flask import Flask, request, jsonify, Response


def _range_for(value):
    """(min, max, step, is_int) heuristico para un parametro de config."""
    is_int = (not isinstance(value, bool)) and isinstance(value, int)
    v = abs(float(value))
    if is_int:
        return 0, max(10, int(v * 3) or 10), 1, True
    if v <= 1:
        return 0.0, round(max(1.0, v * 2), 4), 0.01, False
    if v <= 10:
        return 0.0, round(max(10.0, v * 2), 4), 0.05, False
    return 0.0, round(max(1.0, v * 3), 4), 1.0, False


class WebControlPanel:
    def __init__(self, visualizer, host="0.0.0.0", port=5000):
        self.visualizer = visualizer
        self.host = host
        self.port = port
        base = os.path.dirname(os.path.abspath(__file__))
        self.settings_path = os.path.join(base, "config", "settings.json")
        self.app = Flask(__name__)
        self.setup_routes()
        self.load_and_apply_settings()

    # -------------------------------------------------------------- helpers
    def _find_effect(self, name):
        for e in self.visualizer.drawing_functions:
            if e.get_effect_name() == name:
                return e
        return None

    def _images_dir(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

    def _list_images(self):
        folder = self._images_dir()
        os.makedirs(folder, exist_ok=True)
        names = [f for f in os.listdir(folder)
                 if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]
        # Incluye el logo por defecto de la raiz si no esta ya
        default = "logo2.png"
        if default not in names and os.path.exists(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), default)):
            names.insert(0, default)
        return sorted(set(names))

    def _image_path(self, name):
        base = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(self._images_dir(), name)
        if not os.path.exists(p):
            p = os.path.join(base, name)  # p. ej. logo2.png en la raiz
        return p

    # ---------------------------------------------------- persistencia global
    def capture_settings(self):
        v = self.visualizer
        return {
            "mode": v.change_mode,
            "duration": v.effect_duration,
            "sensitivity": v.audioManager.sensitivity,
            "current": v.current_function.get_effect_name(),
            "active": [e.get_effect_name() for e in getattr(v, "active_effects", [])],
            "particles": {
                "max": v.particle_manager.get_max_particles(),
                "speed": getattr(v, "particle_speed", 1),
                "size": getattr(v, "particle_size", 1),
            },
            "device": v.audioManager.get_device_index(),
            "resolution": [v.actual_resolution[0], v.actual_resolution[1]],
            "fps": getattr(v, "fps", 60),
            "center": {
                "max_scale": v.center_image.max_scale,
                "speed": v.center_image.scale_change_speed,
                "size": getattr(v.center_image, "base_size", 1.0),
                "image": getattr(v.center_image, "image_name", "logo2.png"),
            },
        }

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, "w") as f:
                json.dump(self.capture_settings(), f, indent=4)
        except Exception as e:
            print(f"[WebControlPanel] Error guardando ajustes: {e}")

    def load_and_apply_settings(self):
        try:
            with open(self.settings_path) as f:
                data = json.load(f)
        except Exception:
            return
        self.apply_settings(data)
        print("[WebControlPanel] Ajustes previos cargados.")

    def apply_settings(self, data):
        v = self.visualizer
        try:
            if "mode" in data:
                v.change_mode = data["mode"]
            if "duration" in data:
                v.effect_duration = float(data["duration"])
            if "sensitivity" in data:
                v.audioManager.set_sensitivity(float(data["sensitivity"]))
            if data.get("active"):
                sel = [e for e in v.drawing_functions if e.get_effect_name() in set(data["active"])]
                if sel:
                    v.active_effects = sel
            if data.get("current"):
                e = self._find_effect(data["current"])
                if e:
                    v.current_function = e
            p = data.get("particles", {})
            if "max" in p:
                v.particle_manager.max_particles = int(p["max"])
            if "speed" in p:
                v.particle_speed = float(p["speed"])
                v.particle_manager.particle_speed = float(p["speed"])
            if "size" in p:
                v.particle_size = float(p["size"])
                v.particle_manager.particle_size = float(p["size"])
            if data.get("device") is not None:
                try:
                    v.audioManager.set_device(int(data["device"]))
                except Exception:
                    pass
            if data.get("fps"):
                v.fps = int(data["fps"])
            c = data.get("center", {})
            if c:
                if "max_scale" in c:
                    v.center_image.set_max_scale(c["max_scale"])
                if "speed" in c:
                    v.center_image.set_speed(c["speed"])
                if "size" in c:
                    v.center_image.set_base_size(c["size"])
                if c.get("image"):
                    try:
                        v.enqueue(lambda p=self._image_path(c["image"]): v.center_image.set_image_by_path(p))
                    except Exception:
                        pass
            if data.get("resolution"):
                w, h = int(data["resolution"][0]), int(data["resolution"][1])
                v.enqueue(lambda: v.change_resolution(w, h))
        except Exception as e:
            print(f"[WebControlPanel] Error aplicando ajustes: {e}")

    def _state(self):
        v = self.visualizer
        active_names = {e.get_effect_name() for e in getattr(v, "active_effects", [])}
        effects = []
        for e in v.drawing_functions:
            params = []
            meta = getattr(e, "config_meta", {}) or {}
            for key, value in e.get_config().items():
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    continue
                lo, hi, step, is_int = _range_for(value)
                label = key
                m = meta.get(key)
                if m:
                    lo = m.get("min", lo)
                    hi = m.get("max", hi)
                    step = m.get("step", step)
                    is_int = m.get("is_int", is_int)
                    label = m.get("label", key)
                params.append({
                    "key": key, "label": label, "value": value,
                    "min": lo, "max": hi, "step": step, "is_int": is_int,
                })
            effects.append({
                "name": e.get_effect_name(),
                "active": e.get_effect_name() in active_names,
                "params": params,
            })
        return {
            "effects": effects,
            "current": v.current_function.get_effect_name(),
            "mode": v.change_mode,
            "duration": v.effect_duration / 1000,
            "particles": {
                "max": v.particle_manager.get_max_particles(),
                "speed": getattr(v, "particle_speed", 1),
                "size": getattr(v, "particle_size", 1),
            },
            "sensitivity": self.visualizer.audioManager.sensitivity,
            "devices": v.audioManager.list_input_devices(),
            "device": v.audioManager.get_device_index(),
            "resolution": f"{v.actual_resolution[0]}x{v.actual_resolution[1]}",
            "resolutions": [f"{r[0]}x{r[1]}" for r in v.resolutions],
            "screens": pygame.display.get_num_displays(),
            "fps": getattr(v, "fps", 60),
            "center": {
                "max_scale": v.center_image.max_scale,
                "speed": v.center_image.scale_change_speed,
                "size": getattr(v.center_image, "base_size", 1.0),
                "image": getattr(v.center_image, "image_name", "logo2.png"),
                "images": self._list_images(),
            },
        }

    def _debug(self):
        v = self.visualizer
        audio = v.audioManager.get_audio_data()
        ticks = pygame.time.get_ticks()
        time_left = max(0, (v.effect_duration - (ticks - v.last_function_change_time)) / 1000)
        return {
            "fps": round(v.clock.get_fps(), 1),
            "current": v.current_function.get_effect_name(),
            "mode": v.change_mode,
            "time_left": round(time_left, 1) if v.change_mode != "static" else None,
            "particles": v.particle_manager.getNumParticles(),
            "amplitude": int(np.max(np.abs(audio.astype(np.int32)))) if audio.size else 0,
            "cpu": round(psutil.cpu_percent()),
            "sensitivity": round(v.audioManager.sensitivity, 2),
            "volume": round(v.audioManager.get_volume(audio)),
            "resolution": f"{v.actual_resolution[0]}x{v.actual_resolution[1]}",
        }

    # --------------------------------------------------------------- routes
    def setup_routes(self):
        app = self.app
        v = self.visualizer

        @app.route("/")
        def index():
            return Response(PAGE, mimetype="text/html")

        @app.route("/api/state")
        def state():
            return jsonify(self._state())

        @app.route("/api/debug")
        def debug():
            return jsonify(self._debug())

        @app.route("/api/current", methods=["POST"])
        def set_current():
            e = self._find_effect(request.json.get("name"))
            if e:
                v.current_function = e
                self.save_settings()
            return jsonify(ok=bool(e))

        @app.route("/api/step", methods=["POST"])
        def step():
            direction = int(request.json.get("dir", 1))
            effects = v.active_effects or v.drawing_functions
            try:
                idx = effects.index(v.current_function)
            except ValueError:
                idx = 0
            v.current_function = effects[(idx + direction) % len(effects)]
            self.save_settings()
            return jsonify(current=v.current_function.get_effect_name())

        @app.route("/api/active", methods=["POST"])
        def set_active():
            names = set(request.json.get("names", []))
            selected = [e for e in v.drawing_functions if e.get_effect_name() in names]
            if not selected:
                return jsonify(ok=False, error="Debe haber al menos un efecto activo."), 400
            v.active_effects = selected
            if v.current_function not in selected:
                v.current_function = selected[0]
            self.save_settings()
            return jsonify(ok=True, current=v.current_function.get_effect_name())

        @app.route("/api/mode", methods=["POST"])
        def set_mode():
            v.change_mode = request.json.get("mode", "static")
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/duration", methods=["POST"])
        def set_duration():
            v.effect_duration = float(request.json.get("seconds", 15)) * 1000
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/config", methods=["POST"])
        def set_config():
            data = request.json
            e = self._find_effect(data.get("effect"))
            if not e:
                return jsonify(ok=False), 404
            key, value = data.get("key"), data.get("value")
            cfg = e.get_config()
            if key not in cfg:
                return jsonify(ok=False), 400
            cfg[key] = int(round(float(value))) if isinstance(cfg[key], int) else round(float(value), 4)
            return jsonify(ok=True, value=cfg[key])

        @app.route("/api/config/save", methods=["POST"])
        def save_config():
            e = self._find_effect(request.json.get("effect"))
            if e:
                e.save_config_to_file(e.get_config_file())
            return jsonify(ok=bool(e))

        @app.route("/api/config/reload", methods=["POST"])
        def reload_config():
            e = self._find_effect(request.json.get("effect"))
            if e:
                e.load_config_from_file(e.get_config_file())
            return jsonify(ok=bool(e), effect=self._state())

        @app.route("/api/particles", methods=["POST"])
        def set_particles():
            data = request.json
            if "max" in data:
                v.particle_manager.max_particles = int(data["max"])
            if "speed" in data:
                v.particle_speed = float(data["speed"])
                v.particle_manager.particle_speed = float(data["speed"])
            if "size" in data:
                v.particle_size = float(data["size"])
                v.particle_manager.particle_size = float(data["size"])
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/sensitivity", methods=["POST"])
        def set_sensitivity():
            v.audioManager.set_sensitivity(float(request.json.get("value", 0.5)))
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/device", methods=["POST"])
        def set_device():
            v.audioManager.set_device(int(request.json.get("index")))
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/resolution", methods=["POST"])
        def set_resolution():
            w, h = map(int, request.json.get("resolution").split("x"))
            v.enqueue(lambda: v.change_resolution(w, h))
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/save_all", methods=["POST"])
        def save_all():
            for e in v.drawing_functions:
                try:
                    e.save_config_to_file(e.get_config_file())
                except Exception:
                    pass
            self.save_settings()
            return jsonify(ok=True)

        @app.route("/api/screen", methods=["POST"])
        def set_screen():
            idx = int(request.json.get("index", 0))
            v.enqueue(lambda: v.change_screen(idx))
            return jsonify(ok=True)

        @app.route("/api/fullscreen", methods=["POST"])
        def fullscreen():
            v.enqueue(v.toggle_fullscreen)
            return jsonify(ok=True)

        @app.route("/api/fps", methods=["POST"])
        def set_fps():
            v.fps = max(10, min(120, int(request.json.get("value", 60))))
            self.save_settings()
            return jsonify(ok=True, fps=v.fps)

        @app.route("/api/center", methods=["POST"])
        def set_center():
            data = request.json
            ci = v.center_image
            if "max_scale" in data:
                ci.set_max_scale(data["max_scale"])
            if "speed" in data:
                ci.set_speed(data["speed"])
            if "size" in data:
                ci.set_base_size(data["size"])
            if data.get("image"):
                path = self._image_path(data["image"])
                # La carga toca superficies de pygame -> hazla en el hilo de render
                v.enqueue(lambda p=path: ci.set_image_by_path(p))
            self.save_settings()
            return jsonify(ok=True)

    # ------------------------------------------------------------------ run
    def _lan_ip(self):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def run(self):
        lan = self._lan_ip()
        print(f"[WebControlPanel] En este PC:  http://localhost:{self.port}")
        print(f"[WebControlPanel] En el movil: http://{lan}:{self.port}  (misma red Wi-Fi)")

        # Abre el navegador salvo en modo headless (Raspberry Pi sin escritorio):
        # exporta VISUALIZER_NO_BROWSER=1 para desactivarlo.
        if not os.environ.get("VISUALIZER_NO_BROWSER"):
            def _open():
                try:
                    webbrowser.open(f"http://localhost:{self.port}")
                except Exception:
                    pass
            threading.Timer(1.0, _open).start()

        self.app.run(host=self.host, port=self.port, debug=False,
                     use_reloader=False, threaded=True)


PAGE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Audio Visualizer - Panel Web</title>
<style>
  :root { --bg:#0f1115; --panel:#1a1d24; --panel2:#232732; --acc:#5b8cff; --txt:#e6e9ef; --mut:#9aa3b2; --ok:#3ad29f; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--txt); }
  header { padding:14px 20px; background:var(--panel); border-bottom:1px solid #2a2f3a; display:flex; align-items:center; gap:16px; position:sticky; top:0; z-index:10;}
  header h1 { font-size:16px; margin:0; letter-spacing:.3px; }
  .pill { background:var(--panel2); border-radius:20px; padding:4px 12px; font-size:12px; color:var(--mut); }
  .wrap { max-width:1100px; margin:0 auto; padding:20px; display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; }
  .card { background:var(--panel); border:1px solid #262b36; border-radius:12px; padding:16px; }
  .card h2 { margin:0 0 12px; font-size:13px; text-transform:uppercase; letter-spacing:.6px; color:var(--mut); }
  .full { grid-column:1 / -1; }
  label { display:block; font-size:13px; margin:10px 0 4px; color:var(--mut); }
  select, input[type=number] { width:100%; background:var(--panel2); border:1px solid #333a48; color:var(--txt); border-radius:8px; padding:8px; font-size:14px; }
  input[type=range] { width:100%; accent-color:var(--acc); }
  button { background:var(--panel2); color:var(--txt); border:1px solid #333a48; border-radius:8px; padding:8px 14px; cursor:pointer; font-size:13px; }
  button:hover { border-color:var(--acc); }
  button.primary { background:var(--acc); border-color:var(--acc); color:#fff; }
  .row { display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
  .row > * { flex:0 0 auto; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
  .checks { display:grid; grid-template-columns:1fr 1fr; gap:6px 14px; }
  .checks label { display:flex; align-items:center; gap:8px; margin:2px 0; color:var(--txt); cursor:pointer; }
  .param { margin:10px 0; }
  .param .top { display:flex; justify-content:space-between; font-size:13px; }
  .param .val { color:var(--acc); font-variant-numeric:tabular-nums; }
  .effect-tabs { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px; }
  .effect-tabs button.active { background:var(--acc); border-color:var(--acc); color:#fff; }
  .dbg { display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:8px; }
  .dbg div { background:var(--panel2); border-radius:8px; padding:8px 10px; }
  .dbg .k { font-size:11px; color:var(--mut); text-transform:uppercase; }
  .dbg .v { font-size:18px; font-weight:600; font-variant-numeric:tabular-nums; }
  /* ---- Movil ---- */
  @media (max-width:640px) {
    header { padding:10px 14px; gap:8px; flex-wrap:wrap; }
    header h1 { font-size:15px; }
    .pill { padding:3px 10px; font-size:11px; }
    .wrap { padding:12px; gap:12px; grid-template-columns:1fr; }
    .card { padding:14px; border-radius:14px; }
    .checks { grid-template-columns:1fr; }
    .grid2 { grid-template-columns:1fr; }
    /* Controles mas grandes para el dedo */
    select, input[type=number] { font-size:16px; padding:12px; }
    button { padding:12px 16px; font-size:15px; }
    .checks label { padding:6px 0; font-size:15px; }
    input[type=range] { height:28px; }
    .effect-tabs button { padding:10px 12px; }
    .dbg { grid-template-columns:repeat(auto-fit,minmax(90px,1fr)); }
  }
  /* Areas tactiles mayores en cualquier pantalla tactil */
  @media (pointer:coarse) {
    input[type=range] { height:26px; }
  }
</style>
</head>
<body>
<header>
  <h1>🎵 Audio Visualizer</h1>
  <span class="pill" id="pill-current">—</span>
  <span class="pill" id="pill-fps">FPS —</span>
</header>
<div class="wrap">

  <div class="card">
    <h2>General</h2>
    <label>Efecto actual</label>
    <select id="current"></select>
    <div class="row" style="margin-top:10px">
      <button onclick="step(-1)">◀ Anterior</button>
      <button onclick="step(1)">Siguiente ▶</button>
    </div>
    <label>Modo de cambio</label>
    <select id="mode">
      <option value="static">static (fijo)</option>
      <option value="random">random</option>
      <option value="sequential">sequential</option>
    </select>
    <label>Duracion por efecto (s)</label>
    <input type="number" id="duration" min="1" step="1">
  </div>

  <div class="card">
    <h2>Pantalla</h2>
    <label>Resolucion de la ventana</label>
    <select id="resolution"></select>
    <label>Monitor</label>
    <select id="screen"></select>
    <div class="param" style="margin-top:12px"><div class="top"><span>Limite de FPS (bajalo en Raspberry Pi)</span><span class="val" id="fps-v"></span></div>
      <input type="range" id="fps" min="10" max="60" step="5"></div>
    <div class="row" style="margin-top:12px">
      <button onclick="post('/api/fullscreen',{})">Pantalla completa (on/off)</button>
    </div>
    <label style="margin-top:14px">🎤 Microfono / entrada de audio</label>
    <select id="device"></select>
    <label style="margin-top:14px">Sensibilidad de sonido</label>
    <div class="param"><div class="top"><span></span><span class="val" id="sens-v"></span></div>
      <input type="range" id="sens" min="0" max="5" step="0.05"></div>
  </div>

  <div class="card">
    <h2>Efectos activos (random / sequential)</h2>
    <div class="checks" id="checks"></div>
    <div class="row" style="margin-top:12px">
      <button onclick="setAll(true)">Activar todos</button>
      <button onclick="setAll(false)">Desactivar todos</button>
    </div>
  </div>

  <div class="card">
    <h2>Particulas</h2>
    <label>Maximo</label>
    <input type="number" id="p-max" min="0" step="1">
    <div class="param"><div class="top"><span>Velocidad</span><span class="val" id="p-speed-v"></span></div>
      <input type="range" id="p-speed" min="0.1" max="10" step="0.1"></div>
    <div class="param"><div class="top"><span>Tamano</span><span class="val" id="p-size-v"></span></div>
      <input type="range" id="p-size" min="1" max="100" step="1"></div>
  </div>

  <div class="card">
    <h2>Imagen central</h2>
    <label>Imagen</label>
    <select id="ci-image"></select>
    <div class="param"><div class="top"><span>Potencia de agrandado</span><span class="val" id="ci-scale-v"></span></div>
      <input type="range" id="ci-scale" min="1" max="4" step="0.05"></div>
    <div class="param"><div class="top"><span>Velocidad de agrandado</span><span class="val" id="ci-speed-v"></span></div>
      <input type="range" id="ci-speed" min="0.02" max="0.5" step="0.01"></div>
    <div class="param"><div class="top"><span>Tamano base</span><span class="val" id="ci-size-v"></span></div>
      <input type="range" id="ci-size" min="0.1" max="3" step="0.05"></div>
    <p style="color:var(--mut);font-size:12px;margin:8px 0 0">Coloca tus imagenes en la carpeta <b>images/</b> del proyecto para que aparezcan aqui.</p>
  </div>

  <div class="card full">
    <h2>Configuracion por efecto</h2>
    <div class="effect-tabs" id="effect-tabs"></div>
    <div id="effect-config"></div>
    <div class="row" style="margin-top:14px">
      <button class="primary" id="btn-save">Guardar este efecto</button>
      <button id="btn-reload">Restablecer (del archivo)</button>
      <button id="btn-saveall">💾 Guardar TODO</button>
    </div>
    <p style="color:var(--mut);font-size:12px;margin:10px 0 0">Los ajustes generales (modo, volumen, micro, resolucion, efectos activos...) se guardan solos y se recuerdan al reiniciar. "Guardar TODO" ademas fija la config de todos los efectos.</p>
  </div>

  <div class="card full">
    <h2>Debug (en vivo)</h2>
    <div class="dbg" id="dbg"></div>
  </div>

</div>
<script>
let STATE = null, selEffect = null;
const $ = s => document.querySelector(s);
async function post(url, body){ const r = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})}); return r.json().catch(()=>({})); }
async function get(url){ return (await fetch(url)).json(); }

function opt(v,t){ const o=document.createElement('option'); o.value=v; o.textContent=t||v; return o; }

async function load(){
  STATE = await get('/api/state');
  const cur=$('#current'); cur.innerHTML='';
  STATE.effects.forEach(e=>cur.appendChild(opt(e.name)));
  cur.value=STATE.current;
  $('#mode').value=STATE.mode;
  $('#duration').value=STATE.duration;

  const res=$('#resolution'); res.innerHTML='';
  STATE.resolutions.forEach(r=>res.appendChild(opt(r)));
  res.value=STATE.resolution;

  const scr=$('#screen'); scr.innerHTML='';
  for(let i=0;i<STATE.screens;i++) scr.appendChild(opt(i, 'Monitor '+(i+1)));

  const dev=$('#device'); dev.innerHTML='';
  STATE.devices.forEach(d=>dev.appendChild(opt(d.index, d.name)));
  dev.value=STATE.device;

  $('#fps').value=STATE.fps; $('#fps-v').textContent=STATE.fps;
  $('#sens').value=STATE.sensitivity; $('#sens-v').textContent=(+STATE.sensitivity).toFixed(2);
  $('#p-max').value=STATE.particles.max;
  $('#p-speed').value=STATE.particles.speed; $('#p-speed-v').textContent=(+STATE.particles.speed).toFixed(1);
  $('#p-size').value=STATE.particles.size; $('#p-size-v').textContent=(+STATE.particles.size).toFixed(0);

  const ci=STATE.center; const cim=$('#ci-image'); cim.innerHTML='';
  ci.images.forEach(n=>cim.appendChild(opt(n)));
  cim.value=ci.image;
  $('#ci-scale').value=ci.max_scale; $('#ci-scale-v').textContent=(+ci.max_scale).toFixed(2);
  $('#ci-speed').value=ci.speed; $('#ci-speed-v').textContent=(+ci.speed).toFixed(2);
  $('#ci-size').value=ci.size; $('#ci-size-v').textContent=(+ci.size).toFixed(2);

  buildChecks(); buildTabs();
  if(!selEffect || !STATE.effects.find(e=>e.name===selEffect)) selEffect=STATE.effects[0].name;
  buildConfig(selEffect);
}

function buildChecks(){
  const c=$('#checks'); c.innerHTML='';
  STATE.effects.forEach(e=>{
    const l=document.createElement('label');
    const cb=document.createElement('input'); cb.type='checkbox'; cb.checked=e.active; cb.dataset.name=e.name;
    cb.onchange=applyActive;
    l.appendChild(cb); l.appendChild(document.createTextNode(e.name)); c.appendChild(l);
  });
}
async function applyActive(){
  const names=[...document.querySelectorAll('#checks input:checked')].map(x=>x.dataset.name);
  const r=await post('/api/active',{names});
  if(r.ok===false){ alert(r.error||'Error'); load(); }
}
function setAll(v){ document.querySelectorAll('#checks input').forEach(cb=>cb.checked=v); applyActive(); }

function buildTabs(){
  const t=$('#effect-tabs'); t.innerHTML='';
  STATE.effects.forEach(e=>{
    const b=document.createElement('button'); b.textContent=e.name;
    if(e.name===selEffect) b.classList.add('active');
    b.onclick=()=>{ selEffect=e.name; buildTabs(); buildConfig(e.name); };
    t.appendChild(b);
  });
}
function buildConfig(name){
  const e=STATE.effects.find(x=>x.name===name);
  const box=$('#effect-config'); box.innerHTML='';
  if(!e.params.length){ box.innerHTML='<p style="color:var(--mut)">Este efecto no tiene parametros configurables.</p>'; return; }
  e.params.forEach(p=>{
    const wrap=document.createElement('div'); wrap.className='param';
    const val=p.is_int?p.value:(+p.value).toFixed(3);
    wrap.innerHTML=`<div class="top"><span>${p.label||p.key}</span><span class="val">${val}</span></div>`;
    const r=document.createElement('input'); r.type='range'; r.min=p.min; r.max=p.max; r.step=p.step; r.value=p.value;
    const out=wrap.querySelector('.val');
    r.oninput=()=>{ out.textContent = p.is_int? Math.round(r.value) : (+r.value).toFixed(3); };
    r.onchange=()=>post('/api/config',{effect:name,key:p.key,value:+r.value});
    wrap.appendChild(r); box.appendChild(wrap);
  });
}

// listeners
$('#current').onchange=e=>post('/api/current',{name:e.target.value});
$('#mode').onchange=e=>post('/api/mode',{mode:e.target.value});
$('#duration').onchange=e=>post('/api/duration',{seconds:+e.target.value});
$('#resolution').onchange=e=>post('/api/resolution',{resolution:e.target.value});
$('#screen').onchange=e=>post('/api/screen',{index:+e.target.value});
$('#device').onchange=e=>post('/api/device',{index:+e.target.value});
$('#fps').oninput=e=>{ $('#fps-v').textContent=e.target.value; };
$('#fps').onchange=e=>post('/api/fps',{value:+e.target.value});
$('#sens').oninput=e=>{ $('#sens-v').textContent=(+e.target.value).toFixed(2); };
$('#sens').onchange=e=>post('/api/sensitivity',{value:+e.target.value});
$('#p-max').onchange=e=>post('/api/particles',{max:+e.target.value});
$('#p-speed').oninput=e=>{ $('#p-speed-v').textContent=(+e.target.value).toFixed(1); };
$('#p-speed').onchange=e=>post('/api/particles',{speed:+e.target.value});
$('#p-size').oninput=e=>{ $('#p-size-v').textContent=(+e.target.value).toFixed(0); };
$('#p-size').onchange=e=>post('/api/particles',{size:+e.target.value});
$('#ci-image').onchange=e=>post('/api/center',{image:e.target.value});
$('#ci-scale').oninput=e=>{ $('#ci-scale-v').textContent=(+e.target.value).toFixed(2); };
$('#ci-scale').onchange=e=>post('/api/center',{max_scale:+e.target.value});
$('#ci-speed').oninput=e=>{ $('#ci-speed-v').textContent=(+e.target.value).toFixed(2); };
$('#ci-speed').onchange=e=>post('/api/center',{speed:+e.target.value});
$('#ci-size').oninput=e=>{ $('#ci-size-v').textContent=(+e.target.value).toFixed(2); };
$('#ci-size').onchange=e=>post('/api/center',{size:+e.target.value});
$('#btn-save').onclick=()=>post('/api/config/save',{effect:selEffect}).then(()=>flash('#btn-save','Guardado ✓'));
$('#btn-reload').onclick=async()=>{ await post('/api/config/reload',{effect:selEffect}); await load(); };
$('#btn-saveall').onclick=()=>post('/api/save_all',{}).then(()=>flash('#btn-saveall','Todo guardado ✓'));
async function step(d){ const r=await post('/api/step',{dir:d}); $('#current').value=r.current; }
function flash(sel,txt){ const b=$(sel),o=b.textContent; b.textContent=txt; setTimeout(()=>b.textContent=o,1200); }

async function poll(){
  try{
    const d=await get('/api/debug');
    $('#pill-current').textContent=d.current;
    $('#pill-fps').textContent='FPS '+d.fps;
    if($('#current').value!==d.current) $('#current').value=d.current;
    const items={FPS:d.fps,Efecto:d.current,Modo:d.mode,'Tiempo':d.time_left==null?'—':d.time_left+' s',
      Particulas:d.particles,Amplitud:d.amplitude,'CPU %':d.cpu,Sensib:d.sensitivity,Volumen:d.volume,Resol:d.resolution};
    $('#dbg').innerHTML=Object.entries(items).map(([k,v])=>`<div><div class="k">${k}</div><div class="v">${v}</div></div>`).join('');
  }catch(e){}
}
load(); setInterval(poll, 600);
</script>
</body>
</html>"""
