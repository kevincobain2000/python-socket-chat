#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import os
import thread
from user import User

class Server:
    def __init__(self, port):
        self.port = port
        self.clients = list()
        self.rooms = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        for room in ['tutorial', 'work', 'study', 'python', 'slack', 'javascript']:
            self.rooms[room] = []

        self.commands = ("Commands available:\r\n"
            + "/users                - List all users\r\n"
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
            session = self.server.accept()
            UnloggedUser = User(session)
            thread.start_new_thread(self.__client_handle, (UnloggedUser,))

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

    def __client_handle(self, client):
        generator = self.__read_data(client)
        while client.get_nick() is None:
            self.__server_message("Welcome to the XYZ chat server", client)
            client.send_raw("Your Nickname: ")
            possible_nick = next(generator)
            if len(possible_nick) > 10:
                possible_nick = possible_nick[:10]
            nickname_exists = False
            for u in self.clients:
                if u.get_nick() is not None:
                    if u.get_nick().lower() == possible_nick.lower():
                        nickname_exists = True
                        self.__server_message("This nickname is taken", client)
                        break

            if not nickname_exists:
                if possible_nick.lower() != "server" and possible_nick != "":
                    client.set_nick(possible_nick)
                else:
                    self.__server_message()("Nickname already taken", client)

        self.__server_message(self.commands, client);
        self.clients.append(client)

        self.__server_message(client.get_nick() + " has joined the chat")

        while True:
            try:
                block = next(generator)
            except:
                self.__client_disconnect(client)
                break

            client.send("=> " + block);

            if block.startswith("/"):
                cmd = block.split(" ")
                command = cmd[0].lower()
                if command == "/exit":
                    self.__client_disconnect(client)
                    break
                elif command == "/users":
                    self.__list_users(client)
                elif command == "/rooms":
                    self.__list_rooms(client)
                elif command == "/join":
                    if len(cmd) > 1:
                        prev_room = client.get_room()
                        room = cmd[1]
                        if prev_room:
                            self.__leave_room(prev_room, client)
                        self.__join_room(room, client)
                    else:
                        client.send("Room name missing /join <room>")
                elif command == "/private":
                    if len(cmd) > 2:
                        to_nickname = cmd[1]
                        msg = block[block.index(to_nickname):]
                        self.__send_msg_to_user(to_nickname, client, msg)
                    else:
                        client.send("Parameters missing for private message /private <user> <msg>")
                elif command == "/clear":
                    client.send("\033[2J")
                elif command == "/help":
                    client.send(self.commands)
                else:
                    self.__server_message("Unknown command, try typing /help", client)
            else:
                self.__send_msg_to_room(block, client)

    def __list_rooms(self, client):
        for room in self.rooms:
            self.__server_message(room + "(" + str(len(self.rooms[room])) + ")", client)

    def  __list_users(self, client):
        for c in self.clients:
            self.__server_message(str(c.get_nick()) + str(c.get_room()), client)

    def __send_msg_to_user(self, to_nickname, client, msg):
        for user in self.clients:
            if user.get_nick().lower() == to_nickname.lower():
                message = client.get_nick() + "->" + user.get_nick() + "): " + msg
                self.__server_message(message, user)
                break
            else:
                self.__server_message("User Doesn't exist", client)

    def __send_msg_to_room(self, msg, client):
        if not self.__validate_msg(msg):
            return
        if not client.get_room():
            self.__server_message("You cannot send a message. Please Join a room first.", client)
            self.__server_message("You can list rooms via /rooms", client)
            self.__server_message("To join a room type /join <room>", client)
            return
        for user in self.clients:
            if user.get_nick().lower() in self.rooms[client.get_room()]:
                self.__server_message("(" + client.get_room() + ")" + client.get_nick() + " says: " + msg, user)

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

            room_length = str(len(self.rooms[room]))
            self.__server_message(client.get_nick() + " Joined Room: " + room + " (" + room_length + ")")
            self.__server_message("List of Users in this room :" + room, client)
            for client_name in self.rooms[room]:
                self.__server_message(client_name, client)

    def __leave_room(self, room, client):
        self.rooms[room].remove(client.get_nick().lower())
        for u in self.clients:
            if u.get_nick().lower() in self.rooms[room]:
                self.__server_message(client.get_nick() + " left the room: " + room, u)

    def __server_message(self, msg, user=None):
        if not user:
            for client in self.clients:
                try:
                    client.send("<= " + msg)
                except:
                    self.__client_disconnect(client)
        else:
            user.send("<= " +  msg)

    def __client_disconnect(self, client):
        client.get_session().close()
        for c in self.clients:
            if c.get_nick().lower() == client.get_nick().lower():
                self.clients.remove(c)

        if client.get_room():
            self.rooms[client.get_room()].remove(client.get_nick().lower())

        if client.get_room():
            self.__server_message(client.get_nick() + " has left the room: " + client.get_room())
        else:
            self.__server_message(client.get_nick() + " has left the chat")
