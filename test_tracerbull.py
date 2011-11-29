import tracerbull
import tornado

import pytest
import mockito
import mockito_test
import mockito_util
import random
import traceback

# html/javascript parsing
import bs4
import pyjsparser

# https://bitbucket.org/outcomm/bs4
# hg clone  https://bitbucket.org/outcomm/bs4


class TestBabelShark:
    def _create_test_service(self):
        test_service = {"servicename": "suggestservice", "arguments": {"arg0": "default0", "arg1": "default1"},
                        "hostname": "box1.atbrox.com",
                        "response": {},
                        "protocols": ["websocket"],
                        "num_instances": 1,
                        "num_replicas": 0}
        return test_service

    def test_generate_server_code(self):
        test_service = self._create_test_service()
        working_path = "/home/amund/PycharmProjects/tracerbull"
        websocket_server_code = tracerbull.generate_code(test_service,
                                                         "websocket_server_template.tpl",
                                                         loader=tornado.template.Loader(working_path))
        websocket_server_module = tracerbull.import_generated_code(websocket_server_code)
        dir(websocket_server_module)
        assert hasattr(websocket_server_module, 'suggestservice_websocket')

    def test_generate_cmdline_client_code(self):
        test_service = self._create_test_service()
        working_path = "/home/amund/PycharmProjects/tracerbull"

        # need data for where to connect
        test_service["wshostname"] = test_service["hostname"]
        test_service["wsport"] = random.randint(10000,100000)

        websocket_client_code = tracerbull.generate_code(test_service,
                                                         "websocket_cmdline_client.tpl",
                                                         loader=tornado.template.Loader(working_path))
        print websocket_client_code
        websocket_client_module = tracerbull.import_generated_code(websocket_client_code)
        dir(websocket_client_module)
        assert hasattr(websocket_client_module, 'websocket_client_main')
        #assert hasattr(websocket_server_module, 'suggestservice_websocket')

    def test_generate_html_client_code(self):
        test_service = self._create_test_service()
        working_path = "/home/amund/PycharmProjects/tracerbull"

          # need data for where to connect
        test_service["wshostname"] = test_service["hostname"]
        test_service["wsport"] = random.randint(10000,100000)

        websocket_html_client_code = tracerbull.generate_code(test_service,
                                                         "websocket_client.tpl",
                                                         loader=tornado.template.Loader(working_path))
        soup = bs4.BeautifulSoup(websocket_html_client_code)

        parser = pyjsparser.parser.Parser()
        #print soup.prettify()
        javascripts = soup.find_all("script")
        for javascript in javascripts:
            if 'function' in javascript.text:
                program = parser.parse(javascript.text)
                assert type(program) == pyjsparser.ast.Program

        


    