#!/usr/bin/env python
# coding:utf-8

import os, web, logging, logging.config
from simpleBlog import *

web.config.debug = False
logging.config.fileConfig(ProjectPath + '/conf/logging.ini')

urls = (
    "/login", Login,
    "/logout", Logout,
    "/edit.html", GetEditPage,
    "/post", SavePost,
    "/post/(.+).html", GetPostPage,
    "/archive.html", GetArchivePage,
    "/comment", Comment,
    "/search", Search
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore(ProjectPath + '/run/sessions'))

def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))

if __name__ == "__main__":
    app.run()
