import multiprocessing
import time

__author__ = 'amund'

# read input file with descriiption of services and their default responses
# or potentially one-to-one proxies
# generate tornado processes with those processes
# and a way to manage them and talk to them (simple shell?)

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado import template

from multiprocessing import Process, Queue
import multiprocessing
import socket
import os
import tempfile
import imp
import imputil
import sys
import traceback
import os.path

TIME_TO_WAIT_FOR_SERVERS = 5

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

class BabelShark(object):
    @staticmethod
    def generate_code(service, template_filename, loader=template.Loader(".")):
        print type(service)
        print type(template_filename)
        print type(loader)
        # need template for http and websocket

        generated_code = loader.load(template_filename).generate(**service)
        return generated_code

    @staticmethod
    def generate_host_entries(services):
        pass

    @staticmethod
    def create_process(port, queue, boot_function, application, name, instance_number, service, processor=multiprocessing):
        print "==> create_process:", port, name, instance_number
        p = processor.Process(target=boot_function, args=(queue, port, application, name, instance_number, service))
        print p
        p.start()
        return p


    @staticmethod
    # either http server or websocket
    def start_application_server(queue, port, application, name, instance_number, service):
        print " ==> start_application_server:", port, name, instance_number
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
        print "actual_port = ", actual_port
        info = {"name":name, "instance_number": instance_number, "port":actual_port,
                "pid":pid, "ppid": ppid, "service":service}
        queue.put(info)
        print "queue.size = ", queue.qsize()
        tornado.ioloop.IOLoop.instance().start()

    @staticmethod
    def import_generated_code(generated_code):
        fh = tempfile.NamedTemporaryFile(mode='w')
        fh.write(generated_code)
        fh.flush() # to make it readable with load_source
        my_mod_name = fh.name.split('/')[-1]
        my_mod = imp.load_source(my_mod_name, fh.name)
        fh.close()
        return my_mod

    @staticmethod
    def start_services(services,
                       codegen,
                       importcode,
                       tornadoapp,
                       forker,
                       boot_function,
                       template_path="."):

        # loop through all services
        # create hosts file
        # update kill-file for them (processes)
        # create all files (websocket server, and js/python client files)
        host_file = {}
        kill_file = {}
        queue = Queue()
        for service in services:
            websocket_server_code = codegen(service, "websocket_server_template.tpl",
                                            loader=template.Loader(template_path))
            websocket_server_module = importcode(websocket_server_code)
            websocket_server_class_name = "%s_websocket" % (service["servicename"])
            websocket_server_application =  tornadoapp([
                (r"/", getattr(websocket_server_module, websocket_server_class_name))
            ])
            websocket_server_process = forker(0, queue, boot_function,
                                              websocket_server_application, service["servicename"], 0, service)
            print websocket_server_process
            print "WSS, ", queue.qsize()

        return queue

    @staticmethod
    def create_clients_for_services(queue, output_path="clients"):
        assert queue is not None
        last_time = time.time()
        # wait maximum 10 seconds
        clients = {}
        server_pids = {}
        kill_file = "#!/bin/bash\n"
        while time.time() - last_time < TIME_TO_WAIT_FOR_SERVERS:
            while queue.qsize() == 0 and time.time()-last_time < TIME_TO_WAIT_FOR_SERVERS:
                print "waiting for new servers"
                time.sleep(1)
            if queue.qsize() > 0:
                service_package = queue.get()
                service = service_package["service"]
                service["wshostname"] = service["hostname"]
                service["wsport"] = service_package["port"]
                # TODO: support multiple instances of services
                clients[service["servicename"]] = {}
                clients[service["servicename"]]["cmdline"] = BabelShark.generate_code(service, "websocket_cmdline_client.tpl")
                clients[service["servicename"]]["html"] = BabelShark.generate_code(service, "websocket_client.tpl")
                server_pids[service_package["pid"]] = service["servicename"]
                kill_file += "kill -9 %d # %s - %s:%d\n" % (service_package["pid"],
                                                            service["servicename"],
                                                            service["hostname"],
                                                            service["wsport"])

                last_time = time.time()
        print "finished waiting for servers"

        # TODO: create kill file in output_path of server_pids
        # TODO: create hosts file in output_path of hostname (support localhost mode?)
        return clients, server_pids, kill_file









        # the queue should now contain data about the service
        # need to wait for port numbers for the client code
        #websocket_html_client_code = generate_code(service, "websocket_client.tpl")
        #websocket cmdline_client_code = generate_code(service, "websocket_cmdline_client.tpl")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    q = Queue()

    generated_code = BabelShark.generate_code(services[0], "websocket_server_template.tpl")
    #print "generated code\n", generated_code

    codemodule = BabelShark.import_generated_code(generated_code)
    print dir(codemodule)
    #sys.exit(0)
    application = tornado.web.Application([
        (r"/", getattr(codemodule, 'suggestservice_websocket'))
    ])
    print dir(application), type(application)
    print type(application)
    p = BabelShark.create_process(0, q, BabelShark.start_application_server, application, "myws", 0)
    #start_application_server(q, 40761, application, "yodaapp", 0)
    data = q.get()
    #data = q.get()
    print data


    y = services[0]
    y["wshostname"] = services[0]["hostname"]
    y["wsport"] = str(data["port"])
    print "Y = ", y
    generated_code = BabelShark.generate_code(y, "websocket_client.tpl")
    print "generated code\n", generated_code
    fh = tempfile.NamedTemporaryFile(mode='w')
    fh.write(generated_code)
    fh.flush()
    print fh.name
    print data


    gc = BabelShark.generate_code(y, "websocket_cmdline_client.tpl")
    print "gc = ", gc


    p.join()



