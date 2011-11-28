import tornado.websocket
import tornado.ioloop
import tornado.web
import traceback
import sys
import json
import os
import time

class {{servicename}}_websocket(tornado.websocket.WebSocketHandler):
  def __init__(self, application, request):
    tornado.websocket.WebSocketHandler.__init__(self, application, request)

  def on_message(self, message):
    try:
      t0 = time.time()
      # assuming json
      args = json.loads(message)
      args["{{servicename}}_server_pid"] = os.getpid()
      args["{{servicename}}_server_time"] = time.time()
      args["{{servicename}}_processing_time"] = time.time()-t0
      print "args = ", args
      self.write_message(json.dumps(args))
    except Exception, e:
      print "exception for message:", message
      self.write_message(json.dumps({"got an error":"yoda"}))
      print "after self.write"
      traceback.print_exc(sys.stderr)

  def on_close(self):
    pass
    