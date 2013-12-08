#!/usr/bin/python

'''
build_fvid.py

This script takes a text file containing a movieID on each line and generates
unique sequential IDs for each person, distributor, and genre, to be used for
indexing into the SVM feature vector.

Copyright 2013 Dan Cocuzzo <cocuzzo@cs.stanford.edu>
               Stephen Wu <shw@stanford.edu>
'''

import sys
import imdb
import cPickle as pickle
import ConfigParser
from imdbutils import hydrate

MOVIE_FILE = sys.argv[1]

cfg = ConfigParser.ConfigParser()
cfg.read('params.cfg')
MAX_ACTORS = eval(cfg.get('Misc', 'MAX_ACTORS'))

# db.cfg should contain a uri of the form:
# sqlite:///absolute/path/to/imdb.db
cfg = ConfigParser.ConfigParser()
cfg.read('db.cfg')
db_uri = cfg.get('URI', 'IMDB_URI')

sys.stdout.write('Initializing... ')
sys.stdout.flush()

person_fvid = {}
distro_fvid = {}
genre_fvid = {}
p_id = 0;
d_id = 0;
g_id = 0;

sys.stdout.write('[done]\n')

sys.stdout.write('Loading imdb.db... ')
sys.stdout.flush()
ia = imdb.IMDb('sql', uri=db_uri)
sys.stdout.write('[done]\n')

# all pruning will be done in movielist
mlist = open(MOVIE_FILE, 'r')
mov_id = mlist.readline().strip()

while mov_id != '':
    sys.stdout.write('Reading movie #' + mov_id + ': ')
    sys.stdout.flush()

    movie = hydrate(mov_id, ia, MAX_ACTORS)

    sys.stdout.write(movie['title'])
    sys.stdout.flush()

    # Index personas

    for actor_id in iter(movie['actor']):
        person_fvid[actor_id] = p_id
        p_id += 1

    for director_id in iter(movie['director']):
        person_fvid[director_id] = p_id
        p_id += 1
 
    for producer_id in iter(movie['producer']):
        person_fvid[producer_id] = p_id
        p_id += 1
 
    for composer_id in iter(movie['composer']):
        person_fvid[composer_id] = p_id
        p_id += 1
 
    for cinetog_id in iter(movie['cinetog']):
        person_fvid[cinetog_id] = p_id
        p_id += 1

    # Index distributors

    for distro_id in iter(movie['distro']):
        distro_fvid[distro_id] = d_id
        d_id += 1

    # Index genres
 
    for genre in iter(movie['genre']):
        genre_fvid[genre] = g_id
        g_id += 1
 
    mov_id = mlist.readline().strip()

    sys.stdout.write(' [done]\n')

sys.stdout.write('Pickling... ')
sys.stdout.flush()

OUTPUT_DIR = 'staging/'

fid = open(OUTPUT_DIR + 'person_fvid.pkl','wb')
pickle.dump(person_fvid, fid)
fid.close()

fid = open(OUTPUT_DIR + 'distro_fvid.pkl','wb')
pickle.dump(distro_fvid, fid)
fid.close()

fid = open(OUTPUT_DIR + 'genre_fvid.pkl','wb')
pickle.dump(genre_fvid, fid)
fid.close()

sys.stdout.write('[done]\n')
