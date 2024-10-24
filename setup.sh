#!/bin/bash

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# Detect OS (simplified for Docker/Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    echo "Unsupported OS for this setup script. Exiting."
    exit 1
fi

# Step 1: Install Conda (Miniconda) if not installed
echo "Checking if Conda is installed..."

if ! command_exists conda; then
    echo "Conda is not installed. Installing Miniconda..."

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    rm miniconda.sh
    # Add Conda to the PATH for this script
    export PATH="$HOME/miniconda/bin:$PATH"
    # Initialize Conda in the current shell
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
else
    echo "Conda is already installed."
fi

# Step 2: Set up the Conda environment for Flask backend
echo "Setting up Conda environment for Flask backend..."

if [ -f "./src_code/back-end/environment.yml" ]; then
    conda env create --file ./src_code/back-end/environment.yml || conda env update --file ./src_code/back-end/environment.yml
else
    conda create --name vct_hack python=3.8 -y
    conda activate vct_hack
    pip install -r ./src_code/back-end/requirements.txt
fi

# Activate the Conda environment in the script
eval "$(conda shell.bash hook)"
conda activate vct_hack

# Step 3: Install Node.js and npm if not installed
echo "Checking if Node.js and npm are installed..."

if ! command_exists node; then
    echo "Node.js is not installed. Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
    apt-get install -y nodejs
else
    echo "Node.js and npm are already installed."
fi

# Step 4: Set up the React app using npm
echo "Setting up React frontend..."
cd ./src_code/front-end/chat-interface
npm install

echo "Frontend dependencies installed."

# Final instructions
echo ""
echo "Setup completed successfully!"
echo "To run the Flask backend, activate the Conda environment using 'conda activate vct_hack' and start the Flask server."
echo "To run the React frontend, navigate to the frontend folder and run 'npm start'."
