"""
Test module ( package).

This module provides the MovieSage class, used to make 
user-rating and gross-budget-multiplier predictions about
a given movies.

Copyright 2013 Dan Cocuzzo <cocuzzo@cs.stanford.edu>
               Stephen Wu <shw@stanford.edu>

"""
import sys, os
import ConfigParser

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

FEATURES = cfg.get('Features', 'FEATURES')
BINS_RATING = cfg.get('OutputLabels', 'BINS_RATING')
BINS_BMULT = cfg.get('OutputLabels', 'BINS_BMULT')

cfg = ConfigParser.ConfigParser()
cfg.read(dbConfig)

IMDB_URI = cfg.get('URI', 'IMDB_URI')
# try:
#   trainingPath = cfg.get('Paths', 'training')
# except:
#   trainingPath = os.getcwd()

MODEL_DIR = 'nbmodel'

# print features
# print bins_rating
# print bins_bmult
# print imdbURI
# print trainingPath


# self.features = ['actor',
# features = ['actor',
#                  'director',
#                  'producer',
#                  'composer',
#                  'cinetog',
#                  'prodco',
#                  'genre',
#                  'mpaa',
#                  'runtime',
#                  'month',
#                  'budget'
#                 ]

# bins_rating = ['0','1','2','3','4','5','6','7','8','9','10']
# bins_bmult = ['[0-1)','[1-2)','[2-3)','[3-6)','[6+]']

# ia = IMDb('sql', uri='sqlite:///Users/dan/stanford/cs229/IMDbPY-4.9/sqldb/imdb.db')
# movie = ia.get_movie('2553878')

def predict(movie_id):
  """
  returns the predicted class labels (defined above) for 
  user-rating and gross-budget-mult by choosing the class 
  with the highest posterior probability
  """
  
  # generate custom movie dict by ingesting features from the database
  movie = hydrate(movie_id)
  
  # initialize posteriors
  pos_rating = [0] * len(BINS_RATING)
  pos_bmult = [0] * len(BINS_BMULT)
  
  for feat in FEATURES:
    for id_ in movie[feat]:
      for br in BINS_RATING:
        stmt = 'p_%s[id_][br]' % feat
        pos_rating[br] += eval(stmt)
      for bm in BINS_BMULT:
        stmt = 'p_%s[id_][bm]' % feat
        pos_bmult[bm] += eval(stmt)
  
  pred_rating = BINS_RATING.index(max(pos_bmult))
  pred_bmult = BINS_BMULT.index(max(pos_bmult))

  return (pred_rating, pred_bmult)

def hydrate(movie_id):
  from imdb import IMDb
  ia = IMDb('sql', uri=IMDB_URI)
  movie = ia.get_movie(str(movie_id))
  print movie.keys()
  # swuster i need you here


predict('2553878')



  