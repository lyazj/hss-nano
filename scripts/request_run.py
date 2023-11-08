#!/usr/bin/env python3

from __future__ import print_function
import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'python'))

import sample

samples = sample.list_samples()

if len(sys.argv) == 1:
    for dataset, dataset_samples in samples.items():
        print('-', dataset)
        for prepid in dataset_samples.keys():
            print(' ', '+', prepid)
    sys.exit(0)

def generate_x509up(x509up=None):
    x509up = x509up or os.path.abspath(os.path.join(basedir, 'scripts', 'x509up'))
    if os.system("voms-proxy-init -voms cms -valid 192:00 -out '%s'" % x509up):
        raise RuntimeError('error generating x509 user proxy')
    return x509up

def check_success(fileout):
    try:
        return os.stat(fileout).st_size > 1024*1024
    except Exception:
        return False

def request(dataset, prepid, sample, target_nevents=None, outdir='/eos/user/l/legao/hss/samples/CustomizedNanoAOD'):
    jobstr = '''Universe = vanilla
Executable = %s

+ProjectName="cms.org.cern"

NTHREAD = 8
X509UP = %s
Arguments = $(NEVENT) $(NTHREAD) $(FILEIN) $(FILEOUT) $(X509UP)

requirements = (OpSysAndVer =?= "CentOS7")
request_cpus = 8
request_memory = 4096
x509userproxy = $(X509UP)

+JobFlavour = "tomorrow"

Log    = $(LOGPREFIX).log
Output = $(LOGPREFIX)_1.log
Error  = $(LOGPREFIX)_2.log

should_transfer_files = NO
Queue NEVENT, FILEIN, FILEOUT, LOGPREFIX from (
%s)'''
    executable = os.path.abspath(os.path.join(basedir, 'scripts', 'run.sh'))
    x509up = generate_x509up()
    queue = ''
    outdir, logdir = os.path.join(outdir, 'output', dataset, prepid), os.path.join(outdir, 'log', dataset, prepid)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(logdir, exist_ok=True)
    for nevents, filein in sample.select(target_nevents):
        filename = os.path.basename(filein)
        fileout = os.path.join(outdir, filename)
        if check_success(fileout): continue
        logprefix = os.path.join(logdir, os.path.splitext(filename)[0])
        queue += '%s, %s, %s, %s\n' % (nevents, filein, fileout, logprefix)
    jobfile = prepid + '.jdl'
    open(jobfile, 'w').write((jobstr % (executable, x509up, queue)).replace('/eos/', '/rbf/'))
    os.system("condor_submit -file '%s'" % jobfile)

for prepid in sys.argv[1:]:
    for dataset, dataset_samples in samples.items():
        if prepid not in dataset_samples: continue
        request(dataset, prepid, dataset_samples[prepid])
        break
    else:
        print('Error: prepid not recognized: %s' % prepid)
