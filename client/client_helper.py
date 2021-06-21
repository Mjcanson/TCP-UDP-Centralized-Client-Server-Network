import threading
from bitarray import bitarray
from tracker import Tracker
import json
from threading import Thread
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from binascii import hexlify
from chat_handler import Chat_handler
class ClientHelper:

    def __init__(self, client):
        self.client = client
        self.username = ''
        self.user_option = None
        self.menu_list = ''
        self.udp_instance = None
        self.id = None
        self.reciever_private_k = None
        self.reciever_public_k = None
        self.channelId = None
        self.ip = ''
        self.chat_lock = threading.Lock()
        
        
    def create_request(self,option):
        """
        TODO: create request with a Python dictionary to save the parameters given in this function
              the keys of the dictionary should be 'student_name', 'github_username', and
              'sid'.
            :return: the request created
        """
        request = {'payload': None, 'headers':{}}
        if option == 0:
            self.username = input('Enter a username: ')
            
            request =  {'payload': None, 'headers':{'option': json.dumps(option),'username': self.username}}

        elif option == 1 :
            request =  {'payload': None, 'headers':{'option': json.dumps(option),'username': self.username}}
            #send the request to get the users
        
        elif option == 2:
            # self.send_message(request)
            message = str(input('Enter your message: '))
            recipient = int(input('Enter recipient ID: '))

            request = {'payload': message, 'headers':{'option': json.dumps(option), \
                'recipient':recipient,'username': self.username}}

        elif option == 3:
             request = {'payload': None, 'headers':{'option': json.dumps(option)}}

        elif option == 4:
            #TODO user is only able to send udp messages to clients on the same ip and port. 
            # Do we need to figure out how to send messages to clients on different ports?
            # udp ports different from the original port created when client is initialized?

            
            addr_input = input('Enter the address to bind your UDP client (e.g 127.0.0.1:6000): ')
            
            ip_addr = addr_input.split(':')[0]
            port = addr_input.split(':')[1]
            address = (ip_addr,int(port))

            recipient_addr_input = input('Enter the recipient address: ')
            recipient_addr =  recipient_addr_input.split(':')
            recipient_addr_tuple = (recipient_addr[0],int(recipient_addr[1]))

            message = input('Enter the message: ').encode('utf-8')

            self.udp_instance = Tracker(address,self.username,self.client)
            Thread(target=self.udp_instance.listen).start()
            Thread(target=Tracker.send,kwargs={'self': self.udp_instance ,'message': message,'address': recipient_addr_tuple}).start()
            
            request =  {'payload': 'UDP Message sent', 'headers':{'option': json.dumps(option),'message':message}}

        elif option == 5:
            # request = {'payload': None, 'headers':{'option': json.dumps(option)}}
            message = input("Enter the message: ")

            request = {'payload': None, 'headers':{'option': json.dumps(option),'message': message ,'clientId': self.id,'username': self.username}}


        elif option == 6:

            self.channelId = int(input('Enter the new channel id: '))

            #TODO create reciever Public and private Key
            self.reciever_private_k = self.create_private_key(2048)
            self.reciever_public_k = self.create_public_key(self.reciever_private_k)

            # print('priv: ', len(self.reciever_private_k.export_key()))
            # print('pub: ', len(self.reciever_public_k.export_key()))

            #send reciever public key to sender(server/clienthandler)
            request = {'payload': None, 'headers':{'option': json.dumps(option),'channelId': self.channelId,'public_key': self.reciever_public_k.export_key().decode()}}

        elif option == 7:

            self.channelId = int(input('Enter channel id youd like to join: '))
            self.reciever_private_k = self.create_private_key(2048)
            self.reciever_public_k = self.create_public_key(self.reciever_private_k)
            request = {'payload': None, 'headers':{'option': json.dumps(option),'channelId': self.channelId,'public_key': self.reciever_public_k.export_key().decode()}}

        elif option == 8:
            pass

        elif option == 9:

            request = {'payload': None, 'headers':{'option': json.dumps(option)}}

        elif option == 10:

            request = {'payload': None, 'headers':{'option': json.dumps(option)}}

        elif option == 11:

            request = {'payload': None, 'headers':{'option': json.dumps(option)}}
            
            

        return request



    def create_private_key(self,length):
        #TODO generate RSA object private key

        #generating private key of length (1024) bits
        private_key = RSA.generate(length)

        return private_key
        
        

    def create_public_key(self,p_key):

        #generate public key with private key
        public_key = p_key.publickey()
        
        return public_key
        
            
    def send_request(self, request):
        """
        TODO: send the request passed as a parameter
        :request: a request representing data deserialized data.
        """
        self.client.send(request)
        

    def process_response(self):
        """
        TODO: process a response from the server
              Note the response must be received and deserialized before being processed.
        :response: the serialized response.
        """
        
        resp = self.client.receive()
        # print(resp)
        if resp['headers']['ack'] == 1:
            print('Client name: {}'.format(self.username))
            self.id = resp['headers']['clientid']
            self.ip = resp['headers']['server_ip']
            
            print('Client ID: {}'.format(self.id))

            self.menu_list = json.loads(resp['payload'])

        elif resp['headers']['ack'] == 2:
            
            users_dict = resp['payload']
            # print(str(users_dict))

            #number of connected users
            print('connected users: {}'.format(len(users_dict)))

            for i in users_dict.items():
                print('{} : {}'.format(i[0],i[1]))

        elif resp['headers']['ack'] == 3:
            print('Message sent!')

        elif resp['headers']['ack'] == -3: #when user enters invalid client id
             print('invalid client id')

        elif resp['headers']['ack'] == 4:
            #TODO print number of unread messages
            print('number of unread messages: {}'.format(len(resp['payload'])))
            user_messages = resp['payload']
           
            for i in user_messages:    
            
                for j in user_messages[i]:
                    if j['message_type'] == 'broadcast':

                        #cdma protocol decryption
                        sender_code = j['sender_code']
                        encrypted_data_len = len(j['message']) // 4 
                        dec_code = bitarray(sender_code*encrypted_data_len)

                        # print('dec_code: ' ,dec_code) #TEST

                        dec_data = j['message'] ^ dec_code
                        data = dec_data[0::4]

                        # print('msg: ', data)

                        msg = bytes(data).decode('utf-8')
                        #TODO maybe find a cleaner way to print differen types of messages
                        print('{}: {} ({} from {})'.format(j['time'],msg,j['message_type'],j['sender']))
                        
                    else:
                        print('{}: {} ({} from {})'.format(j['time'],j['message'],j['message_type'],j['sender']))

        elif resp['headers']['ack'] == 5:
            pass
        elif resp['headers']['ack'] == 6:
            print('Message Broadcasted!')

        elif resp['headers']['ack'] == 7:
            chat_private_key = resp['headers']['chat_private_key']
            chat_public_key = resp['headers']['chat_public_key']
            chat_users = resp['headers']['chat_users']
            #TODO think of a better condition to check this
            if chat_private_key:
                address = (self.ip, int(self.channelId))
                ch = Chat_handler(address,True,self,chat_users)
                ch.run()

        elif resp['headers']['ack'] == 8:

            chat_public_key = resp['headers']['chat_public_key']
            chat_users = resp['headers']['chat_users']
            
            #TEST
            # print('number of users on channel: ' ,)
            # print('chat users: ' , chat_users)


            address = (self.ip, int(self.channelId))
            #TODO channelId cannot be used in the address because udp address of each chat user cannot be the same.
            ch = Chat_handler(address,False,self,chat_users)
            ch.run()

            
        elif resp['headers']['ack'] == -8:

            print('invalid channelId. Please try again.')


        elif resp['headers']['ack'] == 10:

            users_map = resp['headers']['users_map']
            users_in_map = resp['headers']['users_in_map']
            
            print('Routing table requested! Waiting for response.... ')

            self.log_map(users_map,users_in_map)
            
            
    
            
        elif resp['headers']['ack'] == 11:

            users_map = resp['headers']['users_map']
            users_in_map = resp['headers']['users_in_map']
            
            print('Routing table requested! Waiting for response.... ')

            self.log_map(users_map,users_in_map)

            res = resp['headers']['lsp_result']
            print('Routing table for {} ({}) computed with Link State Protocol: '.format(self.username,self.id))
            
            #destination, routes, cost
            self.log_lsp(res[0],res[1],res[2])
            
        elif resp['headers']['ack'] == 12:
            dvp_map = resp['headers']['dvp_result']
            users_map = resp['headers']['users_map']
            users_in_map = resp['headers']['users_in_map']

            print('Routing table requested! Waiting for response.... ')
            self.log_map(users_map,users_in_map)
            print('\n')

            print('Routing table computed with Distance Vector Protocol: ')
            self.log_map(dvp_map,users_in_map)


            self.client.close()

    def log_lsp(self,dest, routes,cost):

        titles = ['Destination', 'Path', 'Cost']

        for title in titles: 
            print('\t{:^20s}'.format(title),end= '\t|')
        print('\n')

        for i in range(len(dest)):
            print('\t{:^20s}'.format(dest[i]),end= '\t|')
            print('\t{:^20s}'.format(str(routes[i])),end= '\t|')
            print('\t{:^20d}'.format(cost[i]),end= '\t|')
            print('\n')
        

    def log_map(self,map,users):
        n = 0
        print('Network Map: \n')
        print('          ',end='\t\t')
        for u in users:
            print('|{:^20s}'.format(u),end = '\t\t')
        print('\n--------------------------------------',end='')
        print('------------------------------------------------------------------')
        
        for row in map:
            print(users[n], end='\t\t|')
            for col in row:
                print('\t\t{}'.format(col), end= '\t\t|')
            print('\n')
            n +=1 
       
    
    def start(self):
        """
        TODO: create a request with your student info using the self.request(....) method
              send the request to the server, and then process the response sent from the server.
        """

        #create initial request for menu
        req = self.create_request(0)
        self.send_request(req)
        self.process_response()

        while self.user_option != 13:
           
        
            print(self.menu_list)
            self.user_option = int(input("Your option <enter a number>: "))
            print('user choice: {}'.format(self.user_option))
            if not int(self.user_option) or type(self.user_option) == str(self.user_option) or self.user_option > 13 or self.user_option < 0:
                print('Option Choice invalid. Please try again.')
            else:
                user_req = self.create_request(int(self.user_option))
                self.send_request(user_req)
                self.process_response()
                

        self.client.close()
