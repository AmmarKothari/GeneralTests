import SimpleHTTPServer
import SocketServer

# class ExampleHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

#   def do_GET(self):


import flask

ButtonPressed = 0        
@app.route('/button', methods=["GET", "POST"])
def button():
    if request.method == "POST":
        return render_template("button.html", ButtonPressed = ButtonPressed)
        # I think you want to increment, that case ButtonPressed will be plus 1.
    return render_template("button.html", ButtonPressed = ButtonPressed)


PORT = 8080
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

# with SocketServer.TCPServer(("", PORT), Handler) as httpd:
httpd = SocketServer.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()

