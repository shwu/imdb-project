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
from imdbutils import hydrate

MOVIE_FILE = sys.argv[1]
OUTPUT_DIR = 'nbmodel/'

try:
    outdir_name = sys.argv[2]
    OUTPUT_DIR = '%s/' % outdir_name
except:
    pass

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

p_actor = {}
p_director = {}
p_producer = {}
p_composer = {}
p_cinetog = {}
p_distro = {}
p_genre = {}
p_mpaa = {}
p_rating = {}
p_bmult = {}

rating_count = {} # rating_count['ratingkey'] gives the total count in trainingset for that rating bucket
bmult_count = {} # bmult_count['bmultkey'] gives the total count in trainingset for that bmultiple bucket

actor_rating_count = {} # actor_rating_count['actor_id']['ratingkey'] gives count of that actor in rating
director_rating_count = {}
producer_rating_count = {}
composer_rating_count = {}
cinetog_rating_count = {}
distro_rating_count = {}
genre_rating_count = {}
mpaa_rating_count = {}

actor_bmult_count = {}
director_bmult_count = {}
producer_bmult_count = {}
composer_bmult_count = {}
cinetog_bmult_count = {}
distro_bmult_count = {}
genre_bmult_count = {}
mpaa_bmult_count = {}

sys.stdout.write('[done]\n')

sys.stdout.write('Loading imdb.db... ')
sys.stdout.flush()
ia = imdb.IMDb('sql', uri=db_uri)
sys.stdout.write('[done]\n')

# all pruning will be done in movielist
mlist = open(MOVIE_FILE, 'r')
mov_id = mlist.readline().strip()

while mov_id != '':
    sys.stdout.write('Training on movie #' + mov_id + ': ')
    sys.stdout.flush()

    movie = hydrate(mov_id, ia, MAX_ACTORS)

    sys.stdout.write(movie['title'])
    sys.stdout.flush()

    # generate output classes
    rkey = movie['rating']
    rating_count[rkey] = rating_count.setdefault(rkey, 0) + 1

    bkey = movie['bmult']  
    bmult_count[bkey] = bmult_count.setdefault(bkey, 0) + 1

    # Count appearances
    #for each actor in the cast list
    for actor_id in iter(movie['actor']):
        actor_rating_count[actor_id][rkey] = actor_rating_count.setdefault(actor_id, {}).setdefault(rkey, 0) + 1
        actor_bmult_count[actor_id][bkey] = actor_bmult_count.setdefault(actor_id, {}).setdefault(bkey, 0) + 1

    #for each director
    for director_id in iter(movie['director']):
        director_rating_count[director_id][rkey] = director_rating_count.setdefault(director_id, {}).setdefault(rkey, 0) + 1
        director_bmult_count[director_id][bkey] = director_bmult_count.setdefault(director_id, {}).setdefault(bkey, 0) + 1
        
    #for each producer
    for producer_id in iter(movie['producer']):
        producer_rating_count[producer_id][rkey] = producer_rating_count.setdefault(producer_id, {}).setdefault(rkey, 0) + 1
        producer_bmult_count[producer_id][bkey] = producer_bmult_count.setdefault(producer_id, {}).setdefault(bkey, 0) + 1
    
    #for each composer
    for composer_id in iter(movie['composer']):
        composer_rating_count[composer_id][rkey] = composer_rating_count.setdefault(composer_id, {}).setdefault(rkey, 0) + 1
        composer_bmult_count[composer_id][bkey] = composer_bmult_count.setdefault(composer_id, {}).setdefault(bkey, 0) + 1
                                
    #for each cinematographer
    for cinetog_id in iter(movie['cinetog']):
        cinetog_rating_count[cinetog_id][rkey] = cinetog_rating_count.setdefault(cinetog_id, {}).setdefault(rkey, 0) + 1
        cinetog_bmult_count[cinetog_id][bkey] = cinetog_bmult_count.setdefault(cinetog_id, {}).setdefault(bkey, 0) + 1
    
    #for each distributor
    for distro_id in iter(movie['distro']):
        distro_rating_count[distro_id][rkey] = distro_rating_count.setdefault(distro_id, {}).setdefault(rkey, 0) + 1
        distro_bmult_count[distro_id][bkey] = distro_bmult_count.setdefault(distro_id, {}).setdefault(bkey, 0) + 1
    
    #for each genre
    for genre in iter(movie['genre']):
        genre_rating_count[genre][rkey] = genre_rating_count.setdefault(genre, {}).setdefault(rkey, 0) + 1
        genre_bmult_count[genre][bkey] = genre_bmult_count.setdefault(genre, {}).setdefault(bkey, 0) + 1
    
    #mpaa rating
    for mpaa in iter(movie['mpaa']):
        mpaa_rating_count[mpaa][rkey] = mpaa_rating_count.setdefault(mpaa, {}).setdefault(rkey, 0) + 1
        mpaa_bmult_count[mpaa][bkey] = mpaa_bmult_count.setdefault(mpaa, {}).setdefault(bkey, 0) + 1
    
    mov_id = mlist.readline().strip()

    sys.stdout.write(' [done]\n')

sys.stdout.write('Generating log probabilities... ')
sys.stdout.flush()

# Ex. p_actor[actorid][rkey or bkey] = P(actor | movie is rkey or bkey)
# = count of # movies with actor AND rkey or bkey  /  count of movies with actor
# Laplace smoothing with factor 1

for actor_id, rcounts in actor_rating_count.iteritems():
    p_actor[actor_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_actor[actor_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for director_id, rcounts in director_rating_count.iteritems():
    p_director[director_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_director[director_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for producer_id, rcounts in producer_rating_count.iteritems():
    p_producer[producer_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_producer[producer_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for composer_id, rcounts in composer_rating_count.iteritems():
    p_composer[composer_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_composer[composer_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for cinetog_id, rcounts in cinetog_rating_count.iteritems():
    p_cinetog[cinetog_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_cinetog[cinetog_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for distro_id, rcounts in distro_rating_count.iteritems():
    p_distro[distro_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_distro[distro_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for genre_id, rcounts in genre_rating_count.iteritems():
    p_genre[genre_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_genre[genre_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

for mpaa_id, rcounts in mpaa_rating_count.iteritems():
    p_mpaa[mpaa_id] = {}
    total = sum(rcounts.itervalues())
    for rkey in BINS_RATING:
        p_mpaa[mpaa_id][rkey] = log(rcounts.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

# generate budget-multiple log probabilities

for actor_id, bcounts in actor_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_actor[actor_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)

for director_id, bcounts in director_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_director[director_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)
        
for producer_id, bcounts in producer_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_producer[producer_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)
        
for composer_id, bcounts in composer_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_composer[composer_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)
  
for cinetog_id, bcounts in cinetog_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_cinetog[cinetog_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)

for distro_id, bcounts in distro_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_distro[distro_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)

for genre_id, bcounts in genre_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_genre[genre_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)

for mpaa_id, bcounts in mpaa_bmult_count.iteritems():
    total = sum(rcounts.itervalues())
    for bkey in BINS_BMULT:
        p_mpaa[mpaa_id][bkey] = log(bcounts.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)

# generate priors
total = sum(rating_count.itervalues())
for rkey in BINS_RATING:
    p_rating[rkey] = log(rating_count.setdefault(rkey, 0) + 1) - log(total + NUM_RATING_BINS)

total = sum(bmult_count.itervalues())
for bkey in BINS_BMULT:
    p_bmult[bkey] = log(bmult_count.setdefault(bkey, 0) + 1) - log(total + NUM_BMULT_BINS)

sys.stdout.write('[done]\n')
sys.stdout.write('Pickling... ')
sys.stdout.flush()

fid = open(OUTPUT_DIR + 'p_actor.pkl','wb')
pickle.dump(p_actor, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_director.pkl','wb')
pickle.dump(p_director, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_producer.pkl','wb')
pickle.dump(p_producer, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_composer.pkl','wb')
pickle.dump(p_composer, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_cinetog.pkl','wb')
pickle.dump(p_cinetog, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_distro.pkl','wb')
pickle.dump(p_distro, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_genre.pkl','wb')
pickle.dump(p_genre, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_mpaa.pkl','wb')
pickle.dump(p_mpaa, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_rating.pkl','wb')
pickle.dump(p_rating, fid)
fid.close()

fid = open(OUTPUT_DIR + 'p_bmult.pkl','wb')
pickle.dump(p_bmult, fid)
fid.close()

sys.stdout.write('[done]\n')
