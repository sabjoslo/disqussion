The collector module provides support for retrieving raw post data. The user may want to configure either of the two global variables:
- `FORUM` is the forum from which data is retrieved. Defaults to 'breitbartproduction'.
- `include_` is a list of strings that identify the kinds of posts to query for in GET posts requests. Defaults to ['unapproved','approved','flagged','highlighted'].

The APIBind object is a wrapper for functions that make specialized GET requests to the API.
#####Example:
```
from collector import APIBind
api_bind=APIBind(wait=True)
```
#####Parameters:
- `wait` (bool): If False, the object will throw an Exception if it is asked to query the API but the user has exceeded her rate limit (1000 queries per hour). If True, the object will sleep until the rate limit resets (on the hour). Defaults to False.

####APIBind().get_data(resource, output_type, **kwargs)
Returns the JSON-formatted response to a query of a given output_type from a given resource*. **kwargs contains any additional query parameters.
*https://disqus.com/api/docs/requests/

#####Example
```
api_bind.get_data(resource='threads', output_type='listPosts', thread='6089609724', since='2017-08-23T15:19:00', order='asc', include=include_, limit=100, forum=FORUM)
```
This will return a JSON object containing up to 100 posts in chronologically ascending order (earliest to most recent) on thread 6089609724 on `FORUM` that were made since 3:19 PM on August 23rd, 2017.

#####Parameters
- `resource` (str): Identifies the resource path of the data queried. Examples are 'forums', 'threads', 'trends' and 'users'.
- `output_type` (str): Identifies the output type of the data queried. Examples are 'listThreads' and 'listPosts'.

Any other field that the API accepts as a parameter for the specified resource/output_type pair can also be passed as an argument.

N.B. You do need to pass your API key as an argument. If your environment is correctly configured, it will be automatically included in all your queries (see README.md).

####APIBind().get_thread_data(trending=True, n_threads=100)
Returns the JSON-formatted result of a query where output_type=='listThreads' and resource in ('forums', 'trends').

#####Example
```
api_bind.get_thread_data(trending=False,  n_threads=10)
```

#####Parameters
- `trending` (bool): If True, will formulate query with resource=='trends' (i.e. return data on threads trending in `FORUM`). If False, will formulate query with resource=='forums' (i.e. return data on all threads in `FORUM`). Defaults to True.
- `n_threads` (int): The maximum number of threads to retrieve (maximum is 100). If trending is True and n_threads > 10 it will be automatically adjusted to 10. Defaults to 100.

####APIBind().get_thread_ids(trending=True, n_threads=100)
Performs the same queries as APIBind().get_thread_data, but returns a list of thread IDs instead of the entire JSON-formatted API response.

####APIBind().get_post_data(thread, user, timestamp, id_=None, window=3600, keep_anonymous=True)
Retrieves data on posts to a thread that were created in given a window of time. Writes all retrieved data to a tsv file defined in `utils.getThreadFile`. Each row in the written file corresponds to a unique post.

#####Example
```
api_bind.get_post_data(thread='6089609724', user='244483491', timestamp='2017-08-23T16:02:00', id_='qwer', window=600, keep_anonymous=False)
```
This will retrieve all posts on thread 6089609724 made between 3:52 PM and 4:12 PM on August 23rd, 2017 and save the data in a directory called 244483491 (see the section on the architecture of the working environment in the README file).

#####Parameters
- `thread` (str): The thread to retrieve posts from.
- `user` (str): The user whose directory to store the data in.
- `timestamp` (ISO 8601 timestamp; str): The window of time from which to collect data is centered at `timestamp`.
- `id_` (str): The unique id used to name the data files. Defaults to a random string.
- `window` (int): Retrieve posts from this number of seconds BEFORE `timestamp` until this number of seconds AFTER `timestamp`. Defaults to 3600 seconds or one hour.
- `keep_anonymous` (bool): If set to True, posts by anonymous users will be recored with a user ID 'N/A'. Else, they will be discarded. Defaults to True.

####APIBind().get_user_ids(thread=None, n=100, overwrite=False)
Retrieve and save to a file (`USERS_FILE`) a list of the n users to most recently comment on a given thread. The name of `USERS_FILE` can be customized in config.py.

#####Example
```
api_bind.get_user_ids(thread='6089609724', n=100, overwrite=True)
```

#####Parameters
- `thread` (str): Fetch n unique commenters on this thread. Defaults to the most recent trending thread.
- `n` (int): The number of unique users to fetch. Defaults to 100.
- `overwrite` (bool): If True, the file will be wiped and n new users fetched. Default behaviour appends user ids to existing user ids contained in `USERS_FILE` until the list contains n user ids.

####APIBind().get_posts_for_one_user(user=None, n_posts=None, n_users=100, overwrite=False)
Writes a JSON object of posts made by `user` to a file specified by `utils.getUserFile`. Returns the user id of the user for which posts were retrieved, and the unique id appended to the written file.

#####Example
```
api_bind.get_user_data(user='244483491', n_posts=100, n_users=100, overwrite=True)
```

#####Parameters
- `user` (str): Retrieve posts by this user. If unspecified, call `self.get_user_ids` and choose a user from `USERS_FILE`. In this event, `n_users` and `overwrite` are passed as arguments `n` and `overwrite` respectively to `self.get_user_ids`.
- `n_posts` (int): Retrieve `user`&#39;s `n_posts` most recent posts. Defaults to all posts `user` has made.
