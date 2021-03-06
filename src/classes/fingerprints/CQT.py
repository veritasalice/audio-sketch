# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 17:14:52 2013

@author: loa-guest
"""

'''
classes.fingerprints.cochleo  -  Created on Sep 30, 2013
@author: M. Moussallam
'''

from src.classes.fingerprints.bench import  *
from src.tools import cochleo_tools
import itertools

class CQTPeaksBDB(STFTPeaksBDB):
    ''' handling the fingerprints based on a pairing of Cochleogram peaks 
    
    Most of the methods are the same as STFTPeaksBDB so inheritance is natural
    Only the pairing may be different since the peak zones may not be TF squares
            
    '''    
    
    def __init__(self, dbName, load=False, persistent=None,dbenv=None,
                 **kwargs):
        # Call superclass constructor        
        super(CQTPeaksBDB, self).__init__(dbName, load=load, persistent=persistent,dbenv=dbenv)
    
        self.params = {'delta_t_max':3.0,
                       'fmax': 8000.0,
                       'key_total_nbits':32,
                        'f1_n_bits': 10,
                        'f2_n_bits': 10,
                        'dt_n_bits': 10,
                        'value_total_bits':32,
                        'file_index_n_bits':20,
                        'time_n_bits':12,
                        'time_max':60.0* 20.0,
                        'min_bin_dist':4,
                        'min_fr_dist':4,
                        'wall':True}
        
        for key in kwargs:
            self.params[key] = kwargs[key]
        
        # Formatting the key - FORMAT 1 : Absolute
        self.alpha = ceil((self.params['fmax'])/(2**self.params['f1_n_bits']-1))
        self.beta = ceil((self.params['fmax'])/(2**self.params['f2_n_bits']-1))
        
        # BUGFIX remove the ceiling function cause it causes all values to be zeroes
        self.gamma = self.params['delta_t_max']/(2**self.params['dt_n_bits']-1)
    
    def _build_pairs(self, sparse_stft, params, offset=0, display=False, ax =None):
        ''' internal routine to build key/value pairs from sparse STFT
        given the parameters '''
        keys = []
        values = []
        
        peak_indexes = np.nonzero(sparse_stft[0,:,:])
        
        f_target_width = 3*params['f_width']
        t_target_width = 3*params['t_width']            
        
        #time_step = float(round(params['frmlen'] * 2 ** (4 + params['shift'])))/float(params['fs'])
        time_step = params['overl']/params['downsample'] #0.0078#params['inc']      
        f_vec = params['f']
        
        if display:
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            if ax is None:        
                fig = plt.figure()
                ax = fig.add_subplot(111)
            
            ax.spy(sparse_stft[0,:,:], cmap=cm.bone_r, aspect='auto')
        
#        print "Params : ",f_target_width,t_target_width,time_step
        # then for each of them look in the target zone for other
        for pIdx in range(len(peak_indexes[0])):
            peak_ind = (peak_indexes[0][pIdx], peak_indexes[1][pIdx])                    
            target_points_i, target_points_j = np.nonzero(sparse_stft[0,
                                                        peak_ind[0]: peak_ind[0]+f_target_width,
                                                        peak_ind[1]: peak_ind[1]+t_target_width]) # permit to uncast the [0,0] point
            
            
            # now we can build a pair of peaks , and thus a key
            for i in range(1,len(target_points_i)):
#                print f_vec[peak_ind[0]],f_vec.shape , peak_ind[0], target_points_i[i]
                f1 = f_vec[peak_ind[0]]
                f2 = f_vec[peak_ind[0]+target_points_i[i]]
                t1 = float(peak_ind[1]) *time_step
                delta_t = float(target_points_j[i]) *time_step
                
                # discard points that are too closely located
                if (np.abs(target_points_i[i]-peak_ind[0])<self.params['min_bin_dist']) and target_points_j[i] < self.params['min_fr_dist']:
                    continue
                
                if display:                    
                    ax.arrow(peak_ind[1], peak_ind[0],target_points_j[i], target_points_i[i], head_width=0.05, head_length=0.1, fc='k', ec='k')
#                print (f1, f2, delta_t) , t1
                keys.append((f1, f2, delta_t))
                values.append(t1 + offset)
        return keys, values

class CQTPeaksTripletsBDB(STFTPeaksBDB):
    ''' handling the fingerprints based on a pairing of Cochleogram peaks 
    
    Most of the methods are the same as STFTPeaksBDB so inheritance is natural
    Only the pairing may be different since the peak zones may not be TF squares
            
    '''    
    
    def __init__(self, dbName, load=False, persistent=None,dbenv=None,
                 **kwargs):
        # Call superclass constructor        
        super(CQTPeaksTripletsBDB, self).__init__(dbName, load=load, persistent=persistent,dbenv=dbenv)
    
        self.params = {'delta_t_max':1.0,   ####
                       'fmax': 8000.0,
                       'key_total_nbits':32,
                       'TZ_delta_f':1,
                        'TZ_delta_t':1,
                        'f1_n_bits': 8,
                        'df1_n_bits': 8,
                        'df2_n_bits': 8,
                        'dt_n_bits': 8,
                        'value_total_bits':32,
                        'file_index_n_bits':20,
                        'time_n_bits':12,
                        'time_max':60.0* 20.0,
                        'min_bin_dist':4,
                        'min_fr_dist':4,
                        'f_targ_width':12,
                        't_targ_width':10,
                        'wall':True}
        
        for key in kwargs:
            self.params[key] = kwargs[key]
        
        # Formatting the key - FORMAT 1 : Absolute
        self.alpha = ceil((self.params['fmax'])/(2**self.params['f1_n_bits']-1))
        self.beta = ceil((self.params['fmax'])/(2**self.params['df1_n_bits']-1)) # quantification of delta_f
        self.gamma = ceil((self.params['fmax'])/(2**self.params['df2_n_bits']-1)) # quantification of delta_f2
        # BUGFIX remove the ceiling function cause it causes all values to be zeroes
        self.delta = self.params['delta_t_max']/(2**self.params['dt_n_bits']-1) # octet quantification of delta_t ratio
    
    def _build_pairs(self, sparse_stft, params, offset=0.0, display=False, ax =None):
        ''' internal routine to build key/value pairs from sparse STFT
        given the parameters '''
        keys = []
        values = []
        
        peak_indexes = np.nonzero(sparse_stft[0,:,:])
        
        f_target_width = self.params['f_targ_width']
        t_target_width = self.params['t_targ_width']            
        
        #time_step = float(round(params['frmlen'] * 2 ** (4 + params['shift'])))/float(params['fs'])
        time_step = 2*params['overl']/self.params['fmax']#0.0078#params['inc']      
        self.f_vec = params['f']
        f_vec = params['f']
        
        if display:
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            if ax is None:        
                fig = plt.figure()
                ax = fig.add_subplot(111)
            
            ax.spy(sparse_stft[0,:,:], cmap=cm.bone_r, aspect='auto')
        
#        print "Params : ",f_target_width,t_target_width,time_step
        # then for each of them look in the target zone for other
        for pIdx, (pf,pt) in enumerate(zip(peak_indexes[0],peak_indexes[1])):
                                
            target_Imin = max(0,pf+self.params['TZ_delta_f'])
            target_Imax = min(sparse_stft.shape[1],
                              pf+self.params['TZ_delta_f']+f_target_width)
            target_Jmin = max(0,pt+self.params['TZ_delta_t'])
            target_Jmax = min(sparse_stft.shape[2],
                              pt+self.params['TZ_delta_t']+t_target_width)
#            print peak_ind,target_Imin,target_Imax,target_Jmin,target_Jmax
            target_points_i, target_points_j = np.nonzero(sparse_stft[0,
                                                        target_Imin: target_Imax,
                                                        target_Jmin: target_Jmax])
            print pf,pt
            print zip(target_points_i,target_points_j)
            # in j are the ordered times, and in i are the corresponding frequencies
            # now we can build a pair of peaks , and thus a key
            if isinstance(target_points_i,int):
                continue
            # get all combinations of two other peaks
            for b in itertools.combinations(range(target_points_j.shape[0]),2):
#                print f_vec[peak_ind[0]],f_vec.shape , peak_ind[0], target_points_i[i]
                f1 = f_vec[pf]
#                delta_f1 = f_vec[peak_ind[0]+target_points_i[b[0]]] - f_vec[peak_ind[0]] 
#                delta_f2 = f_vec[peak_ind[0]+target_points_i[b[1]]] - f_vec[peak_ind[0]] 
                # nouvel essai en bin cqt
                delta_f1 = target_points_i[b[0]] 
                delta_f2 = target_points_i[b[1]] 
                
#                t1 = float(pt) #*time_step
                t1 = pt
                ratio_delta_t = float(target_points_j[b[0]])/float(target_points_j[b[1]]+0.0001)
#                delta_t1 = np.round(float(target_points_j[b[0]]) *time_step, decimals=1)
#                delta_t2 = np.round(float(target_points_j[b[1]]) *time_step, decimals=1)
                
                delta_t1 = target_points_j[b[0]]
                delta_t2 = target_points_j[b[1]]
                # discard points that are too closely located
#                f_min = min(target_points_i[b[0]],target_points_i[b[1]])
#                if (np.abs(f_min-pf)<self.params['min_bin_dist']) and target_points_j[min(b)] < self.params['min_fr_dist']:
#                    continue
                
#                if display:                    
#                    ax.arrow(peak_ind[1], peak_ind[0],target_points_j[i], target_points_i[i], head_width=0.05, head_length=0.1, fc='k', ec='k')
#                    print (f1,delta_f1, delta_f2, ratio_delta_t) , (t1 + offset,delta_t1, delta_t2)
#                print (f1,delta_f1, delta_f2, ratio_delta_t) , (t1 + offset,delta_t1, delta_t2)
                keys.append((f1,delta_f1, delta_f2, ratio_delta_t))
                values.append((t1 + offset, delta_t1))
        return keys, values

    def draw_keys(self, keys_values, ax=None, color='r'):
        if ax is None:
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            if ax is None:        
                fig = plt.figure()
                ax = fig.add_subplot(111)
        f_vec = self.f_vec   # UGLY: TO REMOVE
        for key, value in keys_values:
#            print value[0], key[0]
            flist = f_vec.astype(int).tolist()
            x = value[0]
            try:
                y = flist.index(int(key[0]))
            except:
                print key[0], flist
                continue
            ax.arrow(x, y, value[1]+1, key[1]+1, head_width=0.05, head_length=0.1, fc=color, ec=color)
            ax.arrow(x, y, (value[1]/key[3])+1, key[2]+1, head_width=0.05, head_length=0.1, fc=color, ec=color)
    
    def format_key(self, key):
        """ Format the Key as [f1 , f2, delta_t] """
        (f1, delta_f1, delta_f2, ratio_delta_t) = key
        
        return floor((f1 / self.alpha) * 2 ** (self.params['df1_n_bits'] + 
                                               self.params['df2_n_bits'] + 
                                               self.params['dt_n_bits'])) + \
                floor((delta_f1 / self.beta) * 2 ** (self.params['df2_n_bits'] + 
                                                     self.params['dt_n_bits'])) + \
                floor((delta_f2 / self.gamma) * 2 ** (self.params['dt_n_bits'])) + \
                floor((ratio_delta_t) / self.delta)
    
    def format_value(self, fileIndex, value):
        """ Format the value according to the parameters """
        t1, delta_t1 = value
        return floor(((t1 / self.params['time_max']) * (2 ** self.params['time_n_bits'] - 1)) + 
                     fileIndex * (2 ** self.params['time_n_bits']))        

