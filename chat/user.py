#!/usr/bin/python
# -*- coding: utf-8 -*-

class User:
    def __init__(self, session):
        self.connection = session[0]
        self.address = session[1]
        self.nick = None
        self.room = None

    def set_nick(self, nick):
        self.nick = nick

    def get_nick(self):
        return self.nick

    def set_room(self, room):
        self.room = room

    def get_room(self):
        return self.room

    def send(self, msg):
        self.send_raw(str(msg) + "\r\n")

    def send_raw(self, msg):
        self.connection.send(str(msg).encode('utf-8'))

    def get_session(self):
        return self.connection