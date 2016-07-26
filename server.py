#!/usr/bin/python
# -*- coding: utf-8 -*-

from chat.server import Server

if __name__ == '__main__':
    port = 8181
    server = Server(port).start()
