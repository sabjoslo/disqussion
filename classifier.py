import os
from wordplay.core import sentences
from utils import *

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
