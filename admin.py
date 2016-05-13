# 
# -*- coding: utf-8 -*-
# 


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class HttpProcessor(BaseHTTPRequestHandler):
    
    def do_GET(self):
        txt = open('admin/index.html')

        self.moveRectangle()
        saveCurrentImage()

        # Картинка с текущим кадром
        if self.path == "/screen.png":
            self.send_response(200)
            self.send_header("content-type", "image/png")
            self.end_headers()
            png = open('current.png')
            self.wfile.write(png.read())
            return

        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(txt.read())
        return

    # Позиционирование области слежения
    def moveRectangle(self) :
        global point1, point2, width
        
        # right
        if self.path == "/right":
            point1 = (point1[0] + 10, point1[1])
            point2 = (point2[0] + 10, point2[1])

        # left
        if self.path == "/left":
            point1 = (point1[0] - 10, point1[1])
            point2 = (point2[0] - 10, point2[1])

        # top
        if self.path == "/top":
            point1 = (point1[0], point1[1] - 10)
            point2 = (point2[0], point2[1] - 10)

        # bottom
        if self.path == "/bottom":
            point1 = (point1[0], point1[1] + 10)
            point2 = (point2[0], point2[1] + 10)

        # width_plus
        if self.path == "/width_plus":
            width = width + 10
            point2 = (point1[0] + width, point1[1] + width)

        # width_minus
        if self.path == "/width_minus":
            width = width - 10
            point2 = (point1[0] + width, point1[1] + width)

        saveSettings()
        
        return




serv = HTTPServer(("localhost", 7030), HttpProcessor)
serv.serve_forever()
