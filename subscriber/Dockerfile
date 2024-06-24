# Use an official Python runtime as a parent image
FROM python:3.12.1-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install required packages for gRPC and git
RUN apt-get update && apt-get install -y \
    git \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN pip install --no-cache-dir grpcio grpcio-tools

# Install mysql-connector-python package
RUN pip install mysql-connector-python

# Clone the lnd repository to get the .proto files
RUN git clone https://github.com/lightningnetwork/lnd.git

# Generate the Python gRPC files from the .proto files
RUN python -m grpc_tools.protoc -I lnd/lnrpc --python_out=. --grpc_python_out=. lnd/lnrpc/lightning.proto

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Run the application when the container launches
CMD ["python", "-u", "subscribe_graph.py"]
# CMD ["sleep", "infinity"]
