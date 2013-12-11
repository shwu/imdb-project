#!/usr/bin/python

"""
SVM Parameter Sweeping Script

CS229 Final Project
Dan Cocuzzo <cocuzzo@cs.stanford.edu>
Stephen Wu <shw@stanford.edu>

"""
import sys, os
import shutil
from subprocess import call
from imdbutils import file_len, list_diff, copy_anything
import pdb

##########################################
## GLOBALS
##########################################
MODEL_DIR = 'svmmodel'
RESULTS_DIR = 'results_svm'
SWEEP_DIR = 'local/svm_param_sweep'

BUILD_PROG = 'build_svm_imdb.py'
TRAIN_PROG = 'train_svm_imdb.py'
TEST_PROG = 'test_svm_imdb.py'

MID_FILE = sys.argv[1]
TRAIN_FILE = MID_FILE + '.train'
TEST_FILE = MID_FILE + '.test'

try:
  # shutil.rmtree(SWEEP_DIR)
  os.mkdir(SWEEP_DIR)
except:
  pass

# build the feature vector ONCE if necessary
os.system('./%s %s' % (BUILD_PROG, TRAIN_FILE))

CSteps = [1, 2, 4]
GSteps = [1, 2, 4, 8, 16, 32]
# CSteps = [0.25, 0.5, 1, 2, 4]
# GSteps = [0.25, 0.5, 1, 2, 4]

for C in CSteps:
  for G in GSteps:

    print '\n\n** tuning paramers {C=%d, gamma=%d} **\n\n' % (C, G)

    os.system('./%s %s %s' % (TRAIN_PROG, C, G))
    os.system('./%s %s' % (TEST_PROG, TEST_FILE))

    # copy training & testing results
    # pdb.set_trace()
    copy_anything(RESULTS_DIR, os.path.join(SWEEP_DIR, '%s.C%d.G%d' % (RESULTS_DIR, C, G)))

    # cleanup
    os.system('./clean_test_svm.sh')
