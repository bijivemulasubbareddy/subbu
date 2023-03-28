
# Base image
FROM python:3.8.10

# Copy the producer file to the container
COPY . consumer\consumer.py

# Set the working directory
WORKDIR /consumer\consumer.py

RUN pip3 install python-dotenv kafka-python

# Run the socket server
CMD ["python3", "producer.py"]
