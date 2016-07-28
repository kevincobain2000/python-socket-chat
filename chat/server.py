#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import os
import thread
from user import User
from colorama import Fore, Style

class Server:
    def __init__(self, port):
        self.port = port
        self.clients = list()
        self.rooms = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        for room in ['tutorial',
                        'work',
                        'study',
                        'python',
                        'slack',
                        'javascript'
                    ]:
            self.rooms[room] = []

        self.commands = ("Commands available:\r\n"
            + "/users                - List all users\r\n"
            + "/users <room>         - List all users in a room\r\n"
            + "/rooms                - List all rooms\r\n"
            + "/join <room>          - Join <room>\r\n"
            + "/private <nick> <msg> - Send private message to <nick>\r\n"
            + "/exit                 - Quit the room\r\n"
            + "/clear                - Clear the screen\r\n"
            + "/help                 - Show me this\r\n")

    def start(self):
        self.server.bind(('', self.port))
        self.server.listen(5)
        print("Running Server on PORT " + str(self.port));
        while True:
            self.__start_session()

    def __start_session(self):
        session = self.server.accept()
        user = User(session)
        thread.start_new_thread(self.__client_handle, (user,))

    def __client_handle(self, client):
        generator = self.__read_data(client)

        while client.get_nick() is None:
            self.__server_message("Welcome to the XYZ chat server", client)
            client.send_raw("Your Nickname: ")
            possible_nick = next(generator)
            if len(possible_nick) > 10:
                possible_nick = possible_nick[:10]
            nickname_exists = False
            for user in self.clients:
                if user.get_nick() is not None:
                    if user.get_nick().lower() == possible_nick.lower():
                        nickname_exists = True
                        self.__server_message("This nickname is taken", client)
                        break

            if not nickname_exists:
                if possible_nick.lower() != "server" and possible_nick != "":
                    client.set_nick(possible_nick)
                else:
                    self.__server_message("Nickname already taken", client)

        self.clients.append(client)
        self.__server_message(self.commands, client);
        self.__server_message(client.get_nick() + " has joined the chat")
        self.__command_handle(generator, client)

    def __read_data(self, client):
        buff = ""
        while True:
            data = client.get_session().recv(4096)
            try:
                data = data.decode(encoding='utf-8')
            except:
                data = " "

            if not data:
                if not buff:
                    break
            elif buff:
                data = buff + data
                buff = ""

            if '\r\n' in data:
                for line in data.splitlines(True):
                    if line.endswith('\r\n'):
                        yield line.replace("\r", "").replace("\n", "")
                    else:
                        buff = line
            else:
                buff += data

    def __command_handle(self, generator, client):
        while True:
            try:
                block = next(generator)
            except:
                self.__client_disconnect(client)
                break

            client.send("\r\n=> " + block);
            if not block.startswith("/"):
                self.__send_msg_to_room(block, client)
            else:
                cmd = block.split(" ")
                command = cmd[0].lower()
                if command == "/exit":
                    self.__client_disconnect(client)
                    break
                elif command == "/users":
                    if len(cmd) > 1:
                        room = cmd[1]
                        self.__list_users_in_room(room, client)
                    else:
                        self.__list_users(client)
                elif command == "/rooms":
                    self.__list_rooms(client)
                elif command == "/join":
                    if len(cmd) > 1:
                        prev_room = client.get_room()
                        new_room = cmd[1]
                        if prev_room and prev_room != new_room:
                            self.__leave_room(prev_room, client)
                        self.__join_room(new_room, client)
                    else:
                        self.__server_message("Room name missing /join <room>", client)
                elif command == "/private":
                    if len(cmd) > 2:
                        to_nickname = cmd[1]
                        msg = block[block.index(to_nickname):]
                        self.__send_msg_to_user(to_nickname, client, msg)
                    else:
                        self.__server_message("Parameters missing for private message /private <nickname> <msg>", client)
                elif command == "/clear":
                    self.__server_message("\033[2J", client)
                elif command == "/help":
                    self.__server_message(self.commands, client)
                else:
                    self.__server_message("Unknown command, try typing /help", client)

    def __list_rooms(self, client):
        for room in self.rooms:
            self.__server_message(room + "(" + str(len(self.rooms[room])) + ")", client)

    # list users all users
    def  __list_users(self, client):
        for user in self.clients:
            self.__server_message("nickanme: " + str(user.get_nick()) + " (" + str(user.get_room()) + ")", client)
        self.__server_message("Total: " + str(len(self.clients)), client)

    def __list_users_in_room(self, room, client):
        if room not in self.rooms:
            self.__server_message("room doesn't exist: " + room, client)
            return
        for client_name in self.rooms[room]:
            self.__server_message("nickname: " + client_name, client)
        self.__server_message("Total: " + str(len(self.rooms[room])), client)

    def __send_msg_to_user(self, to_nickname, client, msg):
        if not self.__validate_msg(msg):
            return
        for user in self.clients:
            if user.get_nick().lower() == to_nickname.lower():
                message = client.get_nick() + " -> " + user.get_nick() + ": " + msg
                self.__server_message(message, user)
                self.__server_message(message, client)
                break
            else:
                self.__server_message("User Doesn't exist", client)

    def __send_msg_to_room(self, msg, client):
        if not self.__validate_msg(msg):
            return
        if not client.get_room():
            self.__server_message("Please join a room first.", client)
            self.__server_message("You can list rooms via /rooms", client)
            self.__server_message("To join a room type /join <room>", client)
            return
        for user in self.clients:
            if user.get_nick().lower() in self.rooms[client.get_room()]:
                self.__server_message("(" + client.get_room() + ") " + client.get_nick() + ": " + msg, user)

    def __validate_msg(self, msg):
        return msg != ""

    def __join_room(self, room, client):
        if room not in self.rooms:
            self.__server_message("Room doesn't exist. List all rooms via /rooms", client)
        elif client.get_room() == room:
            self.__server_message("You are already in room: " + room, client)
        else:
            client.set_room(room)
            self.rooms[room].append(client.get_nick().lower())
            self.__send_msg_to_room("joined room", client)

    def __leave_room(self, room, client):
        if client.get_nick().lower() in self.rooms[room]:
            self.rooms[room].remove(client.get_nick().lower())
        self.__send_msg_to_room("left room", client)

    def __server_message(self, msg, user=None):
        if not user:
            for client in self.clients:
                try:
                    client.send("<= " + msg)
                except:
                    self.__client_disconnect(client)
        else:
            user.send(Fore.GREEN + "<= " +  msg + Style.RESET_ALL)

    def __client_disconnect(self, client):
        client.get_session().close()
        for user in self.clients:
            if user.get_nick().lower() == client.get_nick().lower():
                self.clients.remove(user)

        if client.get_room():
            self.rooms[client.get_room()].remove(client.get_nick().lower())

        if client.get_room():
            self.__server_message(client.get_nick() + " has left the room: " + client.get_room())
        else:
            self.__server_message(client.get_nick() + " has left the chat")
