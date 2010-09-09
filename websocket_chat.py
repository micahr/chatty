import os
import eventlet
from eventlet import wsgi
from eventlet import websocket
import json

participants = set()

class User:
    def __init__(self,username, socket):
        self.username = username
        self.sock = socket
    def __repr__(self):
        return u"<User: %s>" % self.username

@websocket.WebSocketWSGI
def handle(ws):
    #participants.add(ws)
    try:
        while True:
            m = ws.wait()
            if m is None:
                break
            j = json.loads(m)
            if j['event'] == 'add_user':
                for p in participants:
                    ws.send(json.dumps({'event':'add_user','data':{'username':p.username}}))
                participants.add(User(j['data']['username'],ws))
            for p in participants:
                p.sock.send(m)
    finally:
        try:
            removed = [p for p in participants if p.sock == ws][0]
            participants.remove(removed)
            for p in participants:
                p.sock.send(json.dumps({'event':'remove_user','data':{'username':removed.username}}))
        except IndexError:
            print "There was something wrong"
                  
def dispatch(environ, start_response):
    """Resolves to the web page or the websocket depending on the path."""
    if environ['PATH_INFO'] == '/chat':
        return handle(environ, start_response)
    else:
        start_response('200 OK', [('content-type', 'text/html')])
        return [open(os.path.join(
                     os.path.dirname(__file__), 
                     'websocket_chat.html')).read()]
        
if __name__ == "__main__":
    # run an example app from the command line            
    listener = eventlet.listen(('127.0.0.1', 7000))
    print "\nVisit http://localhost:7000/ in your websocket-capable browser.\n"
    wsgi.server(listener, dispatch)