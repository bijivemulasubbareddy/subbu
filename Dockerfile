FROM python:3.9

# Copy the requirements file to the container
COPY . /SubbuScm/main.py

# # Copy the requirements file to the container
COPY . /SubbuScm/requirements.txt

# Set the working directory to /app
WORKDIR /SubbuScm/main.py

# Install the dependencies
RUN  pip3 install -r requirements.txt

# Expose port 80 for the API
EXPOSE 8000

# Run the app
CMD [ "uvicorn", "main:APP", "--reload", "--host=0.0.0.0","--port= 8000"]