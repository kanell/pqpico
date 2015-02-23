from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

PORT_NUMBER = 9999

class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        self.wfile.write('Hellooooo')

        return


try:
    server = HTTPServer(('',PORT_NUMBER), myHandler)
    print('Started httpserver on port'+str(PORT_NUMBER))

    server.serve_forever()

except KeyboardInterrupt:
    print('Shutting Down')
    server.socket.close()
