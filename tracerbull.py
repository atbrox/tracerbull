from tornado import template

__author__ = 'amund'

# read input file with descriiption of services and their default responses
# or potentially one-to-one proxies
# generate tornado processes with those processes
# and a way to manage them and talk to them (simple shell?)

import tornado.ioloop
import tornado.web
import tornado.httpserver
from multiprocessing import Process, Queue
import socket
import os
import tempfile
import imp
import imputil
import sys

# https://github.com/facebook/tornado/blob/master/tornado/netutil.py
services = [
    {"servicename":"suggestservice",
     "arguments":{"arg0":"default0", "arg1":"default1"},
     "hostname":"box1.atbrox.com",
     "response":{},
     "protocols":["websocket"],
     "num_instances":1,
     "num_replicas":0}, # add default way of handling, e.g. merge, just respond, conversions etc?
]

def generate_code(service, template_filename, loader=template.Loader(".")):
    # need template for http and websocket
    generated_code = loader.load(template_filename).generate(**service)
    return generated_code

def generate_host_entries(services):
    pass


# ref: http://www.pythonexamples.org/2011/01/12/how-to-dynamically-create-a-class-at-runtime-in-python/
def create_application_class(service):
    assert type(service) == dict
    assert(service.has_key("servicename"))
    assert(service.has_key("arguments"))
    arguments = service["arguments"]
    # TODO: use tornado templates below
    response = "{"
    for argument in arguments:
        print argument
        response += "\"%s\"" % (argument)
        response += ": self.get_argument("
        response += "\"%s\"" % (argument)
        response += ", "
        response += "\"%s\"" % (arguments[argument])
        response += "),"
    #print service["servicename"]
    response += '"service":"' + service["servicename"] + '"'
    #resposne += "time"

    response += "}"
    print "response = ", response
    #a = eval(response)
    #print a
#        response[argument] =
    result = type(
        service["servicename"], # class name
        (tornado.web.RequestHandler,), # inherits from
        dict(
            get = lambda self:self.write(response)
        )
    )
    return result
#

def create_process(port, queue, boot_function, application, name, instance_number):
    p = Process(target=boot_function, args=(queue, port, application, name, instance_number))
    p.start()
    return p


# either http server or websocket
def start_application_server(queue, port, application, name, instance_number):
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    actual_port = port
    if port == 0: # special case, an available port is picked automatically
        # only pick first! (for now)
        assert len(http_server._sockets) > 0
        for s in http_server._sockets:
            actual_port = http_server._sockets[s].getsockname()[1]
            break
    pid = os.getpid()
    ppid = os.getppid()
    info = {"name":name, "instance_number": instance_number, "port":actual_port,
            "pid":pid, "ppid": ppid }
    queue.put(info)
    tornado.ioloop.IOLoop.instance().start()

def import_generated_code(generated_code):
    fh = tempfile.NamedTemporaryFile(mode='w')
    fh.write(generated_code)
    fh.flush() # to make it readable with load_source
    my_mod_name = fh.name.split('/')[-1]
    my_mod = imp.load_source(my_mod_name, fh.name)
    fh.close()
    return my_mod

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    q = Queue()
#    appclass = create_application_class(services[0])
#    print type(appclass)
#    application = tornado.web.Application([
#           (r"/", appclass),
#       ])
#    print type(application)
#    class foobar(appclass):
#        def get(self):
#            super(foobar, self).get()
#            self.write("yoda")
#
#    application2 = tornado.web.Application([
#             (r"/", foobar),
#         ])
#
#    name = "yosa"
#
#    p = create_process(0, q, start_http_server, application, name, 0)
#    p2 = create_process(0, q, start_http_server, application2, name + "yo", 0)
#    print q.get()
#    print q.get()

    #generated_code = generate_code(services[0], "http_server_template.tpl")
    #print "generated code\n", generated_code

    generated_code = generate_code(services[0], "websocket_server_template.tpl")
    #print "generated code\n", generated_code

    codemodule = import_generated_code(generated_code)
    print dir(codemodule)
    #sys.exit(0)
    application = tornado.web.Application([
        (r"/", getattr(codemodule, 'suggestservice_websocket'))
    ])
    print dir(application), type(application)
    print type(application)
    p = create_process(0, q, start_application_server, application, "myws", 0)
    #start_application_server(q, 40761, application, "yodaapp", 0)
    data = q.get()
    #data = q.get()
    print data


    y = services[0]
    y["wshostname"] = services[0]["hostname"]
    y["wsport"] = str(data["port"])
    print "Y = ", y
    generated_code = generate_code(y, "websocket_client.tpl")
    print "generated code\n", generated_code
    fh = tempfile.NamedTemporaryFile(mode='w')
    fh.write(generated_code)
    fh.flush()
    print fh.name
    print data


    gc = generate_code(y, "websocket_cmdline_client.tpl")
    print "gc = ", gc


    p.join()



