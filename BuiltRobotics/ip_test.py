import socket

local_ip = socket.gethostbyname(socket.gethostname())

TCP_IP = local_ip
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

print("IP Address: {}".format(TCP_IP))

s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_client.connect((TCP_IP, TCP_PORT))
s_client.send(MESSAGE)
data = s_client.recv(BUFFER_SIZE)

s_client.close()
print "received data:", data


# s_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s_server.bind((TCP_IP, TCP_PORT))
# s_server.listen(1)

# conn, addr = s_server.accept()
# print 'Connection address:', addr
# while 1:
#     data = conn.recv(BUFFER_SIZE)
#     if not data: break
#     print "received data:", data
#     conn.send(data)  # echo
# conn.close()




