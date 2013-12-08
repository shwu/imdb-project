#!/usr/bin/python

"""
Cross-Validation module ( package).

This module partitions the data into K partitions,
performing K-fold cross-validation using
imdb_train.py and imdb_test.py

CS229 Final Project
Dan Cocuzzo <cocuzzo@cs.stanford.edu>
Stephen Wu <shw@stanford.edu>

"""
import sys, os
import shutil
import operator
import math
from subprocess import call
import ConfigParser
from imdbutils import hydrate
import cPickle as pickle
from imdb import IMDb
from imdbutils import file_len, list_diff, copy_anything

##########################################
## GLOBALS
##########################################
MODEL_DIR = 'nbmodel'
RESULTS_DIR = 'results'
XVAL_DIR = 'xval'

# load config file ?

# parse args
movie_id_path = sys.argv[1]
K = int(sys.argv[2])

movie_id_file = os.path.basename(movie_id_path)

movie_count = file_len(movie_id_path)
partition_size = int(math.floor(movie_count / K))

print 'movie_count=%s' % movie_count
print 'partition_size=%s' % partition_size

# K-fold cross-validation
for k in range(1,K+1):
  test_idx = range((k-1)*partition_size+1,k*partition_size+1)
  train_idx = list(set(range(1,movie_count+1)) - set(test_idx))
  train_idx.sort()

  print 'K=%d' % k
  print 'train_idx [%d:%d]' %(min(train_idx),max(train_idx))
  print 'test_idx [%d:%d]' % (min(test_idx),max(test_idx))

  try:
    xval_dir = os.mkdir(XVAL_DIR)
  except:
    pass

  train_file = os.path.join(XVAL_DIR, '%s.K%s.train' % (movie_id_file,k))
  test_file = os.path.join(XVAL_DIR, '%s.K%s.test' % (movie_id_file,k))

  f_train = open(train_file, 'w')
  f_test = open(test_file, 'w')

  # iterate over all movie ids, segment by train/test
  f_mlist = open(movie_id_path)
  movie_id = f_mlist.readline().strip()
  idx = 1
  while (movie_id):
    if (idx in test_idx):
      f_test.write('%s\n' % movie_id)
    else:
      f_train.write('%s\n' % movie_id)
    movie_id = f_mlist.readline().strip()
    idx += 1

  f_train.close()
  f_test.close()

  # now train/test on this partition
  os.system('./train_imdb.py %s' % train_file)
  os.system('./test_imdb.py %s' % test_file)

  # copy training & testing results
  copy_anything(MODEL_DIR, os.path.join(XVAL_DIR, '%s.K%s' % (MODEL_DIR, k)))
  copy_anything(RESULTS_DIR, os.path.join(XVAL_DIR, '%s.K%s' % (RESULTS_DIR, k)))

  # clean training & testing results
  call(['./clean_train.sh'])
  call(['./clean_test.sh'])
