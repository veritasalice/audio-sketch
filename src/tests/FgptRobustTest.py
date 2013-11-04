'''
tests.FgptRobustTest  -  Created on Aug 29, 2013

Purpose is to evaluate the robustness to following perturbation:
- Time Shift
- White Noise
- Compression? 

@author: M. Moussallam
'''

#sys.path.append('../..')
import os
from os import chdir
chdir('/Users/loa-guest/Documents/Laure/audio-sketch')

from src.classes.sketches.base import *
from src.classes.sketches.bench import *
from src.classes.sketches.cortico import *
from src.classes.sketches.cochleo import *


from src.classes.fingerprints import *
from src.classes.fingerprints.bench import *
from src.classes.fingerprints.cortico import *
from src.classes.fingerprints.cochleo import *
from src.classes.fingerprints.CQT import *
from PyMP.signals import LongSignal, Signal
import os.path as op
import matplotlib.pyplot as plt
tempdir = '.'
figuredir = '.'

SND_DB_PATH = os.environ['SND_DB_PATH']
single_test_file1 = op.join(SND_DB_PATH,'jingles/panzani.wav')
single_test_file2 = '/sons/sqam/voicemale.wav'

#audio_files_path = '/sons/rwc/rwc-p-m07'
audio_files_path = '/sons/rwc/rwc-p-m07'
#file_names = os.listdir(audio_files_path)

def SNR(noisy, orig):
    return 10*np.log10(np.linalg.norm(orig)/np.linalg.norm(orig-noisy))

def NoiseTest(sigmas, sparsity, ntest=1):
    falseOffset = 10    
    legends = []
    plt.figure()
    for i, (fgpthand, sk) in enumerate(fgpt_sketches):    
        print fgpthand, sk
        
        # First Test: white additive noise
    #    sk.recompute(single_test_file1)
    #    sk.sparsify(sparsity)
    #    # convert it to a fingeprint compatible with associated handler
    ##    print sk.params
    #    fgpt = sk.fgpt(sparse=True)    
    #    fgpthand.populate(fgpt, sk.params, 0,falseOffset)
    #    anchor = np.sum(fgpthand.retrieve(fgpt, sk.params, nbCandidates=1))
        # Now measure the score achieved with various levels of noise
        
        orig_sig = Signal(single_test_file1, normalize=True, mono=True)
        orig_sig.downsample(fs)
        orig_sig.write(op.join(tempdir, 'orig.wav'))
        sk.recompute(op.join(tempdir, 'orig.wav'))
        sk.sparsify(sparsity)
        fgpt = sk.fgpt(sparse=True)    
        fgpthand.populate(fgpt, sk.params, 0, falseOffset, max_pairs=sparsity)
        anchor = np.sum(fgpthand.retrieve(fgpt, sk.params, nbCandidates=1))
        
        orig_data = np.copy(orig_sig.data)
        snrs = np.zeros((len(sigmas), ntest))
        noisescores = np.zeros((len(sigmas), ntest))
        for isg, sigma in enumerate(sigmas):
            for itest in range(ntest):
                noisy = Signal(orig_data + sigma*np.random.randn(len(orig_data)), orig_sig.fs, normalize=False)      
                        
                snrs[isg,itest] = SNR(noisy.data,orig_data)
                noisy_name = op.join(tempdir, 'noisy%d.wav'%int(snrs[isg,itest])) 
        #        noisy.normalize()
        #        noisy.write(noisy_name)
                
        #        noisy_reread = Signal(noisy_name, mono=True, normalize=True)        
                
                try:
                    sk.recompute(noisy)
                    sk.sparsify(sparsity)
                except:
                    noisy.write(noisy_name)
                    sk.recompute(noisy_name)
        #        print sk.params
                noisy_fgpt = sk.fgpt(sparse=True)    
                hist = fgpthand.retrieve(noisy_fgpt, sk.params, nbCandidates=1)
                noisescores[isg,itest] = float(np.sum(hist))/float(anchor)
            print np.mean(snrs,axis=1),np.mean(noisescores,axis=1), fgpthand.dbObj.stat()['nkeys']
        
        plt.plot( np.mean(snrs,axis=1),np.mean(noisescores,axis=1), linewidth=i+1)
        legends.append(sk.__class__.__name__[:-6])
        # second test : amplitude
        
    plt.legend(legends, loc='lower right')    
    plt.grid()
    plt.xlabel('SNR (dB)')
    plt.ylabel('Keys Overlap Ratio')
    plt.savefig(op.join(figuredir,'NoiseRobustness_k%d.pdf'%sparsity))
    plt.savefig(op.join(figuredir,'NoiseRobustness_k%d.png'%sparsity))

def SparsityTest(sigma, sparsities, ntest=1):
    falseOffset = 10    
    legends = []
    plt.figure()
    for i, (fgpthand, sk) in enumerate(fgpt_sketches):    
        print fgpthand, sk
        
        # First Test: white additive noise
    #    sk.recompute(single_test_file1)
    #    sk.sparsify(sparsity)
    #    # convert it to a fingeprint compatible with associated handler
    ##    print sk.params
    #    fgpt = sk.fgpt(sparse=True)    
    #    fgpthand.populate(fgpt, sk.params, 0,falseOffset)
    #    anchor = np.sum(fgpthand.retrieve(fgpt, sk.params, nbCandidates=1))
        # Now measure the score achieved with various levels of noise
        sk_n = sk
        orig_sig = Signal(single_test_file1, normalize=True, mono=True)
        orig_sig.downsample(fs)
        orig_sig.write(op.join(tempdir, 'orig.wav'))
        sk.recompute(op.join(tempdir, 'orig.wav'))

        
        orig_data = np.copy(orig_sig.data)
        noisy = Signal(orig_data + sigma*np.random.randn(len(orig_data)), orig_sig.fs, normalize=False)
        noise = SNR(noisy.data,orig_data)
        noisy_name = op.join(tempdir, 'noisy%d.wav'%int(noise)) 
        noisy.write(noisy_name)
        sk_n.recompute(noisy_name)
        sparsityscores = np.zeros((len(sparsities),ntest))
        for isg, sparsity in enumerate(sparsities):
            for itest in range(ntest):
                sk.sparsify(sparsity)   #original signal
                fgpt = sk.fgpt(sparse=True)    
                fgpthand.populate(fgpt, sk.params, 0, falseOffset, max_pairs=sparsity)
                anchor = np.sum(fgpthand.retrieve(fgpt, sk.params, nbCandidates=1)) 
                sk_n.sparsify(sparsity)   #noise signal
                sparsity_fgpt = sk_n.fgpt(sparse=True)    
                hist = fgpthand.retrieve(sparsity_fgpt, sk.params, nbCandidates=1)
                sparsityscores[isg,itest] = float(np.sum(hist))/float(anchor)
            print np.mean(sparsityscores,axis=1), fgpthand.dbObj.stat()['nkeys']
        
        plt.plot( sparsities,np.mean(sparsityscores,axis=1), linewidth=i+1)
        legends.append(sk.__class__.__name__[:-6])
        # second test : amplitude
        
    plt.legend(legends, loc='lower right')    
    plt.grid()
    plt.title('Sparsity robustness with noise %dDB:'%noise)
    plt.xlabel('Sparsity (K)')
    plt.ylabel('Keys Overlap Ratio')
    plt.savefig(op.join(figuredir,'SparsityRobustness_k%d.pdf'%noise))
    plt.savefig(op.join(figuredir,'SparsityRobustness_k%d.png'%noise))
 

def TimeShiftTest(shifts, sparsity):    
    falseOffset = 0
    
    legends = []
    plt.figure()
    for i, (fgpthand, sk) in enumerate(fgpt_sketches):    
        print fgpthand, sk
    
        orig_sig = Signal(single_test_file1, normalize=True, mono=True)
        orig_sig.downsample(fs)
        orig_sig.write(op.join(tempdir, 'orig.wav'))
        sk.recompute(op.join(tempdir, 'orig.wav'))
        sk.sparsify(sparsity)
        fgpt = sk.fgpt(sparse=True)   
#        sk.represent(sparse=True)
#        print sk.params 
#        keys, values = fgpthand._build_pairs(fgpt, sk.params, 0,display=True)
#        print keys
        fgpthand.populate(fgpt, sk.params, 0, falseOffset)
        anchor = np.sum(fgpthand.retrieve(fgpt, sk.params, nbCandidates=1))
        
        orig_data = np.copy(orig_sig.data)        
        shiftscores = []
        
        
        for shift in shifts:
            shifted = orig_sig.copy()
            shifted.pad(shift)
            shifted.crop(0, orig_sig.length)  
            shifted.data[0:shift] += 0.001*np.random.randn(shift)                  
            shifted_name = op.join(tempdir, 'shifted%d.wav'%int(shift)) 
            try:
                sk.recompute(shifted)
                sk.sparsify(sparsity)
            except:
                shifted.write(shifted_name)
                sk.recompute(shifted_name)
    
            shifted_fgpt = sk.fgpt(sparse=True)   
#            sk.represent(sparse=True) 
#            plt.figure()
#            keys, values = fgpthand._build_pairs(shifted_fgpt, sk.params, 0,display=True)
#            print keys
#            plt.show()
            hist = fgpthand.retrieve(shifted_fgpt, sk.params, nbCandidates=1)
            shiftscores.append(float(np.sum(hist))/float(anchor))
            print shift, shiftscores[-1], anchor
        
        plt.plot(np.array(shifts).astype(float)/float(fs),shiftscores, linewidth=i+1)
        legends.append(sk.__class__.__name__[:-6])
        # second test : amplitude
        
    plt.legend(legends)    
    plt.xlabel('seconds')
    plt.ylabel('Keys Overlap Ratio')
    plt.grid()
    plt.savefig(op.join(figuredir,'ShiftRobustness_k%d.pdf'%sparsity))
    plt.savefig(op.join(figuredir,'ShiftRobustness_k%d.png'%sparsity))
    

##########
#if __name__ == "__main__":
#     parameters
fs = 8000.0 #11025
sparsity = 100 
# systems to test    
fgpt_sketches = [
#                     (XMDCTBDB(None, load=False,**{'wall':False}),
#                      XMDCTSparseSketch(**{'scales':[2048, 4096, 8192],'n_atoms':150,
#                                                  'nature':'LOMDCT'})),     
#              #       (SWSBDB(None, **{'wall':False,'n_deltas':2}),                  
#               #      SWSSketch(**{'n_formants_max':7,'time_step':0.01})), 
#                (STFTPeaksBDB(None, **{'wall':True,'delta_t_max':60.0}),
#                 STFTPeaksSketch(**{'scale':1024, 'step':512})), 
#                     (CochleoPeaksBDB(None, **{'wall':False}),
#                     CochleoPeaksSketch(**{'fs':fs,'step':128,'downsample':fs,'frmlen':8})),
 (CQTPeaksBDB(None, **{'wall':False}),
     CQTPeaksSketch(**{'n_octave':5,'freq_min':101.0, 'bins':12.0,'downsample':fs})),
 (CQTPeaksBDB(None, **{'wall':False}),
    cqtIHTSketch(**{'n_octave':5,'freq_min':101.0, 'bins':12.0, 'downsample':8000.0, 'max_iter':5}))
# (CQTPeaksTripletsBDB(None, **{'wall':False}),
#     CQTPeaksSketch(**{'n_octave':5,'freq_min':101, 'bins':12.0,'downsample':fs}))
                 ]

# tests
for sparsity in [200]:
    NoiseTest(np.logspace(-5, 0, 20), sparsity, ntest=5)

#sigma = np.spacing(1) #equivalent to no noise
sigma = 0.8 # equivalent to -3DB noise
SparsityTest(sigma, [200,100,50,30,20,10,5],ntest=5)

#    TimeShiftTest(np.linspace(0,3*fs, 50), sparsity)
    
# plotting
plt.show()

#plt.figure()
#plt.plot(noisy_reread.data)
#plt.plot(orig_sig.data,'r:')
#plt.show()


############""
#(keys, values) = fgpthand._build_pairs(fgpt, sk.params, 0) 
##(noisy_keys, noisy_values) = fgpthand._build_pairs(noisy_fgpt, sk.params, 0)
#(shifted_keys, shifted_values) = fgpthand._build_pairs(shifted_fgpt, sk.params, 0)
#
#formatted_keys = map(fgpthand.format_key,keys)
#formatted_noisy_keys = map(fgpthand.format_key,noisy_keys)
#
#results = map(fgpthand.get , keys)
#noisy_results = map(fgpthand.get ,noisy_keys)
#
##plt.plot(formatted_keys);plt.plot(formatted_noisy_keys,':');plt.show()
##
#plt.plot(keys);plt.plot(shifted_keys,':');plt.show()
#plt.plot(values);plt.plot(shifted_values,':');plt.show()