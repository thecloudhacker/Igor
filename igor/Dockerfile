# Grab Python image:
FROM python:3.8-alpine

# Copy Python requirements to the new image
COPY ./requirements.txt /app/requirements.txt

# Switch to working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

# set crontab for backend services

# launch the app
CMD ["app.py" ]