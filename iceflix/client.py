#!/usr/bin/python3

'''Implememtatiom of the client of the application iceflix. Distributed System 2022/2023 by Alejandro Sánchez Arcos''' #pylint: disable=C0301
#pylint: disable=C0200
#pylint: disable=W0613
#pylint: disable=W0201
#pylint: disable=R1710
#pylint: disable=R0201
#pylint: disable=C0410
#pylint: disable=E1101
#pylint: disable=C0103
#pylint: disable=C0303
#pylint: disable=E0213

import sys, cmd, time, getpass, hashlib, threading, random, logging
from colorama import Fore
import IceStorm
import Ice
try:
    import IceFlix # pylint:disable=import-error

except ImportError:
    import os
    Ice.loadSlice(os.path.join(os.path.dirname(__file__), "iceflix.ice"))
    import IceFlix


class FileUploader(IceFlix.FileUploader):
    '''Implementation of fileUploader servant.'''
    def _init_(self, file_name):
        self.cont_file = open(file_name, "rb")
    def receive(self, size, current=None):
        '''Implementation of the receive file.'''
        return self.cont_file.read(size)
    def close(self, current=None):
        '''Implementation of the close file.'''
        self.cont_file.close()
        current.adapter.remove(current.id)

class ChannelAuthenticators(IceFlix.UserUpdate):
    '''Implementation of UserUpdate servant.'''
    def newToken(self, user, token, serviceId, current=None):
        '''Implementation of the channel info for newToken.'''
        print("\nThe authenticator service with id: " + serviceId +" call newToken for user: " + user + ". The new token is: " + token + ".")

    def revokeToken(self, token, serviceId, current=None):
        '''Implementation of the channel info for revokeToken.'''
        print("\nThe authenticator service with id: " + serviceId +" call revokeToken for token: " + token + ".")

    def newUser(self, user, passwordHash, serviceId, current=None):
        '''Implementation of the channel info for newUser.'''
        print("\nThe authenticator service with id: " + serviceId +" call newUser for user: " + user + " and password hash: " + passwordHash + ".")

    def removeUser(self, user, serviceId, current=None):
        '''Implementation of the channel info for removeUser.'''
        print("\nThe authenticator service with id: " + serviceId +" call removeUser for user: " + user + ".")


class ChannelMediaCatalogs(IceFlix.CatalogUpdate):
    '''Implementation of CatalogUpdate servant.'''

    def renameTile(self, mediaId, newName, serviceId, current=None):
        '''Implementation of the channel info for renameTile.'''
        print("\nThe media catalog service with id: " + serviceId +" call renameTile for media id: " + mediaId + ". The new name is: " + newName + ".")

    def addTags(self, mediaId, user, tags, serviceId, current=None):
        '''Implementation of the channel info for addTags.'''
        print("\nThe media catalog service with id: " + serviceId +" call addTags for media id: " + mediaId + " and user" + user + " . The tags added are: " + str(tags)+ ".")

    def removeTags(self, mediaId, user, tags, serviceId, current=None):
        '''Implementation of the channel info for removeTags.'''
        print("\nThe media catalog service with id: " + serviceId +" call removeTags for media id: " + mediaId + " and user" + user + " . The tags removed are: " + str(tags)+ ".")


class ChannelFileServices(IceFlix.FileAvailabilityAnnounce):
    '''Implementation of FileAvailabilityAnnounce servant.'''
    def announceFiles(self, mediaIds, serviceId):
        '''Implementation of the channel info for announceFiles.'''
        print("\nThe file service with id: " + serviceId +" call announceFiles. Media ids are: " + str(mediaIds) + " .")


class AdministratorShell(cmd.Cmd):
    '''Implementation of administrator interface.'''
    def __init__(self, main_service, admin_token, broker):
        '''Implementation of the initialization of the administrator shell.'''
        self.intro = Fore.YELLOW+'\nYou are logged into IceFLix Administrator Interface.' + Fore.RESET+' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.YELLOW + '(Administrator): '+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = ""
        self.admin_token = admin_token
        self.broker = broker
        self.catalog_adapter = self.broker.createObjectAdapterWithEndpoints("CatalogAdapter", "tcp")
        self.autentic_adapter = self.broker.createObjectAdapterWithEndpoints("AuthenticatorAdapter", "tcp")
        self.file_adapter = self.broker.createObjectAdapterWithEndpoints("FileServiceAdapter", "tcp")
        self.fileuploader_adapter = self.broker.createObjectAdapterWithEndpoints("FileUploaderAdapter", "tcp")
        super(AdministratorShell, self).__init__()

    def do_add_user(self, _):
        '''Implementation of the add user option.'''
        print("The choosen option is: add_user. Please introduce the user name of the new user:")
        user_name = input()
        user_psswd = getpass.getpass(prompt="Introduce the password of the new user:")
        hash_user_psswd = hashlib.sha256(user_psswd.encode()).hexdigest()
        if user_name != "" or user_psswd != "":
            try:
                if self.main_service:
                    authenticator = self.main_service.getAuthenticator()
                    authenticator.addUser(user_name, hash_user_psswd, self.admin_token)
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " User:" + (user_name) + " added.\n")
            except IceFlix.TemporaryUnavailable:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable.\n")
            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You have entered an invalid user name or password.\n")

    def do_remove_user(self, _):
        '''Implementation of the remove user option.'''
        print("The choosen option is: remove_user. Please introduce the user name of the user you want remove:")
        user_name = input()
        if user_name != "":
            try:
                if self.main_service:
                    authenticator = self.main_service.getAuthenticator()
                    authenticator.removeUser(user_name, self.admin_token)
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " User: " + (user_name) + " removed.\n")
            except IceFlix.TemporaryUnavailable:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable.\n")

            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator.\n")
        else:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You have entered an invalid user name.\n")

    def do_rename_media(self, _):
        '''Implementation of the rename media option.'''
        print("\n--- YOU HAVE CHOSEN THE OPTION ---: rename_media. Please introduce the id of the media you want to rename:")
        media_id = input()
        print("Introduce the new name for this media id:")
        media_newname = input()
        if media_id != "" and media_newname != "":
            try:
                catalog = self.main_service.getCatalog()
                if self.main_service:
                    catalog.renameTile(media_id, media_newname, self.admin_token)
                    print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Renamed title with" + (media_id) + "id to " + (media_newname) +" name.")
            except IceFlix.Unauthorized:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator. Please check it and try again.\n")

            except IceFlix.WrongMediaId:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_upload_file(self, _):
        '''Implementation of the upload file option.'''
        print("The choosen option is: upload_file. Please introduce the file path: ")
        file = input()
        fileup_servant = FileUploader(file)
        fileup_prx = self.fileuploader_adapter.addWithUUID(fileup_servant)
        try:
            file_uploader = IceFlix.FileUploaderPrx.uncheckedCast(fileup_prx)
            file_service = self.main_service.getFileService()
            if self.main_service:
                file_service.uploadFile(file_uploader, self.admin_token)
                print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Upload file.")
        except IceFlix.Unauthorized:
            print("ERROR. You are not authorized cause the introduced token is not an administrator. Please check it and try again.\n")

    def do_remove_file(self, _):
        '''Implementation of the remove file option.'''
        print("The choosen option is: remove_file. Please introduce the media id you want to remove:")
        media_id = input()
        try:
            file_service = self.main_service.getFileService()
            file_service.removeFile(media_id, self.admin_token)
            print(Fore.GREEN+"\n**SUCCESSFUL OPERATION**."+ Fore.RESET + " Remove media id:" + (media_id))
        except IceFlix.Unauthorized:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " You are not authorized cause the introduced token is not an administrator. Please check it and try again.\n")
        except IceFlix.WrongMediaId:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Wrong media Id. Please check it and try again.\n")

    def do_subscribeChannel_Authenticators(self, _):
        '''Implementation of the subscribe Authenticator channel option.'''
        print("Press Ctrl+D if you want to stop and unsubscribe the authenticators  channel:")
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("Invalid proxy")
            return 2
        try:
            topic_authentic = topic_mgr.retrieve('UserUpdates')
        except IceStorm.NoSuchTopic:
            topic_authentic = topic_mgr.create('UserUpdates')
        
        autentic_servant = ChannelAuthenticators()
        self.autentic_adapter.activate()
        autentic_prx = self.autentic_adapter.addWithUUID(autentic_servant)
        topic_authentic.subscribeAndGetPublisher({}, autentic_prx)

        try:
            while True:
                EOF_error = input()
        except (EOFError):
            topic_authentic.unsubscribe(autentic_prx)

    def do_subscribeChannel_MediaCatalogs(self, _):
        '''Implementation of the subscribe Media Catalog channel option.'''
        print("Press Ctrl+D if you want to stop and unsubscribe the media catalogs channel:")
        topic_mgr = self.get_topic_manager()
        
        if not topic_mgr:
            print("Invalid proxy")
            return 2
        try:
            topic_catalog = topic_mgr.retrieve('CatalogUpdates')
        except IceStorm.NoSuchTopic:
            topic_catalog = topic_mgr.create('CatalogUpdates')
        
        catalog_servant = ChannelMediaCatalogs()
        self.catalog_adapter.activate()
        catalog_prx = self.catalog_adapter.addWithUUID(catalog_servant)
        topic_catalog.subscribeAndGetPublisher({}, catalog_prx)

        try:
            while True:
                EOF_error = input()
        except (EOFError):
            topic_catalog.unsubscribe(catalog_prx)
    
    def do_subscribeChannel_FileServices(self, _):
        '''Implementation of the subscribe File Service channel option.'''
        print("Press Ctrl+D if you want to stop and unsubscribe the file services channel:")
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("Invalid proxy")
            return 2
        try:
            topic_file = topic_mgr.retrieve('FileAvailabilityAnnounce')
        except IceStorm.NoSuchTopic:
            topic_file = topic_mgr.create('FileAvailabilityAnnounce')
        
        file_servant = ChannelFileServices()
        self.file_adapter.activate()
        file_prx = self.file_adapter.addWithUUID(file_servant)
        topic_file.subscribeAndGetPublisher({}, file_prx)

        try:
            while True:
                EOF_error = input()
        except (EOFError):
            topic_file.unsubscribe(file_prx)

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.broker.propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None
        return IceStorm.TopicManagerPrx.checkedCast(proxy)
    
    def do_exit(self, _):
        '''Implementation of the exit option.'''
        'Close the administrator shell and EXIT.'
        print('\nClosed IceFlix Administrator Interface.\n')
        return True
    
    def do_EOF(self, line):
        '''Implementation of the ctrl+D option to exit.'''
        self.do_exit(line)
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
        '''Implementation of the exit option.'''
        print('\nClosed IceFlix User Interface.\n')
        return True

    def do_EOF(self, line):
        '''Implementation of the ctrl+D option to exit.'''
        self.do_exit(line)
        return True


class ClientShell(cmd.Cmd):
    '''Implementation of the client iceflix interface.'''
    def __init__(self, main_service, broker):
        '''Implementation of the initialization of the client shell'''
        self.intro = Fore.CYAN+'\nWELCOME to Iceflix Application.' + Fore.RESET +' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.CYAN+'(IceFLix):'+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = ""
        self.broker = broker
        self.catalog_adapter = self.broker.createObjectAdapterWithEndpoints("CatalogAdapter", "tcp")
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
                            user_shell = UserShell(self.main_service, self.token, user_name)
                            user_shell.cmdloop()
                        else:
                           print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " LOGIN NOT SUCCESFULL by user:" + user_name + ". Please check it and try again.\n")
                    return True
                
                except (IceFlix.TemporaryUnavailable, Ice.UnknownException):
                    print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Temporary Unavailable. Please check it and try again.\n")
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
                        admin_shell = AdministratorShell(self.main_service, admin_token, self.broker)
                        admin_shell.cmdloop()
                    else:
                        print(Fore.RED + "\n**ERROR**. " + Fore.RESET + " Not successful administrator authentication.Please check it and try again.\n")
            except (IceFlix.TemporaryUnavailable, Ice.UnknownException):
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
                    print(f"{i}. ** {media[i]} ** \n")
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

    def do_EOF(self, line):
        'EOF EXIT.'
        self.do_exit(line)
        return True


class Announcement(IceFlix.Announcement):   
    def __init__(self, main_service, list_mainservices):
        self.main_service = main_service
        self.list_mainservices = list_mainservices

        
    def announce(self, service, serviceId, current=None):        
        if service.ice_isA('::IceFlix::Main'):
            #print("entra")
            try:
                self.main_service = IceFlix.MainPrx.checkedCast(service)
                #print(self.list_mainservices)
                if serviceId not in list(self.list_mainservices):
                    self.list_mainservices[serviceId] = self.main_service
                    #print("Main Service connected with id:  " + serviceId)
                elif not self.main_service:
                    self.list_mainservices.pop(self.main_service)
            except (Ice.NoEndpointException, IceFlix.TemporaryUnavailable):
                logging.error("Sorry, the main service is not available")
                print()
                self.list_mainservices.pop(self.main_service)
        
          
    def reconnect_mains(self):
        while True:
            #INTENTO RECONNECT CON OTRO MAIN Y BORRAR LISTAS
            # print("hola")
            # for proxy in self.list_mainservices.values():
            #     try:
            #         proxy.ice_ping()
            #         print(proxy.ice_ping())
                        
            #     except (Ice.ConnectionRefusedException,Ice.ConnectTimeoutException):
            #         for clave,valor in self.list_mainservices.items():
            #                 if valor == proxy:
            #                     del self.list_mainservices[clave]
            #                     print("delete")
                    
            #         print(self.list_mainservices)
                            
            #         print("hola")
            #         #break
            #     #print(proxy)

            if len(self.list_mainservices) != 0:
                print("\nInitializing IceFlix...")
                time.sleep(5.0)
                break
                
            else:
                print("Please wait a moment for another available main service...")
                time.sleep(5.0)


class Client(Ice.Application):
    """Implementation of the client."""
    def __init__(self):
        """Implementation of the initialization of the client."""
        self.token = ""
        self.media = []
        self.main_service = None
        self.list_mainservices = {}

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def get_random_main(self, list_mainservices):
        mains = list(self.list_mainservices.items())
        if len(mains) != 0:
                random_main = random.choice(mains)
                return random_main[1]

    def run(self, _):
        """Implementation of run client."""
        topic_mgr = self.get_topic_manager()
        broker = self.communicator()
        if not topic_mgr:
            print("Invalid proxy")
            return 2
        try:
            topic_announcement = topic_mgr.retrieve('Announcements')
        except IceStorm.NoSuchTopic:
            topic_announcement = topic_mgr.create('Announcements')
        announ_serv = Announcement(self.main_service, self.list_mainservices)
        announ_adapter = self.communicator().createObjectAdapterWithEndpoints("AnnouncementAdapter", "tcp")
        announ_adapter.activate()
        announ_prx = announ_adapter.addWithUUID(announ_serv)
        topic_announcement.subscribeAndGetPublisher({}, announ_prx)
        counter = 0
        while True:
            self.main_service = self.get_random_main(self.list_mainservices)
            if self.main_service:
                print("\nIceFLix Main Service: " + str(self.main_service) + Fore.GREEN +" SUCCESSFULLY CONNECTED." + Fore.RESET + " ")
                cliente_shell = ClientShell(self.main_service, broker)
                threading.Thread(target=announ_serv.reconnect_mains(), daemon=True).start()
                threading.Thread(name='cliente_shell', target=cliente_shell.cmdloop(), daemon=True).start()
                break
            else:
                print("Ups there are not main services. Please wait a moment for an available main service...")
                counter += 1
                time.sleep(5.0)
            
            if counter == 4:
                print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX TIMER EXPIRED. THERE ARE NOT AVAILABLE MAINS AT THIS MOMENT. PLEASE TRY AGAIN LATER :( .")
                break

        print("TO FINISH THE EXECUTION PRESS CTRL C")
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        topic_announcement.unsubscribe(announ_prx)

        #ENTREGA 1:
        # broker = self.communicator()
        # servant = FileUploader()
        # adapter = broker.createObjectAdapterWithEndpoints("FileUploaderAdapter", "tcp")
        # proxy_fileuploader = adapter.add(servant, broker.stringToIdentity("fileuploader1"))
        # proxy_fileuploader = IceFlix.FileUploaderPrx.uncheckedCast(proxy_fileuploader)
        # adapter.activate()
        # self.connect()
        # if self.main_service:
        #     cliente_shell = ClientShell(self.main_service, proxy_fileuploader)
        #     threading.Thread(name='cliente_shell', target=cliente_shell.cmdloop(), daemon=True).start()
        #     self.shutdownOnInterrupt()
        #     # broker.waitForShutdown()
        #     return 0
        # else:
        #     print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX. PLEASE TRY AGAIN :( .")
        #     return -1

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

if __name__ == "__main__":
    sys.exit(Client().main(sys.argv))
