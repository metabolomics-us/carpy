import re
import pprint
import pandas as pd
import os
from cisclient.client import CISClient

class AnnotationReader:
    '''
    This class receives the results of get_annotations_given_splash in client.py 
    and converts those results into a panda for further processing
    '''

    def __init__(self):
        '''
        '''
        pass

    def assign_initial_dict(self, annotation_dict):
        '''
        '''
        self.annotation_dict=annotation_dict

    def assign_splash(self):
        '''
        '''
        self.splash=self.annotation_dict['splash']

    def assign_total_count(self):
        '''
        '''
        self.total_count=self.annotation_dict['total_count']

    def assign_annotations(self):
        '''
        '''
        self.annotations=self.annotation_dict['annotations']

    def remove_initial_dict(self):
        '''
        '''
        self.annotation_dict=None
    
    def assign_keys_from_first_annotation(self):
        '''
        the reason that we say first dict is
        1) avoid assumption that keys are homogenous
        return is typecasted to list then alphabetized
        '''
        self.first_dict_keys=list(self.annotations[0].keys())
        self.first_dict_keys.sort()


    def slice_single_key_across_annotations(self, key):
        '''
        for a given key, we get the values for that key that is found in each annotation
        '''
        temp_key_dict={key:[]}
        for annotation in self.annotations:
            temp_key_dict[key].append(annotation[key])
        return temp_key_dict

    def slice_all_keys_across_annotations(self):
        '''
        '''
        total_dict=dict()
        for key in self.first_dict_keys:
            temp_dict=self.slice_single_key_across_annotations(key)
            total_dict.update(temp_dict)
        self.all_annotation_dict=total_dict

    def reformat_spectrum_attribute(self,key):
        '''
        create two new keys based on key
        go through key, add values to two new keys
        typecast to float
        '''
        self.all_annotation_dict[key+'_mz']=[]
        self.all_annotation_dict[key+'_intensity']=[]
        
        for annotations_spectrum in self.all_annotation_dict[key]:
            temp_mz_list=list()
            temp_intensity_list=list()
            temp_string_split=re.split(' |:',annotations_spectrum)
            #we add every even index to the mz list of lists (all the mz)
            self.all_annotation_dict[key+'_mz'].append(temp_string_split[0::2])
            #we add every odd index to the intensity list of lists
            self.all_annotation_dict[key+'_intensity'].append(temp_string_split[1::2])
        del self.all_annotation_dict[key]

    def add_bin_splash_attribute(self):
        '''
        '''
        bin_splash_list=[self.splash for i in range(0,self.total_count)]
        self.all_annotation_dict['bin_splash']=bin_splash_list

    def all_annotation_dict_to_panda(self):
        '''
        '''
        self.panda_representation=pd.DataFrame.from_dict(self.all_annotation_dict)

    def do_everything(self,annotation_dict):
        '''
        if you didnt know all the steps and just want the quick panda output
        alternate name: initial_dict_to_panda
        '''
        self.assign_initial_dict(annotation_dict)
        self.assign_splash()
        self.assign_total_count()
        self.assign_annotations()
        self.remove_initial_dict()
        self.assign_keys_from_first_annotation()
        self.slice_all_keys_across_annotations()
        self.reformat_spectrum_attribute('spectrum')
        self.reformat_spectrum_attribute('raw_spectrum')
        self.add_bin_splash_attribute()
        self.all_annotation_dict_to_panda()        