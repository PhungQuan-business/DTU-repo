#!/bin/bash

# Download Minikube binary
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Make the binary executable
chmod +x minikube

# Move the binary to /usr/local/bin
sudo mv minikube /usr/local/bin/

# Download the latest release of Kubectl
curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl

# Make the kubectl binary executable
chmod +x kubectl

# Move the kubectl binary to /usr/local/bin
sudo mv kubectl /usr/local/bin/


# Start minikube

## Start Minikube with recommended settings
minikube start \
    --driver=kvm2 \
    --cpus=2 \
    --memory=4096mb 
    # --kubernetes-version=$(kubectl version -o json | jq -r '.serverVersion.gitVersion')


