import cv2
from src.detector import DualModeController
from src.audio_detector import AudioDetector

def main():
    cap = cv2.VideoCapture(0)
    controller = DualModeController(cooldown_seconds=1.0)
    audio_detector = AudioDetector()

    audio_detector.start()

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # 1. Procesar modelo
        annotated_frame, action_name, in_cooldown, active_hand_pos, current_mode = controller.process_frame(frame)

        # 2. RENDERIZAR SEGUN EL MODO ACTIVO
        if current_mode == 'PRESENTATION':
            # Header Modo Presentación (Azul)
            cv2.rectangle(annotated_frame, (0, 0), (w, 35), (200, 80, 0), -1)
            cv2.putText(annotated_frame, "MODO PRESENTACION DIAPOSITIVAS (Ambas manos arriba = Cambiar Modo)", 
                        (15, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

            # Zonas Diapos
            cv2.rectangle(annotated_frame, (0, 35), (int(w * 0.40), h), (255, 100, 0), 2)
            cv2.putText(annotated_frame, "DIAPO ANTERIOR", (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)

            cv2.rectangle(annotated_frame, (int(w * 0.40), 35), (int(w * 0.60), h), (0, 255, 255), 2)
            cv2.putText(annotated_frame, "PAUSA / ESPACIO", (int(w * 0.40) + 10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

            cv2.rectangle(annotated_frame, (int(w * 0.60), 35), (w, h), (0, 255, 0), 2)
            cv2.putText(annotated_frame, "DIAPO SIGUIENTE", (int(w * 0.60) + 10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        elif current_mode == 'MUSIC':
            # Header Modo Música (Verde Spotify)
            cv2.rectangle(annotated_frame, (0, 0), (w, 35), (0, 150, 0), -1)
            cv2.putText(annotated_frame, "MODO MUSICA SPOTIFY (Mano sobre cabeza = Volumen +)", 
                        (15, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

            # Zonas Música
            cv2.rectangle(annotated_frame, (0, 35), (int(w * 0.40), h), (0, 200, 0), 2)
            cv2.putText(annotated_frame, "TRACK ANTERIOR", (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)

            cv2.rectangle(annotated_frame, (int(w * 0.40), 35), (int(w * 0.60), h), (0, 255, 255), 2)
            cv2.putText(annotated_frame, "PLAY / PAUSA", (int(w * 0.40) + 10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

            cv2.rectangle(annotated_frame, (int(w * 0.60), 35), (w, h), (0, 255, 0), 2)
            cv2.putText(annotated_frame, "TRACK SIGUIENTE", (int(w * 0.60) + 10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Marcador visual en la mano activa
        if active_hand_pos:
            circle_color = (255, 150, 0) if current_mode == 'PRESENTATION' else (0, 255, 0)
            cv2.circle(annotated_frame, active_hand_pos, 16, circle_color, -1)
            cv2.circle(annotated_frame, active_hand_pos, 22, (255, 255, 255), 3)

        # 3. Widget de Audio ML (Micrófono)
        mic_status = audio_detector.audio_status
        bar_w = audio_detector.get_bar_length(max_width=120)
        status_color = (0, 255, 0) if "MUSICA" in mic_status else ((0, 255, 255) if "VOZ" in mic_status else (150, 150, 150))
        
        cv2.rectangle(annotated_frame, (w - 230, 45), (w - 10, 105), (30, 30, 30), -1)
        cv2.rectangle(annotated_frame, (w - 230, 45), (w - 10, 105), status_color, 2)
        cv2.putText(annotated_frame, f"MIC: {mic_status}", (w - 220, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.45, status_color, 2)
        cv2.rectangle(annotated_frame, (w - 220, 80), (w - 220 + bar_w, 92), status_color, -1)

        # 4. HUD Inferior
        panel_color = (0, 0, 180) if in_cooldown else (40, 40, 40)
        cv2.rectangle(annotated_frame, (0, h - 45), (w, h), panel_color, -1)
        cv2.putText(annotated_frame, f"MODO ACTIVO: {current_mode} | Accion: {action_name}", (20, h - 16), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        cv2.imshow('ML System - Control Multimodal (Presentacion / Musica)', annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            controller.toggle_mode()

    audio_detector.stop()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()