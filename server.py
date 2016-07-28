#!/usr/bin/python
# -*- coding: utf-8 -*-

from chat.server import Server
import sys

if __name__ == '__main__':
    port = 8181
    args = sys.argv
    if len(args) > 1:
        port = int(args[1])
    server = Server(port).start()
