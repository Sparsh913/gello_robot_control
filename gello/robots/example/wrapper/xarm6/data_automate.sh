#!/bin/bash

# Create base directory for all experiments
BASE_DIR="experiment_data"
mkdir -p $BASE_DIR

# Vial ID for the experiment
VIAL_ID=1

mkdir -p $BASE_DIR/vial_${VIAL_ID}
BASE_DIR=$BASE_DIR/vial_${VIAL_ID}

# Function to move robot to home position
move_to_home() {
    python3 move_home.py
    sleep 5
}

# Constant motion parameters
CONSTANT_SPEEDS=(20 50 80 120 160)
for speed in "${CONSTANT_SPEEDS[@]}"; do
    # Create directory for this parameter set
    DIR="${BASE_DIR}/constant_motion_speed_${speed}"
    mkdir -p "$DIR"
    mkdir -p "$DIR/images"
    # Move to home position
    move_to_home
    
    # Run data collection with current parameters
    python3 data_collection_1.py \
        --motion_type constant \
        --speed $speed \
        --amplitude 80 \
        --vial_id $VIAL_ID
    
    # Copy log files to parameter-specific directory
    mv joint_log_constant.txt "$DIR/"
    mv image_log_constant.txt "$DIR/"
    mv images_constant "$DIR/images/"
done

# Sinusoidal motion parameters # use bc to compute 1/10, 1/8, 1/6, 1/4, 1/2
FREQUENCIES=()
for i in {1..5}; do
    freq=$(echo "scale=2; 1/$i" | bc)
    FREQUENCIES+=($freq)
done
for freq in "${FREQUENCIES[@]}"; do
    DIR="${BASE_DIR}/sinusoidal_motion_freq_${freq}"
    mkdir -p "$DIR"
    mkdir -p "$DIR/images"
    
    move_to_home
    
    python3 data_collection_1.py \
        --motion_type sinusoidal \
        --frequency $freq \
        --amplitude 70 \
        --vial_id $VIAL_ID
    
    mv joint_log_sine.txt "$DIR/"
    mv image_log_sine.txt "$DIR/"
    mv images_sine "$DIR/images/"
done

# Constant with pause parameters
CONSTANT_PAUSE_SPEEDS=(20 50 80 120 160)
PAUSE_TIMES=(0.5 1 2 2 2)
for i in "${!CONSTANT_PAUSE_SPEEDS[@]}"; do
    speed=${CONSTANT_PAUSE_SPEEDS[$i]}
    pause_time=${PAUSE_TIMES[$i]}
    DIR="${BASE_DIR}/constant_pause_motion_speed_${speed}_pause_time_${pause_time}"
    mkdir -p "$DIR"
    mkdir -p "$DIR/images"
    
    move_to_home
    
    python3 data_collection_1.py \
        --motion_type constant_with_pause \
        --speed $speed \
        --amplitude 80 \
        --pause_time $pause_time \
        --vial_id $VIAL_ID
    
    mv joint_log_constant_with_pause.txt "$DIR/"
    mv image_log_constant_with_pause.txt "$DIR/"
    mv images_constant_with_pause "$DIR/images/"
done

echo "All experiments completed!"
