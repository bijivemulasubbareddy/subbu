"""The above code is importing the necessary libraries for the program to run.
"""
import socket
import json
import time
socket_connection = socket.socket()
socket_connection.bind(('',12345))
socket_connection.listen(3)
client, addr = socket_connection.accept()

data = {
    "Battery_Level":3.1,
    "Device_Id":1156053076,
    "First_Sensor_temperature":19.4,
    "Route_From":"Hyderabad, India",
    "Route_To":"Louisville, USA"
}


while True:
    try:
        # print("connected with", addr)
        userdata = (json.dumps(data)+"\n").encode('utf-8')
        client.send(userdata)
        time.sleep(1)
    except Exception as e:
        print(e)
        client.close()



