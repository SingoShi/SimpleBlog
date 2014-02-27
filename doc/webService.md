# Web service

## 1 login/logout
### 1.1 login
    
    URI: /login
    Method: POST
    Data Params: {
        'username': string,
        'password': string,
    }
    Success Return: {
        'error': 0
    }
    Error Return: {
        'error': int
    }
    Description: response SET-COOKIE
    
### 1.2 logout
    
    URI: /logout
    Method: GET
    Success Return: {
        'error': 0
    }
    Error Return: {
        'error': int
    }
    
## 2 posts

### 2.1 new post or edit a post

    URI: /edit.html?postId=***
    Method: GET
    Success Return: edit page with post id(if not postId provide, generate new id)

### 2.2 save a post
    
    URI: /post
    Method: POST
    Data Params: {
        'postId': string,
        'postContent': string,
    }
    Success Return: {
        'error': 0
    }
    Error Return: {
        'error': int
    }
    Description: need login
    
### 2.3 get one post

    URI: /post/(.+).html
    Method: GET
    Success Return: post page
    
### 2.4 get archive

    URI: /archive.html
    Method: GET
    URL Params: ?filter=***
    Success Return: archive page
    Description: return all posts if login, else return all published posts

## 3 comments

### 3.1 post comment
    
    URI: /comment
    Method: POST
    Data Params: {
        'postId': int,
        'comment': int,
        'username': string 
    }
    Success Return: {
        'error': 0
    }
    Error Return: {
        'error': int
    }

### 3.2 get comments
    
    URI: /comment
    Method: GET
    Data Params: {
        'postId': int
    }
    Success Return: {
        'error': 0,
        'result': {
            'comments': [
                {
                    'username': string,
                    'comment': string
                },
                ...
            ]
        }
    }
    Error Return: {
        'error': int
    }
    
## 4 search

### search

    URI: /search
    URL Params: ?filter=***
    Method: GET
    Success Return: {
        'error': 0,
        'result': {
            'keyList': [
                string,
                ...
            ]
        }
    }
    Error Return: {
        'error': int
    }

## 5 statistic

### 5.1 get total visit
    URI: /visit
    Method: GET
    Success Return: {
        'error': 0,
        'result': {
            'count': int
        }
    }
    Error Return: {
        'error': int
    }

### 5.2 get post visit

    URI: /visit
    Method: GET
    URL Params: ?postId=***
    Success Return: {
        'error': 0,
        'result': {
            'count': int
        }
    }
    Error Return: {
        'error': int
    }

### 5.3 update visit count

    URI: /visit
    Method: PUT
    Data Params: {
        'postId': int
    }
    Success Return: {
        'error': 0,
        'result': {
            'count': int
        }
    }
    Error Return: {
        'error': int
    }

## 6 RSS

### 6.1 RSS
    
