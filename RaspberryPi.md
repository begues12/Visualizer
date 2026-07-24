# Audio Visualizer en Raspberry Pi 5

Guía para ejecutar y controlar el visualizador en una Raspberry Pi 5
(Raspberry Pi OS Bookworm, 64-bit, Python 3.11+).

## 1. Dependencias del sistema

```bash
sudo apt update
sudo apt install -y python3-venv python3-dev portaudio19-dev \
    libsdl2-2.0-0 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0
```

- `portaudio19-dev` → necesario para PyAudio (captura de audio).
- `libsdl2-*` → runtime de pygame.

## 2. Instalar el proyecto

```bash
cd ~/Visualizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pi OS usa **piwheels** por defecto, así que `pygame`, `numpy` y compañía se instalan
ya compilados para ARM (rápido, sin build desde código).

## 3. Ejecutar

Con pantalla/HDMI conectada (proyector, TV, monitor) desde el escritorio de la Pi:

```bash
source .venv/bin/activate
python Visualizer2.py
```

- Se abre la ventana pequeña del visualizador.
- El panel web queda en `http://<IP-de-la-Pi>:5000` → contrólalo desde el **móvil** o
  cualquier equipo de la misma red.

### Modo headless / sin navegador en la Pi

Si la Pi no tiene navegador (o la controlas solo desde el móvil), evita que intente
abrir uno:

```bash
export VISUALIZER_NO_BROWSER=1
python Visualizer2.py
```

## 4. Ajustar el rendimiento (importante en la Pi)

Todo esto se controla **en caliente desde el panel web** y se guarda solo:

- **Límite de FPS** (tarjeta *Pantalla*): bájalo a **30 fps** en la Pi. Reduce mucho
  el uso de CPU con un resultado igual de fluido a la vista.
- **Resolución**: usa **640×360** o **854×480**. Cuanto menor, más rápido.
- **Efectos**: los de línea/haz (Lightning, Concert Lasers, Laser Storm, Shockwave)
  y los de partículas rinden bien; si algún efecto va justo, baja su detalle
  (menos haces, menos partículas) desde *Config. Efecto*.

Internamente los efectos reutilizan sus superficies de dibujo entre frames
(no reservan memoria cada frame), lo que ayuda especialmente en ARM.

## 5. Elegir la entrada de audio

En el panel, desplegable **🎤 Micrófono / entrada de audio**:

```bash
# Ver dispositivos ALSA disponibles
arecord -l
```

Para visualizar lo que **suena en la Pi** (no un micro) necesitas un *loopback* de audio
(p. ej. `snd-aloop` o enrutar con PulseAudio/PipeWire). Un micro USB funciona directo.

## 6. Arranque automático (opcional)

Para que arranque sola al encender (kiosko de concierto), crea un servicio systemd de
usuario o añádelo al autostart del escritorio apuntando a:

```bash
cd ~/Visualizer && ./.venv/bin/python Visualizer2.py
```

## Notas

- El firewall no suele bloquear en Pi OS; si usas `ufw`, abre el puerto: `sudo ufw allow 5000`.
- Los ajustes se guardan en `config/settings.json` y la config de cada efecto en
  `Effects/configs/*.json`.
