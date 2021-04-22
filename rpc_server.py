from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading
import time
import wikipathfinder


def server():
    class ThreadedServer(ThreadingMixIn, SimpleXMLRPCServer):
        pass

    # Restriction for path requests

    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    with ThreadedServer(('127.0.0.1', 7999), requestHandler=RequestHandler) as server:
        # add default functions
        server.register_introspection_functions()

        # contains functions available for clients
        class Clientfunctions:

            def up(self, value):
                return value

            def testsleep(self, length):
                time.sleep(length)
                return ("READY")

            def findpath(self, start, end):
                ret_list = wikipathfinder.wikiexecutor(start, end)
                print(ret_list)
                return ret_list

        server.register_instance(Clientfunctions())

        # server side functionality
        class Serverfunctions:
            pass

        print("Server running!")
        server.serve_forever()


if __name__ == "__main__":
    server()
