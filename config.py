# All files created by this package will be named relative to WORKING_DIR.
WORKING_DIR='./'

# Where your public API key is stored in plain text.
PUBLIC_KEY_FILE='public_key'

# Where your secret API key is stored in plain text.
SECRET_KEY_FILE='private_key'

# Where your API access token is stored in plain text.
ACCESS_TOKEN_FILE='access_token'

# What to name the file created by collector.request().get_user_ids().
USERS_FILE='users.txt'

# The directory where files containing natural language data that you want
# read in order to construct the library's set of recognized vocabulary.
VOCAB_DIR='VOCAB/'

# Where the set of recognized vocabulary should be written.
VOCAB_FILE='example_vocab.txt'

# Headers for tsv files.
COL_KEYS=['USER','PARENT','TEXT','TIMESTAMP']
COL_VALUES={'USER':{'label':'Author','var':'user'},
            'PARENT':{'label':'Parent','var':'parent'},
            'TEXT':{'label':'Message','var':'msg'},
            'TIMESTAMP':{'label':'Timestamp','var':'timestamp'}
           }
