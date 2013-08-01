'''
fgpt_scripts.many_sparsities  -  Created on Jul 30, 2013
@author: M. Moussallam

Now let us see how performances evolve with the sparsity
'''
import os
import os.path as op
import time
from scipy.io import savemat
from classes.sketches.bench import *
from classes.sketches.cochleo import *
from classes.sketches.cortico import *
from classes import pydb
from tools.fgpt_tools import db_creation, db_test

import bsddb.db as db
env = db.DBEnv()
env.set_cachesize(10,512*1024*1024,0)
print env.get_cachesize()
# define a pair FgptHandle/Sketch 

# The RWC subset path
audio_path = '/sons/rwc/Learn'
db_path = '/home/manu/workspace/audio-sketch/fgpt_db'
score_path = '/home/manu/workspace/audio-sketch/fgpt_scores'

file_names = [f for f in os.listdir(audio_path) if '.wav' in f]
nb_files = len(file_names)
# define experimental conditions
set_id = 'RWCLearn' # Choose a unique identifier for the dataset considered
sparsities = [100,50,30,10]
seg_dur = 5.0
fs = 8000



## Initialize the sketchifier
#sk = STFTPeaksSketch(**{'scale':2048, 'step':512})
sk = CorticoIndepSubPeaksSketch(**{'fs':fs,'downsample':fs,'frmlen':8,
                                   'shift':0,'fac':-2,'BP':1})
#sk = CochleoPeaksSketch(**{'fs':fs,'step':512,'downsample':fs})
sk_id = sk.__class__.__name__[:-6]

test = False

for sparsity in sparsities:    
    # construct a nice name for the DB object to be saved on disk
    db_name = "%s_%s_k%d_%s_%dsec_%dfs"%(set_id, sk_id, sparsity, sk.get_sig(),
                                            int(seg_dur), int(fs))
        
    # initialize the fingerprint Handler object
    fgpthandle = pydb.CorticoIndepSubPeaksBDB(op.join(db_path, db_name),
                                              load=True,persistent=True,
                                               **{'wall':False,'max_pairs':500})
#    fgpthandle = pydb.STFTPeaksBDB(op.join(db_path, db_name),
#                                   load=True,
#                                   persistent=True, **{'wall':False})
#    fgpthandle = pydb.CochleoPeaksBDB(op.join(db_path, db_name),
#                                   load=True,
#                                   persistent=True, **{'wall':True})
    ################# This is a complete experimental run given the setup ############## 
    # create the base:
    db_creation(fgpthandle, sk, sparsity,
                file_names[1:], 
                force_recompute = True,
                seg_duration = seg_dur, resample = fs,
                files_path = audio_path, debug=False, n_jobs=3)
    
    
    # run a fingerprinting experiment
    test_proportion = 0.1 # proportion of segments in each file that will be tested
    
    if test:
        tstart = time.time()
        scores, failures = db_test(fgpthandle, sk, sparsity,
                         file_names, 
                         files_path = audio_path,
                         test_seg_prop = test_proportion,
                         seg_duration = seg_dur, resample =fs,
                         step = 5.0, tolerance = 7.5, shuffle=True, debug=False,n_jobs=4)
        ttest = time.time() - tstart
        ################### End of the complete run #####################################
        # saving the results
        score_name = "%s_%s_k%d_%s_%dsec_%dfs_test%d.mat"%(set_id, sk_id, sparsity, sk.get_sig(),
                                                int(seg_dur), int(fs), int(100.0*test_proportion))
        
        stats =  os.stat(op.join(db_path, db_name))
        savemat(op.join(score_path,score_name), {'score':scores, 'time':ttest,
                                                 'size':stats.st_size,'failures': failures})
        