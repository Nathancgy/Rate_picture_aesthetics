#!/bin/bash
set -e

echo "===== Setting up Image Quality Assessment Tool ====="

# Create directories
mkdir -p sample_images
mkdir -p my_images
mkdir -p models/MobileNet

# Download sample images if not already present
if [ ! "$(ls -A sample_images 2>/dev/null)" ]; then
    echo "Downloading sample images..."
    # Download some sample images
    curl -L "https://unsplash.com/photos/uf2nnANWa8Q/download?force=true" -o sample_images/landscape.jpg
    curl -L "https://unsplash.com/photos/KMn4VEeEPR8/download?force=true" -o sample_images/portrait.jpg
    curl -L "https://unsplash.com/photos/8Pd8ycDWM6s/download?force=true" -o sample_images/city.jpg
    curl -L "https://unsplash.com/photos/PpYOQgsZDM4/download?force=true" -o sample_images/nature.jpg
    curl -L "https://unsplash.com/photos/IKUYGCFmfw4/download?force=true" -o sample_images/blurry.jpg
    echo "Sample images downloaded."
fi

# Download pre-trained models
echo "Downloading model weights..."
if [ ! -s "models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5" ]; then
    echo "Downloading aesthetic model weights..."
    curl -L "https://github.com/idealo/image-quality-assessment/releases/download/v1.0.0/weights_mobilenet_aesthetic_0.07.hdf5" -o models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5
fi

if [ ! -s "models/MobileNet/weights_mobilenet_technical_0.11.hdf5" ]; then
    echo "Downloading technical model weights..."
    curl -L "https://github.com/idealo/image-quality-assessment/releases/download/v1.0.0/weights_mobilenet_technical_0.11.hdf5" -o models/MobileNet/weights_mobilenet_technical_0.11.hdf5
fi

# Check if model files were downloaded correctly
if [ ! -s "models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5" ] || [ ! -s "models/MobileNet/weights_mobilenet_technical_0.11.hdf5" ]; then
    echo "Error: Failed to download model weights. Using alternative approach..."
    
    # Alternative download URLs
    curl -L "https://s3.eu-central-1.amazonaws.com/idealo-ml-image-quality/weights_mobilenet_aesthetic_0.07.hdf5" -o models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5
    curl -L "https://s3.eu-central-1.amazonaws.com/idealo-ml-image-quality/weights_mobilenet_technical_0.11.hdf5" -o models/MobileNet/weights_mobilenet_technical_0.11.hdf5
    
    # Check again
    if [ ! -s "models/MobileNet/weights_mobilenet_aesthetic_0.07.hdf5" ] || [ ! -s "models/MobileNet/weights_mobilenet_technical_0.11.hdf5" ]; then
        echo "Error: Still failed to download model weights. Please download them manually from:"
        echo "https://github.com/idealo/image-quality-assessment#trained-models"
        echo "and place them in the models/MobileNet directory."
    fi
fi

# Create a Python script for prediction to be run inside the container
cat > predict_script.py << 'EOF'
#!/usr/bin/env python3

import os
import sys
import json
import argparse
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-path', type=str, required=True)
    parser.add_argument('--weights-file', type=str, required=True)
    parser.add_argument('--model-type', type=str, choices=['aesthetic', 'technical'], required=True)
    return parser.parse_args()

def process_image(image_path, target_size=(224, 224)):
    # Load and resize image
    img = load_img(image_path, target_size=target_size)
    # Convert to array and rescale
    x = img_to_array(img)
    x /= 255.
    # Add batch dimension
    x = np.expand_dims(x, axis=0)
    return x

def predict(model, image, image_path):
    # Get prediction
    scores = model.predict(image)[0]
    # Calculate mean score
    mean_score = np.sum(scores * np.arange(1, 11))
    # Print results
    print(f"\nImage: {os.path.basename(image_path)}")
    print(f"Predicted score: {mean_score:.2f}")
    print(f"Predicted score distribution: {scores.tolist()}")
    return scores, mean_score

def main():
    args = parse_args()
    
    # Load model
    model = load_model(args.weights_file)
    
    # Process image
    image = process_image(args.image_path)
    
    # Make prediction
    scores, mean_score = predict(model, image, args.image_path)
    
    # Save results to file
    base_filename = os.path.splitext(os.path.basename(args.image_path))[0]
    results = {
        "image": os.path.basename(args.image_path),
        "model_type": args.model_type,
        "mean_score": float(mean_score),
        "scores": scores.tolist()
    }
    
    output_dir = "/results"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/{base_filename}_{args.model_type}_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
EOF

# Create a simplified requirements file
cat > tensorflow_requirements.txt << 'EOF'
tensorflow==2.9.1
keras==2.9.0
numpy==1.22.4
Pillow==9.1.1
EOF

echo "Setup completed!"
echo "Using a simpler approach with TensorFlow Docker image for Apple Silicon compatibility"

# We'll use the official TensorFlow image instead of building our own
echo "===== Setup completed! ====="
echo "You can now run './assess_images.sh' to evaluate sample images." 