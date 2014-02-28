#!/usr/bin/env python
# coding:utf-8

import os, sys, time
import json, traceback
import glob, logging
import logging.config

sys.path.append(os.path.split(os.path.realpath(__file__))[0] + '/../backend')

from simpleBlog import *

def buildBlog():
    try:
        simpleBlog = SimpleBlog()
        simpleBlog.backup()
        simpleBlog.resetBlog()
        simpleBlog.buildIndex()
        writeFile("%s/frontend/about.html" % (ProjectPath), simpleBlog.genAboutPage())
        writeFile("%s/frontend/home.html" % (ProjectPath), simpleBlog.genHomePage())
        writeFile("%s/frontend/archive.html" % (ProjectPath), simpleBlog.genArchivePage())
        simpleBlog.genSitemap()
        mds = glob.glob("%s/frontend/md/*.md" % (ProjectPath))
        for md in mds:
            postId, meta, content = simpleBlog.getPostMeta(md)
            writeFile(
                    simpleBlog.getFilename('post', postId, 'public'), 
                    simpleBlog.genPostPage(postId, content, meta, simpleBlog.isLatestPost(postId, 'public')))
    except:
        logging.info(traceback.format_exc())

if __name__ == "__main__":
    logging.config.fileConfig(ProjectPath + '/conf/logging.ini')
    buildBlog()

