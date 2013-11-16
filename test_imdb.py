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
from imdbutils import stru, pID, ratingkey, bmultkey

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

  actor_list = movie.get('cast')
  actor_ids = []
  if actor_list:
    for i in xrange(min(MAX_ACTORS, len(actor_list))):
      actor_ids.append(pID(actor_list[i]))
  
  director_list = movie.get('director')
  director_ids = []
  if director_list:
    for i in xrange(len(director_list)):
      director_ids.append(pID(director_list[i]))

  producer_list = movie.get('producer')
  producer_ids = []
  if producer_list:
    for i in xrange(len(producer_list)):
      producer_ids.append(pID(producer_list[i]))
 
  composer_list = movie.get('composer')
  composer_ids = []
  if composer_list:
    for i in xrange(len(composer_list)):
      composer_ids.append(pID(composer_list[i]))

  cinetog_list = movie.get('cinematographer')
  cinetog_ids = []
  if cinetog_list:
    for i in xrange(len(cinetog_list)):
      cinetog_ids.append(pID(cinetog_list[i]))

  distro_list = movie.get('distributors')
  distro_ids = []
  if distro_list:
    for i in xrange(len(distro_list)):
      country = distro_list[i].__dict['data'].get('country')
      if country:
        if stru(country) == '[us]':
          distro_id.append(str(distro_list[i].__dict__['companyID']))

  genre_list = movie.get('genre')
  genres = []
  if genre_list:
    for i in xrange(len(genre_list)):
      genres.append(stru(genre_list[i]))

  mpaa_rating = mov.get('mpaa')
  mpaa = []
  if mpaa_rating:
    mpaa.append(stru(mpaa_rating.split()[1]))

  rating = movie['rating']
  i = 0
  j = 0
  while stru(movie['business']['budget'][i])[0] != '$':
    i += 1
  while stru(movie['business']['gross'][j]).find('(USA)') == -1 or stru(mov['business']['gross'][j][0] != '$':
    j += 1
  budget = int(stru(mov['business']['budget'][i])[1:].split()[0].replace(',',''))
  gross = int(stru(mov['business']['gross'][j]).split()[0][1:].replace(',',''))

  bmult = float(gross)/budget
  rkey = ratingkey(rating)
  bkey = bmultkey(bmult)

  movie_dict = {}
  # inputs
  movie_dict['actor'] = actor_ids
  movie_dict['director'] = director_ids
  movie_dict['producer'] = producer_ids
  movie_dict['composer'] = composer_ids
  movie_dict['cinetog'] = cinetog_ids
  movie_dict['distro'] = distro_ids
  movie_dict['genre'] = genres
  movie_dict['mpaa'] = mpaa
  # outputs
  movie_dict['rating'] = rkey
  movie_dict['bmult'] = bkey
    
  return movie_dict
  

#distro
#genre
#mpaa

predict('2553878')



  
