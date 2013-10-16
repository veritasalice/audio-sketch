'''
manu_sandbox.sketch_objects  -  Created on Oct 15, 2013
@author: M. Moussallam
'''

import sys, os
sys.path.append(os.environ['SKETCH_ROOT'])
from src.settingup import *
from src.classes.sketches.bench import XMDCTSparseSketch
from src.manu_sandbox.pymp_objects import PenalizedMDCTDico

class XMDCTPenalizedPairsSketch(XMDCTSparseSketch):
    """ I now define my own sketch that will use my specific dictionaries 
        during the recompute process"""
    def __init__(self, original_sig=None, **kwargs):
        """ just call the superclass constructor nothing needs to be changed """
        super(XMDCTPenalizedPairsSketch, self).__init__(original_sig=None, **kwargs)
        
        # default parameters
        self.params['biaises'] = None
        self.params['Wfs'] = None
        self.params['Wts'] = None
        self.params['lambdas'] = None
        self.params['debug'] = 0
        # replace with user-provided
        for key in kwargs.keys():
            self.params[key] = kwargs[key]

        # default values: use a linear decrease in the frequencies and        
        if self.params['biaises'] is None:
            self.params['biaises'] = []            
            for s in self.params['scales']:
                self.params['biaises'].append(np.maximum(0.001,
                                                         1.0/np.linspace(1.,float(s)/2, s/2)))

        # default W: a zero matrix
        if self.params['Wfs'] is None:
            self.params['Wfs'] = []
            for s in self.params['scales']:
                self.params['Wfs'].append(np.zeros((s/2,s/2)))        

        # default lambdas = 1
        if self.params['lambdas'] is None:
            self.params['lambdas'] = len(self.params['scales'])*[1]

            

    def _get_dico(self):
        """ only difference, use a specialy designed dictionary here """
        mdct_dico = PenalizedMDCTDico(self.params['scales'],
                                      self.params['biaises'], 
                                      self.params['Wfs'],
                                      self.params['Wts'],
                                      self.params['lambdas'],
                                      debug_level=self.params['debug'])
        
        return mdct_dico
    
if __name__ == "__main__":    
    
    SND_DB_PATH = os.environ['SND_DB_PATH']
    single_test_file1 = op.join(SND_DB_PATH,'jingles/panzani.wav')
    
    sk = XMDCTPenalizedPairsSketch(**{'scales':[64,512, 4096],'n_atoms':20,'debug':2})
    
    sk.recompute(single_test_file1)
    sk.represent()
    plt.show()