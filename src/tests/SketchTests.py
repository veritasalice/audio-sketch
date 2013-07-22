'''
Created on Jan 31, 2013

@author: manu
'''
import unittest
import sys
sys.path.append('/home/manu/workspace/audio-sketch')
sys.path.append('/home/manu/workspace/PyMP')
sys.path.append('/home/manu/workspace/meeg_denoise')

from classes import sketch
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
audio_test_file = '/sons/jingles/panzani.wav'

class SketchTest(unittest.TestCase):

    def runTest(self):
                
        abstractSketch = sketch.AudioSketch()
        print abstractSketch
        self.assertRaises(NotImplementedError,abstractSketch.represent)
        self.assertRaises(NotImplementedError,abstractSketch.recompute)
        self.assertRaises(NotImplementedError,abstractSketch.sparsify, (0))
        self.assertRaises(NotImplementedError,abstractSketch.synthesize, ({}))
        
#        kwargs = {'scale':512, 'step':256}
#        stftpeaksketch = sketch.STFTPeaksSketch(**kwargs)
#        
#        kwargs = {'dico':[64,512,2048], 'n_atoms':100}
#        xmdctmpsketch = sketch.XMDCTSparseSketch()
        learned_base_dir = '/home/manu/workspace/audio-sketch/matlab/'
        
        sketches_to_test = [
#                            sketch.KNNSketch(**{'location':learned_base_dir,
#                                                'shuffle':87,
#                                                'n_frames':100000,
#                                                'n_neighbs':1}),
#                            sketch.SWSSketch(),
#                            sketch.CorticoIHTSketch(**{'downsample':8000,'frmlen':8,'shift':0,'fac':-2,'BP':1,'max_iter':1,'n_inv_iter':5}),
#                            sketch.CochleoIHTSketch(**{'downsample':8000,'frmlen':16,'shift':-1,'max_iter':1,'n_inv_iter':5}),
#                            sketch.CochleoPeaksSketch(),   
                            sketch.CorticoPeaksSketch(**{'downsample':8000,'frmlen':8,'shift':0,'fac':-2,'BP':1}),                         
#                            sketch.XMDCTSparseSketch(**{'scales':[64,512,2048], 'n_atoms':100}),
#                           NOT FINISHED
#                           sketch.WaveletSparseSketch(**{'wavelets':[('db8',6),], 'n_atoms':100}),
#                            sketch.STFTPeaksSketch(**{'scale':2048, 'step':256}),
#                            sketch.STFTDumbPeaksSketch(**{'scale':2048, 'step':256}),              
                            ]
        
        # for all sketches, we performe the same testing
        for sk in sketches_to_test:
            print sk
            self.assertRaises(ValueError, sk.recompute)
            
            print "%s : compute full representation"%sk.__class__
            sk.recompute(audio_test_file)
            
            print "%s : plot the computed full representation" %sk.__class__
            sk.represent()
            
            print "%s : Now sparsify with 1000 elements"%sk.__class__
            sk.sparsify(1000)                    
            
            print "%s : plot the sparsified representation"%sk.__class__
            sk.represent(sparse=True)
            plt.title(sk.__class__)
            
            print "%s : Synthesize the sketch"%sk.__class__
            synth_sig = sk.synthesize(sparse=True)
            
            plt.figure()
            plt.subplot(211)
            plt.plot(sk.orig_signal.data)
            plt.subplot(212)
            plt.plot(synth_sig.data)
            
            
#            synth_sig.play()
            synth_sig.write('Test_%s_%s.wav'%(sk.__class__.__name__,sk.get_sig()))

if __name__ == "__main__":
    
    suite = unittest.TestSuite()

    suite.addTest(SketchTest())

    unittest.TextTestRunner(verbosity=2).run(suite)
    plt.show()
    