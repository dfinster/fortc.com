import http.server
import socketserver
import os
from urllib.parse import unquote
import webbrowser
import time
import threading
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

class PostsChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Trigger rebuild on any file change in /posts
        if not event.is_directory:
            print(f"Change detected in /posts: {event.src_path}. Rebuilding site...")
            subprocess.call(["./mkwww.sh"])

if __name__ == "__main__":
    # Start the file observer for the /posts directory
    posts_dir = os.path.join(os.getcwd(), "posts")
    observer = Observer()
    event_handler = PostsChangeHandler()
    observer.schedule(event_handler, path=posts_dir, recursive=True)
    observer.start()

    try:
        print("Serving at port", PORT)
        webbrowser.open("http://localhost:" + str(PORT))
        httpd = socketserver.TCPServer(("", PORT), PrettyURLHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        httpd.server_close()
