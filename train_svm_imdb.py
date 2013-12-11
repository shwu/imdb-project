#!/usr/bin/python

'''
train-imdb.py

This script takes a text file containing a movieID on each line and trains
a Naive Bayes classifier by generating and pickling log probabilities in
the current directory.

Copyright 2013 Dan Cocuzzo <cocuzzo@cs.stanford.edu>
               Stephen Wu <shw@stanford.edu>
'''

import sys
import imdb
import cPickle as pickle
import numpy as np
from sklearn.svm import SVC

sys.stdout.write('Initializing... ')
sys.stdout.flush()

fid = open('svmmodel/svm_feature_vecs.pkl', 'rb')
X = pickle.load(fid)
fid.close()

fid = open('svmmodel/svm_rating_outs.pkl', 'rb')
y_rating = pickle.load(fid)
fid.close()

fid = open('svmmodel/svm_bmult_outs.pkl', 'rb')
y_bmult = pickle.load(fid)
fid.close()

sys.stdout.write('[done]\n')

sys.stdout.write('Training SVM... ')
sys.stdout.flush()

# TODO: kernel selection and paramater tuning
rating_model = SVC()
bmult_model = SVC()

rating_model.fit(X, y_rating)
bmult_model.fit(X, y_bmult)

sys.stdout.write('[done]\n')

sys.stdout.write('Pickling trained models... ')
sys.stdout.flush()

OUTPUT_DIR = 'svmmodel/'

fid = open(OUTPUT_DIR + 'svm_rating_model.pkl', 'wb')
pickle.dump(rating_model, fid)
fid.close()

fid = open(OUTPUT_DIR + 'svm_bmult_model.pkl', 'wb')
pickle.dump(bmult_model, fid)
fid.close()

sys.stdout.write('[done]\n')
