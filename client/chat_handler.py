import socket
import json
from threading import Thread, Lock
import time


class Chat_handler:
    def __init__(self,addr, isAdmin, client,chat_users):

        #channelid is the port used in address
        # self.chat_users = {}
        self.chat_users = chat_users
        self.ip = addr[0]
        self.channelId = addr[1]
        self.isAdmin = isAdmin
        self.adminUser = None
        self.user = None
        self.username = client.username
        self.log_lock = Lock()
        self.adminUsername = None
        
        
        if isAdmin:
            self.adminUser = client
        
        else:
            self.adminUser = 'admin'


        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP) #udp socket
        self.udp_socket.bind(('',self.channelId)) # '' binds to your local area IP address

        #save users
        self.handler(self.username)
        # print(self.chat_users)
    
    def run(self):
        
        if self.isAdmin:
            print('Private key received from server and channel {} was successfully created! \n'.format(self.channelId))
            print('----------------------- Channel {} ------------------------\n'.format(self.channelId))
            print('All the data in this channel is encrypted\n')
            print('General Admin Guidlines:')
            print('1. #{} is the admin of this channel'.format(self.adminUsername))
            print("2. Type '#exit' to terminate the channel (only for admins)\n\n")
            print('General Chat Guidlines:')
            print('1. Type #bye to exit from this channel. (only for non-admins users)')
            print('Use #<username> to send a private message to that user.')

            listen_thread = Thread(target=self.listen)
            listen_thread.start()
            print('waiting for users to join...')
            
          
            while True:
               
                msg = '{}> {}'.format(self.username, input(''))
                if msg == '{}> #exit'.format(self.username):
                    

                    close_message = 'Channel {} closed by admin.'.format(self.channelId)
                    self.broadcast(close_message.encode('utf-8'))
                    break
                else:
                   
                    self.broadcast(msg.encode('utf-8'))
        else:
            print('----------------------- Channel {} ------------------------\n'.format(self.channelId))
            print('All the data in this channel is encrypted\n')
            print('General Admin Guidlines:')
            print('1. #{} is the admin of this channel'.format(self.adminUsername))
            print("2. Type '#exit' to terminate the channel (only for admins)\n\n")
            print('General Chat Guidlines:')
            print('1. Type #bye to exit from this channel. (only for non-admins users)')
            print('Use #<username> to send a private message to that user.')

            listen_thread = Thread(target=self.listen)
            listen_thread.start()

            joined_msg = '{} just joined!'.format(self.username)
            # self.chat_users[self.username] = 'public key'
            # print(self.chat_users)
            self.broadcast(joined_msg.encode('utf-8'))
            while True:

                msg = '{}> {}'.format(self.username, input(''))

                if msg == '{}> #bye'.format(self.username):
                    leave_message = '{} has left the channel.\n'.format(self.username)
                    self.broadcast(leave_message.encode('utf-8'))
                    break
                else:
                    
                    self.broadcast(msg.encode('utf-8'))

    def receive(self):
        while True:
            data,addr = self.udp_socket.recvfrom(1024)
            print(data.decode('utf-8'))

    def handler(self, user):
        self.chat_users[self.username] = self.isAdmin
    def listen(self):
        self.receive()

    def broadcast(self,message, toItself=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1) #1 means this socket is active
        sock.sendto(message,('<broadcast>',self.channelId)) # <broadcast> is just a wildcard in python

        if toItself: #broadcast to itself 
            self.listen()

