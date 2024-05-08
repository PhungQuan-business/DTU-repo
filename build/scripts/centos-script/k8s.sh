#!/bin/bash
# this script is use for installing k8s
# if you're using minikube then there is no need to run this script


# Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# Enable kernel modules
sudo modprobe overlay
sudo modprobe br_netfilter

# Add kernel settings
sudo tee /etc/sysctl.d/kubernetes.conf<<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

sudo sysctl --system

# Install Docker
sudo dnf install -y dnf-utils
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add Kubernetes repo
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo=https://packages.cloud.google.com/yum/repos/kubernetes-el9-x86_64

# Install Kubernetes components
sudo dnf install -y kubelet kubeadm kubectl

# Enable and start kubelet
sudo systemctl enable kubelet
sudo systemctl start kubelet

# Initialize Kubernetes cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Configure kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Calico network plugin
kubectl apply -f https://docs.projectcalico.org/v3.25/manifests/calico.yaml

# Verify installation
kubectl get nodes
kubectl get pods --all-namespaces