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
