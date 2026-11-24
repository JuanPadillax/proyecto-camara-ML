Comandos de Configuración e Instalación
1. Ubicarse en la raíz del proyecto

2. Crear el entorno virtual (si se requiere rehacer)
python3 -m venv venv

3. Activar el entorno virtual
macOS / Linux: source venv/bin/activate

Windows (PowerShell / CMD): 
.\venv\Scripts\activate

4. Instalar todas las dependencias necesarias
pip install ultralytics sounddevice pyautogui opencv-python numpy

Ejecutar la aplicación principal
python main.py

Salir del entorno virtual al finalizar
deactivate

Gestos Faciales y Cabeza
Mirar hacia Arriba: Cambiar entre Modo Presentación y Modo Música (Cooldown: 2.2s).

Inclinar Cabeza a la Derecha: Subir Volumen (Volumen +) — Exclusivo Modo Música.

Inclinar Cabeza a la Izquierda: Bajar Volumen (Volumen -) — Exclusivo Modo Música.

Gestos con Manos (Cámara)
Mano al sector Izquierdo:

Modo Presentación: Diapositiva Anterior (<-)

Modo Música: Canción Anterior

Mano al sector Derecho:

Modo Presentación: Diapositiva Siguiente (->)

Modo Música: Canción Siguiente

Mano al sector Centro:

Modo Música: Play / Pausa (Abre Spotify automáticamente si está cerrado)