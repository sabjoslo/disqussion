from __future__ import division

import os
from config import *
from core import Vector,sentences,classifier,token_distributions
from utils import *

def test_vector():
    index=['a','b','c','d','e']
    data0=[1,2,3,4,5]
    data1=[2,3,4,5,6]
    v0=Vector(index=index, data=data0, columns='est_prob')
    v1=Vector(index=index, data=data1, columns='est_prob')

    # Test format of Vector().df
    assert v0.df.columns==v1.df.columns
    assert len(v0.df.columns)==1
    column=v0.df.columns[0]
    data_=zip(data0,data1)
    for ix in range(len(index)):
        assert v0.df.loc[index[ix]][column]==data_[ix][0]
        assert v1.df.loc[index[ix]][column]==data_[ix][1]

    # Test partial_kl
    assert abs(v0.partial_kl(v1,'c')-(-0.46245203948177505))<1e-10

def test_tokenize_():
    sentence='<p>This is the user\'s test sentence.</p>'
    tokens=sentences().tokenize_(sentence)
    assert tokens==['user','test','sentence']

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

def test_token_distributions():
    testTD=token_distributions(files=getRelPath('unittests/.fake_data'))
    # Test build_corpus
    testTD.build_corpus()
    assert testTD.corpus==[ ['hello','world'],['talk'],['just','try',
                            'friendly'],['thank','try'],['hello','world']
                          ]

    # Test freq_dist
    testTD.calculate_freq_dist()
    assert set(testTD.freq_dist.keys())==set([ t for tokens in testTD.corpus
                                               for t in tokens ]) 
    assert testTD.freq_dist.values().count(1)==4
    assert testTD.freq_dist.values().count(2)==3
    assert testTD.freq_dist['hello']==2
    assert testTD.freq_dist['world']==2
    assert testTD.freq_dist['try']==2

    # Test prob_dist
    testTD.estimate_prob_dist()
    assert testTD.prob_dist.prob('hello')==2/10
