#!/usr/bin/env python3
"""
Visualize the results of the NIMA image quality assessment.
This script can be used to display the scores in a more visual way.
"""

import os
import sys
import argparse
import json
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Visualize NIMA image quality assessment results')
    parser.add_argument('--image-dir', type=str, default='sample_images',
                        help='Directory containing images (default: sample_images)')
    parser.add_argument('--results-dir', type=str, default='results',
                        help='Directory containing result JSON files (default: results)')
    parser.add_argument('--model-type', type=str, default='both',
                        choices=['aesthetic', 'technical', 'both'],
                        help='Model type to visualize (default: both)')
    return parser.parse_args()

def load_results(results_dir, model_type):
    """Load results from JSON files in the results directory."""
    results = {}
    
    # Get all JSON files in the results directory
    json_files = glob.glob(os.path.join(results_dir, "*.json"))
    
    for json_file in json_files:
        # Load the JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Skip if model type doesn't match
        if model_type != 'both' and data['model_type'] != model_type:
            continue
        
        image_name = data['image']
        
        # Initialize image entry if it doesn't exist
        if image_name not in results:
            results[image_name] = {}
        
        # Add the scores
        results[image_name][data['model_type']] = data['scores']
    
    return results

def calculate_mean_score(scores):
    """Calculate mean score from probability distribution."""
    score_array = np.array(scores)
    return float(np.sum(score_array * np.arange(1, 11)))

def calculate_std_score(scores):
    """Calculate standard deviation of scores."""
    score_array = np.array(scores)
    mean = calculate_mean_score(scores)
    return float(np.sqrt(np.sum(score_array * np.square(np.arange(1, 11) - mean))))

def plot_score_distribution(ax, scores, title, color):
    """Plot the score distribution as a bar chart."""
    mean = calculate_mean_score(scores)
    std = calculate_std_score(scores)
    
    bars = ax.bar(np.arange(1, 11), scores, alpha=0.7, color=color)
    ax.axvline(mean, color='red', linestyle='--', alpha=0.8, label=f'Mean: {mean:.2f}')
    ax.set_title(f"{title}\nMean: {mean:.2f}, Std: {std:.2f}")
    ax.set_xlabel('Score')
    ax.set_ylabel('Probability')
    ax.set_xticks(np.arange(1, 11))
    ax.grid(axis='y', alpha=0.3)
    return mean, std

def visualize_image(image_path, aesthetic_scores=None, technical_scores=None, output_dir='results'):
    """Visualize the image and its quality scores."""
    fig = plt.figure(figsize=(12, 8))
    
    if aesthetic_scores is not None and technical_scores is not None:
        gs = GridSpec(2, 2, width_ratios=[2, 1])
        ax_img = fig.add_subplot(gs[:, 0])
        ax_aesthetic = fig.add_subplot(gs[0, 1])
        ax_technical = fig.add_subplot(gs[1, 1])
        
        # Plot image
        img = Image.open(image_path)
        ax_img.imshow(img)
        ax_img.set_title(os.path.basename(image_path))
        ax_img.axis('off')
        
        # Plot scores
        aes_mean, aes_std = plot_score_distribution(ax_aesthetic, aesthetic_scores, 'Aesthetic Scores', 'blue')
        tech_mean, tech_std = plot_score_distribution(ax_technical, technical_scores, 'Technical Scores', 'green')
        
        # Add overall score as text
        overall_score = (aes_mean + tech_mean) / 2
        ax_img.text(0.5, -0.05, f'Overall Score: {overall_score:.2f}/10', 
                   transform=ax_img.transAxes, 
                   fontsize=14, 
                   ha='center',
                   bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    elif aesthetic_scores is not None:
        gs = GridSpec(1, 2, width_ratios=[2, 1])
        ax_img = fig.add_subplot(gs[0, 0])
        ax_aesthetic = fig.add_subplot(gs[0, 1])
        
        # Plot image
        img = Image.open(image_path)
        ax_img.imshow(img)
        ax_img.set_title(os.path.basename(image_path))
        ax_img.axis('off')
        
        # Plot aesthetic scores
        aes_mean, aes_std = plot_score_distribution(ax_aesthetic, aesthetic_scores, 'Aesthetic Scores', 'blue')
        
        # Add score as text
        ax_img.text(0.5, -0.05, f'Aesthetic Score: {aes_mean:.2f}/10', 
                   transform=ax_img.transAxes, 
                   fontsize=14, 
                   ha='center',
                   bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    elif technical_scores is not None:
        gs = GridSpec(1, 2, width_ratios=[2, 1])
        ax_img = fig.add_subplot(gs[0, 0])
        ax_technical = fig.add_subplot(gs[0, 1])
        
        # Plot image
        img = Image.open(image_path)
        ax_img.imshow(img)
        ax_img.set_title(os.path.basename(image_path))
        ax_img.axis('off')
        
        # Plot technical scores
        tech_mean, tech_std = plot_score_distribution(ax_technical, technical_scores, 'Technical Scores', 'green')
        
        # Add score as text
        ax_img.text(0.5, -0.05, f'Technical Score: {tech_mean:.2f}/10', 
                   transform=ax_img.transAxes, 
                   fontsize=14, 
                   ha='center',
                   bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_scores.png")
    plt.savefig(output_file)
    print(f"Saved visualization to {output_file}")
    plt.close()

def main():
    """Main function."""
    args = parse_args()
    
    # Create results directory if it doesn't exist
    if not os.path.exists(args.results_dir):
        os.makedirs(args.results_dir)
    
    # Load results
    results = load_results(args.results_dir, args.model_type)
    
    if not results:
        print(f"No results found in '{args.results_dir}' for model type '{args.model_type}'.")
        print("Please run the assessment script first to generate results.")
        sys.exit(1)
    
    # Get a list of image files
    image_dir = args.image_dir
    if not os.path.exists(image_dir):
        print(f"Error: Directory '{image_dir}' does not exist.")
        sys.exit(1)
    
    # Process each image
    for image_name, scores_dict in results.items():
        # Find the image file
        image_path = os.path.join(image_dir, image_name)
        if not os.path.exists(image_path):
            print(f"Warning: Image file '{image_path}' not found, skipping visualization.")
            continue
        
        print(f"Processing: {image_name}")
        
        # Get scores
        aesthetic_scores = scores_dict.get('aesthetic')
        technical_scores = scores_dict.get('technical')
        
        # Visualize
        visualize_image(
            image_path, 
            aesthetic_scores, 
            technical_scores,
            output_dir=args.results_dir
        )
    
    print("\nVisualization complete! Check the 'results' directory for output images.")

if __name__ == "__main__":
    main() 