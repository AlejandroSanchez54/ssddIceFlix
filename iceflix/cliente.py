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
        self.token = ""
        self.media = []

    def run(self,argv):

        proxyMainString = input()
        

    def connect(self):
        print("Please enter the proxy of the main service: \n")
        tries = 0
        proxyMainString = input()
        broker = self.communicator()
        proxyMain = broker.stringToProxy(proxyMainString)
        

        while tries<3:
            print("Trying to connect with MainService. Please wait... ")
            try:       
                mainService = IceFlix.MainPrx.checkedCast(proxyMain)
                tries = 3
                return True
            except IceFlix.TemporaryUnavailable:
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

    def autenthicate_user(self, mainService):
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
                    return True
                except IceFlix.Unauthorized:
                    print("Unathorized user. \n")
                except:
                    print("Unexpected error has ocurred.")

    def search_name(self, mainService, exact):
        print("Enter name to search: \n" )
        name = input()

        try:
            catalog = mainService.getCatalog()
            media = catalog.getTilesByName(name,exact)
            if media != []:
                for i in len(media):
                    video = catalog.getTile(media[i], self.token)
                    print("{video.info.name} \n")
                
                self.media = media
            else:
                print("Not found video. \n")
            
        except IceFlix.TemporaryUnavailable:
            print("Temporary Unavailable.\n")

        except IceFlix.Unauthorized:
            print("You are not authorized.\n")
        
        except IceFlix.WrongMediaId:
            print("Wrong media Id.\n")

    def search_tag(self, mainService, includeAllTags):
        print("Enter the name of the tags: \n")
        tags = input().split()
        try:
            catalog = mainService.getCatalog()
            media = catalog.getTilesByTags(tags,includeAllTags, self.token)
            if media != []:
                for i in len(media):
                    video = catalog.getTile(media[i], self.token)
                    print("{video.info.name} \n")
                
                self.media = media
            else:
                print("Not found video. \n")
            
        except IceFlix.TemporaryUnavailable:
            print("Temporary Unavailable.\n")

        except IceFlix.Unauthorized:
            print("You are not authorized.\n")
        
        except IceFlix.WrongMediaId:
            print("Wrong media Id.\n")
    
    def authenticate_admin(self, mainService):
        print("Please introduce the token of the administrator: \n")
        admin_token = input()

        if admin_token != "":
            try:
                authenticator = mainService.getAuthenticator()
                if authenticator.isAdmin(admin_token) == True:
                    print("Successful administrator authentication")
                else:
                    print("Not successful administrator authentication")
            
            except IceFlix.TemporaryUnavailable:
                print("Temporary Unavailable.\n")

            except IceFlix.Unauthorized:
                print("You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print("You have entered an invalid administrator token.\n") 

    def add_user(self, mainService):
        print("The choosen option is: add_user. Please introduce the token of the administrator:\n")
        admin_token = input()
        print("Now introduce the user name of the new user: \n")
        user_name = input()
        user_psswd = getpass.getpass(prompt="Introduce the password of the new user:")
        hash_user_psswd = hashlib.sha256(user_psswd.encode()).hexdigest()
        if user_name != "" or user_psswd !="":
            try:
                authenticator = mainService.getAuthenticator()
                authenticator.addUser(user_name, hash_user_psswd, admin_token)
                print("Succesfull operation. User {user_name} added.\n")
            
            except IceFlix.TemporaryUnavailable:
                print("Temporary Unavailable.\n")

            except IceFlix.Unauthorized:
                print("You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print("You have entered an invalid user name or password.\n")

    def remove_user(self, mainService):
        print("The choosen option is: remove_user. Please introduce the token of the administrator:\n")
        admin_token = input()
        print("Now introduce the user name of the user you want remove: \n")
        user_name = input()

        if user_name != "":
            try:
                authenticator = mainService.getAuthenticator()
                authenticator.removeUser(user_name, admin_token)
                print("Succesfull operation. User {user_name} removed.\n")
            
            except IceFlix.TemporaryUnavailable:
                print("Temporary Unavailable.\n")

            except IceFlix.Unauthorized:
                print("You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print("You have entered an invalid user name.\n")




    
class AdministratorShell(cmd.Cmd):
    # def __init__(self, *args):
    #     super().__init__(*args)
    intro = '\nYou are logged into IceFLix Administrator Interface. Please type the option you want to choose:\n \nType help or ? to list commands.\n'
    prompt= '(Administrator): '


    def do_add_user(self,arg):
        'Add user to IceFLix.'
        print("Add user")

    def do_remove_user(self,arg):
        'Remove user to IceFLix.'
        print("Delete user")

    def do_rename_media(self,arg):
        'Rename a media in the Catalog.'
        print("Rename file")

    def do_upload_file(self,arg):
        'Upload a file into FileService.'
        print("Upload file")

    def do_remove_file(self,arg):
        'Remove a file into FileService.'
        print("Upload file")

    def do_exit(self, arg):
        'Close the administrator shell and EXIT.'
        print('\nClosed IceFlix Administrator Interface.\n')
        return True
class UserShell(cmd.Cmd):
    # def __init__(self, *args):
    #     super().__init__(*args)
    intro = '\nYou are logged into IceFLix User Interface. Please type the option you want to choose:\n \nType help or ? to list commands.\n'
    prompt= '(User): '

    def do_search_by_name(self, arg):
        'Search a media in the catalog by name.'
        cliente= Client()
        cliente.search_name()


    def do_search_by_tag(self, arg):
        'Search a media in the catalog by tag.'
        cliente= Client()
        cliente.search_tag()

    def do_download_file(self, arg):
        'Download a file.'




    def do_exit(self, arg):
        'Close the user shell and EXIT.'
        print('\nClosed IceFlix User Iterface. \n')
        return True



class ClientShell(cmd.Cmd):
    # def __init__(self, *args):
    #     super().__init__(*args)
    intro = 'WELCOME to Iceflix Application. Please type the option you want to choose:\n \nType help or ? to list commands.\n'
    prompt= '(IceFLix): '
    

    def do_connect(self,arg):
        'Connection of Client or Administrator'
        print('Connecting to the Main Service...')
        # print('Please introduce the proxy of the main service. \n ')
        # proxyMain=input
        # cliente= Client.connect(self,proxyMain)
        cliente= Client()
        
        #if(cliente.connect()==True):
            #if(cliente.autenthicate(self, self.mainService)==True):
        
        opcion=input()
        if opcion == "uno":
            sub_client= UserShell()
            sub_client.cmdloop()
        else:
            sub_administrador= AdministratorShell()
            sub_administrador.cmdloop()




    def do_anonimousSearch(self,arg):
        'Anonimous search by name'


    def do_exit(self, arg):
        'Close IceFLix and EXIT.'
        print('\nThank you for using IceFlix application. Come back soon !!! <3 \n')
        return True

if __name__ == '__main__':

    root=ClientShell()
    root.cmdloop()
