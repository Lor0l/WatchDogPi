# Define base image
FROM python:3.10-slim
# Set working directory for RUN COPY CMD commands
WORKDIR /app
# Add files to the container
COPY requirements.txt ./
# Update package lists and install dependencies
RUN apt-get update && \
    apt-get install -y python3-opencv && \
    rm -rf /var/lib/apt/lists/*
# Install OpenCV for Python
RUN pip install --no-cache-dir opencv-python-headless
RUN pip install --no-cache-dir -r requirements.txt
# copy source code to container
COPY ./src .
# Define command that will be executed on container start
CMD ["python", "receive_and_process_img.py"]