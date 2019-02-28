'''
Created on 2019年2月26日

@author: vargen
'''

import sys
import os
from time import sleep
from mimetypes import init

sys.path.append('../') 

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
from managerment.ManageServer import ManagerService

MIMETYPE = {
                'html' : 'text/html',
                'css'  : 'text/css',
                'txt'  : 'text/plain',
                'mpeg' : 'video/mpeg',
                'mpg'  : 'video/mpeg',
                'mov'  : 'video/quicktime'
            }

ENCTYPE  = {
                'default'    : 'application/x-www-form-urlencoded',
                'file'       : 'multipart/form-data',
                'space2plus' : 'text/plain',
                'json'       : 'application/json'
            }  
 
pathsMap = {
                '/favicon.ico'   : {'status': 200, 'html_path': '../web_root/images/wb_favicon.ico'},
                '/home'          : {'status': 200, 'mimetype' : MIMETYPE['html'], 'html_path': '../web_root/static/index.html'},
                '/css/style.css' : {'status': 200, 'mimetype' : MIMETYPE['css'], 'html_path': '../web_root/css/style.css'},
            
                '/login'         : {'status': 200, 'mimetype' : MIMETYPE['html'], 'html_path': '../web_root/static/login.html'},
                '/login_success' : {'status': 200, 'mimetype' : MIMETYPE['html'], 'html_path': '../web_root/static/login_success.html'},
                '/login_fail'    : {'status': 200, 'mimetype' : MIMETYPE['html'], 'html_path': '../web_root/static/login_fail.html'},
                '/audioplayer'   : {'status': 200, 'mimetype' : MIMETYPE['html'], 'html_path': '../web_root/static/audioplayer.html'},
                '/audio_src'     : {'status': 200, 'mimetype' : MIMETYPE['html']},
                
                '/foo'           : {'status': 200},
                '/bar'           : {'status': 302},
                '/baz'           : {'status': 404},
                '/qux'           : {'status': 500}
            }

pathsVisiable = ['/favicon.ico', '/home', '/css/style.css', '/audioplayer']

def webDataToMap(data, enctype):
    map = {}
    if enctype == ENCTYPE['default']:
        dataList = data.split('&')
        for dl in dataList:
            m = dl.split('=')
            k = m[0]
            if len(m) == 2:
                map[k] = m[1]
            else:
                map[k] = ''
    elif enctype == ENCTYPE['json']:
        map = json.load(data)
    
    return map

class HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', MIMETYPE['html']+';charset=UTF-8')
        self.end_headers()
    
    def sendMessageToWeb(self, msg):
        self.send_response(200)
        self.send_header('Content-type', MIMETYPE['html']+';charset=UTF-8')
        self.end_headers()
        self.wfile.flush()
        self.wfile.write(msg.encode('utf-8'))
        
    def do_GET(self):
        if self.path in pathsMap:
            if self.path == '/home':
                logging.info('\n\n>>>Someone try to connect %s %s', self.headers['host'], self.path)
            self.respond(pathsMap[self.path])
        else:
            self.respond({'status': 500})
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) #  Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') #  Gets the data itself
        
        mimetype = self.headers['Content-type']
        if self.path in pathsMap:
            manageServer = ManagerService()
            if self.path == '/login':
                usrInfo = webDataToMap(post_data, mimetype)
                isUsrVaild = manageServer.queryUsr(usrInfo['username'], usrInfo['password'])
                if isUsrVaild:
                    self.respondToAllRequest("/login_success")
                    
                else:
                    self.respondToAllRequest("/login_fail")
            elif self.path == '/audio_src':
                data = {}
                data["audio_src_path"] = manageServer.getAudioSrcPath()
                sendDataJson = json.dumps(data)
                self.sendMessageToWeb(sendDataJson)
        #else:
            logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data)

    def respond(self, opts):
        if self.path in pathsVisiable:
            response = self.handle_http(opts['status'], self.path)
            self.wfile.write(response)
        
    def respondToAllRequest(self, path):
        opts = pathsMap[path]
        if 'status' in opts:
            response = self.handle_http(opts['status'], path)
        else:
            response = self.handle_http(200, path)
        self.wfile.flush()
        self.wfile.write(response)
        
    def handle_http(self, status_code, path):
        self.send_response(status_code)
        
        htmlContent = ''
        htmlPath = ''
        
        if path in pathsMap:
            p = pathsMap[path]
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
    