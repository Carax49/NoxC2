# src/server/core/client_manager.py

from datetime import datetime
import threading


class ClientInfo:

    def __init__(self, uuid,  hostname, username, addr, os, arch, session):
        self.__uuid         = uuid
        self.__hostname     = hostname
        self.__username     = username
        self.__addr         = addr
        self.__os           = os
        self.__arch         = arch
        self.__session      = session
        self.__last_beacon  = datetime.now()

    @property
    def uuid(self):
        return self.__uuid

    @property
    def hostname(self):
        return self.__hostname

    @property
    def username(self):
        return self.__username

    @property
    def address(self):
        return self.__addr

    @property
    def os(self):
        return self.__os

    @property
    def arch(self):
        return self.__arch

    @property
    def session(self):
        return self.__session

    @property
    def last_beacon(self):
        return self.__last_beacon

    @property
    def get_info(self):
        return {
            'uuid' :        self.__uuid,
            'hostname' :    self.__hostname,
            'username' :    self.__username,
            'address' :     self.__addr,
            'os' :          self.__os,
            'arch' :        self.__arch,
            'session' :     self.__session,
            'last_beacon' : self.__last_beacon
        }

    def last_beacon_update(self):
        self.__last_beacon = datetime.now()


class ClientManager:

    def __init__(self):
        self.__clients_list = {}        # {uuid : info}
        self.__lock = threading.Lock()


    def get_client(self, uuid):
        return self.__clients_list.get(uuid)

    def get_client_list(self):
        return self.__clients_list

    def add_client(self, uuid, hostname, username, address, os, arch, session):
        with self.__lock:
            if uuid not in self.__clients_list:
                self.__clients_list[uuid] = ClientInfo(uuid, hostname, username, address, os, arch, session)

    def drop_client(self, uuid):
        with self.__lock:
            if uuid in self.__clients_list:
                del self.__clients_list[uuid]

    def drop_all_clients(self):
        with self.__lock:
            self.__clients_list.clear()

    def count_client(self):
        return len(self.__clients_list)

    def check_valid_cid(self, cid):
        return cid in self.__clients_list


Manager = ClientManager()