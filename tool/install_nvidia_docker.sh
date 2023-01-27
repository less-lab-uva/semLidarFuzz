
# applies the fix documented here: https://github.com/NVIDIA/nvidia-docker/issues/595#issuecomment-519714769
printf "{\n    \"runtimes\": {\n        \"nvidia\": {\n            \"path\": \"nvidia-container-runtime\",\n            \"runtimeArgs\": []\n        }\n    },\n    \"default-runtime\": \"nvidia\"\n}" > /etc/docker/daemon.json
sudo apt-get install nvidia-container-runtime
sudo systemctl restart docker.service