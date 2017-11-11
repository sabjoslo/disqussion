from __future__ import division

import os
import numpy as np
from classifier import classifier
from config import *

def test_classify():
    try:
        testClassifier=classifier(input_='{}/unittests/.fake_data'.format(WORKING_DIR),
                                output_=('test_this.tsv','test_context.tsv')
                                )
        testClassifier.classify('USER','1','TEXT')
        assert ( 'test_this.tsv' in os.listdir(WORKING_DIR) and
                'test_context.tsv' in os.listdir(WORKING_DIR) ), 'Output \
                files not successfully opened in PWD.'
        with open('test_this.tsv','r') as fn:
            ans="""Author\tMessage
1\t<p>Hello, world.</p>
1\t<p>Just trying to be friendly...</p>
1\t<p>Hello again, world.</p>
"""
            assert fn.read()==ans, 'THIS output doesn\'t match.'
        with open('test_context.tsv','r') as fn:
            ans="""Author\tMessage
2\t<p>Who are you talking to?</p>
3\t<p>Thanks for trying!</p>
"""
            assert fn.read()==ans, 'CONTEXT output doesn\'t match.'
    except Exception as e:
        for fn in testClassifier.output_.values():
            os.system('rm {}'.format(fn))
        raise e

    for fn in testClassifier.output_.values():
        os.system('rm {}'.format(fn))
