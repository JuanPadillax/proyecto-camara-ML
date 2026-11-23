import os
import time
import platform
import numpy as np
from ultralytics import YOLO
import pyautogui

pyautogui.PAUSE = 0.05

def send_presentation_command(command_type):
    if command_type == 'next':
        pyautogui.press('right')
    elif command_type == 'prev':
        pyautogui.press('left')


def send_music_command(command_type):
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
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) + 8)' 2>/dev/null &")
        elif command_type == 'volumedown':
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) - 8)' 2>/dev/null &")
    else:
        if command_type == 'next':
            pyautogui.press('nexttrack')
        elif command_type == 'prev':
            pyautogui.press('prevtrack')
        elif command_type == 'playpause':
            pyautogui.press('playpause')
        elif command_type == 'volumeup':
            pyautogui.press('volumeup')
        elif command_type == 'volumedown':
            pyautogui.press('volumedown')


class DualModeController:
    def __init__(self, mode_cooldown_sec=2.2, action_cooldown_sec=0.7):
        self.model = YOLO('yolov8n-pose.pt')
        self.last_action_time = 0
        self.last_mode_toggle_time = 0
        self.mode_cooldown_sec = mode_cooldown_sec
        self.action_cooldown_sec = action_cooldown_sec
        self.last_action_name = "Esperando..."
        self.mode = 'PRESENTATION'

    def toggle_mode(self, current_time):
        self.mode = 'MUSIC' if self.mode == 'PRESENTATION' else 'PRESENTATION'
        self.last_mode_toggle_time = current_time
        self.last_action_time = current_time
        self.last_action_name = f"CAMBIO A MODO {self.mode}"
        print(f"-> MODO CAMBIADO A: {self.mode}")

    def process_frame(self, frame):
        h, w, _ = frame.shape
        current_conf = 0.22
        y_max_limit = h * 0.85  # Permite detectar tus brazos aunque estés de pie alejándote de la cámara

        results = self.model(frame, verbose=False, conf=current_conf)[0]
        action_triggered = None
        current_time = time.time()
        
        in_action_cooldown = (current_time - self.last_action_time) < self.action_cooldown_sec
        in_mode_cooldown = (current_time - self.last_mode_toggle_time) < self.mode_cooldown_sec
        active_hand_pos = None

        if results.keypoints is not None and len(results.keypoints) > 0:
            kpts = results.keypoints.xy[0].cpu().numpy()
            confs = results.keypoints.conf[0].cpu().numpy() if results.keypoints.conf is not None else None

            if len(kpts) >= 11:
                # Keypoints: 0: Nariz, 1: Ojo Izq, 2: Ojo Der, 9: Muñeca Izq, 10: Muñeca Der
                nose_x, nose_y = kpts[0]
                l_eye_x, l_eye_y = kpts[1]
                r_eye_x, r_eye_y = kpts[2]
                
                nose_conf = confs[0] if confs is not None else 1.0
                l_eye_conf = confs[1] if confs is not None else 1.0
                r_eye_conf = confs[2] if confs is not None else 1.0

                lw_x, lw_y = kpts[9]
                rw_x, rw_y = kpts[10]
                lw_conf = confs[9] if confs is not None else 1.0
                rw_conf = confs[10] if confs is not None else 1.0

                # --------------------------------------------------------
                # DETECCION FACIAL ESCALABLE Y RELATIVA AL TAMAÑO DEL ROSTRO
                # --------------------------------------------------------
                looking_up = False
                head_tilt_action = None

                if nose_conf > 0.2 and l_eye_conf > 0.2 and r_eye_conf > 0.2:
                    # Distancia real en píxeles entre ambos ojos (Escala del rostro)
                    eye_dist = np.hypot(l_eye_x - r_eye_x, l_eye_y - r_eye_y)

                    if eye_dist > 3:  # Validar que el rostro esté dentro del marco
                        eyes_mid_y = (l_eye_y + r_eye_y) / 2.0
                        nose_vertical_diff = nose_y - eyes_mid_y
                        
                        # Ratios independientes de la distancia a la cámara
                        pitch_ratio = nose_vertical_diff / eye_dist
                        roll_ratio = (l_eye_y - r_eye_y) / eye_dist

                        # Mirar hacia arriba: La nariz se eleva recortando la distancia 2D con los ojos
                        looking_up = (pitch_ratio < 0.22)

                        # Inclinación lateral (Solo activa en Modo Música)
                        if self.mode == 'MUSIC' and not looking_up:
                            if roll_ratio < -0.32:
                                head_tilt_action = 'volumeup'
                            elif roll_ratio > 0.32:
                                head_tilt_action = 'volumedown'

                # --------------------------------------------------------
                # EJECUCION DE GESTOS
                # --------------------------------------------------------
                if looking_up and not in_mode_cooldown:
                    self.toggle_mode(current_time)
                    action_triggered = f"MODO: {self.mode}"

                elif head_tilt_action and not in_action_cooldown and not in_mode_cooldown:
                    send_music_command(head_tilt_action)
                    self.last_action_time = current_time
                    action_triggered = "VOLUMEN +" if head_tilt_action == 'volumeup' else "VOLUMEN -"

                elif not looking_up and not head_tilt_action:
                    candidates = []
                    for wx, wy, conf in [(lw_x, lw_y, lw_conf), (rw_x, rw_y, rw_conf)]:
                        if conf > current_conf and wx > 0 and wy > 0 and wy < y_max_limit:
                            candidates.append((wy, wx))

                    if candidates:
                        candidates.sort()
                        best_y, best_x = candidates[0]
                        active_hand_pos = (int(best_x), int(best_y))

                        if not in_action_cooldown and not in_mode_cooldown:
                            if self.mode == 'PRESENTATION':
                                if best_x < w * 0.50:
                                    send_presentation_command('prev')
                                    action_triggered = "DIAPO ANTERIOR (<-)"
                                else:
                                    send_presentation_command('next')
                                    action_triggered = "DIAPO SIGUIENTE (->)"

                            elif self.mode == 'MUSIC':
                                left_bound = w * 0.333
                                right_bound = w * 0.666

                                if best_x < left_bound:
                                    send_music_command('prev')
                                    action_triggered = "TRACK ANTERIOR"
                                elif best_x > right_bound:
                                    send_music_command('next')
                                    action_triggered = "TRACK SIGUIENTE"
                                else:
                                    send_music_command('playpause')
                                    action_triggered = "PLAY / PAUSA SPOTIFY"

                            if action_triggered:
                                self.last_action_time = current_time
                                self.last_action_name = action_triggered

        annotated_frame = results.plot()
        is_busy = in_action_cooldown or in_mode_cooldown
        return annotated_frame, self.last_action_name, is_busy, active_hand_pos, self.mode