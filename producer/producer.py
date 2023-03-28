from ensurepip import bootstrap
import socket    
import json 
import os
from pathlib import Path
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv()

server_connection = socket.socket()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")             
server_connection.connect((HOST, int(PORT)))
bootstrap_servers =os.getenv("bootstrap_servers")  


producer = KafkaProducer(bootstrap_servers = bootstrap_servers, retries = 5)

topicName = os.getenv("topic_name")

while True:
    try:
        data=server_connection.recv(70240)
        # json_acceptable_string = data.replace("'", "\"")
        # load_data = json.loads(json_acceptable_string)
        # print(load_data)
        # for data in load_data:
        print(data)
        producer.send(topicName, data)

    except Exception as exception:
        print(exception)
socket_connection.close()