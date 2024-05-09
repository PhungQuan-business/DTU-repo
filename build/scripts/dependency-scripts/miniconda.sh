#!/bin/bash

# Set the desired Miniconda version
# MINICONDA_VERSION=py39_4.12.0
MINICONDA_VERSION=py39_24.3.0

# Download the Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_24.3.0-0-Linux-x86_64.sh
# Make the installer executable
chmod +x Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh

# Run the installer
./Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -b -p $HOME/miniconda3

# Update PATH in the current shell session
export PATH="$HOME/miniconda3/bin:$PATH"

# Update PATH in the current user's bashrc
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> $HOME/.bashrc

# Clean up the installer
rm Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh

# Print a success message
echo "Miniconda ${MINICONDA_VERSION} has been installed successfully."


# Uninstall miniconda
## remove miniconda from environment path

# nano ~/.bashrc
# remove export PATH="$HOME/miniconda3/bin:$PATH"

## remove Miniconda directory
# rm -rf $HOME/miniconda3

## clear cached Miniconda files
# sudo dnf clean all

