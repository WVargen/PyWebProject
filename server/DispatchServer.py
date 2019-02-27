'''
Created on 2019年2月26日

@author: vargen
'''
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from urllib.parse import urlparse
import logging

MIMETYPE = {
               'html' : 'text/html',
               'css'  : 'text/css',
               'txt'  : 'text/plain',
               'mpeg' : 'video/mpeg',
               'mpg'  : 'video/mpeg',
               'mov'  : 'video/quicktime'
            }
  
pathsMap = {
            '/favicon.ico'   : {'status': 200, 'html_path': '../web_root/images/wb_favicon.ico'},
            '/home'          : {'status': 200, 'mimetype' : MIMETYPE['html'], 'html_path': '../web_root/static/index.html'},
            '/css/style.css' : {'status': 200, 'mimetype' : MIMETYPE['css'], 'html_path': '../web_root/css/style.css'},
            
            '/login'         : {'status': 200},
            
            '/foo'           : {'status': 200},
            '/bar'           : {'status': 302},
            '/baz'           : {'status': 404},
            '/qux'           : {'status': 500}
        }


class HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', MIMETYPE['html'])
        self.end_headers()

    def do_GET(self):
        if self.path in pathsMap:
            self.respond(pathsMap[self.path])
        else:
            self.respond({'status': 500})
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) #  Gets the size of data
        post_data = self.rfile.read(content_length) #  Gets the data itself
        
        if self.path in pathsMap:
            if self.path == '/login':
                
                print("11111")
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self.do_HEAD()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)

    def handle_http(self, status_code, path):
        self.send_response(status_code)
        
        htmlContent = ''
        htmlPath = ''
        if self.path in pathsMap:
            p = pathsMap[self.path]
            if 'mimetype' in p:
                mimetype = p['mimetype']
                self.send_header('Content-type', mimetype)
            else:
                self.send_header('Content-type', MIMETYPE['html'])
            if 'html_path' in p:
                htmlPath = p['html_path']
                with open(htmlPath, 'rb') as f:
                    htmlContent = f.read()
            self.end_headers()
        else:
            self.send_header('Content-type', MIMETYPE['html'])
            self.end_headers()
            htmlContent = '''
           <html><head><title>Title goes here.</title></head>
           <body><p>This is a test.</p>
           <p>You accessed path: {}</p>
           </body></html>
           '''.format(path).encode('utf_8')
        return htmlContent

def run(server_class=HTTPServer, handler_class=HTTPServer_RequestHandler, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting server...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server...\n')
                
if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
    