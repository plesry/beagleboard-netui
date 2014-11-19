#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from netui import app
from netui.config import DevelopmentConfig

app.config.from_object(DevelopmentConfig)

if __name__ == '__main__':
    WSGIServer(app).run()
