import socket
import json

class Tracker:

    def __init__(self,addr,username,clientH):
        self.client = clientH
        # print(type(clientH))
        self.ip = addr[0] #NOTE type str. only using this for print out
        self.port = addr[1]
        self.username = username

        #socekt.SOCK_DGRAM defines that this socket will be sending a datagram
        #socket.IPPROTO_UDP to ensure we use UDP protocol 
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP) #udp socket
        self.udp_socket.bind(('',self.port)) # '' binds to your local area IP address

        # print("UDP client running and accepting other clients at udp address {}:{}".format(self.ip,self.port))


    #sending message for client through udp
    #address: tuple (ip, port)
    def send(self, message, address):
        print(f'Message sent to udp address: {address[0]}:{address[1]}')
        self.udp_socket.sendto(message, address)


    #we are just recieving data, no need to accept clients like tcp
    def receive(self):
        while True:
            data,addr = self.udp_socket.recvfrom(1024)
            print('Message: {} recieved from {}'.format(data.decode('utf-8'),addr))
            
    def chat_receive(self):
        while True:
            data,addr = self.udp_socket.recvfrom(1024)
            print('Message: {} recieved from {}'.format(data.decode('utf-8'),addr))


        
    #listen in this case is just calling method receive
    def listen(self):
        self.receive()


    def chat_listen(self):
        print('waiting for other users to join...')
        self.chat_receive()
        # while True:
        #     # self.receive()
        #     pass


    def start_channel(self):
        while True:
            message = input('> ')
            if message == '#bye':
                pass
        


    #when broadcasting, we are sending message to every client including our client
    def broadcast(self,message, toItself=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1) #1 means this socket is active
        sock.sendto(message,('<broadcast>',self.port)) # <broadcast> is just a wildcard in python

        #TODO might have to scrap this
        # option = 5
        # request = {'payload': 'broadcast message sent', 'headers':{'option': json.dumps(option), \
        #     'message': message ,'username': self.username}}

        # self.client.send_request(request)
        print("message sent!")
        
        if toItself: #broadcast to itself 
            self.listen()


# tracker = Tracker(5002)
#messages needs to be passed in bytes
# tracker.listen()
# tracker.broadcast(b'hello world',toItself=True) 