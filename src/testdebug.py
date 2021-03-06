# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 11:05:18 2013

@author: loa-guest
"""

import unittest
import sys
import os
import sys, os
sys.path.append(os.environ['SKETCH_ROOT'])
import src.classes.sketches.base as base
import src.classes.sketches.bench as bench
import src.classes.sketches.misc as misc
import src.classes.sketches.cochleo as cochleo
import src.classes.sketches.cortico as cortico
from src.tools import cochleo_tools 
import matplotlib.pyplot as plt
import profile

#plt.switch_backend('Agg')
SND_DB_PATH = os.environ['SND_DB_PATH']
audio_test_file = os.path.join(SND_DB_PATH,'jingles/panzani.wav')
#audio_test_file  = '/Users/loa-guest/Documents/Laure/libs/PyMP/data/ClocheB.wav'
#signal = Signal(son, normalize=True, mono=True)
#class SketchTest(unittest.TestCase):
#
#    def runTest(self):
#                
#        abstractSketch = base.AudioSketch()
#        print abstractSketch
#        self.assertRaises(NotImplementedError,abstractSketch.represent)
#        self.assertRaises(NotImplementedError,abstractSketch.recompute)
#        self.assertRaises(NotImplementedError,abstractSketch.sparsify, (0))
#        self.assertRaises(NotImplementedError,abstractSketch.synthesize, ({}))
        
#        kwargs = {'scale':512, 'step':256}
#        stftpeaksketch = sketch.STFTPeaksSketch(**kwargs)
#        
#        kwargs = {'dico':[64,512,2048], 'n_atoms':100}
#        xmdctmpsketch = sketch.XMDCTSparseSketch()
        #learned_base_dir = '/home/manu/workspace/audio-sketch/matlab/'
        
#        sketches_to_test = [
#                            misc.KNNSketch(**{'location':learned_base_dir,
#                                                'shuffle':87,
#                                                'n_frames':100000,
#                                                'n_neighbs':1}),
#                            misc.SWSSketch(),
#                            cortico.CorticoIHTSketch(**{'downsample':8000,'frmlen':8,'shift':0,'fac':-2,'BP':1,'max_iter':1,'n_inv_iter':5}),
#sk1 = cochleo.CochleoIHTSketch(**{'downsample':8000,'frmlen':8,'shift':-1,'max_iter':5,'n_inv_iter':2})
#sk2 = cochleo.CochleoPeaksSketch(**{'fs':8000})
                           #cortico.CorticoIndepSubPeaksSketch(**{'downsample':8000,'frmlen':8,'shift':0,'fac':-2,'BP':1}),   
#sk2 = cortico.CorticoPeaksSketch(**{'downsample':8000,'frmlen':8,'shift':-1,'fac':-2,'BP':1})
#sk1 = cortico.CorticoPeaksSketch(**{'n_octave':6,'freq_min':101.0, 'bins':12.0, 'downsample':8000, 'max_iter':5, 'rep_class': cochleo_tools.Quorticogram})
#                            cortico.CorticoSubPeaksSketch(**{'downsample':8000,
#                                                             'sub_slice':(0,6),'n_inv_iter':10}),
#                            cortico.CorticoSubPeaksSketch(**{'downsample':8000,
#                                                             'sub_slice':(0,11),'n_inv_iter':10}),
#                            cortico.CorticoSubPeaksSketch(**{'downsample':8000,
#                                                             'sub_slice':(4,6),'n_inv_iter':10}),
#                            cortico.CorticoSubPeaksSketch(**{'downsample':8000,
#                                                             'sub_slice':(4,11),'n_inv_iter':10})
#                                                     
#                            bench.XMDCTSparseSketch(**{'scales':[64,512,2048], 'n_atoms':100}),
#                           NOT FINISHED
#                           sketch.WaveletSparseSketch(**{'wavelets':[('db8',6),], 'n_atoms':100}),
                            #bench.STFTPeaksSketch(**{'scale':2048, 'step':256}),
                            #bench.STFTDumbPeaksSketch(**{'scale':2048, 'step':256}),  
#sk2 = bench.CQTPeaksSketch(**{'n_octave':7,'freq_min':101.0, 'bins':36.0, 'downsample':8000})    
#sk2 = bench.cqtIHTSketch(**{'n_octave':7,'freq_min':101.0, 'bins':36.0, 'downsample':8000, 'max_iter':5})
sk = bench.cqtIHTSketch(**{'n_octave':5,'freq_min':101.0, 'bins':12.0,
                           'downsample':8000, 'max_iter':5,'fen_type':1})
sk.recompute(audio_test_file)
import time
t = time.time()
sk.sparsify(200)
print "Without profiling:",time.time()-t
sk.represent(sparse = True)
plt.show()
#sk2 = bench.CQTPeaksSketch(**{'n_octave':5,'freq_min':101.0, 'bins':12.0,'downsample':8000})
#sk2.recompute(audio_test_file)
                            #]
        
        # for all sketches, we performe the same testing
            
#print "%s : compute full representation"%sk1.__class__
#sk11 = sk1.recompute(audio_test_file)
#sk22 = sk2.recompute(audio_test_file)
#print "%s : plot the computed full representation" %sk1.__class__
#sk1.represent()
#sk2.represent()
#            
#            print "%s : Now sparsify with 1000 elements"%sk.__class__
#            sk.sparsify(200)                    
##            
#            print "%s : plot the sparsified representation"%sk.__class__
#            sk.represent(sparse=True)
#            plt.title(sk.__class__)
        
        # Remove the original signal
#            sk.orig_signal = None 
        
        #print "%s : Synthesize the sketch"%sk.__class__
            #synth_sig = sk.synthesize(sparse=True)
            
            #plt.figure()
#            plt.subplot(211)
#            plt.plot(sk.orig_signal.data)
#            plt.subplot(212)
            #plt.plot(synth_sig.data)
            
            
#            synth_sig.play()
            #synth_sig.write('Test_%s_%s.wav'%(sk.__class__.__name__,sk.get_sig()))

#if __name__ == "__main__":
#    
#    suite = unittest.TestSuite()
#
#    suite.addTest(SketchTest())
#
#    unittest.TextTestRunner(verbosity=2).run(suite)
#    plt.show()
    
profile.runctx('sk.sparsify(200)',globals(),locals())
#profile.runctx('sk2.sparsify(200)',globals(),locals())