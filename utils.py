import random
import string      
from config import *

def getColumnLabel(colkey):
    return COL_VALUES[colkey]['label']

def getColumnVar(colkey):
    return COL_VALUES[colkey]['var']

def getEntryIndex(headers,entry):
    label=COL_VALUES[entry]['label']
    return headers.index(label)

def getRelPath(fn):
    return WORKING_DIR+fn

def getPublicKey():
    with open(getRelPath(PUBLIC_KEY_FILE),'r') as fh:
        return fh.read().strip()

def getSecretKey():
    with open(getRelPath(SECRET_KEY_FILE),'r') as fh:
        return fh.read().strip()

def getAccessToken():
    with open(getRelPath(ACCESS_TOKEN_FILE),'r') as fh:
        return fh.read().strip()

# The file written to by collector.request().get_posts_for_one_user.
def getUserFile(user,id_=None):
    if isinstance(id_,type(None)):
        id_=''.join(random.choice(string.lowercase) for _ in range(4))
    return getRelPath('{}/user{}-{}.json'.format(user,user,id_)),id_

# The file written to by collector.request().get_post_data.
def getThreadFile(thread,user,id_=None):
    if isinstance(id_,type(None)):
        id_=''.join(random.choice(string.lowercase) for _ in range(4))
    return getRelPath('{}/thread{}-{}.tsv'.format(user,thread,id_))

# Encode a non-ASCII string to ASCII. If a non-ASCII character is
# encountered, delete it.
def to_ascii(s):
    return s.encode('ascii','ignore')

# A generator for all the threads a given user posted to
def getAllThreadsByUser(user,id_):
    import json

    fn,id_=getUserFile(user,id_)
    with open(fn,'r') as fh:
        json_obj=json.loads(fh.read())
        for post in json_obj:
            yield post['thread'],post['createdAt']

# Returns a list of the thread files in a user's directory.
def getAllThreadFiles(user,id_=None):
    import os
    import re

    return [ '{}/{}'.format(user,f) for f in os.listdir(WORKING_DIR+user) if
             len(re.findall(r""+getThreadFile('[0-9]*',user,id_='[a-z]*').lstrip(getRelPath(user+'/')),f))>0
           ]

def zip_(fn):
    import os

    os.system('bzip2 -vf {}'.format(fn))

def unzip_(fn):
    import os

    os.system('bunzip2 -v {}.bz2'.format(fn))

def startLog():
    import logging

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)
