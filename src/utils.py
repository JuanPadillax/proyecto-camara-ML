import numpy as np

def calculate_angle(a, b, c):
    """
    Calcula el ángulo interno entre tres puntos (a -> b -> c).
    b es el punto del vértice (ejemplo: el codo).
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    # Ángulo en radianes respecto a la horizontal
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    # Normalizar si supera los 180 grados
    if angle > 180.0:
        angle = 360.0 - angle
        
    return angle