import sys
import pdb

# buckets the budget multiple
## V0
# def bmultkey(bmultiple):
#     if bmultiple < 1:
#         return '[0-1)'
#     elif bmultiple < 2:
#         return '[1-2)'
#     elif bmultiple < 3:
#         return '[2-3)'
#     elif bmultiple < 6:
#         return '[3-6)'
#     else: # bmultiple >= 6
#         return '[6+]';

## V1 12/8/13
# def bmultkey(bmultiple):
#     if bmultiple < 0.25:
#         return '[0-0.25)'
#     elif bmultiple < 0.5:
#         return '[0.25-0.5)'
#     elif bmultiple < 1:
#         return '[0.5-1)'
#     elif bmultiple < 2:
#         return '[1-2)'
#     elif bmultiple < 3:
#         return '[2-3)'
#     elif bmultiple < 6:
#         return '[3-6)'
#     else: # bmultiple >= 6
#         return '[6+]'

## V2 12/8/13
def bmultkey(bmultiple):
    if bmultiple < 0.5:
        return '[0-0.5)'
    elif bmultiple < 1:
        return '[0.5-1)'
    elif bmultiple < 2:
        return '[1-2)'
    else: # bmultiple >= 2
        return '[2+]'


# buckets the rating
def ratingkey(rating):
    return str(int(rating+0.5))

# returns PersonID in string form
def pID(person):
    return str(person.__dict__['personID'])

# convert unicode to string
def stru(string):
    return string.encode('ascii', 'replace')

# get budget as int
def get_budget(movie):
    i = 0
    while stru(movie['business']['budget'][i])[0] != '$':
        i += 1
    budget = int(stru(movie['business']['budget'][i])[1:].split()[0].replace(',',''))
    return budget

# get gross as int
def get_gross(movie):
    j = 0
    while stru(movie['business']['gross'][j]).find('(USA)') == -1 or stru(movie['business']['gross'][j])[0] != '$':
        j += 1
    gross = int(stru(movie['business']['gross'][j]).split()[0][1:].replace(',',''))
    return gross

# get bmult as (key) string
def get_bmult(movie):
    return bmultkey(float(get_gross(movie)) / get_budget(movie))

# get rating as (key) string
def get_rating(movie):
    return ratingkey(movie['rating'])

# get list of string actor IDs
def get_actors(movie, MAX_ACTORS):
    cast_list = movie.get('cast')
    actors = []
    if cast_list:
        for i in xrange(min(MAX_ACTORS, len(cast_list))):
            actors.append(pID(cast_list[i]))
    return actors

# get list of string director IDs
def get_directors(movie):
    director_list = movie.get('director')
    directors = []
    if director_list:
        for i in xrange(len(director_list)):
            directors.append(pID(director_list[i]))
    return directors

# get list of string producer IDs
def get_producers(movie):
    producer_list = movie.get('producer')
    producers = []
    if producer_list:
        for i in xrange(len(producer_list)):
            producers.append(pID(producer_list[i]))
    return producers

# get list of string composers IDs
def get_composers(movie):
    composer_list = movie.get('composer')
    composers = []
    if composer_list:
        for i in xrange(len(composer_list)):
            composers.append(pID(composer_list[i]))
    return composers

# get list of string cinematographer IDs
def get_cinetogs(movie):
    cinetog_list = movie.get('cinematographer')
    cinetogs = []
    if cinetog_list:
        for i in xrange(len(cinetog_list)):
            cinetogs.append(pID(cinetog_list[i]))
    return cinetogs

# get list of string distributor IDs - limited to US ditributors
def get_distros(movie):
    distro_list = movie.get('distributors')
    distros = []
    if distro_list:
        for i in xrange(len(distro_list)):
            country = distro_list[i].__dict__['data'].get('country')
            if country and stru(country) == '[us]':
                distros.append(str(distro_list[i].__dict__['companyID']))
    return distros

# get list of string genres
def get_genres(movie):
    genre_list = movie.get('genre')
    genres = []
    if genre_list:
        for i in xrange(len(genre_list)):
            genres.append(stru(genre_list[i]))
    return genres

# get list of mpaa ratings (should contain at most 1 element)
def get_mpaa(movie):
    mpaa = movie.get('mpaa')
    mpaas = []
    if mpaa:
        try:
            rating = stru(mpaa.split()[1])
        except:
            pass
        if rating in ['G','PG','PG-13','R','NC-17']:
            mpaas.append(rating)
    return mpaas

# converts a movie_id into a movie dict
def hydrate(movie_id, db, MAX_ACTORS):
    movie = db.get_movie(movie_id)
    movie_dict = {}
    movie_dict['actor'] = get_actors(movie, MAX_ACTORS)
    movie_dict['director'] = get_directors(movie)
    movie_dict['producer'] = get_producers(movie)
    movie_dict['composer'] = get_composers(movie)
    movie_dict['cinetog'] = get_cinetogs(movie)
    movie_dict['distro'] = get_distros(movie)
    movie_dict['genre'] = get_genres(movie)
    movie_dict['mpaa'] = get_mpaa(movie)
    movie_dict['rating'] = get_rating(movie)
    movie_dict['bmult'] = get_bmult(movie)

    # for debugging purposes
    movie_dict['title'] = stru(movie['long imdb canonical title'])

    return movie_dict

def mpaa_to_label(mpaa):
    if mpaa == 'G':
        return 0
    elif mpaa == 'PG':
        return 1
    elif mpaa == 'PG-13':
        return 2
    elif mpaa == 'R':
        return 3
    elif mpaa == 'NC-17':
        return 4
    else:
        return 0 # assume G/undefined rating otherwise

################################
# miscellaneous functions

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def list_diff(a, b):
        b = set(b)
        return [aa for aa in a if aa not in b]

def copy_anything(src, dst):
    import shutil
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise
