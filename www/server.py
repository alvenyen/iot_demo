#!/usr/bin/env python
import sys
import os
import inspect
import BaseHTTPServer
import CGIHTTPServer
import cgitb; cgitb.enable()
from daemon import Daemon

RUNNING_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class DemoServer(Daemon):
    def run(self):
        os.chdir(RUNNING_DIR)
        server = BaseHTTPServer.HTTPServer
        handler = CGIHTTPServer.CGIHTTPRequestHandler
        server_address = ("", 8081)
        handler.cgi_directories = ["/cgi-bin"]
        self.httpd = server(server_address, handler)
        self.httpd.serve_forever()

    def terminate(self):
        self.httpd.server_close()
        
if __name__ == '__main__':
    daemon = DemoServer('/tmp/demo_server.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)