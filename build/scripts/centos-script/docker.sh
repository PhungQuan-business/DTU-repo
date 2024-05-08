# chmod +x /path/to/yourscript.sh

## remove old version of Docker
sudo yum remove docker \
                docker-client \
                docker-client-latest \
                docker-common \
                docker-latest \
                docker-latest-logrotate \
                docker-logrotate \
                docker-engine

## Set up the repository
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

## Install Docker engine
# Install the latest version
# If prompted to accept the GPG key, verify that the fingerprint 
# matches 060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35, 
# and if so, accept it.
sudo yum install docker-ce \
                docker-ce-cli \
                containerd.io \
                docker-buildx-plugin \
                docker-compose-plugin

# Start Docker
sudo systemctl start docker

# Enable Docker
sudo systemctl enable docker

# Verify docker installation
sudo docker run hello-world
