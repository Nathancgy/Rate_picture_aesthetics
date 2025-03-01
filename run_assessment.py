#!/usr/bin/env python3
"""
Unified script to run image quality assessment and visualize the results.
This script handles the whole process from setup to visualization.
"""

import os
import sys
import argparse
import subprocess
import time
import json
import glob

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run NIMA image quality assessment and visualize results')
    parser.add_argument('--image-dir', type=str, default='sample_images',
                        help='Directory containing images (default: sample_images)')
    parser.add_argument('--model-type', type=str, default='both',
                        choices=['aesthetic', 'technical', 'both'],
                        help='Model type to use (default: both)')
    parser.add_argument('--setup', action='store_true',
                        help='Run setup script first to download models and sample images')
    parser.add_argument('--skip-visualization', action='store_true',
                        help='Skip the visualization step')
    return parser.parse_args()

def run_setup():
    """Run the setup script to download models and sample images."""
    print("Running setup script...")
    try:
        subprocess.run(['./setup.sh'], check=True)
        print("Setup completed successfully.")
    except subprocess.CalledProcessError:
        print("Error running setup script. Please check if Docker is installed and running.")
        sys.exit(1)
    except FileNotFoundError:
        print("setup.sh not found. Make sure you're in the correct directory.")
        sys.exit(1)

def run_assessment(image_dir, model_type):
    """Run the assessment script."""
    print(f"Running assessment for {model_type} model(s) on images in {image_dir}...")
    
    cmd = ['./assess_images.sh']
    if model_type != 'both':
        cmd.append(f'--{model_type}')
    if image_dir != 'sample_images':
        cmd.append('--custom')
    
    try:
        # Run the assessment script and display output in real-time
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Display output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Check for errors
        return_code = process.poll()
        if return_code != 0:
            stderr = process.stderr.read()
            print(f"Error running assessment: {stderr}")
            sys.exit(return_code)
        
        print("Assessment completed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running assessment: {e}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("assess_images.sh not found. Make sure you're in the correct directory.")
        sys.exit(1)

def run_visualization(image_dir, model_type):
    """Run the visualization script."""
    print("\nRunning visualization...")
    
    # Check if visualization script exists
    if not os.path.exists('visualize_results.py'):
        print("Warning: visualize_results.py not found. Skipping visualization.")
        return
    
    try:
        # Run the visualization script
        subprocess.run([
            'python3', 'visualize_results.py', 
            f'--image-dir={image_dir}', 
            f'--model-type={model_type}'
        ], check=True)
        
        print("Visualization completed. Check the 'results' directory for output images.")
    except subprocess.CalledProcessError as e:
        print(f"Error running visualization: {e}")
    except Exception as e:
        print(f"Error running visualization: {e}")

def check_results():
    """Check if results were generated."""
    results_dir = 'results'
    if not os.path.exists(results_dir):
        return False
    
    # Check for JSON result files
    json_files = glob.glob(os.path.join(results_dir, "*.json"))
    return len(json_files) > 0

def main():
    """Main function."""
    args = parse_args()
    
    # Make script files executable
    try:
        subprocess.run(['chmod', '+x', 'setup.sh', 'assess_images.sh'], check=True)
    except subprocess.CalledProcessError:
        print("Warning: Could not make scripts executable. You may need to run 'chmod +x setup.sh assess_images.sh' manually.")
    
    # Run setup if requested
    if args.setup:
        run_setup()
    
    # Create directories if they don't exist
    for directory in ['sample_images', 'my_images', 'results']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Run assessment
    run_assessment(args.image_dir, args.model_type)
    
    # Check if results were generated
    if not check_results():
        print("Warning: No result files were generated. The assessment may have failed.")
    
    # Run visualization if not skipped
    if not args.skip_visualization:
        run_visualization(args.image_dir, args.model_type)
    
    print("\nAll tasks completed!")
    print("You can find the detailed results in the 'results' directory.")

if __name__ == "__main__":
    main() 