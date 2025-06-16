from ultralytics import YOLO
import argparse

def train_model(data_yaml, epochs=50, imgsz=640, batch=8):
    """
    Train a custom YOLOv8 model for machine detection
    
    Args:
        data_yaml (str): Path to YAML file defining dataset
        epochs (int): Number of training epochs
        imgsz (int): Image size
        batch (int): Batch size
    """
    # Load a pretrained YOLO model (recommended for transfer learning)
    model = YOLO('yolov8n.pt')
    
    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name='machine_detection'
    )
    
    # Export the trained model
    model.export(format='onnx')
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True, help='Path to data.yaml')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--imgsz', type=int, default=640, help='Image size')
    parser.add_argument('--batch', type=int, default=8, help='Batch size')
    
    args = parser.parse_args()
    
    print(f"Starting training with parameters:")
    print(f"Data: {args.data}")
    print(f"Epochs: {args.epochs}")
    print(f"Image size: {args.imgsz}")
    print(f"Batch size: {args.batch}")
    
    train_model(args.data, args.epochs, args.imgsz, args.batch)