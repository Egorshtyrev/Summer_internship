import cv2
from ultralytics import YOLO
import time
import requests
import os
from datetime import datetime, timedelta

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
INACTIVITY_THRESHOLD = 1800  # 30 minutes in seconds
CHECK_INTERVAL = 60  # Check every minute

# Custom trained model for machines (you need to train this)
MACHINE_MODEL_PATH = 'machine_detection.pt'

# Initialize YOLO models
coco_model = YOLO('yolov8n.pt')  # Standard COCO model
machine_model = YOLO(MACHINE_MODEL_PATH)  # Custom trained model for machines

last_detection_time = time.time()

def send_inactivity_alert():
    """Send inactivity alert to Telegram"""
    message = (f"⚠️ Machine inactivity alert!\n"
               f"No machines detected for 30 minutes.\n"
               f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    )
    return response.json()

def detect_machines():
    global last_detection_time
    
    cap = cv2.VideoCapture(1)  # Second camera
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Detect machines using custom model
        machine_results = machine_model(frame, conf=0.6)
        
        # Also check for vehicles in COCO model (classes 1-8 are vehicles)
        vehicle_results = coco_model(frame, classes=[1,2,3,5,7], conf=0.6)
        
        # Combine results
        total_machines = len(machine_results[0].boxes) + len(vehicle_results[0].boxes)
        
        if total_machines > 0:
            last_detection_time = time.time()
            status = "ACTIVE: Machines detected"
        else:
            inactive_duration = time.time() - last_detection_time
            status = f"INACTIVE: {inactive_duration:.0f}s since last detection"
            
            # Check if we've reached the threshold
            if inactive_duration >= INACTIVITY_THRESHOLD:
                send_inactivity_alert()
                last_detection_time = time.time()  # Reset timer
        
        # Display status on frame
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 255, 0) if "ACTIVE" in status else (0, 0, 255), 2)
        
        # Display the frame (optional)
        cv2.imshow('Machine Detection', frame)
        
        # Exit on 'q'
        if cv2.waitKey(1) == ord('q'):
            break
        
        # Wait before next check
        time.sleep(CHECK_INTERVAL)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_machines()