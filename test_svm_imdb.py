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

actual_rating = []
predicted_rating = []
actual_bmult = []
predicted_bmult = []

sys.stdout.write('[done]\n')

sys.stdout.write('Loading model... ')
sys.stdout.flush()

fid = open('svmmodel/budget.dat', 'r')
MAX_BUDGET = int(fid.readline().strip())
fid.close()

fid = open('svmmodel/svm_bmult_model.pkl', 'rb')
bmult_model = pickle.load(fid)
fid.close()

fid = open('svmmodel/svm_rating_model.pkl', 'rb')
rating_model = pickle.load(fid)
fid.close()

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
    sys.stdout.write('Predicting movie #' + mov_id + ': ')
    sys.stdout.flush()

    movie = hydrate(mov_id, ia, MAX_ACTORS)

    sys.stdout.write(movie['title'])
    sys.stdout.flush()

    # initialize feature vector
    current_fv = [0]*FV_LENGTH

    # generate actual outputs
    actual_rating.append(BINS_RATING.index(movie['rating']))
    actual_bmult.append(BINS_BMULT.index(movie['bmult']))
     
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

    current_fv[BUDGET_OFFSET] = float(movie['budget']) / MAX_BUDGET
   
    predicted_rating.append(rating_model.predict(current_fv)[0])
    predicted_bmult.append(bmult_model.predict(current_fv)[0])
 
    mov_id = mlist.readline().strip()

    sys.stdout.write(' [done]\n')

rating_sq_err = 0
bmult_sq_err = 0
rating_abs_err = 0
bmult_abs_err = 0
rating_sum_err = 0
bmult_sum_err = 0
num_rating_errors = 0
num_bmult_errors = 0

test_size = len(actual_rating)
error_rating = predicted_rating
error_bmult = predicted_bmult

for i in xrange(test_size):
    err_r = predicted_rating[i] - actual_rating [i]
    err_b = predicted_bmult[i] - actual_bmult[i]
    error_rating[i] = err_r
    error_bmult[i] = err_b
    if err_r != 0:
        num_rating_errors += 1
    if err_b != 0:
        num_bmult_errors += 1
    rating_sq_err += pow(err_r, 2)
    bmult_sq_err += pow(err_b, 2)
    rating_abs_err += abs(err_r)
    bmult_abs_err += abs(err_b)
    rating_sum_err = err_r
    bmult_sum_err = err_b
    
avg_abs_rating_err = float(rating_abs_err) / test_size 
avg_abs_bmult_err = float(bmult_abs_err) / test_size 
avg_sq_rating_err = float(rating_sq_err) / test_size 
avg_sq_bmult_err = float(bmult_sq_err) / test_size 
abs_rating_err_variance = avg_sq_rating_err - pow(avg_abs_rating_err, 2)
abs_bmult_err_variance = avg_sq_bmult_err - pow(avg_abs_bmult_err, 2)
avg_rating_err = float(rating_sum_err) / test_size 
avg_bmult_err = float(bmult_sum_err) / test_size 
rating_err_variance = avg_sq_rating_err - pow(avg_rating_err, 2)
bmult_err_variance = avg_sq_bmult_err - pow(avg_bmult_err, 2)

OUTPUT_DIR = 'results_svm/'
stats_file = open(OUTPUT_DIR + 'stats.out', 'w')
stats_file.write('test_size=' + str(test_size) + '\n')
stats_file.write('error_rating=' + str(float(num_rating_errors) / test_size) + '\n')
stats_file.write('error_bmult=' + str(float(num_bmult_errors) / test_size) + '\n')
stats_file.write('diff_rating=' + str(avg_abs_rating_err) + '\n')
stats_file.write('diff_bmult=' + str(avg_abs_bmult_err) + '\n')
stats_file.write('sqdiff_rating=' + str(avg_sq_rating_err) + '\n')
stats_file.write('sqdiff_bmult=' + str(avg_sq_bmult_err) + '\n')
stats_file.write('abs_rating_err_variance=' + str(abs_rating_err_variance) + '\n')
stats_file.write('abs_bmult_err_variance=' + str(abs_bmult_err_variance) + '\n')
stats_file.write('rating_err_variance=' + str(rating_err_variance) + '\n')
stats_file.write('bmult_err_variance=' + str(bmult_err_variance) + '\n')
stats_file.close()

sys.stdout.write('test_size=' + str(test_size) + '\n')
sys.stdout.write('error_rating=' + str(float(num_rating_errors) / test_size) + '\n')
sys.stdout.write('error_bmult=' + str(float(num_bmult_errors) / test_size) + '\n')
sys.stdout.write('diff_rating=' + str(avg_abs_rating_err) + '\n')
sys.stdout.write('diff_bmult=' + str(avg_abs_bmult_err) + '\n')
sys.stdout.write('sqdiff_rating=' + str(avg_sq_rating_err) + '\n')
sys.stdout.write('sqdiff_bmult=' + str(avg_sq_bmult_err) + '\n')
sys.stdout.write('abs_rating_err_variance=' + str(abs_rating_err_variance) + '\n')
sys.stdout.write('abs_bmult_err_variance=' + str(abs_bmult_err_variance) + '\n')
sys.stdout.write('rating_err_variance=' + str(rating_err_variance) + '\n')
sys.stdout.write('bmult_err_variance=' + str(bmult_err_variance) + '\n')