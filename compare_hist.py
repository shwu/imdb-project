#!/usr/bin/python

"""
compare_hist.py plotting module

CS229 Final Project
Dan Cocuzzo <cocuzzo@cs.stanford.edu>
Stephen Wu <shw@stanford.edu>

"""
import sys, os
import ConfigParser
import pdb

paramsConfig = 'params.cfg'

# parse the config file to obtain list of feature names
cfg = ConfigParser.ConfigParser()
cfg.read(paramsConfig)

FEATURES = eval(cfg.get('Features', 'FEATURES'))
BINS_RATING = eval(cfg.get('OutputLabels', 'BINS_RATING'))
BINS_BMULT = eval(cfg.get('OutputLabels', 'BINS_BMULT'))
MAX_ACTORS = eval(cfg.get('Misc', 'MAX_ACTORS'))

nb_dir = sys.argv[1]
svm_dir = sys.argv[2]
FIGURES_DIR = sys.argv[3]

try:
  os.mkdir(FIGURES_DIR)
except:
  pass

nb_rating_file = os.path.join(nb_dir, 'rating.out')
nb_bmult_file = os.path.join(nb_dir, 'bmult.out')

svm_rating_file = os.path.join(svm_dir, 'rating.out')
svm_bmult_file = os.path.join(svm_dir, 'bmult.out')

rating_true = []
rating_nb = []
rating_svm = []
rating_abserr_nb = []
rating_abserr_svm = []

bmult_true = []
bmult_nb = []
bmult_svm = []
bmult_abserr_nb = []
bmult_abserr_svm = []

## parse naive bayes rating
fid = open(nb_rating_file)
lines = fid.readlines()
fid.close()
for line in lines:
  tokens = line.split('|')
  rating_true.append(int(tokens[2]))
  rating_nb.append(int(tokens[3]))
  rating_abserr_nb.append(int(tokens[4]))

# parse naive bayes bmult
fid = open(nb_bmult_file)
lines = fid.readlines()
fid.close()
for line in lines:
  tokens = line.split('|')
  bmult_true.append(BINS_BMULT.index(tokens[2]))
  bmult_nb.append(BINS_BMULT.index(tokens[3]))
  bmult_abserr_nb.append(int(tokens[4]))

# parse svm rating
fid = open(svm_rating_file)
lines = fid.readlines()
fid.close()
for line in lines:
  tokens = line.split('|')
  rating_svm.append(int(tokens[3]))
  rating_abserr_svm.append(int(tokens[4]))

# parse svm bmult
fid = open(svm_bmult_file)
lines = fid.readlines()
fid.close()
for line in lines:
  tokens = line.split('|')
  bmult_svm.append(int(tokens[3]))
  bmult_abserr_svm.append(int(tokens[4]))


## TODO: add confusion matrices above

###################################
## RATING distribution histograms
###################################

# visualize true and predicted ratings in a histogram
x = [rating_true, rating_nb, rating_svm]
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
fig_path = os.path.join(FIGURES_DIR, 'hist_rating_compare.png')
plt.savefig(fig_path, bbox_inches='tight')
# plt.show()
plt.close()

# visualize the difference in rating predictions in a histogram
x = [rating_abserr_nb, rating_abserr_svm]
b = [b-0.5 for b in range(len(BINS_RATING)+1)]
n, bins, patches = plt.hist(x, bins=b, facecolor='r', alpha=0.75)
plt.xlabel('|Rating{true} - Rating{pred}|')
plt.ylabel('Frequency')
plt.title('Histogram of |Error| in Rating Predictions')
plt.xlim(-0.5,10.5)
a = plt.gca()
a.set_xticks(map(int,BINS_RATING))
plt.grid(True)
fig_path = os.path.join(FIGURES_DIR, 'hist_rating_abserr.png')
plt.savefig(fig_path, bbox_inches='tight')
# plt.show()
plt.close()

###################################
## BMULT distribution histograms
###################################

# visualize true and predicted bmult in a histogram
x = [bmult_true, bmult_nb, bmult_svm]
b = [b-0.5 for b in range(len(BINS_RATING)+1)]
n, bins, patches = plt.hist(x, bins=b, alpha=0.75)
# pdb.set_trace()
plt.xlabel('BMult')
plt.ylabel('Frequency')
plt.title('Histogram of Movie Budget-Multiple Earnings')
plt.xlim(-0.5,len(BINS_BMULT)-0.5)
a = plt.gca()
a.set_xticks(range(len(BINS_BMULT)))
a.set_xticklabels(BINS_BMULT)
plt.grid(True)
fig_path = os.path.join(FIGURES_DIR, 'hist_bmult_compare.png')
plt.savefig(fig_path, bbox_inches='tight')
# plt.show()
plt.close()

# visualize the difference in bmult predictions in a histogram
x = [rating_abserr_nb, rating_abserr_svm]
b = [b-0.5 for b in range(len(BINS_RATING)+1)]
n, bins, patches = plt.hist(x, bins=b, facecolor='r', alpha=0.75)
plt.xlabel('|BMult{true} - BMult{pred}|')
plt.ylabel('Frequency')
plt.title('Histogram of |Error| in BMult predictions')
plt.xlim(-0.5,len(BINS_BMULT)-0.5)
a = plt.gca()
a.set_xticks(range(len(BINS_BMULT)))
plt.grid(True)
fig_path = os.path.join(FIGURES_DIR, 'hist_bmult_abserr.png')
plt.savefig(fig_path, bbox_inches='tight')
# plt.show()
plt.close()