The classifier object provides support to:
- Take a given tsv file and categorize its contents based on the value of a specified column, and
- Rewrite the contents of the file to two output files based on this categorization.
#####Example
```
from core import classifier
userClassifier=classifier(input_='244483491/6089609724-qwer.tsv', output=('244483491/this-qwer.tsv','244483491/context-qwer.tsv'))
```

#####Parameters
- `input_` (str, existing file name): Classify the contents of this file.
- `output_` (tuple of str objects, each a file name): `output_` contains a `this` file name and a `context` file name, respectively. When classifying, observations that match `by_val` (see `classifier().classify`) will be written in the `this` file and all others will be written in the `context` file.

####classifier().classify(by, by_val, column, overwrite=False)
Classify line-by-line observations in `input_` and write classified observations to `output_`.

#####Example
```
userClassifier.classify(by='USER', by_val='244483491', column='TEXT')
```
This will write posts made on thread 6089609724 by user 244483491 to 244483491/this-qwer.tsv and other posts made on the thread to 244483491/context-qwer.tsv.

#####Parameters
- `by` (str; one of `config.COL_KEYS`): The column if `input_` to look in for `by_val`.
- `by_val`: For any line of `input_`, if the value in column `by` matches `by_val`; classify the observation as `this`; else, classify as `context`.
- `column` (str; one of `config.COL_KEYS`): Write this column of `input_` to `output_`.
