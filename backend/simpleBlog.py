#!/usr/bin/env python
# coding:utf-8

import os, web, logging
import json, hashlib, traceback
import glob, time
import pytz, datetime
from markdown import Markdown

ProjectPath = os.path.split(os.path.realpath(__file__))[0] + '/..'
Success = { "error": 0 }
AuthError = { "error": 1 }
SaveError = { "error": 2 }
MetaError = { "error": 4 }
InputError = { "error": 8 }

#############################################################################

def readFile(filename):
    ret = ''
    try:
        with open(filename, "r") as fp:
            ret = fp.read()
    except:
        logging.error(traceback.format_exc())
    return ret

def writeFile(filename, content):
    try:
        with open(filename, "w") as fp:
            fp.write(content)
    except:
        logging.error(traceback.format_exc())

def auth(func):
    def wrapper(*args, **kv):
        if web.ctx.session.has_key('login') and web.ctx.session.login:
            return func(*args, **kv)
        else:
            return json.dumps(AuthError)
    return wrapper

#############################################################################

class Setting():
    try:
        blogSetting = readFile("%s/setting/blogSetting.json" % (ProjectPath))
        blogSettingObj = json.loads(blogSetting)
        cfgObj = json.loads(readFile("%s/setting/config.json" % (ProjectPath)))
        template = readFile("%s/template/template.html" % (ProjectPath))
        template = template.replace("%blogSetting%", blogSetting)
        newPost = readFile("%s/setting/newPost.md" % (ProjectPath))
        if os.path.exists("%s/frontend/index.json" % (ProjectPath)):
            index = json.loads(readFile("%s/frontend/index.json" % (ProjectPath)))
        else:
            index = None
        tz = pytz.timezone(cfgObj['timezone'])
    except:
        logging.error(traceback.format_exc())

class SimpleBlog():
    def backup(self):
        backupName = "%s.tgz" % int(time.time())
        os.system("cd %s; tar -czf %s frontend/" % (ProjectPath, backupName))
        if os.path.exists("%s/%s" % (ProjectPath, backupName)):
            os.system("mv %s/%s %s/backup/" % (ProjectPath, backupName, ProjectPath))

    def resetBlog(self):
        os.system("rm -rf %s/frontend/*.*" % (ProjectPath))

    def getPostId(self):
        files = sorted(glob.glob("%s/frontend/post/*" % (ProjectPath)))
        if files:
            id = int(files[-1].split('/')[-1].split('.')[0]) + 1
        else:
            id = 1
        return str(id)

    def getFilename(self, type, postId, status):
        return  "%s/frontend/%s/%s.%s%s" % (ProjectPath,
                                            type, postId,
                                            'html' if type == 'post' else 'md',
                                            '' if status == "public" else '_')

    def genEditPage(self, postId=None):
        if not postId:
            postId = self.getPostId()
            content = Setting.newPost
        else:
            if os.path.exists("%s/frontend/md/%s.md" % (ProjectPath, postId)):
                content = readFile("%s/frontend/md/%s.md" % (ProjectPath, postId))
            else:
                content = readFile("%s/frontend/md/%s.md_" % (ProjectPath, postId))

        pagedata = {
            "postId": int(postId),
            "content": content,
            "type": "edit"
        }
        return Setting.template.replace("%path%", "").replace("%pageData%", json.dumps(pagedata))

    def isLatestPost(self, postId, status):
        files = sorted(glob.glob("%s/frontend/post/*.html" % (ProjectPath)))
        if files:
            id = int(files[-1].split('/')[-1].split('.')[0]) + 1
            if int(postId) >= id:
                return True
            else:
                return False
        else:
            return True

    def genPostPage(self, postId, content, meta, isLatest, path="../"):
        pagedata = {
            "postId": int(postId) if postId else 0,
            "type": "post",
            "latest": isLatest
        }
        #now = datetime.datetime.now(Setting.tz)
        #postDate = now.strftime('%Y/%m/%d')
        pagedata["postTitle"] = meta["title"] if meta.has_key('title') else ""
        pagedata["postDate"] = meta["date"] if meta.has_key('date') else ""
        pagedata["status"] = meta["status"] if meta.has_key('status') else "private"
        page = Setting.template.replace("%path%", path).replace("%pageData%", json.dumps(pagedata))
        return page.replace("%postMd%", content)

    def genAboutPage(self):
        about = json.dumps({
            "type": "about",
            "content": readFile("%s/setting/about.md" % (ProjectPath))
        })
        return Setting.template.replace("%path%", "").replace("%pageData%", about)

    def genMeta(self, mdMeta):
        meta = {}
        for key, value in mdMeta.iteritems():
            tmp = value[0].strip() if value else ''
            if key in ['category', 'tags']:
                meta[key] = []
                for word in tmp.split(' '):
                    word = word.strip()
                    if word:
                        meta[key].append(word)
            else:
                meta[key] = tmp
        return meta

    def getPostMeta(self, postFile):
        if not postFile:
            return "", {}, ""
        postId = postFile.split('/')[-1].split('.')[0]
        content = readFile(postFile)
        md = Markdown(extensions=["meta"])
        md.convert(content.decode('utf-8'))
        meta = self.genMeta(md.Meta)
        return postId, meta, content

    def genHomePage(self):
        files = sorted(glob.glob("%s/frontend/md/*.md" % (ProjectPath)))
        latest = True if files else False
        postId, meta, content = self.getPostMeta(files[-1] if latest else '')
        return self.genPostPage(postId, content, meta, latest, "")

    def genArchiveObj(self, file, output):
        postId, meta, content = self.getPostMeta(file)
        obj = {
            "postDate": meta["date"],
            "postTitle": meta["title"],
            "postId": postId,
            "status": meta["status"]
        }
        if not output['files'].has_key(file):
            output['archives'].append(obj)
            output['files'][file] = True

    def genArchivePage(self, archives = None):
        pagedata = {
            "type": "archive",
            "archives": []
        }
        if archives == None:
            files = glob.glob("%s/frontend/md/*.md" % (ProjectPath))
            archives = { 'files': {}, 'archives': [] }
            for file in files:
                self.genArchiveObj(file, archives)
            archives = archives['archives']
        pagedata["archives"] = archives
        return Setting.template.replace("%path%", "").replace("%pageData%", json.dumps(pagedata))

    def addIndex(self, index, meta, file):
        if meta.has_key('category'):
            for category in meta['category']:
                if category:
                    if not index['categories'].has_key(category):
                        index['categories'][category] = {}
                    index['categories'][category][file] = 1
                    if not index['keywords'].has_key(category):
                        index['keywords'][category] = {}
                    index['keywords'][category][file] = 1
        if meta.has_key('tags'):
            for tag in meta['tags']:
                if tag:
                    if not index['keywords'].has_key(tag):
                        index['keywords'][tag] = {}
                    index['keywords'][tag][file] = 1

    def delIndex(self, index, meta, file):
        if meta.has_key('category'):
            for category in meta['category']:
                if category and index['categories'].has_key(category):
                    if index['categories'][category].has_key(file):
                        index['categories'][category].pop(file)
                if category and index['keywords'].has_key(category):
                    if index['keywords'][category].has_key(file):
                        index['keywords'][category].pop(file)
        if meta.has_key('tags'):
            for tag in meta['tags']:
                if tag and index['keywords'].has_key(tag):
                    if index['keywords'][tag].has_key(file):
                        index['keywords'][tag].pop(file)

    def buildIndex(self):
        files = glob.glob("%s/frontend/md/*.md*" % (ProjectPath))
        index = {
            'categories': {},
            'keywords': {}
        }
        for file in files:
            postId, meta, content = self.getPostMeta(file)
            self.addIndex(index, meta, file)
        Setting.index = index
        writeFile("%s/frontend/index.json" % (ProjectPath), json.dumps(Setting.index, indent=4))

    def updateIndex(self, oldMeta, oldPost, meta, post):
        if Setting.index == None:
            self.buildIndex()

        self.delIndex(Setting.index, oldMeta, oldPost)
        self.addIndex(Setting.index, meta, post)
        writeFile("%s/frontend/index.json" % (ProjectPath), json.dumps(Setting.index, indent=4))

    def genSitemap(self):
        sitemap = '''
            <?xml version="1.0" encoding="UTF-8"?>
            <urlset
                  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
            {urlitems}
            </urlset>
        '''
        urlitem = '''
            <url>
              <loc>http://{domain}/post/{postId}.html</loc>
              <changefreq>daily</changefreq>
            </url>
        '''
        urlitems = ''
        files = glob.glob("%s/frontend/md/*.md" % (ProjectPath))
        domain = Setting.blogSettingObj['domain']
        if files:
            for file in files:
                postId = file.split('/')[-1].split('.')[0]
                urlitems += urlitem.format(domain=domain, postId=postId)
            writeFile("%s/frontend/sitemap.xml" % (ProjectPath), sitemap.format(urlitems=urlitems))

##################################################################################################

class Login():
    def POST(self):
        web.header('Content-Type', 'application/json')
        param = json.loads(web.data())
        if param['username'] == Setting.cfgObj['username']:
            if hashlib.md5(str(param['password'])).hexdigest() == Setting.cfgObj['password']:
                web.ctx.session.login = True
                web.setcookie('login', param['username'])
                return json.dumps(Success)
        return json.dumps(AuthError)

class Logout():
    def GET(self):
        web.header('Content-Type', 'application/json')
        web.setcookie('login', '', expires= -1)
        web.ctx.session.kill()
        return json.dumps(Success)

class GetEditPage(SimpleBlog):
    @auth
    def GET(self):
        web.header('Content-Type', 'text/html')
        param = web.input()
        postId = param['postId'] if param and param.has_key('postId') else None
        return self.genEditPage(postId)

class SavePost(SimpleBlog):
    @auth
    def POST(self):
        web.header('Content-Type', 'application/json')
        try:
            param = json.loads(web.data())
            try:
                postId = str(int(param['postId']))
                postContent = param['postContent'].encode('utf-8')
            except:
                logging.error("%s", traceback.format_exc())
                return json.dumps(InputError)

            if os.path.exists('%s/frontend/md/%s.md' % (ProjectPath, postId)):
                oldStatus = 'public'
                postId, oldMeta, tmp = self.getPostMeta('%s/frontend/md/%s.md' % (ProjectPath, postId))
            else:
                oldStatus = 'private'
                if os.path.exists('%s/frontend/md/%s.md_' % (ProjectPath, postId)):
                    postId, oldMeta, tmp = self.getPostMeta('%s/frontend/md/%s.md_' % (ProjectPath, postId))
                else:
                    oldMeta = {}
            try:
                md = Markdown(extensions=["meta"])
                md.convert(postContent.decode('utf-8'))
                meta = self.genMeta(md.Meta)
                for key in ["category", "tags", "date", "title", "status"]:
                    if not meta.has_key(key) or not meta[key]:
                        raise ValueError("input error")
                    if key == "status" and meta[key] not in ["public", "private"]:
                        raise ValueError("input error")
            except:
                logging.error("%s", traceback.format_exc())
                return json.dumps(MetaError)

            status = meta['status'] if meta.has_key('status') else 'private'
            os.system('rm -rf %s/frontend/md/%s.md*' % (ProjectPath, postId))
            os.system('rm -rf %s/frontend/post/%s.html*' % (ProjectPath, postId))
            isLatest =  self.isLatestPost(postId, status)
            writeFile(self.getFilename('md', postId, status), postContent)
            writeFile(self.getFilename('post', postId, status), self.genPostPage(postId, postContent, meta, isLatest and status == 'public'))

            if isLatest:
                writeFile("%s/frontend/home.html" % (ProjectPath), self.genHomePage())
            if oldStatus != status:
                writeFile('%s/frontend/archive.html' % (ProjectPath), self.genArchivePage())
                self.genSitemap()
            if oldStatus != status or oldMeta != meta:
                self.updateIndex(oldMeta,
                                 self.getFilename('md', postId, oldStatus),
                                 meta,
                                 self.getFilename('md', postId, status))
            return json.dumps(Success)
        except:
            logging.error("SavePost get exception: %s", traceback.format_exc())
            return json.dumps(SaveError)

class GetPostPage(SimpleBlog):
    def GET(self, postId):
        web.header('Content-Type', 'text/html')
        if os.path.exists("%s/frontend/post/%s.html" % (ProjectPath, postId)):
            return readFile("%s/frontend/post/%s.html" % (ProjectPath, postId))
        if os.path.exists("%s/frontend/post/%s.html_" % (ProjectPath, postId)):
            if web.ctx.session.has_key('login') and web.ctx.session.login:
                return readFile("%s/frontend/post/%s.html_" % (ProjectPath, postId))
        raise web.notfound()

class GetArchivePage(SimpleBlog):
    def GET(self):
        web.header('Content-Type', 'text/html')
        param = web.input()
        filter = param['filter'] if param.has_key('filter') else ''
        if Setting.index == None:
            self.buildIndex()
        archives = { 'files': {}, 'archives': [] }
        for keyword, files in Setting.index['keywords'].iteritems():
            if not filter or keyword == filter:
                for file in files:
                    if web.ctx.session.has_key('login') and web.ctx.session.login:
                        self.genArchiveObj(file, archives)
                    elif file.endswith('.md'):
                        self.genArchiveObj(file, archives)

        return self.genArchivePage(archives['archives'])

class Comment():
    pass

class Search(SimpleBlog):
    def GET(self):
        web.header('Content-Type', 'application/json')
        param = web.input()
        filter = param['filter'] if param.has_key('filter') else ''
        if Setting.index == None:
            self.buildIndex()
        ret = {
            'error': 0,
            'keyList': []
        }
        if not filter:
            searchIdx = Setting.index['categories']
        else:
            searchIdx = Setting.index['keywords']
        for keyword, value in searchIdx.iteritems():
            if value and filter in keyword:
                if web.ctx.session.has_key('login') and web.ctx.session.login:
                    ret['keyList'].append(keyword)
                else:
                    for file in value:
                        if file.endswith('.md'):
                            ret['keyList'].append(keyword)
                            break
        return json.dumps(ret)

class Visit():
    def GET(self):
        web.header('Content-Type', 'application/json')
        param = web.input()
        postId = param["postId"] if param.has_key("postId") else "*"
        files = glob.glob("%s/frontend/visit/%s.cnt" % (ProjectPath, postId))
        cnt = 0
        for file in files:
            tmp = readFile(file)
            cnt += int(tmp) if tmp else 0
        return json.dumps({ 'error': 0, 'result': { 'count': cnt } })

    def PUT(self):
        web.header('Content-Type', 'application/json')
        param = json.loads(web.data())
        if param.has_key("postId"):
            postId = param["postId"]
            file = "%s/frontend/visit/%s.cnt" % (ProjectPath, postId)
            tmp = readFile(file)
            cnt = 1 + (int(tmp) if tmp else 0)
            writeFile(file, str(cnt))
            return json.dumps({ 'error': 0, 'result': { 'count': cnt } })
        else:
            return json.dumps(InputError)

