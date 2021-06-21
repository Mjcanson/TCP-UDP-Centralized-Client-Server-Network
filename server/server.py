# don't modify this imports.
import socket
from threading import Thread
from client_handler import ClientHandler

class Server(object):
    """
    The server class implements a server socket that can handle multiple client connections.
    It is really important to handle any exceptions that may occur because other clients
    are using the server too, and they may be unaware of the exceptions occurring. So, the
    server must not be stopped when a exception occurs. A proper message needs to be show in the
    server console.
    """
    MAX_NUM_CONN = 10  # keeps 10 clients in queue

    def __init__(self, host="127.0.0.1", port=12000):
      
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # your implementation for this socket here
        self.handlers = {}  # initializes client_handlers list

    def _bind(self):
       
        self.server.bind((self.host,self.port))
      

    def _listen(self):
        
        try:
            self._bind()
            print('Server is running without issues')
            self.server.listen(Server.MAX_NUM_CONN)
            print("Listening at " + str(self.host) + "/" + str(self.port))

        except (ConnectionError,OSError) as error:  
            print(error)
       

    def _accept_clients(self):

        while True:
            clientsocket, addr = self.server.accept()
            #starts threading for clients
            Thread(target=self._handler, args=(clientsocket,addr)).start()



    def _handler(self, clienthandler, addr):
        """
        TODO: create an object of the ClientHandler.
              see the clienthandler.py file to see
              the parameters that must be passed into
              the ClientHandler's constructor to create
              the object.
              Once the ClientHandler object is created,
              add it to the dictionary of client handlers initialized
              on the Server constructor (self.handlers)
        :clienthandler: the clienthandler child process that the server creates when a client is accepted
        :addr: the addr list of server parameters created by the server when a client is accepted.
        """
        clienth = ClientHandler(self, clienthandler, addr)

        #dic of clienthandler 
        #TODO OPTION 1 needs to be revised since were using addr as keys now
        self.handlers[addr] = clienth

    

        clienth.run()
    def run(self):
        """
        Already implemented for you
        Run the server.
        :return: VOID
        """
        
        self._listen()
        self._accept_clients()



# main execution
if __name__ == '__main__':
    server = Server()
    server.run()
    