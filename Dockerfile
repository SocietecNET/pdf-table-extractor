# Use the official Miniconda3 image as the base image
FROM continuumio/miniconda3

# Set environment variables
# ENV API_KEY=windai

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for Camelot, OpenCV, and OpenGL
RUN apt-get update && \
    apt-get install -y \
        gcc \
        build-essential \
        ghostscript \
        python3-tk \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libgl1-mesa-glx \
        libegl1-mesa \
        libgles2-mesa \
        libglvnd0 \
        libgl1-mesa-dri \
        libopengl0 \
        && apt-get clean

# Create a Conda environment and install dependencies
RUN conda create -n camelot_env python=3.11 -y

# Activate the environment and install Camelot and Flask
RUN /bin/bash -c "source activate camelot_env && \
    conda install -c conda-forge camelot-py[cv] flask pymupdf -y && \
    pip install -r requirements.txt"

# Ensure the Conda environment is activated
SHELL ["conda", "run", "-n", "camelot_env", "/bin/bash", "-c"]

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["conda", "run", "--no-capture-output", "-n", "camelot_env", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
