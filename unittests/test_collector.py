"""For use with pytest
"""

import json
import os
import time
from wordplay.utils import *
import collector
from collector import INCLUDE
from config import *
from utils import *
collector.USERS_FILE='test{}'.format(collector.USERS_FILE)

api_bind=collector.APIBind()

def test_format_request():
    kwargs=dict(user='01',include=INCLUDE,limit=100)
    request_args=[]
    for k,v in kwargs.items():
        if k=='include':
            for v_ in v:
                request_args.append((k,v_))
        else:
            request_args.append((k,v))
    req=api_bind._format_request(resource='users',output_type='listPosts',
                                 **kwargs)
    ans='{url}{resource}/{o_t}.json?{joined_str}&api_key={key}'.format(
                                                  url=api_bind.BASE_URL,
                                                  resource='users',
                                                  o_t='listPosts',
                                                  joined_str='&'.join([
                                                        '{}={}'.format(k,v)
                                                        for k,v in
                                                        request_args ]),
                                                  key=getPublicKey()
                                                 )
    assert req==ans

def test_get_thread_and_user_data():
    # Test getting trending posts
    threads=api_bind.get_thread_ids()
    assert len(threads)==10
    assert len(set(threads))==len(threads)

    thread=threads[0]
    # Test get_user_ids
    users=api_bind.get_user_ids(thread=thread,n=10)
    assert len(users)==10
    assert len(set(users))==len(users)
    assert collector.USERS_FILE in os.listdir(os.getcwd())
    with open(collector.USERS_FILE,'r') as fh:
        users_=[ l for l in fh.read().split('\n') if l.strip() ]
        assert set(users_)==set(users)
    
    user=users[0]

    # Test _update_user_data
    user_data=[]
    json_obj=api_bind._get_user_data(user=user)
    api_bind._update_user_data(user,user_data,json_obj)
    assert len(user_data)>0

    user_,id_=api_bind.get_posts_for_one_user(user=user)
    fn,id_=getUserFile(user,id_)
    with open(fn,'r') as fh:
        json_obj=json.loads(fh.read())
    threads_=[ dict_['thread'] for dict_ in json_obj ]
    assert thread in threads_

    os.system('rm {}'.format(collector.USERS_FILE))

def test_get_post_data():
    test_data=[{"thread":"598856823","createdAt":"2012-03-06T00:00:55"},{"thread":"598873202","createdAt":"2012-03-05T21:34:11"}]
    user='xyz'
    os.system('mkdir -p {}'.format(WORKING_DIR+user))
    fn,id_=getUserFile(user)
    test_file=open(fn,'w')
    json.dump(test_data,test_file)
    test_file.close()

    for ix in (0,1):
        kwargs=test_data[ix]
        kwargs['timestamp']=kwargs['createdAt']
        del kwargs['createdAt']
        kwargs['id_'],kwargs['user']=id_,user
        api_bind.get_post_data(**kwargs)
        thread_file=getThreadFile(kwargs['thread'],user=user,id_=id_)
        assert os.path.exists(thread_file)
        with open(thread_file,'r') as fh:
            headers=fh.readline().strip().split('\t')
            timestamp_ix=getEntryIndex(headers,'TIMESTAMP')
            ctime=iso8601_to_unix(kwargs['timestamp'])
            prev_time=0
            line=fh.readline().strip()
            while line.strip():
                timestamp=line.strip().split('\t')[timestamp_ix]
                ttime=iso8601_to_unix(timestamp)
                assert abs(ttime-ctime)<3600
                assert ttime>prev_time
                prev_time=ttime
                line=fh.readline().strip()
            assert prev_time>ctime

    os.system('rm -rf {}'.format(WORKING_DIR+user))
