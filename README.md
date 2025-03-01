# Image Quality Assessment Tool

This project provides an easy way to score the aesthetic and technical quality of images using Google's NIMA (Neural Image Assessment) model implemented through the [idealo/image-quality-assessment](https://github.com/idealo/image-quality-assessment) framework.

## Overview

NIMA is a deep learning system that can predict how likely an image is to be perceived as aesthetically pleasing by humans. The model uses MobileNet architecture pre-trained on the AVA (Aesthetic Visual Analysis) dataset for aesthetic ratings and the TID2013 dataset for technical ratings.

This tool provides:
- A containerized environment using Docker to run the NIMA model
- Pre-downloaded sample images for testing
- Simple scripts to assess image quality with a single command
- Visualization tools to display and understand the results

![Example Assessment](https://github.com/idealo/image-quality-assessment/raw/master/readme_figures/images_aesthetic/aesthetic1.jpg_aesthetic.svg)

## Prerequisites

- **Docker**: Required to run the NIMA model in a container
- **Python 3.6+**: For the visualization tools
- **Basic Python packages**: Listed in `requirements.txt`

## Quick Start

The easiest way to get started is to run:

```bash
python3 run_assessment.py --setup
```

This will set up everything and run assessment on sample images.

## Step-by-Step

1. **Setup environment**:
   ```bash
   ./setup.sh
   ```

2. **Assess sample images**:
   ```bash
   ./assess_images.sh
   ```

3. **Assess your own images**:
   - Place images in the `my_images` directory
   - Run:
     ```bash
     ./assess_images.sh --custom
     ```

4. **Visualize results**:
   ```bash
   python3 visualize_results.py
   ```

## Detailed Documentation

For more detailed usage instructions, see [USAGE.md](USAGE.md).

## How It Works

The assessment uses two different NIMA models:

1. **Aesthetic Model**: Assesses how visually pleasing an image is
2. **Technical Model**: Evaluates technical aspects like focus, noise, and exposure

For each image, you'll get:
- A score distribution across 10 rating levels (1-10)
- Mean score: Average rating (higher is better)
- Standard deviation: Consistency of ratings

## Acknowledgements

This project uses the implementation and pre-trained models from [idealo/image-quality-assessment](https://github.com/idealo/image-quality-assessment).