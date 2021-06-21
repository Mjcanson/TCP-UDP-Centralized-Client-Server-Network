########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab3: Server support for multiple clients
# Goal: Learning Networking in Python with TCP sockets
# Student Name: Michael Canson 
# Student ID: 920601003
# Student Github Username: Mjcanson
# Lab Instructions: No partial credit will be given. Labs must be completed in class, and must be committed to your
#               personal repository by 9:45 pm.
# Running instructions: This program needs the server to run. The server creates an object of this class.
#
########################################################################################################################

import threading
import json
import pickle
import time
import secrets
import random
import datetime
from bitarray import bitarray
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256


from menu import Menu
class ClientHandler:

    def __init__(self, server_instance, clienthandler, addr):
        self.server_ip = addr[0]
        self.client_id = addr[1]
        self.server = server_instance
        self.handler = clienthandler
        self.menu = Menu.get(self)
        self.print_lock = threading.Lock()
        self.messages = {} #will save all the messages that are sent to the clienthandler instance
        self.username = ""
        self.chat_public_key = None
        self.chat_private_key = None
        self.channelId_list = {}
        self.users_in_channel = {}
        self.network_map = {}
        self.users = {}
        self.users_map = None

    # TODO: implement the ClientHandler for this project.
    def process_requests(self):
      
        while True:
            data = self.handler.recv(1024)
            # print(data)
            if not data:
                break
            deserialized_data = pickle.loads(data)
            self.process_request(deserialized_data)
        
    def process_request(self,request):
        """
        TODO: This implementation is similar to the one you did in the method process_request(...)
              that was implemented in the server of lab 3.
              Note that in this case, the clienthandler is not passed as a parameter in the function
              because you have a private instance of it in the constructor that can be invoked from this method.
        :request: the request received from the client. Note that this must be already deserialized
        :return: VOID
        """
        
        option = Menu.option(request['headers']['option'])
        req_headers = Menu.request_headers(option,request)
        

        response = {'payload': None, 'headers':{ 'ack': -1}} #-1 means 

        if option == 0:
            #TODO save username and client_id it requested for
            self.username = req_headers
            response = {'payload': self.menu, 'headers': {'server_ip': self.server_ip[0],'clientid':self.client_id,'ack': 1}}

        elif option == 1:
            response['payload'] = self.users_connected()
            response['headers']['ack'] = 2  
            
        elif option == 2:
            message = request['payload']
            recipient = request['headers']['recipient']
            username = request['headers']['username']
            response['headers']['ack'] = self.save_messages(message, recipient,username,'private message')
            
            

        elif option == 3:
            response['payload'] = self.messages
            # self.messages = {} #clear messages list after user reads them
            response['headers']['ack'] = 4

        elif option == 4:
            
            response['headers']['ack'] = 5
            
        elif option == 5:
            
            broadcaster_id = request['headers']['clientId']
            message = request['headers']['message']
            username = request['headers']['username']
       
       
            response['headers']['ack'] = self.cdma_protocol(message,broadcaster_id,username)
            

        elif option == 6:
            receiver_public_key = RSA.import_key(request['headers']['public_key'])
            channelId= request['headers']['channelId']

            #generate chat public and private key
            # self.chat_private_key = self.create_private_key(1024)
            # self.chat_public_key = self.create_public_key(  self.chat_private_key)
            # print('priv: ', len(chat_private_key.export_key()))
            # print('pub: ', len(chat_public_key.export_key()))

            self.chat_private_key = secrets.token_bytes(nbytes=190)
            self.chat_public_key = secrets.token_bytes(nbytes=190)

            #encrypt chat private key
            #NOTE chat private key is transformed as a string
            cipher_message = self.RSA_encrypt(receiver_public_key,  self.chat_private_key)

            # {channelId: (admin, chat public key) , ...}
            self.channelId_list[channelId] = self.chat_public_key

            self.users_in_channel[self.username] = True
            

            response = {'payload': None, 'headers': {'chat_users':self.users_in_channel,
                'chat_private_key': cipher_message,'chat_public_key': self.chat_public_key ,'ack': 7}}

        elif option == 7:
            receiver_public_key = RSA.import_key(request['headers']['public_key'])
            channelId= request['headers']['channelId']
            # print('passed channelid', channelId)

            for c in self.server.handlers.values():
                for id in c.channelId_list.keys():
                    
                    if channelId == id:
                        self.users_in_channel.update(c.users_in_channel)
                        self.users_in_channel[self.username] = False        
                        
                        response = {'payload': None, 'headers': {'chat_users':self.users_in_channel,
                        'chat_public_key': c.chat_public_key,'ack': 8}}

                    else:
                        response = {'payload': None, 'headers': {'ack': -8}}
                
        elif option == 8:
            pass
        

        elif option == 9:
            users_in_map = self.users_connected()
            users_list = []

            for u in users_in_map.keys():
                users_list.append(u)

            self.users_map = self.create_map_network()
            
            response = {'payload': None, 'headers': {'users_map': self.users_map , 'users_in_map': users_list,'ack': 10}}
            
        elif option == 10:
            users_in_map = self.users_connected()
            users_list = []

            for u in users_in_map.keys():
                users_list.append(u)

            self.users_map = self.create_map_network()
            lsp_result  = self.link_state_protocol(users_list)
            response = {'payload': None, 'headers': {'lsp_result': lsp_result ,'users_map': self.users_map , 'users_in_map': users_list,'ack': 11}}
        
        elif option == 11:
            users_in_map = self.users_connected()
            
            users_list = []
            for u in users_in_map.keys():
                users_list.append(u)

            if type(self.users_map) == None:
                self.dv_protocol(self.users_map,users_in_map)

            else:
                self.users_map = self.create_map_network()
                dv_map = self.dv_protocol(self.users_map,users_in_map)
                print(self.users_map)
                print(dv_map)

            response = {'payload': None, 'headers': { 'dvp_result': dv_map, 'users_map': self.users_map ,'users_in_map': users_list,'ack': 12}}

        self.send(response)

    def create_map_network(self):
        #returns a list of network map

        #returns names
        users_to_map = self.users_connected()
        # print(users_to_map.values())

        network_map = []
        for x in range(len(users_to_map)):
            network_map.append([])

        # print(network_map)
        for i in range(len(users_to_map)):
            for j in range(len(users_to_map)):

                network_map[i].append('-')
                if i == j:
                    network_map[i][j] = 0
                else:
                    #1 means no link between two clients
                    network_map[i][j] = (random.randint(1,35))
            
        for n in range(len(network_map)):
            for v in range(n):

                network_map[v][n] = network_map[n][v]

        return network_map  


    def dv_protocol(self, users_map, users):
        matrix = users_map
        map = matrix
        temp_map = map
        row = 0
        count = 0
        while True:
            for i in range(len(users)):
                dist = self.distance(matrix,row,i,users)
                temp_map[row][i] = dist
                count = i
            row += 1
            if row == len(users) and temp_map == map:
                print('exited at: {}'.format(count))
                return map
            if row == len(users):
                temp_map == map
                row = 0

       

    def distance(self, matrix, current_vector, dest_vector,users):
        min_dist = matrix[current_vector][dest_vector]
        
        for j in range(len(users)):
            if j != current_vector:
                min_dist = min(min_dist, (matrix[current_vector][j] + matrix[j][dest_vector]))
                
                #test
                # print('min distance at {}: {} '.format(j, min_dist))
                # print('weight: {} '.format( (matrix[current_vector][j] + matrix[j][dest_vector])))
        #test
        # print('returned min distance: {}'.format(min_dist))
        return min_dist

    def link_state_protocol(self,users):
        destination = []
        routes = []
        cost = []

        for i in users:
            destination.append(i)

        #test
        # print('destionation list : ', destination)

        for x in range(len(destination)):
            routes.append([])

        for z in range(len(destination)):
            cost.append(0)

        #test
        # print('initial routes list: ' , routes)
        # print('initial cost list: ' , cost)

        for i in range(len(users) -1):
            cost[i] = self.users_map[0][i+1]
            routes[i] = [destination[i]]
        
        for j in range(1, len(users)):
            cur_cost = cost[j-1]
            for k in range(j, len(users)-1):
                if (self.users_map[j][k+1] + self.users_map[0][k]) < cur_cost:
                    temp_r = routes[j-1].pop()
                    routes[j-1].append(users[j+1])
                    routes[j-1].append(temp_r)
                    cost[j-1] = self.users_map[j][k+1] + self.users_map[0][k]
        
        return destination,routes,cost


    def create_private_key(self,length):
      
        #generating private key of length (1024) bits
        private_key = RSA.generate(length)

        return private_key
        
        
    def create_public_key(self,p_key):

        #generate public key with private key
        public_key = p_key.publickey()
        
        return public_key
    
    def RSA_encrypt(self, pu_key,message):
        #initialize PKCS1_OAEP object for encryption of chat private key
        cipher_encryptor = PKCS1_OAEP.new(key=pu_key,hashAlgo=SHA256)
       
         #encrypt message
         #NOTE .export_key() converts message(RSA object) to bytes
         
        # encrypted_message = cipher_encryptor.encrypt(message.export_key())
        encrypted_message = cipher_encryptor.encrypt(message)

        return encrypted_message


    def cdma_protocol(self,message,broadcaster_id,username):
        #TODO encrypt message using CDMA protocol

        #codes are static to having 4 different channels/codes
        codes = [[1, 1, 1, 1], [0, 0, 1, 1],[0,0,0,0],[0,1,1,0]] 
        client_code = codes[broadcaster_id % 4] #assign a code to broadcaster based on its id

        # print('client code: ', client_code)

        msg_data = message.encode('utf-8') #transfom message into bytes
        data = bitarray()
        data.frombytes(msg_data) #transform msg to bitarrays

        repeated_data= bitarray()
        for bit in data:
            for i in range(4):
                repeated_data.append(bit)
                i+=1

        # print('repeated data: ', repeated_data)

        spread_code = bitarray(client_code)*len(msg_data)*8

        encrypted_data = spread_code ^ repeated_data

        # print('XOR DATA' , encrypted_data)
        
        return self.save_messages(encrypted_data,client_code,username,'broadcast')

        #TODO save encrypted data into messages list
        """ Return: encoded message for client helper to decode using cdma protocol"""
        
        pass

    def users_connected(self):
        connected_users = {}
        
        
        for ch, data in self.server.handlers.keys():
            # print('ch: ',ch)
            # print('data: ',data)
            connected_users[self.server.handlers[(ch,data)].username] = data
        
        return connected_users #TODO return the list of users connected to the server
    
    def save_messages(self, message, recipient,sender,message_type):
    
        # try:
            recipient_handler = None
            if message_type == 'broadcast':
                for r in self.server.handlers.keys():
                    recipient_handler = self.server.handlers[r]
                    messages_list = recipient_handler.messages

                    if self.client_id not in messages_list.keys():
                        messages_list[self.client_id] = [] #create new list if sender not exist
                    
                    messages_info = {}
                    messages_info['message'] = message #NOTE message is encrypted data
                    messages_info['time'] = time.ctime()
                    messages_info['sender'] = self.username
                    messages_info['sender_code'] = recipient #NOTE that reciepient is the client_code
                    messages_info['message_type'] = message_type
                    messages_list[self.client_id].append(messages_info)


            # recipient_handler = None
            else:
          
                for k in self.server.handlers.keys():
                
                    if recipient == k[1]:
                        recipient_handler = self.server.handlers[k]
                if recipient_handler == None:
                    return -3
                
                #TODO 2. Get the list of messages from this recipient handle 
                messages_list = recipient_handler.messages

                #TODO 3. check if sender exists
                if self.client_id not in messages_list.keys():
                    messages_list[self.client_id] = [] #create new list if sender not exist
                messages_info = {}
                messages_info['message'] = message
                messages_info['time'] = time.ctime()
                messages_info['sender'] = sender
                messages_info['message_type'] = message_type
                # messages_info = (message, time.ctime()) #you can use timedate as well for a timestamp 
                
                messages_list[self.client_id].append(messages_info)
            # print(str(recipient_handler.messages))

            if message_type == 'broadcast':
                return 6
            else:
                return 3
        # except Exception as err:
        #     self.log(err[1])

    
    def send(self, data):
        
        # print(data)
        serialized_data = pickle.dumps(data)
        self.handler.send(serialized_data)

    def receive(self, max_mem_alloc=4096):
       
        deserialized_data = pickle.loads(self.handler.recv(max_mem_alloc)) 
        return deserialized_data

    def sendID(self, clientid):
       
        msg = {'clientid:' : clientid}
        self.send(msg)

    def log(self, message):
        
        self.print_lock.acquire()
        print(message)
        self.print_lock.release()

    def run(self):
        """
        Already implemented for you
        """
        self.process_requests()




      
       
