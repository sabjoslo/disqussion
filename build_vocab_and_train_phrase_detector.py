"""
Used to generate vocab.txt.bz2 and example_phrase_model."""

from wordplay.core import token_distributions
from collector import APIBind
from classifier import classifier
from config import *
from utils import *
from vocabulary import reset_vocab,train_phrase_detector

api_bind=APIBind(wait=True)

for i in range(3):
    for j in range(3):
        user,id_=api_bind.get_posts_for_one_user(n_posts=100,n_users=1,
                                                 overwrite=True)
        for thread,timestamp in getAllThreadsByUser(user,id_):
            api_bind.get_post_data(thread=thread,user=user,timestamp=timestamp,id_=id_
                                )
        this_prefix='{}/this-{}'.format(user,id_)
        context_prefix='{}/context-{}'.format(user,id_)
        for thread in getAllThreadFiles(user,id_):
            userClassifier=classifier(input_=thread,
                                    output_=('{}.tsv'.format(this_prefix),
                                            '{}.tsv'.format(context_prefix)
                                            )
                                    )
            userClassifier.classify('USER',user,'TEXT')
        this_dist=token_distributions(files='{}.tsv'.format(this_prefix))
        this_dist.build_corpus()
        this_dist.save_corpus('{}_corpus'.format(this_prefix))
        context_dist=token_distributions(files='{}.tsv'.format(context_prefix))
        context_dist.build_corpus()
        context_dist.save_corpus('{}_corpus'.format(context_prefix))

    reset_vocab()

    for j in range(3):
        train_phrase_detector('example_phrase_model')
