#!/usr/bin/python3
from distutils.log import error
import sys, cmd, time, getpass, hashlib
import Ice
try:
    import IceFlix
except ImportError:
    Ice.loadSlice("iceflix.ice")





class Client(Ice.Application):
    def __init__(self):
        self.token=""

    def run(self,argv):

        proxyMainString= input
        

    def connect(self):
        print("Please enter the proxy of the main service: \n")
        tries=0
        proxyMainString=input
        proxyMain= self.communicator().stringToProxy(proxyMainString)

        while tries<3:
            print("Trying to connect with MainService. Please wait... ")
            try:       
                mainService = IceFlix.MainPrx.checkedCast(proxyMain)
                tries=3
            except IceFlix.TemporaryUnavailable as unavailable:
                print("Main Service is TemporaryUnavailable.")
                time.sleep(5.0)
                #raise IceFlix.TemporaryUnavailable() from unavailable
            except:
                print("Unknown error. Please stay sure you introduce the correct proxy.")

            tries= tries + 1
        if not mainService:
            raise RuntimeError('Invalid proxy')
        else:
            print("Connected to the mainService.")

    def autenthicate(self, mainService):
        if self.token!="":
            print("Error. You are loggin in. \n")
        else:
            print("Please introduce your username")
            username=input()
            password= getpass.getpass(prompt="Now, enter your password:")
            hash_password = hashlib.sha256(password.encode()).hexdigest()
            if username=="" or password=="":
                print("Unexpected error has ocurred. You should introduce a username and a password")
            else:
                try:
                    authenticator = mainService.getAuthenticator()
                    self.token = authenticator.refreshAuthorization(username,hash_password)
                except IceFlix.Unauthorized:
                    print("Unathorized user. \n")
                except:
                    print("Unexpected error has ocurred.")



class ClientShell(cmd.Cmd):
    intro = 'Welcome to the client shell. Type help or ? to list commands.\n'
    prompt= '(client) '


    def do_connect(self,arg):
        'Connection of Client or Administrator'
        print('Authenticating')
        # print('Please introduce the proxy of the main service. \n ')
        # proxyMain=input
        # cliente= Client.connect(self,proxyMain)
        UserShell.cmdloop




    def do_anonimousSearch(self,arg):
        'Client or Administrator authentication'
        print('Doing search')


    def do_exit(self, arg):
        'Close the client and EXIT.'
        print('Thank you for using IceFlix Client')
        return True

class UserShell(cmd.Cmd):
    intro = 'Welcome to the user shell. Type help or ? to list commands.\n'
    prompt= '(user) '

    def do_exit(self, arg):
        'Close the client and EXIT.'
        print('Thank you for using IceFlix Client')
        return True


if __name__ == '__main__':
    ClientShell().cmdloop()
