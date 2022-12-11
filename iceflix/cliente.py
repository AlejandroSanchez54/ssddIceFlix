#!/usr/bin/python3

'''
Implememtatiom of the client of the application iceflix. Distributed System 2022/2023 by Alejandro Sánchez Arcos''' #pylint:disable=C0301
import sys, cmd, time, getpass, hashlib, threading
from colorama import Fore
import Ice
try:
    import IceFlix # pylint:disable=import-error

except ImportError:
    import os
    Ice.loadSlice(os.path.join(os.path.dirname(__file__), "iceflix.ice"))
    import IceFlix


class FileUploader(IceFlix.FileUploader):
    '''Implementation of fileUploader servant.'''
    def _init_(self, fichero):
        self.cont_file = open(fichero, "rb")
    def receive(self, size, current=None):
        '''Implementation of the receive file.'''
        return self.cont_file.read(self.size)
    def close(self, current=None):
        '''Implementation of the close file.'''
        self.cont_file.close()

class AdministratorShell(cmd.Cmd):
    '''Implementation of administrator interface.'''
    def __init__(self, main_service, file_uploader):
        '''Implementation of the initialization of the administrator shell.'''
        self.intro = Fore.YELLOW+'\nYou are logged into IceFLix Administrator Interface.' + Fore.RESET+' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.YELLOW + '(Administrator): '+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = ""
        self.file_uploader = file_uploader
        super(AdministratorShell, self).__init__()

    def do_add_user(self, _):
        '''Implementation of the add user option.'''
        print("The choosen option is: add_user. Please introduce the token of the administrator:")
        admin_token = input()
        print("Now introduce the user name of the new user:")
        user_name = input()
        user_psswd = getpass.getpass(prompt="Introduce the password of the new user:")
        hash_user_psswd = hashlib.sha256(user_psswd.encode()).hexdigest()
        if user_name != "" or user_psswd != "":
            try:
                if self.main_service:
                    authenticator = self.main_service.getAuthenticator()
                    authenticator.addUser(user_name, hash_user_psswd, admin_token)
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " User:" + (user_name) + " added.\n")
                    return True
            except IceFlix.TemporaryUnavailable:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable.\n")
            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You have entered an invalid user name or password.\n")

    def do_remove_user(self, _):
        '''Implementation of the remove user option.'''
        print("The choosen option is: remove_user. Please introduce the token of the administrator:")
        admin_token = input()
        print("Now introduce the user name of the user you want remove:")
        user_name = input()
        if user_name != "":
            try:
                if self.main_service:
                    authenticator = self.main_service.getAuthenticator()
                    authenticator.removeUser(user_name, admin_token)
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " User: " + (user_name) + " removed.\n")
                    return True
            except IceFlix.TemporaryUnavailable:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable.\n")

            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You have entered an invalid user name.\n")

    def do_rename_media(self, _):
        '''Implementation of the rename media option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: rename_media. Please introduce the token of the administrator:")
        admin_token = input()
        print("Now introduce the id of the media you want to rename:")
        media_id = input()
        print("Introduce the new name for this media id:")
        media_newname = input()
        if media_id != "" and media_newname != "":
            try:
                catalog = self.main_service.getCatalog()
                if self.main_service:
                    catalog.renameTile(media_id, media_newname, admin_token)
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Renamed title with" + (media_id) + "id to " + (media_newname) +" name.")
            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator. Please check it and try again.\n")

            except IceFlix.WrongMediaId:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_upload_file(self, _):
        '''Implementation of the upload file option.'''
        print("The choosen option is: upload_file. Please introduce the administrator token:")
        admin_token = input()
        try:
            file_uploader = self.file_uploader()
            file_service = self.main_service.getFileService()
            file_service.uploadFile(file_uploader, admin_token)
            print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Upload file.")
        except IceFlix.Unauthorized:
            print("ERROR. You are not authorized cause the introduced token is not an administrator. Please check it and try again.\n")

    def do_remove_file(self, _):
        '''Implementation of the remove file option.'''
        print("The choosen option is: remove_file. Please introduce the administrator token:")
        admin_token = input()
        print("Introduce the media id you want to remove:")
        media_id = input()
        try:
            file_service = self.main_service.getFileService()
            file_service.removeFile(media_id, admin_token)
            print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Remove media id:" + (media_id))
        except IceFlix.Unauthorized:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator. Please check it and try again.\n")
        except IceFlix.WrongMediaId:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_exit(self, _):
        '''Implementation of the exit option.'''
        'Close the administrator shell and EXIT.'
        print('\nClosed IceFlix Administrator Interface.\n')
        return True


class UserShell(cmd.Cmd):
    '''Implementation of user interface.'''
    def __init__(self, main_service, token, user_name, file_uploader):
        '''Implementation of the initialization of the user shell.'''
        self.intro = Fore.MAGENTA+'\nYou are logged into IceFLix User Interface.' + Fore.RESET+' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.MAGENTA + f'(User: {user_name}):'+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = token
        self.file_uploader = file_uploader
        super(UserShell, self).__init__()

    def do_search_by_name(self, _):
        '''Implementation of the search by name option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: search_by_name. Please introduce the name of the media you want to search:")
        name = input()
        print("Do you want an exact search? Introduce Yes or No. By default the search will be exact.")
        option = input()
        exact = True
        if option.lower() == "yes":
            exact = True
        elif option.lower() == "no":
            exact = False
        try:
            catalog = self.main_service.getCatalog()
            media = catalog.getTilesByName(name, exact)
            if media != []:
                print("\n------------- Media catalog: -------------\n")
                for i in range(len(media)):
                    video = catalog.getTile(media[i], self.token)
                    print(f"{i}. ** {video.info.name} ** \n")
            else:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Not found video. Please check it and try again. \n")
            self.media = media
        except IceFlix.TemporaryUnavailable:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable. Please check it and try again.\n")
        except IceFlix.Unauthorized:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized. Please check it and try again.\n")
        except IceFlix.WrongMediaId:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_search_by_tag(self, _):
        '''Implementation of the search by tag option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: search_by_tag. Please enter the name of the tags separating by blank spaces (WITHOUT COMMAS):")
        tags = input().split()
        print("Do you want to include all tags? Introduce Yes or No. By default the search will be exact.")
        option = input()
        include_alltags = True
        if option.lower() == "yes":
            include_alltags = True
        elif option.lower() == "no":
            include_alltags = False
        try:
            catalog = self.main_service.getCatalog()
            media = catalog.getTilesByTags(tags, include_alltags, self.token)
            if media != []:
                print("\n------------- Media catalog: -------------\n")
                for i in range(len(media)):
                    video = catalog.getTile(media[i], self.token)
                    print(f"{i}. ** {video.info.name} ** \n")
                    print(f"What do you want to do with {video.info.name}:\n 1. Add tags\n 2. Remove tags\n")
                    option = int(input())
                    if option == 1:
                        print("Introduce the new tags you want to add:")
                        new_tags = input().split()
                        catalog.addTags(video.mediaId, new_tags, self.token)
                        print(f"Added tag/s: {new_tags} in {video.info.name}")
                    elif option == 2:
                        print("Introduce the new tags you want to remove:")
                        delete_tags = input().split()
                        catalog.removeTags(video.mediaId, delete_tags, self.token)
                        print(f"Remove tag/s: {delete_tags} in {video.info.name}")
                    else: pass
            else:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Not found video. Please check it and try again. \n")
            self.media = media
        except IceFlix.TemporaryUnavailable:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable. Please check it and try again.\n")
        except IceFlix.Unauthorized:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized. Please check it and try again.\n")
        except IceFlix.WrongMediaId:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_download_file(self, _):
        '''Implementation of the download file option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: download_file. Please introduce the media id:\n")
        media_id = input()
        if self.token != "":
            try:
                file_service = self.main_service.getFileService()
                file_handler = file_service.openFile(media_id, self.token)
                file_desc = open(media_id, 'wb')
                while True:
                    bytes_received = file_handler.receive(1024, self.token)
                    if len(bytes_received) == 0:
                        break
                    file_desc.write(bytes_received)
                file_handler.close(self.token)
            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized. Please try again.\n")
            except IceFlix.WrongMediaId:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_exit(self, _):
        'Close the user shell and EXIT.'
        print('\nClosed IceFlix User Interface.\n')
        return True


class ClientShell(cmd.Cmd):
    '''Implementation of the client iceflix interface.'''
    def __init__(self, main_service, file_uploader):
        '''Implementation of the initialization of the client shell'''
        self.intro = Fore.CYAN+'\nWELCOME to Iceflix Application.' + Fore.RESET +' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.CYAN+'(IceFLix):'+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = ""
        self.file_uploader = file_uploader
        super(ClientShell, self).__init__()

    def do_login_user(self, _):
        '''Implementation of the login user option.'''
        if self.token == "":
            print("\n--- YOU HAVE CHOSEN THE OPTION ---: login_user. Please introduce your username:")
            user_name = input()
            passwrd = getpass.getpass(prompt="Now, enter your password:")
            hash_password = hashlib.sha256(passwrd.encode()).hexdigest()
            if user_name != "" or passwrd != "":
                try:
                    if self.main_service:
                        authenticator = self.main_service.getAuthenticator()
                        self.token = authenticator.refreshAuthorization(user_name, hash_password)
                        if authenticator.isAuthorized(self.token):
                            print(Fore.GREEN + "\n**SUCCESSFUL AUTHENTICATION OF USER:" + Fore.RESET + " " + (user_name) + Fore.GREEN + " **" + Fore.RESET + " ")
                            user_shell = UserShell(self.main_service, self.token, user_name, self.file_uploader)
                            user_shell.cmdloop()
                        else:
                           print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " LOGIN NOT SUCCESFULL by user:" + user_name + ". Please check it and try again.\n")
                    return True
                except IceFlix.Unauthorized:
                    print(Fore.RED + "\n**ERROR**. " + Fore.RESET + user_name + "  is not authorized. Please check it and try again.\n")
            else:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You must introduce a username and a password. Please check it and try again.\n")
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are loggin in. \n")
    
    def do_login_administrator(self, _):
        '''Implementation of the login administrator option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: login_administrator. Please introduce the token of the administrator:")
        admin_token = input()
        if admin_token != "":
            try:
                if self.main_service:
                    authenticator = self.main_service.getAuthenticator()
                    if authenticator.isAdmin(admin_token):
                        print(Fore.GREEN + "\n**SUCCESSFUL AUTHENTICATION OF ADMINISTRATOR.**." + Fore.RESET + " ")
                        admin_shell = AdministratorShell(self.main_service, self.file_uploader)
                        admin_shell.cmdloop()
                    else:
                        print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Not successful administrator authentication.Please check it and try again.\n")
            except IceFlix.TemporaryUnavailable:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable. Please check it and try again.\n")

            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized. Please try again.\n")
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You have entered an invalid administrator token. Please check it and try again.\n")

    def do_anonimous_search(self, _):
        '''Implementation of the anonimous search option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: anonimous_search. Please introduce the name of the media you want to search:")
        name = input()
        print("Do you want an exact search? Introduce Yes or No. By default the search will be exact.")
        option = input()
        exact = True
        if option.lower() == "yes":
            exact = True
        elif option.lower() == "no":
            exact = False
        try:
            catalog = self.main_service.getCatalog()
            media = catalog.getTilesByName(name, exact)
            if media != []:
                print("\n------------- Media catalog ID's: -------------\n")
                for i in range(len(media)):
                    print(f"{i}. ** {media[i].mediaId} ** \n")
            else:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Not found video. Please try again. \n")
        except IceFlix.TemporaryUnavailable:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable. Please try again.\n")
        except IceFlix.WrongMediaId:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_exit(self, _):
        'Close IceFLix and EXIT.'
        print('\nThank you for using IceFlix application. Come back soon !!!'+Fore.RED +' <3' + Fore.RESET + '\n')
        return True


class Client(Ice.Application):
    """Implementation of the client."""
    def __init__(self):
        """Implementation of the initialization of the client."""
        self.token = ""
        self.media = []
        self.main_service = None

    def run(self, _):
        """Implementation of run client."""
        broker = self.communicator()
        servant = FileUploader()
        adapter = broker.createObjectAdapterWithEndpoints("FileUploaderAdapter", "tcp")
        proxy_fileuploader = adapter.add(servant, broker.stringToIdentity("fileuploader1"))
        proxy_fileuploader = IceFlix.FileUploaderPrx.uncheckedCast(proxy_fileuploader)
        adapter.activate()
        self.connect()
        if self.main_service:
            cliente_shell = ClientShell(self.main_service, proxy_fileuploader)
            threading.Thread(name='cliente_shell', target=cliente_shell.cmdloop(), daemon=True).start()
            self.shutdownOnInterrupt()
            broker.waitForShutdown()
            return 0
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX. PLEASE TRY AGAIN :( .")
            return -1

    def connect(self):
        """Implementation of connect to the mainService"""
        print("Please enter the proxy of the Main Service:")
        for tries in range(3):
            proxy_mainstr = input()
            print("\nTrying to connect with Main Service. Please wait... ")
            try:
                broker = self.communicator()
                proxy_main = broker.stringToProxy(proxy_mainstr)
                self.main_service = IceFlix.MainPrx.checkedCast(proxy_main)
                if self.main_service:
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Connected to the Main Service...")
                    break
                else:
                    print(Fore.RED + "\n**ERROR**." + Fore.RESET+" Connection refused. Incorrect proxy. You have ", (3-(tries+1)), " tries")
                    time.sleep(5.0)
            except IceFlix.TemporaryUnavailable:
                print(Fore.RED + "\n**ERROR**. Main Service is Temporary Unavailable.\n")
                time.sleep(5.0)
            except Ice.NoEndpointException:
                print(Fore.RED+"\n**ERROR**."+Fore.RESET+" Connection refused. Incorrect proxy. You have ", (3-(tries+1)), " tries")
                time.sleep(5.0)

if __name__ == '__main__':
    sys.exit(Client().main(sys.argv))