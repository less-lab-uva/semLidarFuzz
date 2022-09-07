# Base Image
FROM python:3.10.6-slim

# used in generating figures
RUN pip3 install numpy==1.23.2
RUN pip3 install matplotlib==3.5.2
# used in downloading study data from Google Drive
RUN pip3 install gdown

# used for unzipping the study data
RUN apt-get update
RUN apt-get install xz-utils