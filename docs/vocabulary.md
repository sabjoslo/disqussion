Functions used to manage the package&#39;s recognized vocabulary. This is basically construed as a set of all the tokens in individual files in `VOCAB_DIR`. The module makes a few assumptions:
- `VOCAB_DIR` contains only directories.
- These directories contain files containing tokens to be included in the package&#39;s recognized vocabulary.
- The tokens are written in plain text and separated only by spaces or new line characters.
This is consistent with the intention that the files in `VOCAB_DIR` be corpi saved from instances of `core.token_distributions` in a directory named after the relevant user id, as in `sample.py`. For example:
```
$ ls $VOCAB_DIR
90608246
$ ls $VOCAB_DIR/90608246
context-shtw_corpus
this-shtw_corpus
$ head $VOCAB_DIR/90608246/context-shtw_corpus
know dog
hear self sacrifice save planet know wanna
total bs lot diet come grain abundance meat byproduct scrap process pet food live home heat cool
happen away hollywierdos dog real psychotic episode
nice
kill puppy save planetstart animal kingdom work way human extermination far crazy bastids
fair warning abuse animal presence viciously attack exception
delingpole kill puppy save planet study warn pets cause global warminggreat idea peta war tree hugger
question just taxpayer money spend study money come publish raw datum sick tired pay tax poop authorize expense bleed money earn eat hamburger afford pay california crazy high tax rid high learning parasite
just kill kid little schnauzer border collie black lab belong gon na let critter destroy planet
```

####reset_vocab()
Set the contents of `VOCAB_FILE` equal to the union of the sets of tokens found in all files in `VOCAB_DIR`.

####get_vocab()
Return as a list the contents of `VOCAB_FILE`.

####train_phrase_detector(model_name)
Train the phrase model stored in a file called `model_name` using the contents of the files in `VOCAB_DIR`. This model can then be passed to an instance of core.token_distributions to identify n>1-grams when creating the instance&#39;s corpus.

If `model_name` refers to an existing model, this model will continue to be trained. Otherwise, a new model will be created with one round of training.
