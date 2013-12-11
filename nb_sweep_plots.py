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
  SWEEP_DIR = sys.argv[1]
  MODEL_TYPE = sys.argv[2]
  PARAM_NAME = sys.argv[3]
  PARAM_STEP_DESC = sys.argv[4]
  ptmp = PARAM_STEP_DESC.split(':')
  pmin = int(ptmp[0])
  pstep = int(ptmp[1])
  pmax = int(ptmp[2])
  PARAM_STEPS = range(pmin, pmax+pstep, pstep)
  FIGURES_DIR = os.path.join(SWEEP_DIR, 'figures')
except:
  print 'bad args. usage: ./nb_sweep_plots.py <SWEEP_DIR> <MODEL_TYPE> <PARAM_NAME> <PARAM_MIN:PARAM_STEP:PARAM_MAX>'
  sys.exit(1);

try:
  os.mkdir(FIGURES_DIR)
except:
  pass

print 'generating plots for MODEL_TYPE=%s, %s=[%d:%d:%d] for NB_SWEEP results in: %s' % (MODEL_TYPE, PARAM_NAME, pmin, pstep, pmax, SWEEP_DIR)

error_rating  = []
diff_rating   = []
sqdiff_rating = []

error_bmult  = []
diff_bmult   = []
sqdiff_bmult = []

for p in PARAM_STEPS:
  stats_file = os.path.join(SWEEP_DIR, 'results_%s.%d' % (MODEL_TYPE, p), STATS_FILE)
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


import matplotlib.pyplot as plt

################
## ERROR plots
################

BASE_ERROR_RATING = 1-(1/float(len(BINS_RATING)))
BASE_ERROR_BMULT = 1-(1/float(len(BINS_BMULT)))

XAXIS = PARAM_STEPS

# pdb.set_trace()

# make dat shit POP!
pr1, = plt.plot(XAXIS, [BASE_ERROR_RATING for i in range(len(PARAM_STEPS))], 'r--')
pr2, = plt.plot(XAXIS, error_rating, 'ro')
plt.plot(XAXIS, error_rating, 'r:')
pb1, = plt.plot(XAXIS, [BASE_ERROR_BMULT for i in range(len(PARAM_STEPS))], 'b--')
pb2, = plt.plot(XAXIS, error_bmult, 'bo')
plt.plot(XAXIS, error_bmult, 'b:')
plt.xlabel('MAX_ACTORS Model Parameter')
plt.ylabel('Error Rate')
plt.title('Naive-Bayes Parameter Tuning / Learning Curve: Training Error')
plt.grid(True)
plt.xlim(pmin-float(pstep)/2, pmax+float(pstep)/2)
plt.ylim(0,1)
ax = plt.gca()
ax.set_xticks(XAXIS)
ax.legend([pr1, pr2, pb1, pb2], 
          ["Random RATING error", "Naive-Bayes RATING pred. error", "Random BMULT error", "Naive-Bayes BMULT pred. error"],
          scatterpoints=1,
          loc='center right')
plt.show()
fig_path = os.path.join(FIGURES_DIR, 'psweep_error.png')
plt.savefig(fig_path)
plt.close()

################
## SQDIFF plots
################

pr1, = plt.plot(XAXIS, sqdiff_rating, 'ro')
plt.plot(XAXIS, sqdiff_rating, 'r:')
pb1, = plt.plot(XAXIS, sqdiff_bmult, 'bo')
plt.plot(XAXIS, sqdiff_bmult, 'b:')
plt.xlabel('MAX_ACTOR Model Parameter')
plt.ylabel('|Truth - Prediction|^2')
plt.title('Naive-Bayes Parameter Tuning / Learning Curve: Mean-Squared Error')
plt.grid(True)
plt.xlim(pmin-float(pstep)/2, pmax+float(pstep)/2)
plt.ylim(0,3)
ax = plt.gca()
ax.set_xticks(XAXIS)
ax.legend([pr1, pb1],
          ["Naive-Bayes RATING pred. MSE", "Naive-Bayes BMULT pred. MSE"],
          loc='upper right')
plt.show()
fig_path = os.path.join(FIGURES_DIR, 'psweep_sqdiff.png')
plt.savefig(fig_path)
plt.close()





