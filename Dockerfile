# pull official base image
FROM python:3.8.8-slim-buster

# Install libraries
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get install -y netcat \
&& apt-get clean

# Copy requirements first to leverage Docker caching
COPY ./requirements.txt /usr/src/app/requirements.txt

# Set working directory for RUN, CMD, ENTRYPOINT, COPY, and ADD commands
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
