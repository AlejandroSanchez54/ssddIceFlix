#!/usr/bin/python3
from distutils.log import error
import sys, cmd
import Ice
try:
    import IceFlix
except ImportError:
    Ice.loadSlice("iceflix.ice")



class Client(Ice.Application):
    def __init__(self):
        self.token=""

    def run(self, argv):
        broker = self.communicator()
        Client.authenticate(self,argv[1])

    def connect(self, proxyMain):

        proxy= self.communicator().stringToProxy(proxyMain)
        print(proxy)

        # while(i<3):
        #     try:





class ClientShell(cmd.Cmd):
    intro = 'Welcome to the client shell. Type help or ? to list commands.\n'
    prompt= '(client) '


    def do_connect(self,arg):
        'Connection of Client or Administrator'
        print('Authenticating')
        print('Please introduce the proxy of the main service. \n ')
        proxyMain= input()
        Client.main(self,proxyMain)
        




    def do_anonimousSearch(self,arg):
        'Client or Administrator authentication'
        print('DOing search')


    def do_exit(self, arg):
        'Close the client and EXIT.'
        print('Thank you for using IceFlix Client')
        return True



if __name__ == '__main__':
    ClientShell().cmdloop()
