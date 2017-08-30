from __future__ import division

import logging
import math
import numpy as np
import os
import pandas as pd
import re
import string
from bs4 import BeautifulSoup
from gensim.models import Word2Vec
from gensim.models.phrases import Phraser, Phrases
from nltk import FreqDist, MLEProbDist
import spacy
tokenizer=spacy.load('en_core_web_sm')
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords
stopwords=set(stopwords)
stopwords.add('s') # Leftover from "'s" after punctuation is stripped.
from config import *
from utils import *

class Vector():
    def __init__(self,index,data,columns=None):
        if not hasattr(columns,'__iter__'):
            columns=[columns]
        self.df=pd.DataFrame(data, index=index, columns=columns)

    def partial_kl(self,q,which,column=None):  
        assert hasattr(q,'df')
        if isinstance(column,type(None)):
            assert len(self.df.columns)==len(q.df.columns)==1
            assert self.df.columns==q.df.columns
            column=self.df.columns[0]
        p_i=self.df.loc[which][column]
        q_i=q.df.loc[which][column]
        return p_i*math.log(2*p_i/(p_i+q_i))

class sentences():
    """A handler to generate tokens from the words in a tsv file.
    """

    def __init__(self, phrase_model=None):
        startLog()

        # Initialize phrase-detector
        self.phrases=self.get_phraser(fn=phrase_model)
        self.phraser=Phraser(self.phrases)

    # Declare and initialize handler for tsv file to be read from.
    def open_file(self,fn,column=None):
        self.fn=open(fn,'r')
        self.headers=self.fn.readline().strip('\n').split('\t')
        # Reset file handler's line count
        self.fn.seek(0)
        self.column=column

    def close_file(self):
        self.fn.close()

    # Generates "sentences" from the tsv file of the form sentence =
    # [['word0','word1','word2'],['word3','word4','word5']]. The class
    # attribute column specifies the column of the file to be read from.
    # If training is set to True, sentences will be passed to the class's
    # phrase-detection model to train it to generate phrasegrams.
    def tokens_from_tsv(self):
        self.fn.seek(0)
        
        # Discard header row
        self.fn.readline()
        assert self.column in self.headers
        col_ix=self.headers.index(self.column)
        line=self.fn.readline().split('\t')
        while any([ l.strip() for l in line ]):
            yield self.tokenize_(to_ascii(line[col_ix].strip()))
            line=self.fn.readline().split('\t')

    def tokens_from_plain_text(self,training=False):
        self.fn.seek(0)
        line=self.fn.readline()
        while line.strip():
            yield self.tokenize_(to_ascii(line.strip()),training=training)
            line=self.fn.readline()

    def __iter__(self):
        return self.tokens_from_plain_text()

    # Generate and remove extraneous punctuation from tokens. If training =
    # True, tokens are used to train a phrase-detection model.
    def tokenize_(self,sentence,training=False):
        # Much of this taken from 
        # https://www.analyticsvidhya.com/blog/2017/04/natural-language-processing-made-easy-using-spacy-%e2%80%8bin-python/

        # Remove HTML
        sentence=BeautifulSoup(sentence, "html5lib").get_text()

        # Return the lemma of each token. Exclude pronouns, stopwords and
        # punctuation.
        words=tokenizer(sentence)
        lemmas=[ word.lemma_ for word in words if word.lemma_ != '-PRON-' ]
        no_punc=[ re.sub('[{}]'.format(string.punctuation),'',lemma) for
                  lemma in lemmas ]
        tokens=[ token for token in no_punc if ( token not in stopwords and
                 token.strip() )]

        if training:
            # Add new words to phrase-detector
            self.phrases.add_vocab([tokens])

        return self.phraser[tokens]

    # Look for a phrase detection model saved at path fn. If not found or fn
    # is None, return an untrained phrase detection model.
    def get_phraser(self,fn=None):
        if isinstance(fn,type(None)):
            return Phrases()
        if os.path.exists(fn):
            logging.info('Found {}. Loading phrase detection model.\
                         '.format(fn))
            return Phrases().load(fn)
        else:
            logging.info('Can\'t find {}. Loading empty phrase detection model.\
                         '.format(fn))
            return Phrases()

    def train_phrase_detector(self,fn=None):
        for sentence in self.tokens_from_plain_text(training=True):
            pass

    def save_phrase_model(self,fn):
        self.phrases.save(fn)

class classifier(sentences):
    """Take a given tsv file, and categorize its contents based on the
    value of a specified column. Write its contents to two output files
    based on this categorization.
    """

    def __init__(self,input_,output_=('this.tsv','context.tsv')):
        self.open_file(input_)
        self.input_=self.fn
        assert self.input_.name==self.fn.name==input_
        assert hasattr(output_,'__iter__'), 'output_ must be an iterable.'
        self.output_=dict(zip(('this','context'),output_))

    def _dump(self,fh,obs,content):
        fh.write('{}\t{}'.format(obs,content))

    def classify(self,by,by_val,column,overwrite=False):
        self.fn.seek(0)

        # Discard header row
        self.fn.readline()

        by,column=getColumnLabel(by),getColumnLabel(column)
        assert by in self.headers and column in self.headers
        by_ix=self.headers.index(by)
        fileWriteMode='w' if overwrite else 'a'
        
        # Detect if output files have already been written to
        new_file=dict()
        for fn in self.output_.values():
            if not os.path.exists(fn):
                new_file[fn]=True
                continue
            f=os.popen('cat {}'.format(fn))
            if len(f.read().strip())==0:
                new_file[fn]=True
            else:
                new_file[fn]=False
            f.close()
        thisFh=open(self.output_['this'],fileWriteMode)
        contextFh=open(self.output_['context'],fileWriteMode)
        for fh in [ thisFh,contextFh ]:
            if new_file[fh.name]:
                fh.write('{}\t{}\n'.format(by,column))
        col_ix=self.headers.index(column)
        line=self.fn.readline().split('\t')
        while any([ l.strip() for l in line ]):
            obs=line[by_ix]
            if obs==by_val:
                self._dump(thisFh,obs,line[col_ix])
            else:
                self._dump(contextFh,obs,line[col_ix])
            line=self.fn.readline().split('\t')
        for fh in [ thisFh,contextFh ]:
            fh.close()

class token_distributions():
    def __init__(self,corpus=None,files=None,phrase_model=None,
                 column='TEXT'):
        assert ( not isinstance(corpus,type(None)) or 
                 not isinstance(files,type(None)) )
        if not isinstance(corpus,type(None)):
            self.load_corpus(corpus)
        if isinstance(files,basestring):
            self.files=[files]
        else:
            self.files=files
        self.set_phrase_model(phrase_model)
        assert column in COL_KEYS
        self.column=getColumnLabel(column)

    def set_phrase_model(self,phrase_model=None):
        self.filehandler=sentences(phrase_model=phrase_model)
       
    def build_corpus(self):
        self.corpus=[]
        for f in self.files:
            self.filehandler.open_file(f,self.column)
            for sentence in self.filehandler.tokens_from_tsv():
                self.corpus.append(sentence)
            self.filehandler.close_file()

    # Save this instance's corpus to disk so it can be quickly accessed
    # later. The file is saved in plain text, with words separated by a 
    # space and sentences separated by a new line. It is by default saved in
    # VOCAB_DIR and is included in the package's recognized vocabulary.
    def save_corpus(self,fn,add_to_vocab=True):
        if add_to_vocab:
            from vocabulary import VOCAB_DIR
            fn=getRelPath(VOCAB_DIR+fn)
        os.system('mkdir -p {}'.format(os.path.dirname(fn)))
        fh=open(fn,'w')
        logging.info('Writing to {}.'.format(fn))
        fh.write('\n'.join([ ' '.join(s) for s in self.corpus ]))
        fh.close()

    # Load a saved corpus. Set from_vocab to False if fn is not stored in
    # VOCAB_DIR (default).
    def load_corpus(self,fn,from_vocab=True):
        if from_vocab:
            from vocabulary import VOCAB_DIR
            fn=getRelPath(VOCAB_DIR+fn)
        fh=open(fn,'r')
        logging.info('Reading from {}.'.format(fn))
        self.corpus=[ s.split() for s in fh.read().split('\n') ]
        fh.close()

    def calculate_freq_dist(self):
        self.freq_dist=FreqDist()
        for token in [ t for tokens in self.corpus for t in tokens ]:
            self.freq_dist[token]+=1

    def estimate_prob_dist(self):
        self.prob_dist=MLEProbDist(self.freq_dist)

    def get_vector(self,vocab=None):
        if isinstance(vocab,type(None)):
            vocab=self.prob_dist.samples()
        assert hasattr(vocab, 'index')
        data_=map(lambda x:self.prob_dist.prob(x) if x in
                  self.prob_dist.samples() else np.nan,
                  vocab)
        self.vector=Vector(index=vocab, data=data_, columns='est_prob')

if __name__=='__main__':
    pass
