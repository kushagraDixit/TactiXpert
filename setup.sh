#!/bin/bash

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    echo "Unsupported OS. Exiting setup."
    exit 1
fi

# Step 1: Install Conda (Miniconda) if not installed
echo "Checking if Conda is installed..."

if ! command_exists conda; then
    echo "Conda is not installed. Installing Miniconda..."

    if [[ "$OS" == "Linux" ]]; then
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
        bash miniconda.sh -b -p $HOME/miniconda
        eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    elif [[ "$OS" == "Mac" ]]; then
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh
        bash miniconda.sh -b -p $HOME/miniconda
        eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    elif [[ "$OS" == "Windows" ]]; then
        # Download and run the Miniconda installer for Windows
        echo "Downloading and installing Miniconda for Windows..."
        curl -o miniconda.exe https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
        start /wait "" miniconda.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3
        eval "$($HOME/miniconda/Scripts/conda shell.bash hook)"
    else
        echo "Unsupported OS. Cannot install Conda."
        exit 1
    fi

    echo "Conda installation completed."
else
    echo "Conda is already installed."
fi

# Step 2: Set up the Conda environment for Flask backend
echo "Setting up Conda environment for Flask backend..."

if [ -f "./back-end/environment.yml" ]; then
    conda env create -f ./back-end/environment.yml
    conda activate your_env_name
else
    conda create --name your_env_name python=3.8 -y
    conda activate your_env_name
    pip install -r ./back-end/requirements.txt
fi

# Step 3: Install Node.js and npm if not installed
echo "Checking if Node.js and npm are installed..."

if ! command_exists node; then
    echo "Node.js is not installed. Installing Node.js and npm..."

    if [[ "$OS" == "Linux" ]]; then
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [[ "$OS" == "Mac" ]]; then
        brew install node
    elif [[ "$OS" == "Windows" ]]; then
        echo "Downloading and installing Node.js for Windows..."
        curl -o nodejs.msi https://nodejs.org/dist/v16.14.0/node-v16.14.0-x64.msi
        start /wait "" msiexec /i nodejs.msi /quiet /norestart
    else
        echo "Unsupported OS. Cannot install Node.js."
        exit 1
    fi

    echo "Node.js and npm installation completed."
else
    echo "Node.js and npm are already installed."
fi

# Step 4: Set up the React app using npm
echo "Setting up React frontend..."
cd front-end/chat-interface
npm install

echo "Frontend dependencies installed."

# Final instructions
echo ""
echo "Setup completed successfully!"
echo "To run the Flask backend, activate the Conda environment using 'conda activate your_env_name' and start the Flask server."
echo "To run the React frontend, navigate to the frontend folder and run 'npm start'."
