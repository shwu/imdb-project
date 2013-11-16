#!/usr/bin/python
import sys
import imdb
import cPickle

MOVIE_FILE = sys.argv[1]
NUM_TITLES = 2698956 # select count(*) from title
MAX_ACTORS = 10

'''
guarantees on movies:
- must be a movie
- must have a rating
- must not be an adult movie
- must have a 'business' section, and a 'budget' section within that
- must have 'gross' within 'business'
- must have 'opening weekend'
'''

# buckets the budget multiple
def bmultkey(bmultiple):
    if bmultiple < 1:
        return '[0-1)'
    elif bmultiple < 2:
        return '[1-2)'
    elif bmultiple < 3:
        return '[2-3)'
    elif bmultiple < 6:
        return '[3-6)'
    else: # bmultiple >= 6
        return '[6+]';

# buckets the rating
def ratingkey(rating):
    return str(int(rating+0.5))

# returns PersonID in string form
def pID(person):
    return str(person.__dict__['personID'])

# convert unicode to string
def stru(string):
    return string.encode('ascii', 'replace')

# MOVIE DICT (sample point) KEYS:

# actor: array of actor (person) ids
# director: array of director (person) ids
# producer: array of producer (person) ids
# composer: array of composer (person) ids
# cinetog: array of cinematographer (person) ids
# distro: array of distributor (company) ids
# genre: array of genre codes (custom)
# mpaa
# runtime
# month
# budget: [US budget bucket]
# gross: [US gross bucket]
# bmult: US gross as multiple of budget      string (dict key)
# rating: rating 0-10, single decimal point  string (dict key)


# LOGPROB DICTS

# p_actor (actors)
# p_director (director)
# p_producer (producers)
# p_composer (composers)
# p_cinetog (cinematographers)
# p_distro (distributor co's)
# p_genre (genres)
# p_mpaa (mpaa rating)
# p_runtime (runtime ~ 10 min buckets)
# p_month (US release month)
# p_budget (? US dollars)

# GROSS (output) probability
# p_gross (multiple of budget)
# p_rating (star rating)

print 'Initializing...'
p_actor = {}
p_director = {}
p_producer = {}
p_writer = {}
p_composer = {}
p_cinetog = {}
p_distro = {}
p_genre = {}
p_mpaa = {}
p_runtime = {}
p_month = {}
p_budget = {}
p_gross = {}
p_rating = {}

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
month_rating_count = {}

actor_bmult_count = {}
director_bmult_count = {}
producer_bmult_count = {}
composer_bmult_count = {}
cinetog_bmult_count = {}
distro_bmult_count = {}
genre_bmult_count = {}
mpaa_bmult_count = {}
month_bmult_count = {}

print 'Loading imdb.db...'
ia = imdb.IMDb('sql', uri='sqlite:///Users/dan/stanford/cs229/IMDbPY-4.9/sqldb/imdb.db')

# all pruning will be done in movielist
mlist = open(MOVIE_FILE, 'r')
mov_id = mlist.readline().strip()

while mov_id != '':
    print 'Loading Movie #' + mov_id
    mov = ia.get_movie(mov_id)
    print 'Processing ' + (mov['long imdb canonical title']),

    # generate output classes
    rating = mov['rating'] # guaranteed to exist
    budget = int(stru(mov['business']['budget'][0])[1:].replace(',',''))
    gross = int(stru(mov['business']['gross'][0]).split()[0][1:].replace(',',''))
    bmult = float(gross) / budget
    rkey = ratingkey(rating)
    bkey = bmultkey(bmult)    

    rating_count[rkey] = rating_count.setdefault(rkey, 0) + 1
    bmult_count[bkey] = bmult_count.setdefault(bkey, 0) + 1

    #for each actor in the cast list
    cast_list = mov.get('cast')
    if cast_list:
        for i in xrange(min(MAX_ACTORS, len(cast_list))):
            actor_id = pID(cast_list[i])
            actor_rating_count[actor_id][rkey] = actor_rating_count.setdefault(actor_id, {}).setdefault(rkey, 0) + 1
            actor_bmult_count[actor_id][bkey] = actor_bmult_count.setdefault(actor_id, {}).setdefault(bkey, 0) + 1

    #for each director
    director_list = mov.get('director')
    if director_list:
        for i in xrange(len(director_list)):
            director_id = pID(director_list[i])
            director_rating_count[director_id][rkey] = director_rating_count.setdefault(director_id, {}).setdefault(rkey, 0) + 1
            director_bmult_count[director_id][bkey] = director_bmult_count.setdefault(director_id, {}).setdefault(bkey, 0) + 1
        
    #for each producer
    producer_list = mov.get('producer')
    if producer_list:
        for i in xrange(len(producer_list)):
            producer_id = pID(producer_list[i])
            producer_rating_count[producer_id][rkey] = producer_rating_count.setdefault(producer_id, {}).setdefault(rkey, 0) + 1
            producer_bmult_count[producer_id][bkey] = producer_bmult_count.setdefault(producer_id, {}).setdefault(bkey, 0) + 1
    
    #for each composer
    composer_list = mov.get('composer')
    if composer_list:
        for i in xrange(len(composer_list)):
            composer_id = pID(composer_list[i])
            composer_rating_count[composer_id][rkey] = composer_rating_count.setdefault(composer_id, {}).setdefault(rkey, 0) + 1
            composer_bmult_count[composer_id][bkey] = composer_bmult_count.setdefault(composer_id, {}).setdefault(bkey, 0) + 1
                                
    #for each cinematographer
    cinetog_list = mov.get('cinematographer')
    if cinetog_list:
        for i in xrange(len(cinetog_list)):
            cinetog_id = pID(cinetog_list[i])
            cinetog_rating_count[cinetog_id][rkey] = cinetog_rating_count.setdefault(cinetog_id, {}).setdefault(rkey, 0) + 1
            cinetog_bmult_count[cinetog_id][bkey] = cinetog_bmult_count.setdefault(cinetog_id, {}).setdefault(bkey, 0) + 1
    
    #for each distributor
    distro_list = mov.get('distributors')
    if distro_list:
        for i in xrange(len(distro_list)):
            if stru(distro_list[i].__dict__['data']['country']) == '[us]':
                distro_id = str(distro_list[i].__dict__['companyID'])
                distro_rating_count[distro_id][rkey] = distro_rating_count.setdefault(distro_id, {}).setdefault(rkey, 0) + 1
                distro_bmult_count[distro_id][bkey] = distro_bmult_count.setdefault(distro_id, {}).setdefault(bkey, 0) + 1
    
    #for each genre
    genre_list = mov.get('genre')
    if genre_list:
        for i in xrange(len(genre_list)):
            genre = stru(genre_list[i])
            genre_rating_count[genre][rkey] = genre_rating_count.setdefault(genre, {}).setdefault(rkey, 0) + 1
            genre_bmult_count[genre][bkey] = genre_bmult_count.setdefault(genre, {}).setdefault(bkey, 0) + 1
    
    #mpaa rating
    mpaa = mov.get('mpaa')
    if mpaa:
        mpaa = stru(mpaa.split()[1])
        mpaa_rating_count[mpaa][rkey] = mpaa_rating_count.setdefault(mpaa, {}).setdefault(rkey, 0) + 1
        mpaa_bmult_count[mpaa][bkey] = mpaa_bmult_count.setdefault(mpaa, {}).setdefault(bkey, 0) + 1
    
    #for each runtime jk we cant find runtime

    #release month
    month = stru(mov['business']['opening weekend'][0].split()[3])
    month_rating_count[month][rkey] = month_rating_count.setdefault(month, {}).setdefault(rkey, 0) + 1
    month_bmult_count[month][bkey] = month_bmult_count.setdefault(month, {}).setdefault(bkey, 0) + 1

    mov_id = mlist.readline().strip()
    print '...done'

fid = open('rating_count.pkl', 'wb')
cPickle.dump(rating_count, fid)
fid.close()

fid = open('actor_rating_count.pkl', 'wb')
cPickle.dump(actor_rating_count, fid)
fid.close()

''' other dicts, to be pickled
actor_rating_count = {} # actor_rating_count['actor_id']['ratingkey'] gives count of that actor in rating
director_rating_count = {}
producer_rating_count = {}
composer_rating_count = {}
cinetog_rating_count = {}
distro_rating_count = {}
genre_rating_count = {}
mpaa_rating_count = {}
month_rating_count = {}

actor_bmult_count = {}
director_bmult_count = {}
producer_bmult_count = {}
composer_bmult_count = {}
cinetog_bmult_count = {}
distro_bmult_count = {}
genre_bmult_count = {}
mpaa_bmult_count = {}
month_bmult_count = {}
'''
