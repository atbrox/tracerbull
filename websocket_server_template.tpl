import tornado.ioloop
import tornado.web
import tornado.websocket
import traceback
import sys
import json

class {{servicename}}_websocket:
  def __init__(self, application, request):
    tornado.websocket.WebSocketHandler.__init__(self, application, request)

  def on_message(self, message):
    try:
      # assuming json
      args = json.loads(message)
    except Exception, e:
      traceback.print_exc(sys.stderr)

  def on_close(self):
    pass
    