
# applies the fix documented here: https://github.com/NVIDIA/nvidia-docker/issues/595#issuecomment-519714769
printf "{\n    \"runtimes\": {\n        \"nvidia\": {\n            \"path\": \"nvidia-container-runtime\",\n            \"runtimeArgs\": []\n        }\n    },\n    \"default-runtime\": \"nvidia\"\n}" > /etc/docker/daemon.json
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get install nvidia-container-runtime
sudo systemctl restart docker.service