from multiprocessing import Queue
from mako import codegen
import multiprocessing
from mockito.mockito import when, verify
from mockito.spying import spy
import tracerbull
import tornado


import pytest
import mockito
import mockito_test
import mockito_util

from mockito import any

import random
import traceback

# html/javascript parsing
import bs4
#import pyjsparser
import os # getcwd
import time
import signal
import psutil


# https://bitbucket.org/outcomm/bs4
# hg clone  https://bitbucket.org/outcomm/bs4
# hg clone https://bitbucket.org/nullie/pyjsparser

def create_test_service():
    test_service = {"servicename": "suggestservice", "arguments": {"arg0": "default0", "arg1": "default1"},
                    "hostname": "box1.atbrox.com",
                    "response": {},
                    "protocols": ["websocket"],
                    "num_instances": 1,
                    "num_replicas": 0}
    return test_service

class TestIntegration:
    def kill_servers(self, server_pids):
        for pid in server_pids:
            print "killing server on pid %s" % (pid)
            os.kill(int(pid), signal.SIGKILL)
            
    def create_test_service_and_return_queue(self):
        services = [create_test_service(), create_test_service()]
        working_path = os.getcwd()

        queue = tracerbull.BabelShark.start_services(services,
                                             codegen=tracerbull.BabelShark.generate_code,
                                             importcode=tracerbull.BabelShark.import_generated_code,
                                             forker=tracerbull.BabelShark.create_process,
                                             boot_function=tracerbull.BabelShark.start_application_server,
                                             tornadoapp=tornado.web.Application,
                                             template_path=working_path)
        return queue, len(services)

    def test_start_services_and_create_clients(self):
        queue, _ = self.create_test_service_and_return_queue()

        # generate and load client code
        clients, server_pids, kill_file = tracerbull.BabelShark.create_clients_for_services(queue)
        for service in clients:
            assert clients[service].has_key("cmdline")
            assert clients[service].has_key("html")
            cmdline_client_code = clients[service]["cmdline"]
            cmdline_client = tracerbull.BabelShark.import_generated_code(cmdline_client_code)

            # client communicates with server
            argv = [None, '{"yo":"flow"}']
            result = cmdline_client.websocket_client_main(argv)
            print "SENDING = ", argv
            print "RESULT = ", result
            print "SERVER PIDS = ", server_pids

        # kill servers
        self.kill_servers(server_pids)

    def test_start_services(self):
        queue, expected_num_services = self.create_test_service_and_return_queue()

        #verify(tracerbull.BabelShark, times=len(services)).create_process(any(),any(),any(),
        #                                        any(), any(),any())
        t0 = time.time()
        while queue.qsize() < expected_num_services and time.time()-t0 < 10:
            print "sleeping,"
            time.sleep(1)
        assert queue.qsize() == 2
        process_package = queue.get()
        assert queue.qsize() == 1
        assert process_package.has_key("pid")
        assert int(process_package["pid"]) in psutil.get_pid_list()
        os.kill(process_package["pid"], signal.SIGKILL)

        process_package = queue.get()
        assert queue.qsize() == 0
        assert process_package.has_key("pid")
        assert int(process_package["pid"]) in psutil.get_pid_list()
        os.kill(process_package["pid"], signal.SIGKILL)



class TestStartServices:
    def test_create_process(self):
        port = 1245
        queue = spy(Queue())
        boot_function=tracerbull.BabelShark.start_application_server
        application = "some app"
        name = "mytestname"
        instance_number = 0
        process_mock = mockito.mock()
        pid = os.getpid()
        ppid = os.getppid()
        info = {"name":name, "instance_number": instance_number, "port":port,
                "pid":pid, "ppid": ppid, "hostname": "box1.atbrox.com",
                "arguments":{"arg0":"default0", "arg1":"default1"}}
        when(process_mock).start().thenReturn(queue.put(info))
        when(multiprocessing).Process(target=any(),args=any()).thenReturn(process_mock)
        tracerbull.BabelShark.create_process(port, queue, boot_function,application, name,instance_number,
                                             service=None,
                                             processor=multiprocessing)
        verify(process_mock,times=1).start()
        verify(queue, times=1).put(info)
        
    def test_start_services_basic(self):
        when(tracerbull.BabelShark).create_process(any(),any(),any(),
                                            any(), any(),any()).thenReturn("ws_process")
        services = [create_test_service(), create_test_service()]
        working_path = os.getcwd()

        queue = tracerbull.BabelShark.start_services(services,
                                             codegen=tracerbull.BabelShark.generate_code,
                                             importcode=tracerbull.BabelShark.import_generated_code,
                                             forker=tracerbull.BabelShark.create_process,
                                             boot_function=tracerbull.BabelShark.start_application_server,
                                             tornadoapp=tornado.web.Application,
                                             template_path=working_path)

        verify(tracerbull.BabelShark, times=len(services)).create_process(any(),any(),any(),
                                                any(), any(),any(), any())

class TestCodeGeneration:


    def test_generate_server_code(self):
        test_service = create_test_service()
        working_path = os.getcwd()
        websocket_server_code = tracerbull.BabelShark.generate_code(test_service,
                                                         "websocket_server_template.tpl",
                                                         loader=tornado.template.Loader(working_path))
        websocket_server_module = tracerbull.BabelShark.import_generated_code(websocket_server_code)
        dir(websocket_server_module)
        assert hasattr(websocket_server_module, 'suggestservice_websocket')

    def test_generate_cmdline_client_code(self):
        test_service = create_test_service()
        working_path = os.getcwd()

        # need data for where to connect
        test_service["wshostname"] = test_service["hostname"]
        test_service["wsport"] = random.randint(10000,100000)

        websocket_client_code = tracerbull.BabelShark.generate_code(test_service,
                                                         "websocket_cmdline_client.tpl",
                                                         loader=tornado.template.Loader(working_path))
        print websocket_client_code
        websocket_client_module = tracerbull.BabelShark.import_generated_code(websocket_client_code)
        dir(websocket_client_module)
        assert hasattr(websocket_client_module, 'websocket_client_main')
        #assert hasattr(websocket_server_module, 'suggestservice_websocket')

    def test_generate_html_client_code(self):
        test_service = create_test_service()
        working_path = os.getcwd()

          # need data for where to connect
        test_service["wshostname"] = test_service["hostname"]
        test_service["wsport"] = random.randint(10000,100000)

        websocket_html_client_code = tracerbull.BabelShark.generate_code(test_service,
                                                         "websocket_client.tpl",
                                                         loader=tornado.template.Loader(working_path))
        soup = bs4.BeautifulSoup(websocket_html_client_code)

        #parser = pyjsparser.parser.Parser()
        #print soup.prettify()
        javascripts = soup.find_all("script")
        for javascript in javascripts:
            if 'function' in javascript.text:
                #program = parser.parse(javascript.text)
                print javascript.text
                #assert type(program) == pyjsparser.ast.Program

        


    
