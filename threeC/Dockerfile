FROM python:3.8

RUN apt update && apt install -y vim

# Mount the code directory here
WORKDIR /threeC

COPY requirements.txt requirements.txt

# install dependencies
RUN pip install -r requirements.txt

# Add project path to Python
ENV PYTHONPATH "${PYTHONPATH}:/threeC"

