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
