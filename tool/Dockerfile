# Base Image
FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

# Install Python
RUN apt update
RUN apt install python3.6-distutils python3.6-dev python3.6-venv python3-pip -y

# Font used in image generation
RUN apt-get install fonts-freefont-ttf -y

# Python PIP Dependencies
RUN pip3 install --upgrade pip
RUN pip3 install numpy==1.19.5
RUN pip3 install open3d==0.15.2
RUN pip3 install pymongo==4.1.1
RUN pip3 install Pillow==8.4.0
RUN pip3 install vispy==0.10.0
RUN pip3 install shortuuid==1.0.9
RUN pip3 install tqdm==4.64.1

# Fix for open3d https://github.com/vt-vl-lab/3d-photo-inpainting/issues/23
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libxrender-dev mesa-utils-extra libegl1-mesa-dev libgles2-mesa-dev xvfb libfontconfig1-dev wget docker.io -y
ENV DISPLAY=:0
RUN pip3 install scipy==1.5.4
RUN pip3 install matplotlib==3.3.4
RUN pip3 install scikit-image==0.17.2
