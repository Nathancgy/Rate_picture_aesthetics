#!/usr/bin/env python3
"""
Parse NIMA results from Docker output and save them for visualization.
This is a helper script to connect the Docker-based assessment tool with the visualization tool.
"""

import os
import sys
import json
import argparse
import re
import subprocess
from collections import defaultdict

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Parse NIMA assessment results and prepare for visualization')
    parser.add_argument('--image-dir', type=str, default='sample_images',
                        help='Directory containing images (default: sample_images)')
    parser.add_argument('--model-type', type=str, default='both',
                        choices=['aesthetic', 'technical', 'both'],
                        help='Model type to parse results for (default: both)')
    return parser.parse_args()

def run_assessment(image_dir, model_type):
    """Run the assessment script and capture its output."""
    cmd = ['./assess_images.sh']
    if model_type != 'both':
        cmd.append(f'--{model_type}')
    if image_dir != 'sample_images':
        cmd.append('--custom')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running assessment: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

def parse_results(output_text):
    """Parse the output text to extract score distributions."""
    results = defaultdict(dict)
    
    # Pattern to match score distributions
    score_pattern = r"Predicted score distribution: \[([\d\.\s,]+)\]"
    # Pattern to match image file names
    image_pattern = r"Evaluating: ([\w\.\-]+)"
    # Pattern to match model type
    model_pattern = r"===== Evaluating (\w+) quality"
    
    current_image = None
    current_model = None
    
    for line in output_text.split('\n'):
        # Check for model type
        model_match = re.search(model_pattern, line)
        if model_match:
            current_model = model_match.group(1).lower()
            continue
        
        # Check for image file
        image_match = re.search(image_pattern, line)
        if image_match:
            current_image = image_match.group(1)
            continue
        
        # Check for score distribution
        score_match = re.search(score_pattern, line)
        if score_match and current_image and current_model:
            score_str = score_match.group(1)
            scores = [float(s.strip()) for s in score_str.split(',')]
            results[current_image][current_model] = scores
    
    return results

def save_results(results, output_dir='results'):
    """Save the parsed results to JSON files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for image, models in results.items():
        output_file = os.path.join(output_dir, f"{os.path.splitext(image)[0]}_scores.json")
        with open(output_file, 'w') as f:
            json.dump(models, f, indent=2)
        print(f"Saved results for {image} to {output_file}")

def main():
    """Main function."""
    args = parse_args()
    
    print(f"Running assessment for {args.model_type} model(s) on images in {args.image_dir}...")
    output = run_assessment(args.image_dir, args.model_type)
    
    print("Parsing results...")
    results = parse_results(output)
    
    if not results:
        print("No results found. Check if the assessment ran correctly.")
        sys.exit(1)
    
    print(f"Found results for {len(results)} image(s).")
    save_results(results)
    
    print("\nNow running visualization...")
    # Run the visualization script with the same arguments
    subprocess.run(['python3', 'visualize_results.py', 
                   f'--image-dir={args.image_dir}', 
                   f'--model-type={args.model_type}'])

if __name__ == "__main__":
    main() 