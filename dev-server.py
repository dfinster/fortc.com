import http.server
import socketserver
import os
from urllib.parse import unquote
import webbrowser

PORT = 8000
DIRECTORY = os.path.join(os.getcwd(), "output")

class PrettyURLHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Remove query parameters and fragment identifiers
        path = unquote(path.split('?', 1)[0].split('#', 1)[0])
        # Remove leading slash to get relative path
        relpath = path.lstrip("/")
        local_path = os.path.join(DIRECTORY, relpath)

        if os.path.isdir(local_path):
            # If the path is a directory, serve its index.html
            local_path = os.path.join(local_path, "index.html")
        elif not os.path.splitext(local_path)[1]:
            # If no file extension, check if a corresponding .html file exists
            if os.path.exists(local_path + ".html"):
                local_path = local_path + ".html"
        return local_path

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

os.chdir(DIRECTORY)
handler = PrettyURLHandler
httpd = socketserver.TCPServer(("", PORT), handler)
print("Serving at port", PORT)
webbrowser.open("http://localhost:" + str(PORT))
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
