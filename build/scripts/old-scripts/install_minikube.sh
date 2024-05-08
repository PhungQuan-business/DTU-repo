#!/bin/bash
# chmod +x /path/to/yourscript.sh
# Update package list
sudo apt update

# Install required dependencies
sudo apt install -y curl

# Download and install Minikube binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify Minikube installation
minikube version

# enable minikube registry for storing local images
minikube addons enable registry

# enable metrics-server
minikube addons enable metrics-server

# start the private registry
docker run --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):5000"

# because of some problem so can not the image directly local image, so you should do this workaround
# save the image
# docker image save -o image.tar my_image:tag
# load the image into minikube registry
# minikube image load image.tar

