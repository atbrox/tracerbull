from mako import codegen
from mockito.mockito import when
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
import pyjsparser


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


class TestStartServices:
    def test_start_services(self):
        when(tracerbull.BabelShark).create_process(any(),any(),any(),
                                            any(), any(),any()).thenReturn("ws_process")
        services = [create_test_service()]
        working_path = "/home/amund/PycharmProjects/tracerbull"
        tracerbull.BabelShark.start_services(services,
                                             codegen=tracerbull.BabelShark.generate_code,
                                             importcode=tracerbull.BabelShark.import_generated_code,
                                             forker=tracerbull.BabelShark.create_process,
                                             boot_function=tracerbull.BabelShark.start_application_server,
                                             tornadoapp=tornado.web.Application,
                                             template_path=working_path)

class TestCodeGeneration:


    def test_generate_server_code(self):
        test_service = create_test_service()
        working_path = "/home/amund/PycharmProjects/tracerbull"
        websocket_server_code = tracerbull.BabelShark.generate_code(test_service,
                                                         "websocket_server_template.tpl",
                                                         loader=tornado.template.Loader(working_path))
        websocket_server_module = tracerbull.BabelShark.import_generated_code(websocket_server_code)
        dir(websocket_server_module)
        assert hasattr(websocket_server_module, 'suggestservice_websocket')

    def test_generate_cmdline_client_code(self):
        test_service = create_test_service()
        working_path = "/home/amund/PycharmProjects/tracerbull"

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
        working_path = "/home/amund/PycharmProjects/tracerbull"

          # need data for where to connect
        test_service["wshostname"] = test_service["hostname"]
        test_service["wsport"] = random.randint(10000,100000)

        websocket_html_client_code = tracerbull.BabelShark.generate_code(test_service,
                                                         "websocket_client.tpl",
                                                         loader=tornado.template.Loader(working_path))
        soup = bs4.BeautifulSoup(websocket_html_client_code)

        parser = pyjsparser.parser.Parser()
        #print soup.prettify()
        javascripts = soup.find_all("script")
        for javascript in javascripts:
            if 'function' in javascript.text:
                program = parser.parse(javascript.text)
                print javascript.text
                assert type(program) == pyjsparser.ast.Program

        


    