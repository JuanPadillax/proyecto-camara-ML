import cv2

cap = cv2.VideoCapture(0) # 0 suele ser la cámara por defecto

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("No se pudo acceder a la cámara")
        break

    cv2.imshow('Prueba Webcam', frame)

    # Presiona 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()