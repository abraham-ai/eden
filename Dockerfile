FROM python:3.8

WORKDIR /usr/local/

COPY . .

RUN apt-get update
RUN apt install -y libgl1-mesa-glx
RUN python3 setup.py develop

ENTRYPOINT ["python3","server_for_docker.py"]