"""Functions used to manage the package's recognized vocabulary.
"""

import os
from wordplay.core import sentences
from config import *
from utils import *

# Set the contents of VOCAB_FILE equal to the union of the sets of tokens 
# found in all files in VOCAB_DIR
def reset_vocab():
    vdir=getRelPath(VOCAB_DIR)
    vfile=getRelPath(VOCAB_FILE)

    vocab=set()
    for dir_ in os.listdir(vdir):
        if dir_=='.DS_Store':
            continue
        for fn in os.listdir(vdir+dir_):
            with open(vdir+dir_+'/'+fn,'r') as fh:
                for sentence in fh.read().split('\n'):
                    for token in sentence.split():
                        vocab.add(token)
    with open(vfile,'w') as fh:
        fh.write(' '.join(list(vocab)))
    zip_(vfile)

def get_vocab():
    vfile=getRelPath(VOCAB_FILE)

    unzip_(vfile)
    with open(vfile,'r') as fh:
        _vocab=fh.read().split()
    zip_(vfile)
    return _vocab

def train_phrase_detector(model_name):
    vdir=getRelPath(VOCAB_DIR)

    trainer=sentences(phrase_model=model_name)
    for dir_ in os.listdir(vdir):
        if dir_=='.DS_Store':
            continue
        for fn in os.listdir(vdir+dir_):
            trainer.open_file(vdir+dir_+'/'+fn)
            trainer.train_phrase_detector()
            trainer.close_file()
    trainer.save_phrase_model(model_name)
