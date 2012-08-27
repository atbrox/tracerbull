#!/usr/bin/env python

import sys
from websocket import create_connection

def websocket_client_main(argv):
    ws = create_connection("ws://{{wshostname}}:{{wsport}}/")
    ws.send(argv[1])
    result =  ws.recv()
    print "Received '%s'" % result
    ws.close()
    return result

if __name__ == "__main__":
    websocket_client_main(sys.argv)
