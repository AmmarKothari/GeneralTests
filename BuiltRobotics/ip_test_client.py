import socket

local_ip = socket.gethostbyname(socket.gethostname())

TCP_IP = local_ip
TCP_IP = '127.0.0.1'
TCP_PORT = 50000
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

print("IP Address: {}".format(TCP_IP))

s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_client.connect((TCP_IP, TCP_PORT))
s_client.send(MESSAGE)
data = s_client.recv(BUFFER_SIZE)

s_client.close()
print "received data:", data