#!/usr/bin/env python2

from __future__ import print_function
import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'python'))

import sample

samples = sample.list_samples()

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print('Usage: %s [ <prepid> [ <nevent> [ <dryrun> ] ] ]' % os.path.basename(sys.argv[0]))
    print('Available prepids:')
    for dataset, dataset_samples in samples.items():
        print('-', dataset)
        for prepid in dataset_samples.keys():
            print(' ', '+', prepid)
    sys.exit(0)

def generate_x509up(x509up=None):
    x509up = x509up or os.path.abspath(os.path.join(basedir, 'scripts', 'x509up'))
    if os.popen("2>/dev/null voms-proxy-info --file '%s'" % x509up).read().find('timeleft  : 191') < 0:
        if os.system("voms-proxy-init -voms cms -valid 192:00 -out '%s'" % x509up):
            raise RuntimeError('error generating x509 user proxy')
    return x509up

def check_success(fileout):
    os.system("touch '%s'" % fileout)
    return os.stat(fileout).st_size > 1024*1024

def request(dataset, prepid, sample, target_nevents=None, dryrun=False, outdir='/eos/user/l/legao/hss/samples/CustomizedNanoAOD'):
    jobstr = '''Universe = vanilla
Executable = %s

+ProjectName="cms.org.cern"

X509UP = %s
PROG = %s
NTHREAD = 8
Arguments = $(X509UP) $(PROG) $(NEVENT) $(NTHREAD) $(FILEIN) $(FILEOUT)

requirements = (OpSysAndVer =?= "CentOS7")
request_cpus = 8
request_memory = 4096
use_x509userproxy = True
x509userproxy = $(X509UP)

+JobFlavour = "tomorrow"

Log    = $(LOGPREFIX).log
Output = $(LOGPREFIX)_1.log
Error  = $(LOGPREFIX)_2.log

should_transfer_files = NO
Queue NEVENT, FILEIN, FILEOUT, LOGPREFIX from (
%s)'''
    executable = os.path.abspath(os.path.join(basedir, 'scripts', 'x509run'))
    x509up = generate_x509up()
    prog = os.path.abspath(os.path.join(basedir, 'scripts', 'run.sh'))
    outdir = os.path.join(outdir, dataset, prepid)
    logdir = os.path.join(basedir, 'scripts', 'log', dataset, prepid)
    if os.system("mkdir -p '%s' '%s'" % (outdir, logdir)):
        raise RuntimeError('error making directories')
    queue = ''
    for nevents, filein in sample.select(target_nevents):
        filename = os.path.basename(filein)
        fileout = os.path.join(outdir, filename.replace('MiniAODv2', 'CustomizedNanoAODv9'))
        success = check_success(fileout)
        print('%s %s' % (('Skipping' if success else 'Adding'), fileout))
        if success: continue
        logprefix = os.path.join(logdir, os.path.splitext(filename)[0])
        queue += '%s, %s, %s, %s\n' % (nevents, filein, fileout, logprefix)
    jobfile = prepid + '.jdl'
    open(jobfile, 'w').write(jobstr % (executable, x509up, prog, queue))
    ((print() or print) if dryrun else os.system)("condor_submit -file '%s'" % jobfile)

prepid = sys.argv[1]
nevent = (int(sys.argv[2]) if len(sys.argv) > 2 else None) or None
dryrun = eval(sys.argv[3]) if len(sys.argv) > 3 else False
for dataset, dataset_samples in samples.items():
    if prepid != 'all' and prepid not in dataset_samples: continue
    for pid in (dataset_samples.keys() if prepid == 'all' else [prepid]):
        request(dataset, pid, dataset_samples[pid], nevent, dryrun)
    if prepid != 'all': break
else:
    if prepid != 'all': raise RuntimeError('prepid not recognized: %s' % prepid)
