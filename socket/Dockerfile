
# # Base image
# FROM python:3.8.10


# # Set the working directory
# WORKDIR ./socket
# # Copy the socket server file to the container
# COPY . /socket

# RUN pip3 install kafka-python

# # Expose the port on which the socket server will run
# EXPOSE 12345

# # Run the socket server
# CMD ["python3", "server.py"]
FROM python:3.10.6

WORKDIR /app/socket

RUN pip install python-dotenv

COPY . ./

CMD ["python3","./server.py"]



