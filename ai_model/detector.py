"""
EcoSentinel AI Detection Module
Simulates YOLOv8-style wildlife detection using OpenCV.
In production, replace with actual YOLOv8 model weights.
"""

import random
import io
import os
import cv2
import numpy as np  
from PIL import Image


ANIMAL_CONFIGS = {
    'elephant': {'color': (0, 128, 255), 'severity': 'critical', 'weight': 15},
    'tiger': {'color': (m0, 0, 220), 'severity': 'critical', 'weight': 12},
    'leopard': {'color': (0, 165, 255), 'severity': 'high', 'weight': 10},
    'bear': {'color': (42, 42, 128), 'severity': 'high', 'weight': 8},
    'wild_boar': {'color': (0, 100, 0), 'severity': 'medium', 'weight': 10},
    'deer': {'color': (0, 180, 100), 'severity': 'low', 'weight': 20},
    'unknown': {'color': (128, 128, 128), 'severity': 'medium', 'weight': 5},
}


def get_random_animal():
    """Weighted random animal selection."""
    animals = list(ANIMAL_CONFIGS.keys())
    weights = [ANIMAL_CONFIGS[a]['weight'] for a in animals]
    return random.choices(animals, weights=weights, k=1)[0]


def draw_detection_overlay(img_array, animal_type, confidence):
    """Draw bounding box and label on image using OpenCV."""
    h, w = img_array.shape[:2]
    
    # Generate a realistic bounding box (center-focused)
    bx = int(w * random.uniform(0.1, 0.4))
    by = int(h * random.uniform(0.1, 0.4))
    bw = int(w * random.uniform(0.3, 0.55))
    bh = int(h * random.uniform(0.3, 0.55))
    bx2 = min(bx + bw, w - 1)
    by2 = min(by + bh, h - 1)

    config = ANIMAL_CONFIGS.get(animal_type, ANIMAL_CONFIGS['unknown'])
    color = config['color']
    
    # Draw bounding box
    cv2.rectangle(img_array, (bx, by), (bx2, by2), color, 3)
    
    # Label background
    label = f"{animal_type.upper().replace('_', ' ')} {confidence*100:.1f}%"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(img_array, (bx, by - th - 12), (bx + tw + 10, by), color, -1)
    cv2.putText(img_array, label, (bx + 5, by - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # EcoSentinel watermark
    cv2.putText(img_array, "EcoSentinel AI Detection",
                (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 100), 2)
    
    # Confidence bar
    bar_w = int((w - 20) * confidence)
    cv2.rectangle(img_array, (10, h - 35), (10 + bar_w, h - 25), (0, 255, 100), -1)
    cv2.rectangle(img_array, (10, h - 35), (w - 10, h - 25), (0, 255, 100), 1)

    return img_array


def simulate_detection(uploaded_file):
    """
    Simulate animal detection on an uploaded image.
    Returns a dict with animal_type, confidence, severity, and annotated image bytes.
    """
    try:
        # Read image via PIL → numpy array
        pil_image = Image.open(uploaded_file)
        pil_image = pil_image.convert('RGB')
        # Resize for faster processing
        pil_image.thumbnail((800, 600))
        img_array = np.array(pil_image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Simulated detection result
        animal_type = get_random_animal()
        confidence = round(random.uniform(0.72, 0.98), 3)
        severity = ANIMAL_CONFIGS[animal_type]['severity']

        # Draw overlay
        annotated = draw_detection_overlay(img_bgr.copy(), animal_type, confidence)

        # Encode annotated image to bytes
        _, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
        annotated_bytes = buffer.tobytes()

    except Exception as e:
        # Fallback if image processing fails
        animal_type = get_random_animal()
        confidence = round(random.uniform(0.72, 0.98), 3)
        severity = ANIMAL_CONFIGS[animal_type]['severity']
        annotated_bytes = None

    return {
        'animal_type': animal_type,
        'confidence': confidence,
        'severity': severity,
        'annotated_bytes': annotated_bytes,
    }
