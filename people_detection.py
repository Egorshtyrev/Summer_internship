import cv2
import numpy as np
from ultralytics import YOLO
import time
import requests
import os
from datetime import datetime

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = '7844049761:AAG5_27DvsUGz26miLyGR29eYEDkfe6Me10'
TELEGRAM_CHAT_ID = 1124318054
ALERT_INTERVAL = 5  # Minimum seconds between alerts
video_path = r"C:\Users\User\Desktop\workfolder\Brics\Summer internship\human detection\cam2.avi"

# Camera Configuration
CAMERA_NAME = "Front Entrance"
DETECTION_ZONE = np.array([[460, 1048], [771, 463], [1719, 619], [1610, 1048]], np.int32)

# Initialize YOLO model
model = YOLO('yolov8n.pt')  # For human detection
last_alert_time = 0

def send_telegram_alert(image_path, detection_count):
    """Enhanced alert with timestamped screenshot"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = (f"SECURITY ALERT - {CAMERA_NAME}\n"
               f"Humans detected: {detection_count}\n"
               f"Time: {timestamp}")
    
    try:
        with open(image_path, 'rb') as photo:
            response = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
                files={'photo': photo},
                data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            )
        print(f"📤 Alert sent to Telegram at {timestamp}")
        return response.json()
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
        return None

def is_in_detection_zone(box, zone):
    """Precise zone detection with coordinate validation"""
    x_center = int((box[0] + box[2]) / 2)
    y_center = int((box[1] + box[3]) / 2)
    return cv2.pointPolygonTest(zone, (x_center, y_center), False) >= 0

def process_frame(frame):
    """Main detection processor with visual enhancements"""
    global last_alert_time
    
    # Visualize detection zone
    cv2.polylines(frame, [DETECTION_ZONE], True, (0, 255, 0), 3)
    cv2.putText(frame, "Detection Zone", DETECTION_ZONE[0], 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Human detection
    results = model(frame, classes=0, conf=0.7)
    annotated_frame = results[0].plot()
    
    # Zone detection logic
    zone_detections = []
    for box in results[0].boxes.xyxy.cpu().numpy():
        if is_in_detection_zone(box, DETECTION_ZONE):
            zone_detections.append(box)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"DETECTED: Human in zone at {timestamp} (Camera: {CAMERA_NAME})")
    
    # Alert system
    if zone_detections:
        current_time = time.time()
        if current_time - last_alert_time > ALERT_INTERVAL:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            alert_img = f"alert_{CAMERA_NAME}_{timestamp}.jpg"
            
            # Add visual alert indicator
            cv2.putText(annotated_frame, "ALERT! HUMAN DETECTED", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            cv2.imwrite(alert_img, annotated_frame)
            send_telegram_alert(alert_img, len(zone_detections))
            last_alert_time = current_time
            os.remove(alert_img)
    
    return annotated_frame

def main():
    """Main execution with improved error handling"""
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video source: {video_path}")
        
        print(f"\nStarted {CAMERA_NAME} surveillance at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Detection Zone Active | Alert Interval: {ALERT_INTERVAL}s")
        print("Press 'ESC' to terminate monitoring\n")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Video stream ended or frame read error")
                break
                
            processed_frame = process_frame(frame)
            cv2.imshow(f'{CAMERA_NAME} - Live Monitoring', processed_frame)
            
            # ESC key (keycode 27) to exit
            if cv2.waitKey(1) == 27:
                print("\nManual shutdown initiated by operator (ESC pressed)")
                break
                
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nSystem shutdown at {datetime.now().strftime('%H:%M:%S')}")
        print("Surveillance terminated")

if __name__ == "__main__":
    main()