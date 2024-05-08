#!/bin/bash
# chmod +x /path/to/yourscript.sh
# Check if Docker is already installed
if [ -x "$(command -v docker)" ]; then
  echo "Docker is already installed."
  exit 0
fi

# Update package index and install required packages
if [ -x "$(command -v apt-get)" ]; then
  sudo apt-get update
  sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
elif [ -x "$(command -v yum)" ]; then
  sudo yum update
  sudo yum install -y \
    yum-utils \
    device-mapper-persistent-data \
    lvm2
else
  echo "Unsupported package manager. Please install Docker manually."
  exit 1
fi

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker's repository
sudo add-apt-repository \
  "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) \
  stable"

# Install Docker
if [ -x "$(command -v apt-get)" ]; then
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io
elif [ -x "$(command -v yum)" ]; then
  sudo yum install -y docker-ce docker-ce-cli containerd.io
fi

# Start Docker service
sudo systemctl start docker

# Enable Docker service to start on boot
sudo systemctl enable docker

echo "Docker installation completed."
