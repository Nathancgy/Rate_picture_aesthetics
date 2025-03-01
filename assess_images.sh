#!/bin/bash
set -e

# Function to display usage
display_usage() {
    echo "Usage: $0 [--aesthetic | --technical | --both | --custom]"
    echo "  --aesthetic : Evaluate aesthetic quality only (default if no option specified)"
    echo "  --technical : Evaluate technical quality only"
    echo "  --both      : Evaluate both aesthetic and technical quality"
    echo "  --custom    : Evaluate your own images from my_images directory instead of samples"
    exit 1
}

# Default values
MODEL="aesthetic"
IMAGE_DIR="sample_images"

# Parse command line arguments
if [[ $# -gt 0 ]]; then
    case "$1" in
        --aesthetic) MODEL="aesthetic" ;;
        --technical) MODEL="technical" ;;
        --both) MODEL="both" ;;
        --custom) IMAGE_DIR="my_images" ;;
        --help) display_usage ;;
        *) display_usage ;;
    esac
fi

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed or not in PATH. Please install Docker first."
    exit 1
fi

# Check if image directory is empty
if [ ! "$(ls -A $IMAGE_DIR 2>/dev/null)" ]; then
    if [ "$IMAGE_DIR" == "sample_images" ]; then
        echo "Error: No sample images found. Please run './setup.sh' to download sample images."
    else
        echo "Error: No images found in $IMAGE_DIR directory. Please add your images there."
    fi
    exit 1
fi

# Create results directory
mkdir -p results

# Function to evaluate images
evaluate_images() {
    local model_type=$1
    local weights_file=""
    
    if [ "$model_type" == "aesthetic" ]; then
        weights_file="/models/weights_mobilenet_aesthetic_0.07.hdf5"
        echo -e "\n===== Evaluating AESTHETIC quality of images in $IMAGE_DIR ====="
    else
        weights_file="/models/weights_mobilenet_technical_0.11.hdf5"
        echo -e "\n===== Evaluating TECHNICAL quality of images in $IMAGE_DIR ====="
    fi
    
    # Process each image
    for img in "$IMAGE_DIR"/*; do
        if [[ $img =~ \.(jpg|jpeg|png)$ ]]; then
            echo -e "\nEvaluating: $(basename "$img")"
            
            # Run the Docker container with TensorFlow directly
            docker run --rm \
                -v "$(pwd)/$IMAGE_DIR:/images" \
                -v "$(pwd)/models/MobileNet:/models" \
                -v "$(pwd)/results:/results" \
                -v "$(pwd)/predict_script.py:/predict_script.py" \
                tensorflow/tensorflow:2.9.1 \
                python3 /predict_script.py \
                --image-path "/images/$(basename "$img")" \
                --weights-file "$weights_file" \
                --model-type "$model_type"
        fi
    done
}

# Main execution
echo "===== Image Quality Assessment Tool ====="

if [ "$MODEL" == "aesthetic" ] || [ "$MODEL" == "both" ]; then
    evaluate_images "aesthetic"
fi

if [ "$MODEL" == "technical" ] || [ "$MODEL" == "both" ]; then
    evaluate_images "technical"
fi

echo -e "\n===== Assessment completed! ====="
echo "Results have been displayed above and saved to the 'results' directory."
echo "You can run with different options to evaluate aesthetic or technical quality:"
echo "  ./assess_images.sh --aesthetic  : Aesthetic quality only"
echo "  ./assess_images.sh --technical  : Technical quality only"
echo "  ./assess_images.sh --both       : Both aesthetic and technical quality"
echo "  ./assess_images.sh --custom     : Assess your own images in my_images directory" 