
# Base image
FROM python:3.8.10

# Set the working directory
WORKDIR /app/consumer

# Copy the consumer server file to the container
COPY . /app/consumer

RUN pip install pymongo kafka-python python-dotenv

CMD python -u consumer.py

