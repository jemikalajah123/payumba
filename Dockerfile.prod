# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# set environment variables
ENV PYTHONUNBUFFERED 1

#set environment vars to be used
ENV AUTHOR="Philip"

#port from the container to expose to host
EXPOSE 8000

#Tell image what to do when it starts as a container
CMD /payumba/start.sh