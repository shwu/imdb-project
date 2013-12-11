#!/usr/bin/python

"""
cross-validation plotting module

CS229 Final Project
Dan Cocuzzo <cocuzzo@cs.stanford.edu>
Stephen Wu <shw@stanford.edu>

"""
import sys, os
import ConfigParser

# debugger
import pdb

DEBUG=False

def debug(msg):
  if (DEBUG):
    print('debug: %s' % s)

#################################
########## main script ##########
#################################

PARAMS_CONFIG = 'params.cfg'
STATS_FILE = 'stats.out'

# parse the config file to obtain list of feature names
cfg = ConfigParser.ConfigParser()
cfg.read(PARAMS_CONFIG)

FEATURES = eval(cfg.get('Features', 'FEATURES'))
BINS_RATING = eval(cfg.get('OutputLabels', 'BINS_RATING'))
BINS_BMULT = eval(cfg.get('OutputLabels', 'BINS_BMULT'))
MAX_ACTORS = eval(cfg.get('Misc', 'MAX_ACTORS'))

try:
  XVAL_DIR = sys.argv[1]
  MODEL_TYPE = sys.argv[2]
  NUM_PARTITIONS = sys.argv[3]
  K = int(NUM_PARTITIONS)
  FIGURES_DIR = os.path.join(XVAL_DIR, 'figures')
except:
  print 'bad args. usage: ./xval_plots.py <XVAL_DIR> <MODEL_TYPE> <NUM_PARTITIONS>'
  sys.exit(1);

try:
  os.mkdir(FIGURES_DIR)
except:
  pass

print 'generating plots for MODEL_TYPE=%s, K=%s for XVAL results in: %s' % (MODEL_TYPE, NUM_PARTITIONS, XVAL_DIR)

error_rating  = []
diff_rating   = []
sqdiff_rating = []

error_bmult  = []
diff_bmult   = []
sqdiff_bmult = []

for k in range(1, K+1):
  stats_file = os.path.join(XVAL_DIR, 'results_%s.K%d' % (MODEL_TYPE, k), STATS_FILE)
  fid = open(stats_file)
  lines = fid.readlines()
  fid.close()
  for line in lines:
    val = float(line.split('=')[1])
    if line.find('error_rating') == 0:
      error_rating.append(val)
    elif line.find('error_bmult') == 0:
      error_bmult.append(val)
    elif line.find('diff_rating') == 0:
      diff_rating.append(val)
    elif line.find('diff_bmult') == 0:
      diff_bmult.append(val)
    elif line.find('sqdiff_rating') == 0:
      sqdiff_rating.append(val)
    elif line.find('sqdiff_bmult') == 0:
      sqdiff_bmult.append(val)
    else:
      debug('unknown entry in stats file: %s' % line)

# FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures')

# visualize true bmults in a histogram
# x = [BINS_BMULT.index(v) for v in hist_bmult_true]
# b = [b-0.5 for b in range(len(BINS_BMULT)+1)]
# n, bins, patches = plt.hist(x, bins=b, alpha=0.75, normed=True)
# plt.xlabel('Budget-Multiplier')
# plt.ylabel('Frequency')
# plt.title('Histogram of True Budget-Multipliers')
# plt.xlim(-0.5, len(BINS_BMULT)+0.5)
# a = plt.gca()
# a.set_xticks(range(len(BINS_BMULT)))
# a.set_xticklabels(BINS_BMULT)
# plt.grid(True)
# fig_path = os.path.join(FIGURES_DIR, 'hist_bmult_true.png')
# plt.savefig(fig_path, bbox_inches='tight')
# plt.close()


import matplotlib.pyplot as plt

################
## ERROR plots
################

BASE_ERROR_RATING = 1-(1/float(len(BINS_RATING)))
BASE_ERROR_BMULT = 1-(1/float(len(BINS_BMULT)))

XAXIS = range(1,K+1)

# make dat shit POP!
pr1, = plt.plot(XAXIS, [BASE_ERROR_RATING for i in range(1,K+1)], 'r--')
pr2, = plt.plot(XAXIS, error_rating, 'ro')
plt.plot(XAXIS, error_rating, 'r:')
pb1, = plt.plot(XAXIS, [BASE_ERROR_BMULT for i in range(1,K+1)], 'b--')
pb2, = plt.plot(XAXIS, error_bmult, 'bo')
plt.plot(XAXIS, error_bmult, 'b:')
plt.xlabel('Cross-Val Partition')
plt.ylabel('Error Rate')
plt.title('Cross-Validation: Naive Bayes Error Rate')
plt.grid(True)
plt.xlim(0.5, K+0.5)
plt.ylim(0,1)
ax = plt.gca()
ax.set_xticks(XAXIS)
ax.legend([pr1, pr2, pb1, pb2], 
          ["random rating",
           "naive bayes rating prediction", 
           "random bmult", 
           "naive bayes bmult prediction"],
          # ["random rating",
          #  "svm rating prediction", 
          #  "random bmult", 
          #  "svm bmult prediction"],
          scatterpoints=1,
          loc='lower right')
# plt.show()
fig_path = os.path.join(FIGURES_DIR, 'xval_error.png')
plt.savefig(fig_path)
plt.close()
print 'saved figure: %s' % fig_path

################
## SQDIFF plots
################

pr1, = plt.plot(XAXIS, sqdiff_rating, 'ro')
plt.plot(XAXIS, sqdiff_rating, 'r:')
pb1, = plt.plot(XAXIS, sqdiff_bmult, 'bo')
plt.plot(XAXIS, sqdiff_bmult, 'b:')
plt.xlabel('Cross-Val Partition')
plt.ylabel('M.S. Error')
plt.title('Cross-Validation: Naive Bayes Mean-Squared Error')
plt.grid(True)
plt.xlim(0.5, K+0.5)
plt.ylim(0,3.5)
ax = plt.gca()
ax.set_xticks(XAXIS)
ax.legend([pr1, pb1],
          ["naive bayes rating prediction", 
           "naive bayes bmult prediction"], 
          # ["svm rating prediction", 
          #  "svm bmult prediction"],
          loc='upper right')
# plt.show()
fig_path = os.path.join(FIGURES_DIR, 'xval_sqdiff.png')
plt.savefig(fig_path)
plt.close()
print 'saved figure: %s' % fig_path





