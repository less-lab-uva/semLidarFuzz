# Base Image
FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

# Install Python
RUN apt update
RUN apt install python3.6-distutils python3.6-dev python3.6-venv python3-pip -y

# Python PIP Dependencies
RUN pip3 install --upgrade pip
RUN pip3 install numpy==1.19.5
RUN pip3 install open3d==0.15.2
RUN pip3 install pymongo==4.1.1
RUN pip3 install Pillow==8.4.0
RUN pip3 install vispy==0.10.0
RUN pip3 install shortuuid==1.0.9
RUN pip3 install gdown

# Fix for open3d
RUN apt-get install ffmpeg libsm6 libxext6 libxrender-dev mesa-utils-extra libegl1-mesa-dev libgles2-mesa-dev xvfb -y