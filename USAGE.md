# Image Quality Assessment Tool Usage Guide

This guide provides detailed instructions on how to use the Image Quality Assessment tool to score the quality of images.

## Quick Start

The easiest way to get started is to run:

```bash
python3 run_assessment.py --setup
```

This will:
1. Set up the Docker environment
2. Download sample images
3. Download pre-trained models
4. Run assessment on sample images
5. Visualize the results

## Step-by-Step Guide

### 1. Setup

Before you can assess images, you need to set up the environment:

```bash
./setup.sh
```

This script will:
- Create necessary directories
- Download sample images (if not already present)
- Download pre-trained models for aesthetic and technical quality assessment
- Create a Dockerfile
- Build the Docker image (this may take a few minutes)

### 2. Assess Sample Images

To assess the quality of the sample images:

```bash
./assess_images.sh
```

By default, this will evaluate the aesthetic quality of all images in the `sample_images` directory.

Options:
- `--aesthetic`: Evaluate aesthetic quality only (default)
- `--technical`: Evaluate technical quality only
- `--both`: Evaluate both aesthetic and technical quality
- `--custom`: Evaluate your own images from the `my_images` directory

Example:
```bash
./assess_images.sh --both
```

### 3. Add Your Own Images

To assess your own images:

1. Place your images in the `my_images` directory
2. Run the assessment script with the `--custom` flag:

```bash
./assess_images.sh --custom
```

### 4. Visualize Results

For a better visual representation of the results, use the visualization script:

```bash
python3 visualize_results.py
```

Options:
- `--image-dir`: Directory containing images (default: `sample_images`)
- `--model-type`: Model type to visualize (aesthetic, technical, or both)

Example:
```bash
python3 visualize_results.py --image-dir=my_images --model-type=both
```

### 5. All-in-One Script

For convenience, you can also use the all-in-one script:

```bash
python3 run_assessment.py [options]
```

Options:
- `--image-dir`: Directory containing images (default: `sample_images`)
- `--model-type`: Model type to use (aesthetic, technical, or both)
- `--setup`: Run setup script first to build Docker image and download models
- `--skip-visualization`: Skip the visualization step

Example:
```bash
python3 run_assessment.py --image-dir=my_images --model-type=both
```

## Understanding the Results

The assessment provides two types of scores:

1. **Aesthetic Score**: Evaluates how visually pleasing an image is (composition, color harmony, etc.)
2. **Technical Score**: Evaluates technical aspects (sharpness, noise, exposure, etc.)

For each image, you'll get:
- A score distribution across 10 rating levels (1-10)
- Mean score: Average rating (higher is better)
- Standard deviation: Consistency of ratings

## Troubleshooting

1. **Docker Issues**:
   - Make sure Docker is installed and running
   - Run `docker --version` to verify installation

2. **Permission Issues**:
   - If scripts are not executable, run:
     ```bash
     chmod +x setup.sh assess_images.sh
     ```

3. **Missing Dependencies**:
   - For visualization, you'll need matplotlib and other Python packages:
     ```bash
     pip install matplotlib numpy pillow
     ```

4. **No Results Found**:
   - Check if the Docker image was built correctly
   - Verify that the image directory contains valid image files (jpg, jpeg, png) 