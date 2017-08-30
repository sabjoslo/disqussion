This library provides support for retrieving and analyzing natural language data. It is configured to retrieve data from the forum [Breitbart](www.breitbart.com) via the [Disqus API](https://disqus.com/api/docs/) ([Disqus](https://disqus.com) is a comment plug-in used by many online forums); however, it can be configured to retrieve data via any API with the same structure as the Disqus API.

For an example of how to use the library to get the partial-KL vector of a user's word usage from the other posts on a thread, see or run sample.py.

The user can configure her working environment by changing the values of various variables in config.py

####Working environment
This package is set up to organize your data files in your working directory (set in config.py) as follows:
- `USERS_FILE` (set in config.py) is in `WORKING_DIR`.
- `WORKING_DIR` also contains directories that are named with Disqus user ids. These directories are intended to store data used for analysis of individual users.
    - Post data generated from a call to `collector.request().get_posts_for_one_user` or `collector.request().get_post_data` is stored in these nested user directories (the user id is passed as an argument when making these calls).
#####Example
```
$ ls $WORKING_DIR
> users.txt 18220329 48682505 # $USERS_FILE and two user directories
$ ls $WORKING_DIR/18220329
> thread6098769032-qefa.tsv thread6098625952-qefa.tsv user18220329-qefa.json
```
