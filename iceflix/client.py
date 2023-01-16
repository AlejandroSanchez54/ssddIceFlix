#!/usr/bin/python3

'''Implememtatiom of the client of the application iceflix. Distributed System 2022/2023 by Alejandro Sánchez Arcos''' #pylint: disable=C0301
#pylint: disable=W0311
#pylint: disable=W1201
#pylint: disable=C0103
#pylint: disable=E1101
#pylint: disable=W0613
#pylint: disable=R0201


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

class Announcement(IceFlix.Announcement):
    '''Implementation of Announcement servant.'''
    def __init__(self, main_service, list_mainservices):
        self.main_service = main_service
        self.list_mainservices = list_mainservices

    def announce(self, service, serviceId, current=None):
        '''Implementation of announce.'''
        if service.ice_isA('::IceFlix::Main'):
            try:
                self.main_service = IceFlix.MainPrx.checkedCast(service)
                if serviceId not in list(self.list_mainservices):
                    self.list_mainservices[serviceId] = self.main_service
            except (IceFlix.TemporaryUnavailable, Ice.UnknownException):
                logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + "Please check it and try again.\n")


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
        logging.info(" The authenticator service with id: " + Fore.MAGENTA + serviceId + Fore.RESET +" call newToken for user: " + user + ". The new token is: " + token + ".")

    def revokeToken(self, token, serviceId, current=None):
        '''Implementation of the channel info for revokeToken.'''
        logging.info(" The authenticator service with id: " +  Fore.MAGENTA +serviceId + Fore.RESET +" call revokeToken for token: " + token + ".")

    def newUser(self, user, passwordHash, serviceId, current=None):
        '''Implementation of the channel info for newUser.'''
        logging.info(" The authenticator service with id: " + Fore.MAGENTA + serviceId + Fore.RESET +" call newUser for user: " + user + " and password hash: " + passwordHash + ".")

    def removeUser(self, user, serviceId, current=None):
        '''Implementation of the channel info for removeUser.'''
        logging.info(" The authenticator service with id: " + Fore.MAGENTA + serviceId + Fore.RESET +" call removeUser for user: " + user + ".")


class ChannelMediaCatalogs(IceFlix.CatalogUpdate):
    '''Implementation of CatalogUpdate servant.'''

    def renameTile(self, mediaId, newName, serviceId, current=None):
        '''Implementation of the channel info for renameTile.'''
        logging.info(" The media catalog service with id: " + Fore.BLUE + serviceId + Fore.RESET +" call renameTile for media id: " + mediaId + ". The new name is: " + newName + ".")

    def addTags(self, mediaId, user, tags, serviceId, current=None):
        '''Implementation of the channel info for addTags.'''
        logging.info(" The media catalog service with id: " + Fore.BLUE + serviceId + Fore.RESET +" call addTags for media id: " + mediaId + " and user" + user + " . The tags added are: " + str(tags)+ ".")

    def removeTags(self, mediaId, user, tags, serviceId, current=None):
        '''Implementation of the channel info for removeTags.'''
        logging.info(" The media catalog service with id: " + Fore.BLUE + serviceId + Fore.RESET +" call removeTags for media id: " + mediaId + " and user" + user + " . The tags removed are: " + str(tags)+ ".")


class ChannelFileServices(IceFlix.FileAvailabilityAnnounce):
    '''Implementation of FileAvailabilityAnnounce servant.'''
    def announceFiles(self, mediaIds, serviceId):
        '''Implementation of the channel info for announceFiles.'''
        logging.info(" The file service with id: " + Fore.YELLOW + serviceId + Fore.RESET +" call announceFiles. Media ids are: " + str(mediaIds) + " .")


class ChannelAnnouncements(IceFlix.Announcement):
    '''Implementation of ChannelAnnouncements servant.'''
    def announce(self, service, serviceId, current=None):
        '''Implementation of the channel info for announceFiles.'''
        if service.ice_isA('::IceFlix::Main'):
            logging.info(" Announcing" + Fore.CYAN + " MAIN service: " + Fore.RESET + str(service) +"   --with service id: " + serviceId + " .")

        elif service.ice_isA('::IceFlix::Authenticator'):
            logging.info(" Announcing"  + Fore.MAGENTA + " AUTHENTICATOR service: " + Fore.RESET + str(service) +"   --with service id: " + serviceId + " .")

        elif service.ice_isA('::IceFlix::MediaCatalog'):
            logging.info(" Announcing" + Fore.BLUE + " MEDIA CATALOG service: " + Fore.RESET + str(service) +"   --with service id: " + serviceId + " .")

        elif service.ice_isA('::IceFlix::FileService'):
            logging.info(" Announcing" + Fore.YELLOW + " FILE service: " + Fore.RESET + str(service) +"   --with service id: " + serviceId + " .")


class AdministratorShell(cmd.Cmd):
    '''Implementation of administrator interface.'''
    def __init__(self, main_service, admin_token, broker, catalog_adapter, autentic_adapter, file_adapter, fileuploader_adapter, announ_adapter):
        '''Implementation of the initialization of the administrator shell.'''
        self.intro = Fore.YELLOW+'\nYou are logged into IceFLix Administrator Interface.' + Fore.RESET+' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.YELLOW + '(Administrator): '+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = ""
        self.admin_token = admin_token
        self.broker = broker
        self.catalog_adapter = catalog_adapter
        self.autentic_adapter = autentic_adapter
        self.file_adapter = file_adapter
        self.fileuploader_adapter = fileuploader_adapter
        self.announ_adapter = announ_adapter
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
                    logging.info(Fore.GREEN + " SUCCESSFUL OPERATION." + Fore.RESET + " User: " + (user_name) + " added.\n")
            except IceFlix.TemporaryUnavailable:
                logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
        else:
            logging.error(Fore.RED + " You have entered an invalid user name or password.\n" + Fore.RESET + " ")

    def do_remove_user(self, _):
        '''Implementation of the remove user option.'''
        print("The choosen option is: remove_user. Please introduce the user name of the user you want remove:")
        user_name = input()
        if user_name != "":
            try:
                if self.main_service:
                    authenticator = self.main_service.getAuthenticator()
                    authenticator.removeUser(user_name, self.admin_token)
                    logging.info(Fore.GREEN + " SUCCESSFUL OPERATION." + Fore.RESET + " User: " + (user_name) + " removed.\n")
            except IceFlix.TemporaryUnavailable:
                logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
        else:
            logging.error(Fore.RED + " You have entered an invalid user name.\n" + Fore.RESET + " ")

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
                    logging.info(Fore.GREEN + " SUCCESSFUL OPERATION." + Fore.RESET + " Renamed title with" + (media_id) + "id to " + (media_newname) +" name.")
            except IceFlix.TemporaryUnavailable:
                logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
            except IceFlix.WrongMediaId:
                logging.error(Fore.RED + " Wrong media Id. " + Fore.RESET + "Please check it and try again.\n")

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
                logging.info(Fore.GREEN + " SUCCESSFUL OPERATION." + Fore.RESET + " Upload file.")
        except IceFlix.TemporaryUnavailable:
                logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")

    def do_remove_file(self, _):
        '''Implementation of the remove file option.'''
        print("The choosen option is: remove_file. Please introduce the media id you want to remove:")
        media_id = input()
        try:
            file_service = self.main_service.getFileService()
            file_service.removeFile(media_id, self.admin_token)
            logging.info(Fore.GREEN + " SUCCESSFUL OPERATION." + Fore.RESET + " Remove media id:" + (media_id))
        except IceFlix.WrongMediaId:
            logging.error(Fore.RED + " Wrong media Id. " + Fore.RESET + "Please check it and try again.\n")

    def do_subscribeChannel_Authenticators(self, _):
        '''Implementation of the subscribe Authenticator channel option.'''
        print("Press Ctrl+D if you want to stop and unsubscribe the authenticators  channel:")
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX CAUSE ICESTORM IS NOT AVAILABLE AT THIS MOMENT. PLEASE TRY AGAIN LATER :( .")
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
                print("ENTRO")
                EOF_error = input()
        except (EOFError):
            topic_authentic.unsubscribe(autentic_prx)

    def do_subscribeChannel_MediaCatalogs(self, _):
        '''Implementation of the subscribe Media Catalog channel option.'''
        print("Press Ctrl+D if you want to stop and unsubscribe the media catalogs channel:")
        topic_mgr = self.get_topic_manager()

        if not topic_mgr:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX CAUSE ICESTORM IS NOT AVAILABLE AT THIS MOMENT. PLEASE TRY AGAIN LATER :( .")
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
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX CAUSE ICESTORM IS NOT AVAILABLE AT THIS MOMENT. PLEASE TRY AGAIN LATER :( .")
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

    def do_subscribeChannel_Announcements(self, _):
        '''Implementation of the subscribe File Service channel option.'''
        print("Press Ctrl+D if you want to stop and unsubscribe the announcements channel:")
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "CONNECTION REFUSED TO ICEFLIX CAUSE ICESTORM IS NOT AVAILABLE AT THIS MOMENT. PLEASE TRY AGAIN LATER :( .")
            return 2
        else:
            print("\nConnection with IceStorm..." + Fore.GREEN + " ** SUCCESSFULL **\n" + Fore.RESET)
        try:
            topic_announ = topic_mgr.retrieve('Announcements')
        except IceStorm.NoSuchTopic:
            topic_announ = topic_mgr.create('Announcements')

        announ_servant = ChannelAnnouncements()
        self.announ_adapter.activate()
        announ_prx = self.announ_adapter.addWithUUID(announ_servant)
        topic_announ.subscribeAndGetPublisher({}, announ_prx)

        try:
            while True:
                EOF_error = input()
        except (EOFError):
            topic_announ.unsubscribe(announ_prx)

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        counter = 0
        print("Connecting with IceStorm...")
        while counter < 3:
            try:
                proxy = self.broker.propertyToProxy(key)
                if proxy is None:
                    print("property '{}' not set".format(key))
                    time.sleep(3.0)
                else:
                    return IceStorm.TopicManagerPrx.checkedCast(proxy)
            except Ice.ConnectionRefusedException:
                print("\nYou have " + Fore.RED + str(15-(counter*5)) + Fore.RESET + " seconds left to reconnect with IceStorm...")
                counter += 1
                time.sleep(5.0)
        if counter == 3:
            print(Fore.RED + "\n**ERROR**. " + Fore.RESET + "Connection with icestorm refused.")
            return None

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
    def __init__(self, main_service, token, user_name, hash_password):
        '''Implementation of the initialization of the user shell.'''
        self.intro = Fore.MAGENTA+'\nYou are logged into IceFLix User Interface.' + Fore.RESET+' Please type the option you want to choose:\n \nType help or ? to list commands.\n'
        self.prompt = Fore.MAGENTA + f'(User: {user_name}):'+ Fore.RESET + ' '
        self.main_service = main_service
        self.token = token
        self.user_name = user_name
        self.hash_password = hash_password
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
                logging.error(Fore.RED + " Not found video." + Fore.RESET + " Please try again. \n")
            self.media = media
        except IceFlix.TemporaryUnavailable:
            logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
            self.token = ""
        except IceFlix.Unauthorized:
            self.refresh_newtoken()
        except IceFlix.WrongMediaId:
            logging.error(Fore.RED + " Wrong media Id. " + Fore.RESET + "Please check it and try again.\n")
            self.token = ""

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
                        logging.info(Fore.GREEN + " SUCCESSFUL OPERATION. " + Fore.RESET + "Added tag/s: " + str(new_tags) + " in " + str(video.info.name))
                    elif option == 2:
                        print("Introduce the new tags you want to remove:")
                        delete_tags = input().split()
                        catalog.removeTags(video.mediaId, delete_tags, self.token)
                        logging.info(Fore.GREEN + " SUCCESSFUL OPERATION. " + Fore.RESET + "Remove tag/s:" + str(delete_tags) + " in " + str(video.info.name))
                    else: pass
            else:
                logging.error(Fore.RED + " Not found video." + Fore.RESET + " Please try again. \n")
            self.media = media
        except IceFlix.TemporaryUnavailable:
            logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
            self.token = ""
        except IceFlix.Unauthorized:
           self.refresh_newtoken()
        except IceFlix.WrongMediaId:
            logging.error(Fore.RED + " Wrong media Id. " + Fore.RESET + "Please check it and try again.\n")
            self.token = ""

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
                self.refresh_newtoken()
            except IceFlix.WrongMediaId:
                logging.error(Fore.RED + " Wrong media Id. " + Fore.RESET + "Please check it and try again.\n")

    def refresh_newtoken(self):
        try:
            if self.main_service:
                authenticator = self.main_service.getAuthenticator()
                self.token = authenticator.refreshAuthorization(self.user_name, self.hash_password)
        except IceFlix.Unauthorized:
            logging.error(Fore.RED + " You are not authorized." + Fore.RESET + " Please try again.\n")

    def do_exit(self, _):
        '''Implementation of the exit option.'''
        print('\nClosed IceFlix User Interface.\n')
        return True

    def do_EOF(self, line):
        '''Implementation of the ctrl+D option to exit.'''
        print('\nClosed IceFlix User Interface.\n')
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
        self.catalog_adapter = self.broker.createObjectAdapterWithEndpoints("CatalogAdapter_c", "tcp")
        self.autentic_adapter = self.broker.createObjectAdapterWithEndpoints("AuthenticatorAdapter_c", "tcp")
        self.file_adapter = self.broker.createObjectAdapterWithEndpoints("FileServiceAdapter_c", "tcp")
        self.fileuploader_adapter = self.broker.createObjectAdapterWithEndpoints("FileUploaderAdapter_c", "tcp")
        self.announ_adapter = self.broker.createObjectAdapterWithEndpoints("Announcements_c", "tcp")
        super(ClientShell, self).__init__()

    def do_login_user(self, _):
        '''Implementation of the login user option.'''
        print(self.token)
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
                            logging.info(Fore.GREEN + " SUCCESSFUL AUTHENTICATION OF USER: " + Fore.RESET + " " + (user_name))
                            user_shell = UserShell(self.main_service, self.token, user_name, hash_password)
                            user_shell.cmdloop()
                            self.token = ""
                        else:
                           logging.error(Fore.RED + " LOGIN NOT SUCCESFULL by user: "+ Fore.RESET + user_name + ". Please check it and try again.\n")
                except (IceFlix.TemporaryUnavailable, Ice.UnknownException):
                    logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
                except IceFlix.Unauthorized:
                    logging.error(Fore.RED + " You are not authorized." + Fore.RESET + " Please try again.\n")
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
                    hash_admin = hashlib.sha256(admin_token.encode()).hexdigest()
                    authenticator = self.main_service.getAuthenticator()
                    if authenticator.isAdmin(hash_admin):
                        logging.info(Fore.GREEN + " SUCCESSFUL AUTHENTICATION OF ADMINISTRATOR." + Fore.RESET + " ")
                        admin_shell = AdministratorShell(self.main_service, hash_admin, self.broker, self.catalog_adapter, self.autentic_adapter, self.file_adapter, self.fileuploader_adapter, self.announ_adapter)
                        admin_shell.cmdloop()
                    else:
                        logging.error(Fore.RED + " Not successful administrator authentication." + Fore.RESET + " Please check it and try again.\n")
            except (IceFlix.TemporaryUnavailable, Ice.UnknownException):
                logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")

            except IceFlix.Unauthorized:
                logging.error(Fore.RED + " You are not authorized." + Fore.RESET + " Please try again.\n")
        else:
            logging.error(Fore.RED + " You have entered an invalid administrator token." + Fore.RESET + " Please check it and try again.\n")

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
                logging.error(Fore.RED + " Not found video." + Fore.RESET + " Please try again. \n")
        except IceFlix.TemporaryUnavailable:
            logging.error(Fore.RED + " Temporary Unavailable." + Fore.RESET + " Please check it and try again.\n")
        except IceFlix.WrongMediaId:
            logging.error(Fore.RED + " Wrong media Id. " + Fore.RESET + "Please check it and try again.\n")

    def do_exit(self, _):
        '''Implementation of the exit option.'''
        print('\nThank you for using IceFlix application. Come back soon !!!'+Fore.RED +' <3' + Fore.RESET + '\n')
        return True

    def do_EOF(self, line):
        '''Implementation of the ctrl+D option to exit.'''
        self.do_exit(line)
        return True


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
        counter = 0
        print("----------------------------------------------------------------------")
        logging.info(" Connecting with IceStorm...")
        print("----------------------------------------------------------------------")

        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return 2
        else:
            return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def get_random_main(self, list_mainservices):
        mains = list(self.list_mainservices.items())
        if len(mains) != 0:
                random_main = random.choice(mains)
                return random_main[1]

    def run(self, _):
        """Implementation of run client."""
        announ_adapter = self.communicator().createObjectAdapterWithEndpoints("AnnouncementAdapter", "tcp")
        counter_re = 0
        finish = False
        while counter_re < 5 and finish == False:
                    try:
                        topic_mgr = self.get_topic_manager()
                        broker = self.communicator()
                        if not topic_mgr:
                            logging.error(Fore.RED + "CONNECTION REFUSED TO ICEFLIX CAUSE ICESTORM IS NOT AVAILABLE AT THIS MOMENT." + Fore.RESET + "PLEASE TRY AGAIN LATER :( .")
                            return 2
                        else:
                            logging.info(" Connection with IceStorm..." + Fore.GREEN + " ** SUCCESSFULL **\n" + Fore.RESET)
                        try:
                            topic_announcement = topic_mgr.retrieve('Announcements')
                        except IceStorm.NoSuchTopic:
                            topic_announcement = topic_mgr.create('Announcements')
                        announ_serv = Announcement(self.main_service, self.list_mainservices)
                        announ_adapter.activate()
                        announ_prx = announ_adapter.addWithUUID(announ_serv)
                        topic_announcement.subscribeAndGetPublisher({}, announ_prx)
                        counter = 0
                        print("----------------------------------------------------------------------")
                        logging.info(" Connecting with IceFlix...")
                        print("----------------------------------------------------------------------")
                        try:
                            while True:
                                self.main_service = self.get_random_main(self.list_mainservices)
                                topic_mgr.ice_ping()
                                if self.main_service:
                                    logging.info(" IceFLix Main Service: " + str(self.main_service) + Fore.GREEN +" ** SUCCESSFULLY CONNECTED **" + Fore.RESET + " ")
                                    print("\nInitializing IceFlix...")
                                    time.sleep(3.0)
                                    cliente_shell = ClientShell(self.main_service, broker)
                                    threading.Thread(name='cliente_shell', target=cliente_shell.cmdloop(), daemon=True).start()
                                    finish = True
                                    break
                                else:
                                    logging.warning(Fore.RESET + " Ups there are not main services. Please wait a moment for an available main service... ** " + Fore.RED + str(20-(counter * 5)) + Fore.RESET +" seconds left until disconnection **")
                                    counter += 1
                                    time.sleep(5.0)
                                if counter == 4:
                                    logging.error(Fore.RED + " CONNECTION REFUSED TO ICEFLIX TIMER EXPIRED." + Fore.RESET +  " THERE ARE NOT AVAILABLE MAINS AT THIS MOMENT. PLEASE TRY AGAIN LATER :( .")
                                    return 2
                        except Ice.ConnectionRefusedException:
                            logging.warning(" Ups, IceStorm is disconnected...")

                        topic_announcement.unsubscribe(announ_prx)
                    except Ice.ConnectionRefusedException:
                        counter_re += 1
                        logging.error(Fore.RED + " Connection with icestorm refused." + Fore.RESET +  "You have " + Fore.RED + str(5-counter_re) + Fore.RESET +" attempts left to try a reconnection...")
                        time.sleep(5.0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s' +' ** %(levelname)s **' + '%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    sys.exit(Client().main(sys.argv))
