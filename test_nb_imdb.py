#!/usr/bin/python

"""
Test module ( package).

This module provides the MovieSage class, used to make 
user-rating and gross-budget-multiplier predictions about
a given movies.

CS229 Final Project
Dan Cocuzzo <cocuzzo@cs.stanford.edu>
Stephen Wu <shw@stanford.edu>

"""
import sys, os
import operator
import math
import ConfigParser
from imdbutils import hydrate
import cPickle as pickle
from imdb import IMDb

# for stats and visualization
import numpy as np
import matplotlib.pyplot as plt

# debugger
import pdb

##########################################
# FEATURE probability dicts:

# p_actor (actors)
# p_director (director)
# p_producer (producers)
# p_composer (composers)
# p_cinetog (cinematographers)
# p_distro (distribution co's)
# p_genre (genres)
# p_mpaa (mpaa rating)
# p_runtime (runtime ~ 10 min buckets)
# p_month (US release month)
# p_budget (? US dollars ~ ? buckets)

# GROSS (output) probability
# p_gross (mult of budget)
# p_rating (star rating)
##########################################

# MOVIE DICT (sample point) KEYS:

# actor: array of actor (person) ids
# director: array of director (person) ids
# producer: array of producer (person) ids
# composer: array of composer (person) ids
# cinetog: array of cinematographer (person) ids
# distro: array of distribution co (company) ids
# genre: array of genre codes (custom)
# mpaa: array of MPAA code (single elem array)
# runtime: array of runtime in minutes (single elem array)
# month: array of US release month (single elem array)
# budget: array of US budget bucket (single elem array)
# gross: array US gross bucket ~ not included

# NOT USED FOR TESTING (TRAINING ONLY):

# bmult: US gross as multiple of budget 
# rating: rating 0-10, single decimal point


# class MovieSage():

  # self.features = [];

  # def __init__(self, configFile=None):

    # if not configFile:
    #   print "error: MovieSage constructor expects valid configFile."
    #   sys.exit(0)

paramsConfig = 'params.cfg'
dbConfig = 'db.cfg'

# parse the config file to obtain list of feature names
cfg = ConfigParser.ConfigParser()
cfg.read(paramsConfig)

FEATURES = eval(cfg.get('Features', 'FEATURES'))
BINS_RATING = eval(cfg.get('OutputLabels', 'BINS_RATING'))
BINS_BMULT = eval(cfg.get('OutputLabels', 'BINS_BMULT'))
MAX_ACTORS = eval(cfg.get('Misc', 'MAX_ACTORS'))

cfg = ConfigParser.ConfigParser()
cfg.read(dbConfig)

IMDB_URI = cfg.get('URI', 'IMDB_URI')
# try:
#   trainingPath = cfg.get('Paths', 'training')
# except:
#   trainingPath = os.getcwd()

MODEL_DIR = 'nbmodel'
RESULTS_DIR = 'results'

# print FEATURES
# print BINS_RATING
# print BINS_BMULT
# print MAX_ACTORS
# print IMDB_URI

def load_db():
  try:
    db = IMDb('sql', uri=IMDB_URI)
  except:
    print "unable to load imdb database [%s]" % IMDB_URI
    sys.exit(1)

  return db

# load the pickled model files and put them into a dict, keyed by feature labels
def load_model():
  nbmodel = {}
  for feat in FEATURES:
    pickle_file = os.path.join(MODEL_DIR, 'p_%s.pkl' % feat)
    fid = open(pickle_file, 'rb')
    nbmodel[feat] = pickle.load(fid)
    fid.close()

  # load the output labels explicitly
  fid = open(os.path.join(MODEL_DIR, 'p_rating.pkl'), 'rb')
  nbmodel['rating'] = pickle.load(fid)
  fid.close()
  fid = open(os.path.join(MODEL_DIR, 'p_bmult.pkl'), 'rb')
  nbmodel['bmult'] = pickle.load(fid)
  fid.close()

  return nbmodel


def predict(movie_id, nbmodel, imdb_db):
  """
  returns the predicted class labels (defined above) for 
  user-rating and gross-budget-mult by choosing the class 
  with the highest posterior probability
  """
  
  # generate custom movie dict by ingesting features from the database
  movie = hydrate(movie_id, imdb_db, MAX_ACTORS)
  true_rating = movie['rating']
  true_bmult = movie['bmult']
  
  # initialize posteriors
  # pos_rating = [0] * len(BINS_RATING)
  # pos_bmult = [0] * len(BINS_BMULT)
  pos_rating = {}
  pos_bmult = {}
  
  for feat in FEATURES:
    for id_ in movie[feat]:
      for br in BINS_RATING:
        stmt = "nbmodel['%s'].setdefault(id_,{}).setdefault(br,0)" % feat
        val = eval(stmt)
        try:
          pos_rating[br] += val
        except KeyError:
          pos_rating[br] = val
      for bm in BINS_BMULT:
        stmt = "nbmodel['%s'].setdefault(id_,{}).setdefault(bm,0)" % feat
        val = eval(stmt)
        try:
          pos_bmult[bm] += val
        except KeyError:
          pos_bmult[bm] = val

  # add class priors
  for br in BINS_RATING:
    pos_rating[br] += nbmodel['rating'][br]
  for bm in BINS_BMULT:
    pos_bmult[bm] += nbmodel['bmult'][bm]
  
  pred_rating = max(pos_rating.iteritems(), key=operator.itemgetter(1))[0]
  pred_bmult = max(pos_bmult.iteritems(), key=operator.itemgetter(1))[0]

  return ([true_rating, pred_rating], [true_bmult, pred_bmult])

#################################
########## main script ##########
#################################

if (len(sys.argv) < 2):
  print "bad args."
  sys.exit(1)

imdb_db = load_db()
nbmodel = load_model()

print "testing on file: %s" % sys.argv[1]
try:
  f_mlist = open(sys.argv[1], 'r')
except:
  print "unable to open test file [%s]" % sys.argv[1]
  sys.exit(1)

test_size = 0
error_rating = 0
error_bmult = 0
sqdiff_rating = 0.0
sqdiff_bmult = 0.0

hist_rating_true = []
hist_rating_pred = []
hist_rating_dist = []

hist_bmult_true = []
hist_bmult_pred = []
hist_bmult_dist = []

f_rating = open(os.path.join(RESULTS_DIR, 'rating.out'), 'w')
f_bmult = open(os.path.join(RESULTS_DIR, 'bmult.out'), 'w')
f_stats = open(os.path.join(RESULTS_DIR, 'stats.out'), 'w')

movie_id = f_mlist.readline().strip()
while (movie_id):
  test_size += 1
  rating, bmult = predict(movie_id, nbmodel, imdb_db)

  rating_true = rating[0]
  rating_pred = rating[1]

  bmult_true = bmult[0]
  bmult_pred = bmult[1]

  # measure the rating and bmult error
  error_rating += 0 if (rating_true == rating_pred) else 1
  error_bmult += 0 if (bmult_true == bmult_pred) else 1
  
  # compute distance metrics
  rating_dist = abs(BINS_RATING.index(rating_pred) - BINS_RATING.index(rating_true))
  bmult_dist = abs(BINS_BMULT.index(bmult_pred) - BINS_BMULT.index(bmult_true))

  # accumulate the sum of squared-differences
  sqdiff_rating += math.pow(rating_dist, 2)
  sqdiff_bmult += math.pow(bmult_dist, 2)

  # collect error distribution stats for a histogram
  hist_rating_true.append(rating_true)
  hist_rating_pred.append(rating_pred)
  hist_rating_dist.append(rating_dist)

  hist_bmult_true.append(bmult_true)
  hist_bmult_pred.append(bmult_pred)
  hist_bmult_dist.append(bmult_dist)

  result_rating = 'PASS' if (rating_true == rating_pred) else 'FAIL'
  result_bmult = 'PASS' if (bmult_true == bmult_pred) else 'FAIL'

  print('%s|%s|%s|%s|%s|%s' % (movie_id, 'RATING', result_rating, rating_true, rating_pred, rating_dist))
  print('%s|%s|%s|%s|%s|%s' % (movie_id, 'BMULT ', result_bmult, bmult_true, bmult_pred, bmult_dist))

  f_rating.write('%s|%s|%s|%s|%s\n' % (movie_id, result_rating, rating_true, rating_pred, rating_dist))
  f_bmult.write('%s|%s|%s|%s|%s\n' % (movie_id, result_bmult, bmult_true, bmult_pred, bmult_dist))

  movie_id = f_mlist.readline().strip()
  # end of test loop

f_mlist.close()
f_rating.close()
f_bmult.close()

error_rating = float(error_rating) / test_size
error_bmult = float(error_bmult) / test_size
sqdiff_rating = float(sqdiff_rating) / test_size
sqdiff_bmult = float(sqdiff_bmult) / test_size

f_stats.write('test_size=%d\n' % test_size)
f_stats.write('error_rating=%f\n' % error_rating)
f_stats.write('error_bmult=%f\n' % error_bmult)
f_stats.write('sqdiff_rating=%f\n' % sqdiff_rating)
f_stats.write('sqdiff_bmult=%f\n' % sqdiff_bmult)

f_stats.close()

# generate histograms for experimental clarity
import matplotlib.pyplot as plt
import numpy as np

rating_titles = ['hist_rating_true', 'hist_rating_pred', 'hist_rating_dist']
rating_distributions = ['hist_rating_true', 'hist_rating_pred', 'hist_rating_dist']
colors = ['g','b','r']

# visualize true and predicted ratings in a histogram
x1 = map(int, hist_rating_true)
x2 = map(int, hist_rating_pred)
x = [x1,x2]
b = [b-0.5 for b in range(len(BINS_RATING)+1)]
n, bins, patches = plt.hist(x, bins=b, alpha=0.75)
# pdb.set_trace()
plt.xlabel('Rating')
plt.ylabel('Frequency')
plt.title('Histogram of Movie Ratings')
plt.xlim(-0.5,10.5)
a = plt.gca()
a.set_xticks(map(int,BINS_RATING))
plt.grid(True)
plt.savefig('results/figures/hist_rating_compare.png', bbox_inches='tight')
plt.close()

# visualize the difference in predictions in a histogram
x = map(int, hist_rating_dist)
b = [b-0.5 for b in range(len(BINS_RATING)+1)]
n, bins, patches = plt.hist(x, bins=b, facecolor='r', alpha=0.75)
plt.xlabel('|Rating{true} - Rating{pred}|')
plt.ylabel('Frequency')
plt.title('Histogram of |Rating{true} - Rating{pred}|')
plt.xlim(-0.5,10.5)
a = plt.gca()
a.set_xticks(map(int,BINS_RATING))
plt.grid(True)
plt.savefig('results/figures/hist_rating_dist.png', bbox_inches='tight')
plt.close()

## unused ~ leave here for now.
# for t,d,clr in zip(rating_titles, rating_distributions, colors):
#   x = map(int, eval(d))
#   b = [b-0.5 for b in range(len(BINS_RATING)+1)]
#   n, bins, patches = plt.hist(x, bins=b, facecolor=clr, alpha=0.75)
#   # pdb.set_trace()
#   plt.xlabel('Rating')
#   plt.ylabel('Frequency')
#   plt.title(t)
#   plt.xlim(-0.5,10.5)
#   a = plt.gca()
#   a.set_xticks(map(int,BINS_RATING))
#   plt.grid(True)
#   plt.savefig('results/figures/%s.png' % t, bbox_inches='tight')
#   plt.close()

bmult_titles = ['hist_bmult_true', 'hist_bmult_pred', 'hist_bmult_dist']
bmult_distributions = ['hist_bmult_true', 'hist_bmult_pred', 'hist_bmult_dist']

# visualize true and predicted bmults in a histogram
x1 = [BINS_BMULT.index(v) for v in hist_bmult_true]
x2 = [BINS_BMULT.index(v) for v in hist_bmult_pred]
x = [x1, x2]
b = [b-0.5 for b in range(len(BINS_BMULT)+1)]
n, bins, patches = plt.hist(x, bins=b, alpha=0.75)
plt.xlabel('Budget-Multiplier')
plt.ylabel('Frequency')
plt.title('Histogram of Budget Multipliers')
plt.xlim(-0.5, len(BINS_BMULT)+0.5)
a = plt.gca()
a.set_xticks(range(len(BINS_BMULT)))
a.set_xticklabels(BINS_BMULT)
plt.grid(True)
plt.savefig('results/figures/hist_bmult_compare.png', bbox_inches='tight')
plt.close()

# visualize the difference in predictions in a histogram
x = map(int, hist_rating_dist)
b = [b-0.5 for b in range(len(BINS_RATING)+1)]
n, bins, patches = plt.hist(x, bins=b, facecolor='r', alpha=0.75)
plt.xlabel('|BMult{true} - BMult{pred}|')
plt.ylabel('Frequency')
plt.title('Histogram of |BMult{true} - BMult{pred}|')
plt.xlim(-0.5,len(BINS_BMULT)-0.5)
a = plt.gca()
a.set_xticks(range(len(BINS_BMULT)))
# a.set_xticklabels(BINS_BMULT)
plt.grid(True)
plt.savefig('results/figures/hist_bmult_dist.png', bbox_inches='tight')
plt.close()

# report descriptive statistics to the console
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print 'NAIVE BAYES TEST STATISTICS'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print 'test_size=%d' % test_size
print 'error_rating=%f' % error_rating
print 'error_bmult=%f' % error_bmult
print 'sqdif_rating=%f' % sqdiff_rating
print 'sqdiff_bmult=%f' % sqdiff_bmult

# fin
