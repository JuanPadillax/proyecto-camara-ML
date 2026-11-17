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

Comandos de Ejecución
Ejecutar la aplicación principal
python main.py

Salir del entorno virtual al finalizar
deactivate

Controles y Gestos del Sistema

Controles por Teclado
m: Alternar entre Modo Presentación (Azul) y Modo Música (Verde).
q: Salir de la aplicación y cerrar ventanas/audio.

Gestos con la Cámara
Mano al sector Izquierdo:
Modo Presentación: Diapositiva Anterior (<-)
Modo Música: Canción Anterior

Mano al sector Derecho:
Modo Presentación: Diapositiva Siguiente (->)
Modo Música: Canción Siguiente

Mano al sector Centro:
Modo Música: Play / Pausa (Abre Spotify si está cerrado)

Mano sobre la Cabeza:
Modo Presentación: Sin acción asignada
Modo Música: Subir Volumen

Ambas Manos Levantadas:
Modo Presentación: Cambiar a Modo Música
Modo Música: Cambiar a Modo Presentación