# The xmp sections  

The blog page include two xmp sections `<xmp style="display: none"></xmp>`:

1. blogSetting section
2. pageData section

Each section contains json-format data, the schema is like followings:

## blogSetting  

for blogSetting section `<xmp style="display: none" id="blogSetting">`

    {
        "blogTitle": "Singo's Blog", 
        "blogOwner": "Singo"
    }

## pageData

for pageData section `<xmp style="display: none" id="pageData">`, the schema depends on data type:

### archive  
	
    {
    	'type': 'archive',
    	'archives': [
        	{
            	'postDate': '2013/11/23',
            	'postTitle': 'this is test',
            	'postId': '/post/1',
            	'status': 'private'
        	},
        	...
    	]
    }

### about

    {
        'type': 'about',
        'content': 'the markdown text',
    }

### post

    {
        'type': 'post',
        'latest': true,
        'postDate': '2013/11/23'
        'postId': '222',
        'postTitle': 'this is test',
        'status': 'public'
    }
    
### new

    {
        'type': 'edit',
        'content': 'text',
        'postId': '222'
    }

## postMd

if type is post, postMd section `<xmp style="display: none" id="postMd">` which contains markdown text is included
