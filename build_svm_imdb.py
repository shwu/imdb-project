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
from math import log
import ConfigParser
from imdbutils import hydrate, mpaa_to_label
import numpy as np
from sklearn.svm import SVC

MOVIE_FILE = sys.argv[1]

cfg = ConfigParser.ConfigParser()
cfg.read('params.cfg')
MAX_ACTORS = eval(cfg.get('Misc', 'MAX_ACTORS'))
BINS_RATING = eval(cfg.get('OutputLabels', 'BINS_RATING'))
BINS_BMULT = eval(cfg.get('OutputLabels', 'BINS_BMULT'))
NUM_RATING_BINS = len(BINS_RATING)
NUM_BMULT_BINS = len(BINS_BMULT)

# db.cfg should contain a uri of the form:
# sqlite:///absolute/path/to/imdb.db
cfg = ConfigParser.ConfigParser()
cfg.read('db.cfg')
db_uri = cfg.get('URI', 'IMDB_URI')

'''
guarantees on movies:
- must be a movie
- must have a rating
- must not be an adult movie
- must have a 'business' section, and a 'budget' section within that
- must have 'gross' within 'business'
- must have 'opening weekend'
'''

sys.stdout.write('Initializing... ')
sys.stdout.flush()

feature_vecs = []
rating_labels = []
bmult_labels = []

sys.stdout.write('[done]\n')

sys.stdout.write('Loading feature indices... ')
sys.stdout.flush()

'''
fid = open('staging/person_fvid.pkl', 'rb')
person_fvid = pickle.load(fid)
fid.close()

fid = open('staging/distro_fvid.pkl', 'rb')
distro_fvid = pickle.load(fid)
fid.close()
'''
fid = open('staging/genre_fvid.pkl', 'rb')
genre_fvid = pickle.load(fid)
fid.close()

# Feature vectoor is of the form:
# [ genres, mpaa, budget, pIDs? ] (extensible)

#NUM_PERSONS = len(person_fvid)
#NUM_DISTROS = len(distro_fvid)
NUM_GENRES = len(genre_fvid)
#PERSON_OFFSET = 0
#DISTRO_OFFSET = PERSON_OFFSET + NUM_PERSONS
#GENRE_OFFSET = DISTRO_OFFSET + NUM_DISTROS
GENRE_OFFSET = 0
MPAA_OFFSET = GENRE_OFFSET + NUM_GENRES
BUDGET_OFFSET = MPAA_OFFSET + 1
FV_LENGTH = NUM_GENRES + 2

sys.stdout.write('[done]\n')

sys.stdout.write('Loading imdb.db... ')
sys.stdout.flush()
ia = imdb.IMDb('sql', uri=db_uri)
sys.stdout.write('[done]\n')

# all pruning will be done in movielist
mlist = open(MOVIE_FILE, 'r')
mov_id = mlist.readline().strip()

max_budget = 0 # for normalization purposes

while mov_id != '':
    sys.stdout.write('Reading movie #' + mov_id + ': ')
    sys.stdout.flush()

    movie = hydrate(mov_id, ia, MAX_ACTORS)

    sys.stdout.write(movie['title'])
    sys.stdout.flush()

    # initialize feature vector
    current_fv = [0]*FV_LENGTH

    # generate output labels
    rating_labels.append(BINS_RATING.index(movie['rating']))
    bmult_labels.append(BINS_BMULT.index(movie['bmult']))
     
    # Populate feature vector
    '''
    for actor_id in iter(movie['actor']):
        current_fv[PERSON_OFFSET + person_fvid[actor_id]] = 1

    for director_id in iter(movie['director']): 
        current_fv[PERSON_OFFSET + person_fvid[director_id]] = 1

    for producer_id in iter(movie['producer']):
        current_fv[PERSON_OFFSET + person_fvid[producer_id]] = 1
    
    for composer_id in iter(movie['composer']):
        current_fv[PERSON_OFFSET + person_fvid[composer_id]] = 1
                                
    for cinetog_id in iter(movie['cinetog']):
        current_fv[PERSON_OFFSET + person_fvid[cinetog_id]] = 1
    
    for distro_id in iter(movie['distro']):
        current_fv[DISTRO_OFFSET + distro_fvid[distro_id]] = 1
    '''
    for genre in iter(movie['genre']):
        current_fv[GENRE_OFFSET + genre_fvid[genre]] = 1
    
    for mpaa in iter(movie['mpaa']):
        current_fv[MPAA_OFFSET] = float(mpaa_to_label(mpaa)) / 4 # to normalize

    current_fv[BUDGET_OFFSET] = movie['budget']
    if movie['budget'] > max_budget:
        max_budget = movie['budget']
   
    feature_vecs.append(current_fv)
 
    mov_id = mlist.readline().strip()

    sys.stdout.write(' [done]\n')

sys.stdout.write('Normalizing Features... ')
sys.stdout.flush()

for fv in iter(feature_vecs):
    fv[BUDGET_OFFSET] = float(fv[BUDGET_OFFSET]) / max_budget

sys.stdout.write('[done]\n')

sys.stdout.write('Pickling feature vectors... ')
sys.stdout.flush()

X = np.array(feature_vecs)
y_rating = np.array(rating_labels)
y_bmult = np.array(bmult_labels)

OUTPUT_DIR = 'svmmodel/'

fid = open(OUTPUT_DIR + 'svm_feature_vecs.pkl', 'wb')
pickle.dump(X, fid)
fid.close()

fid = open(OUTPUT_DIR + 'svm_rating_outs.pkl', 'wb')
pickle.dump(y_rating, fid)
fid.close()

fid = open(OUTPUT_DIR + 'svm_bmult_outs.pkl', 'wb')
pickle.dump(y_bmult, fid)
fid.close()

fid = open(OUTPUT_DIR + 'budget.dat', 'w')
fid.write(str(max_budget) + '\n')
fid.close()

sys.stdout.write('[done]\n')
