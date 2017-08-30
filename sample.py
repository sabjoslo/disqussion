#!/usr/bin/python
if __name__=='__main__':
    refresh=False

    from collector import request
    api_bind=request(wait=True)

    # Save a list of n users from a recently-trending post to a file
    # user.txt, save data for all the posts made by one of these users.
    user,id_=api_bind.get_posts_for_one_user(n_posts=100,overwrite=refresh)

    # For this user, for each thread in their data file, get the posts of
    # all other users
    from utils import getAllThreadsByUser
    for thread,timestamp in getAllThreadsByUser(user,id_):
            api_bind.get_post_data(thread=thread,user=user,
                                   timestamp=timestamp,id_=id_)

    # Categorize the rows in these thread data files based on if they were
    # posted by the specified user or not. Write two new tsv files: this.tsv
    # will contain all the posts written by the specified user, and
    # context.tsv will contain all the posts written by anyone else.
    from core import classifier
    from utils import getAllThreadFiles

    this_prefix='{}/this-{}'.format(user,id_)
    context_prefix='{}/context-{}'.format(user,id_)

    for thread in getAllThreadFiles(user,id_):
        userClassifier=classifier(input_=thread,
                                  output_=('{}.tsv'.format(this_prefix),
                                           '{}.tsv'.format(context_prefix)
                                          )
                                 )
        userClassifier.classify('USER',user,'TEXT')

    # Create probability distributions of the tokens in the 'Message' column
    # of this.tsv and context.tsv, respectively.

    # Create an object to access the frequency and probability
    # distributions of the tokens in this.tsv. Use the (pre-trained) phrase-
    # detection model 'example_phrase_model' to generate phrasegrams as 
    # tokens. This model can be generated using core.sentences (see the docs
    # for that model on how to do this).

    from core import token_distributions
    this_dist=token_distributions(files='{}.tsv'.format(this_prefix),
                                  phrase_model='example_phrase_model')

    # Add all the tokens in this.tsv to the object's corpus.
    this_dist.build_corpus()
    # Once the corpus is built, save it to disk for easy reuse.
    this_dist.save_corpus('{}_corpus'.format(this_prefix))
    tmp=this_dist.corpus
    this_dist.load_corpus('{}_corpus'.format(this_prefix))
    # Or just pass the path of the saved corpus when initializing a new
    # instance
    # E.g. this_dist=token_distributions(corpus='this_corpus')
    assert tmp==this_dist.corpus
    del tmp

    # Create a corpus based on context.tsv.
    context_dist=token_distributions(files='{}.tsv'.format(context_prefix),
                                     phrase_model='example_phrase_model')
    context_dist.build_corpus()
    context_dist.save_corpus('{}_corpus'.format(context_prefix))

    # Now there are two new plain text files saved in a folder called VOCAB 
    # on disk. We can use the contents of these files to build a set of 
    # vocabulary that can be gradually added to, used to train models and 
    # serve as a common vocabulary for later analysis.
    from vocabulary import reset_vocab
    reset_vocab()

    # We can also use the new corpi to train and save a new phrase-detection
    # model. This model identifies likely phrasegrams (">1-grams") that can
    # be included in later token extraction tasks. For example, if the model
    # is specified when rerun on this_dist and context_dist, corpi including
    # the phrasegrams will overwrite the existing corpi.
    from vocabulary import train_phrase_detector
    train_phrase_detector('example_phrase_model')

    # See the phrasegrams
    from gensim.models.phrases import Phrases, Phraser
    Phraser(Phrases().load('example_phrase_model')).phrasegrams
    
    # Reset the phrase model
    this_dist.set_phrase_model('example_phrase_model')
    context_dist.set_phrase_model('example_phrase_model')

    # Rebuild and resave the corpi in order to incorporate the new 
    # phrasegrams
    this_dist.build_corpus()
    this_dist.save_corpus('{}_corpus'.format(this_prefix))
    context_dist.build_corpus()
    context_dist.save_corpus('{}_corpus'.format(context_prefix))

    # Calculate the frequency distribution.
    this_dist.calculate_freq_dist()
    this_dist.freq_dist['word']

    # Estimate the probability distribution using a MLE strategy
    this_dist.estimate_prob_dist()
    this_dist.prob_dist.prob('word')
    assert this_dist.prob_dist.prob('word')==this_dist.freq_dist.freq('word')

    # And do it all over again for context.tsv.
    context_dist.calculate_freq_dist()
    context_dist.estimate_prob_dist()
    context_dist.prob_dist.prob('word')

    # Create a vector representation of these probability distributions
    # First, establish the vocabulary set that will be used to index the
    # vectors (so that the nth element of both vectors corresponds to the
    # same word). The vocabulary built earlier can be used for this.
    # First, reset the vocabulary so it's consistent with the tokens used to
    # create the frequency/probability distributions.
    reset_vocab()
    from vocabulary import get_vocab
    vocab=get_vocab()
    this_dist.get_vector(vocab)
    context_dist.get_vector(vocab)

    print this_dist.vector.partial_kl(context_dist.vector,'america')
