import json
import logging
import os
import time
from wordplay.collectors import DisqusCollector
from wordplay.utils import *
from utils import *

FORUM='breitbartproduction'
INCLUDE=['unapproved','approved','flagged','highlighted']

# A wrapper for functions to interact directly with the Disqus API
class APIBind(DisqusCollector):
    def __init__(self, forum=FORUM, include=INCLUDE, wait=False, log=True,
                 id_=None):
        DisqusCollector.__init__(self, forum=forum, include=include,
                                 wait=False, log=log, id_=id_)

    # Returns as a json object the API's response to a query for thread
    # data.
    def get_thread_data(self,trending=True,n_threads=100):
        object_='trends' if trending else 'forums'
        response=self.get_data(object_,'listThreads',limit=n_threads,
                               forum=self.forum)
        return json.loads(response.content)

    # List only the thread ids returned by class function get_thread_data().
    def get_thread_ids(self,trending=True,n_threads=100):
        json_obj=self.get_thread_data(trending=trending,n_threads=n_threads)
        if trending:
            return [ d['thread']['id'] for d in json_obj['response'] ]
        else:
            return [ d['id'] for d in json_obj['response'] ]

    def _get_data_str(self,**kwargs):
        data_str=''
        for col in COL_KEYS:
            data_str+='{}\t'.format(kwargs[getColumnVar(col)])
        data_str=data_str.rstrip()
        return data_str

    # Retrieve data for posts to a thread in a window around a specific
    # point in time. Writes all retrieved data to a tsv file set by
    # getThreadFile (see the README for information on setting up the
    # working environment), where each row is a unique post.
    #
    # Parameters:
    # thread: The thread to retrieve posts from.
    # user: The user whose directory to store the data in.
    # id_: The unique id to used to name the data file. If unspecified, will
    # default to a random string.
    # timestamp: The window of time will be centered at this time (ISO 8601
    # timestamp).
    # window: Get posts from this amount of time BEFORE time until this
    # amount of time AFTER time. Defaults to one hour.
    # keep_anonymous: If set to True, posts by anonymous users will be
    # recorded with a user id 'N/A'. Else, they will be discarded.
    def get_post_data(self,thread,user,timestamp,id_=None,window=3600,
                      keep_anonymous=True):
        fn=getThreadFile(thread=thread,user=user,id_=id_)
        timestamp_=iso8601_to_unix(timestamp)
        # Open tsv with thread id in file name
        with open(fn, 'a') as fh:
            # Write headers
            fh.write('\t'.join([ getColumnLabel(col) for col in COL_KEYS ]))
            response=self.get_data('threads','listPosts',thread=thread,
                                   since=unix_to_iso8601(timestamp_-window),
                                   order='asc',limit=100,
                                   include=self.include,forum=self.forum)
            json_obj=json.loads(response.content)
            nextval=self.get_next_val(json_obj)
            _created_at=unix_to_iso8601(timestamp_-window)
            while iso8601_to_unix(_created_at)-timestamp_<window:
                for post in json_obj['response']:
                    assert post['forum']==self.forum
                    assert post['thread']==thread
                    # Write post author and message to file.
                    if post['author']['isAnonymous'] and not keep_anonymous:
                        continue
                    elif post['author']['isAnonymous']:
                        _user='N/A'
                    else:
                        _user=post['author']['id']
                    _parent=post['parent']
                    _msg=to_ascii(post['message'])
                    _created_at=post['createdAt']
                    if iso8601_to_unix(_created_at)-timestamp_>=window:
                        break
                    data_str=self._get_data_str(user=_user,parent=_parent,
                                                msg=_msg,
                                                timestamp=_created_at)
                    fh.write('\n{}'.format(data_str))
                # Paginate through more results, if applicable.
                if isinstance(nextval,type(None)):
                    break
                response=self.get_data('threads','listPosts',thread=thread,
                                       since=_created_at,order='asc',
                                       include=self.include,cursor=nextval,
                                       limit=100,forum=self.forum)
                json_obj=json.loads(response.content)
                nextval=self.get_next_val(json_obj)
        return
    
    # Get list of n users from one thread. These user ids are saved to 
    # USERS_FILE in the user's WORKING_DIR (see the package's README for 
    # setting up the environment).
    #
    # Parameters:
    # thread: Fetch n unique commenters on this thread. Defaults to the most
    # recent trending thread.
    # n: The number of unique users to fetch. Defaults to 100.
    # overwrite: If True, the file will be wiped and n new users fetched.
    # Default behaviour appends user ids to existing user ids contained in
    # USERS_FILE until the list contains n user ids.
    def get_user_ids(self,thread=None,n=100,overwrite=False):
        if not thread:
            thread=self.get_thread_ids(n_threads=1)[0]
        fileName=getRelPath(USERS_FILE)
        if overwrite or not os.path.exists(fileName) or not isinstance(thread,type(None)):
            users=set()
            n_existing=0
        else:
            readFileHandle=open(fileName,'r')
            users=readFileHandle.read().split('\n')
            users=set([ user for user in users if user.strip() ])
            n_existing=len(users)
            logging.info('Found {} saved user ids.'.format(n_existing))
            readFileHandle.close()
        if len(users)<n:
            response=self.get_data('threads','listPosts',thread=thread,
                                   forum=self.forum,limit=100)
            json_obj=json.loads(response.content)
        while len(users)<n:
            for d in json_obj['response']:
                assert d['forum']==self.forum
                assert d['thread']==thread
                if 'id' not in d['author'] or d['author']['isPrivate']:
                    continue
                users.add(d['author']['id'])
                if len(users)>=n:
                    break
            nextval=self.get_next_val(json_obj)
            response=self.get_data('threads','listPosts',thread=thread,
                                   forum=self.forum,cursor=nextval,limit=100)
            json_obj=json.loads(response.content)
            logging.info('Got {} users.'.format(len(users)))
        users=list(users)[:max(n_existing,n)]
        fileHandle=open(fileName,'w')
        for user in users:
            fileHandle.write(user+'\n')
        fileHandle.close()
        users=users[:n]
        return users

    # Takes a json object of user data as argument, and writes selected
    # items of the object to a plain text file.
    def _write_user_data(self,user,user_data):
        fn,id_=getUserFile(user)
        with open(fn,'w') as fileHandle:
            json.dump(user_data,fileHandle)
        return user,id_

    def _update_user_data(self,user,user_data,json_obj,limit=None):
        user_=json_obj['response'][0]['author']['id']
        assert user_==user
        for post in json_obj['response']:
            if isinstance(limit,int):
                if len(user_data)>=limit:
                    return 1
            if post['forum']!=self.forum:
                continue
            assert post['author']['id']==user
            info_dict=dict()
            for datapt in [ 'isFlagged','isApproved','raw_message','thread',
                            'createdAt','isEdited','message','isDeleted',
                            'isHighlighted','likes','parent' ]:
                info_dict[datapt]=post[datapt]
            user_data.append(info_dict)
        return 0

    def _get_user_data(self,user,limit=100,cursor=None):
        kwargs_=dict(
                     user=user,
                     limit=limit,
                     cursor=cursor,
                     include=self.include
                    )
        kwargs_=dict([ (k,v) for k,v in kwargs_.items() if not
                       isinstance(v,type(None)) ])
        response=self.get_data('users','listPosts',**kwargs_)
        return json.loads(response.content)

    # Query, get and write all the post data for one user.
    def get_posts_for_one_user(self,user=None,n_posts=None,overwrite=False,
                               n_users=100):
        if isinstance(user,type(None)):
            user=self.get_user_ids(n=n_users,overwrite=overwrite)[0]
        os.system('mkdir -p {}'.format(user))
        user_data=[]
        json_obj=self._get_user_data(user=user)
        done=self._update_user_data(user,user_data,json_obj,limit=n_posts)
        while json_obj['cursor']['hasNext'] and not done:
            nextval=self.get_next_val(json_obj)
            json_obj=self._get_user_data(user=user,cursor=nextval)
            done=self._update_user_data(user,user_data,json_obj,limit=n_posts)
        return self._write_user_data(user,user_data)
