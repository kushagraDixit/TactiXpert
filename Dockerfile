# Use a basic Debian image to build from
FROM debian:buster-slim

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    curl \
    && apt-get clean

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && /opt/conda/bin/conda clean -tipsy

# Make Conda available by adding it to PATH
ENV PATH=/opt/conda/bin:$PATH

# Install Node.js and npm for the React frontend
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Set the working directory for the application
WORKDIR /app

# Copy the entire project directory into the container
COPY . .

# Install Python dependencies (using Conda) for the Flask backend
RUN conda env create --file ./src_code/back-end/environment.yml

# Use conda run to run commands in the Conda environment
SHELL ["conda", "run", "-n", "vct_hack", "/bin/bash", "-c"]

# Install npm dependencies for the React frontend
WORKDIR /app/src_code/front-end/chat-interface
RUN npm install

WORKDIR /app/src_code/front-end
# Expose the ports for Flask (5000) and React (3000)
EXPOSE 5000
EXPOSE 3000

# Start both the Flask and React apps concurrently
CMD ["conda", "run", "-n", "vct_hack", "bash", "-c", "npm run dev"]
