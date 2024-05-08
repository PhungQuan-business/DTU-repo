#!/bin/bash

# Update package repositories
sudo dnf update -y

# Install required packages
sudo dnf install -y \
    conntrack \
    libselinux-utils \
    qemu-kvm \
    qemu-img \
    virt-manager \
    virt-viewer \
    virt-install \
    libvirt-client \
    libvirt-daemon-kvm \
    libvirt-daemon-config-network

# Enable and start libvirtd service
sudo systemctl enable --now libvirtd

# Allow non-root users to access libvirt
sudo usermod -a -G libvirt $(whoami)
newgrp libvirt
