# -----------Install Docker-----------
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


# -----Install kubectl------
# download latest release
curl -LO "https://dl.k8s.io/release/$(curl -L -s \
  https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# validate binary(optional)
# curl -LO "https://dl.k8s.io/release/$(curl -L -s \
#   https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
# echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

# install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# check version
kubectl version --client

# -----Install minikube-------
# Update package list
sudo apt update

# Install required dependencies
sudo apt install -y curl

# Download and install Minikube binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify Minikube installation
minikube version

# start minikube
minikube start

# enable minikube registry for storing local images
minikube addons enable registry

# start the private registry
docker run --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):5000"

# Enable metric server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# because of some problem so can not the image directly local image, so you should do this workaround
# save the image
docker image save -o image.tar my_image:tag
# load the image into minikube registry
minikube image load image.tar

