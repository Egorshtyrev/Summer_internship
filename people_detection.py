import cv2
from ultralytics import YOLO
import time
import requests
import os
from datetime import datetime

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
ALERT_INTERVAL = 5  # Minimum seconds between alerts

# Initialize YOLO model
model = YOLO('yolov8n.pt')  # For human detection
last_alert_time = 0

def send_telegram_alert(image_path, detection_count):
    """Send alert with image to Telegram"""
    caption = f"🚨 Human detected! Count: {detection_count}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    with open(image_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
        response = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
            files=files,
            data=data
        )
    return response.json()

def detect_humans():
    global last_alert_time
    
    cap = cv2.VideoCapture(0)  # First camera
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Detect humans (class 0 in COCO)
        results = model(frame, classes=0, conf=0.7)  # 70% confidence threshold
        annotated_frame = results[0].plot()
        
        # Check if humans detected
        if len(results[0].boxes) > 0:
            current_time = time.time()
            if current_time - last_alert_time > ALERT_INTERVAL:
                # Save the frame with detections
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"human_detection_{timestamp}.jpg"
                cv2.imwrite(image_path, annotated_frame)
                
                # Send alert
                send_telegram_alert(image_path, len(results[0].boxes))
                last_alert_time = current_time
                
                # Remove the image after sending
                os.remove(image_path)
        
        # Display the frame (optional)
        cv2.imshow('Human Detection', annotated_frame)
        
        # Exit on 'q'
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_humans()