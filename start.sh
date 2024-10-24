#!/bin/bash

# Save the current directory
ROOT_DIR=$(pwd)

# Check if the 'vct_hack' Conda environment exists
if ! conda env list | grep -q 'vct_hack'; then
  echo "Conda environment 'vct_hack' not found. Creating the environment..."
  
  # Create the environment using requirements.txt
  conda create --name vct_hack --file "$ROOT_DIR/requirements.txt" -y
  
  echo "Conda environment 'vct_hack' created successfully."
fi

# Activate the environment
echo "Activating Conda environment 'vct_hack'..."
conda activate vct_hack

# Start the Flask app
cd "$ROOT_DIR/server"
flask run &

# Start the React app
cd "$ROOT_DIR/client"
npm start
