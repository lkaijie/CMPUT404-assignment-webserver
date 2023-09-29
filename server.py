#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
import os
from typing import Dict
from pathlib import Path
class MyWebServer(socketserver.BaseRequestHandler):
    
    NOT_ALLOWED = "HTTP/1.1 405 Method Not Allowed\r\n"
    NOT_FOUND = "HTTP/1.0 404 Not Found\r\n"
    
    def parse_request(self, data) -> Dict:
        """Parse the HTTP request

        Args:
            data (request): request in bytes

        Returns:
            Dict: returns a dictionary containing info about the request
        """
        request = {}
        seperator = "\r\n"
        
        request_main = data.decode(encoding="utf-8").split(seperator)
        # print(request_main)
        
        
        request_line = request_main[0].split()
        
        request["method"], request["path"] = request_line[0], request_line[1]
        # request_headers = {}
        request["path"] = "www" + request["path"]
        print(request)
        return request
        
    def process_request(self, request_line) -> str:
        print(request_line["path"])
        if request_line["method"] != "GET":
            # return 405
            return self.NOT_ALLOWED
        else:
            path = request_line["path"]
            
            if (os.path.exists(request_line["path"])):
                print("valid")
                if Path(request_line["path"]).is_dir():
                    if path[-1] == '/':
                        path += "index.html"
                        response = self.get_file("html", path)
                    else:
                        # 301 error, correct the path
                        response = "HTTP/1.1 301 Moved Permanently\r\n"
                        response += f"Location: http://127.0.0.1:8080{path[3:]}/\r\n\r\n"
                        print(f"301 Moved Permanently: {response}")
                        return response
                        
                    pass
                elif Path(request_line["path"]).is_file():
                    if path.endswith(".html"):
                        response = self.get_file("html", path)
                    elif path.endswith(".css"):
                        response = self.get_file("css", path)
                    else:
                        # return 404
                        print("invalid file type2")
                        return self.NOT_FOUND
                    pass
                
                
                
            else:
                print("invalid file path")
                # return 404
                return self.NOT_FOUND
        return response
                
            
    def get_file(self, file_type, path) -> str:
        if file_type == "html":
            mimetype = "text/html"
        elif file_type == "css":
            mimetype = "text/css"
            
        response = "HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: {mimetype}\r\n"
        response += f"Content-Length: {os.path.getsize(path)}\r\n\r\n"
        response += open(path).read()
        print(response)
        
        return response    
    
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)
        # print(self.data)
        request_line = self.parse_request(self.data)
        response = self.process_request(request_line=request_line)
        print(response)
        self.request.sendall(bytearray(response, 'utf-8'))
        
        
        # self.request.sendall(bytearray("OK",'utf-8'))
        # self.request.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()