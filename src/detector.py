import os
import time
import platform
from ultralytics import YOLO
import pyautogui

pyautogui.PAUSE = 0.05

def send_presentation_command(command_type):
    """Comandos exclusivos para Diapositivas / PDFs (Sin tocar Spotify)."""
    if command_type == 'next':
        pyautogui.press('right')
    elif command_type == 'prev':
        pyautogui.press('left')
    elif command_type == 'playpause':
        pyautogui.press('space')


def send_music_command(command_type):
    """Comandos exclusivos para Control de Música (Spotify / Apple Music)."""
    system_os = platform.system()

    if system_os == 'Darwin':  # macOS
        if command_type == 'next':
            os.system("osascript -e 'if application \"Spotify\" is running then tell application \"Spotify\" to next track' 2>/dev/null &")
        elif command_type == 'prev':
            os.system("osascript -e 'if application \"Spotify\" is running then tell application \"Spotify\" to previous track' 2>/dev/null &")
        elif command_type == 'playpause':
            cmd = """
            osascript -e '
            if application "Spotify" is running then
                tell application "Spotify" to playpause
            else if application "Music" is running then
                tell application "Music" to playpause
            else
                do shell script "open -a Spotify"
            end if' 2>/dev/null &
            """
            os.system(cmd)
        elif command_type == 'volumeup':
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) + 10)' 2>/dev/null &")
    else:
        # Windows / Linux
        if command_type == 'next':
            pyautogui.press('nexttrack')
        elif command_type == 'prev':
            pyautogui.press('prevtrack')
        elif command_type == 'playpause':
            pyautogui.press('playpause')
        elif command_type == 'volumeup':
            pyautogui.press('volumeup')


class DualModeController:
    def __init__(self, cooldown_seconds=1.0):
        self.model = YOLO('yolov8n-pose.pt')
        self.cooldown_seconds = cooldown_seconds
        self.last_action_time = 0
        self.last_action_name = "Esperando..."

        # Estado inicial: PRESENTATION o MUSIC
        self.mode = 'PRESENTATION'

    def toggle_mode(self):
        self.mode = 'MUSIC' if self.mode == 'PRESENTATION' else 'PRESENTATION'
        self.last_action_name = f"CAMBIO A MODO {self.mode}"
        print(f"-> MODO CAMBIADO A: {self.mode}")

    def process_frame(self, frame):
        h, w, _ = frame.shape
        results = self.model(frame, verbose=False, conf=0.28)[0]
        action_triggered = None
        current_time = time.time()
        in_cooldown = (current_time - self.last_action_time) < self.cooldown_seconds
        active_hand_pos = None

        if results.keypoints is not None and len(results.keypoints) > 0:
            kpts = results.keypoints.xy[0].cpu().numpy()
            confs = results.keypoints.conf[0].cpu().numpy() if results.keypoints.conf is not None else None

            if len(kpts) >= 11:
                nose_y = kpts[0][1] if (confs is not None and confs[0] > 0.25) else 0
                
                # Coordenadas y confianzas de Hombros y Muñecas
                ls_y, rs_y = kpts[5][1], kpts[6][1]
                lw_x, lw_y = kpts[9]
                rw_x, rw_y = kpts[10]

                lw_conf = confs[9] if confs is not None else 1.0
                rw_conf = confs[10] if confs is not None else 1.0
                ls_conf = confs[5] if confs is not None else 1.0
                rs_conf = confs[6] if confs is not None else 1.0

                # --------------------------------------------------------
                # GESTO DE CAMBIO DE MODO: AMBAS MANOS LEVANTADAS
                # --------------------------------------------------------
                both_hands_up = (
                    lw_conf > 0.3 and rw_conf > 0.3 and 
                    lw_y > 0 and rw_y > 0 and 
                    (lw_y < h * 0.45 and rw_y < h * 0.45)
                )

                if both_hands_up and not in_cooldown:
                    self.toggle_mode()
                    self.last_action_time = current_time
                    action_triggered = f"MODO: {self.mode}"

                # --------------------------------------------------------
                # PROCESAMIENTO DE GESTOS SEGUN MODO ACTIVO
                # --------------------------------------------------------
                elif not both_hands_up:
                    candidates = []
                    for wx, wy, conf in [(lw_x, lw_y, lw_conf), (rw_x, rw_y, rw_conf)]:
                        if conf > 0.28 and wx > 0 and wy > 0 and wy < h * 0.75:
                            candidates.append((wy, wx))

                    if candidates:
                        candidates.sort()
                        best_y, best_x = candidates[0]
                        active_hand_pos = (int(best_x), int(best_y))

                        if not in_cooldown:
                            # 1. MODO PRESENTACION
                            if self.mode == 'PRESENTATION':
                                if best_x < w * 0.40:
                                    send_presentation_command('prev')
                                    action_triggered = "DIAPO ANTERIOR (<-)"
                                elif best_x > w * 0.60:
                                    send_presentation_command('next')
                                    action_triggered = "DIAPO SIGUIENTE (->)"
                                else:
                                    send_presentation_command('playpause')
                                    action_triggered = "PAUSA / ESPACIO"

                            # 2. MODO MUSICA
                            elif self.mode == 'MUSIC':
                                if nose_y > 0 and best_y < nose_y:
                                    send_music_command('volumeup')
                                    action_triggered = "VOLUMEN +"
                                elif best_x < w * 0.40:
                                    send_music_command('prev')
                                    action_triggered = "TRACK ANTERIOR"
                                elif best_x > w * 0.60:
                                    send_music_command('next')
                                    action_triggered = "TRACK SIGUIENTE"
                                else:
                                    send_music_command('playpause')
                                    action_triggered = "PLAY / PAUSA SPOTIFY"

                            if action_triggered:
                                self.last_action_time = current_time
                                self.last_action_name = action_triggered

        annotated_frame = results.plot()
        return annotated_frame, self.last_action_name, in_cooldown, active_hand_pos, self.mode