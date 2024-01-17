#!/usr/bin/env python2

from __future__ import print_function
import os
import sys
import re

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'python'))

PREFETCH_PREFIX = 'root://eosuser.cern.ch//eos/user/l/legao/hss/prefetch'

import sample

samples = sample.list_samples()

sys.argv.append('root://xrootd-cms-global.cern.ch//store/mc/RunIISummer20UL18MiniAODv2/Z1JetsToNuNu_M-50_LHEFilterPtZ-400ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/40000/B8CB7A75-9E0F-114E-9E33-A25142BB071F.root')  # DEBUG
if len(sys.argv) < 2 or len(sys.argv) > 4:
    print('Usage: %s <url>' % os.path.basename(sys.argv[0]))
    sys.exit(0)
url = sys.argv[1]

name, dataset = re.search(r'^root://[^/]*/(/store/mc/[^/]*/([^/]*)/MINIAODSIM/.*\.root)$', url).groups()
for sample in samples[dataset].values():
    for file in sample.filelist:
        file = file['file'][0]
        if file['name'] == name:
            if os.system("xrdcp '%s' '%s'" % (url, PREFETCH_PREFIX + name)) == 0:
                open(os.path.join(sample.directory, 'prefetch-%s' % os.path.basename(name)), 'w').write(PREFETCH_PREFIX + name)
