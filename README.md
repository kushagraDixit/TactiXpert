# The public version of the project is available to try at : [Project Link](http://35.93.137.150:3000/)

# Project Setup and Usage Guide

This project requires **Miniconda** and **Node.js** to be installed on your system.

### Prerequisites

1. **Install Miniconda**: [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html) and follow the installation instructions.
2. **Install Node.js**: [Download Node.js](https://nodejs.org/) and install it.

---

## Setup Instructions

### Step 1: Set up the Back-End

Navigate to the backend source directory and create the conda environment:

```bash
cd TactiXpert/src_code/back-end
conda env create --name vct_hack --file=environment.yml
```

This command will create the conda environment `vct_hack` using the `environment.yml` file.

Activate the environment and start the Flask server:

```bash
conda activate vct_hack
python app.py
```

The Flask server will start on **port 5000**.

### Step 2: Set up the Front-End

Open a new Terminal and Navigate to the directory and install the required dependencies:

```bash
cd TactiXpert/src_code/front-end/chat-interface
npm install
```

Then, start the React development server:

```bash
npm start
```

The React app server will start on **port 3000**.

---

## Using the Project

Once both servers are running, you can access the chat interface at `http://localhost:3000`.

Enjoy using the chat interface!
