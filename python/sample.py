from __future__ import print_function
import os
import json
import requests

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Sample:

    def __init__(self, directory):  # directory: to the sample DB

        self.directory = directory
        self.mcm_prepid = os.path.basename(self.directory)
        self.mcm_dataset = os.path.basename(os.path.dirname(self.directory))

        # Load DAS dataset name.
        dataset = open(os.path.join(directory, 'dataset')).read().strip()
        self.dataset = dataset

        # Load DAS file list.
        try:
            filelist = json.load(open(os.path.join(directory, 'filelist')))
        except Exception:
            print('querying dataset %s' % dataset)
            filelist = self.query(dataset)
            if not filelist: raise RuntimeError('failed querying dataset %s' % dataset)
            open(os.path.join(directory, 'filelist'), 'w').write(filelist)
            filelist = json.loads(filelist)
        self.filelist = filelist

        # Load optional event number upper limit.
        try:
            self.maxevent = self.adjust_maxevent(int(open(os.path.join(directory, 'maxevent')).read()))
        except Exception:
            self.maxevent = None

        # Load XSDB information.
        try:
            xsdb = json.load(open(os.path.join(directory, 'xsdb')))
        except Exception:
            print('querying xsdb %s' % dataset)
            xsdb = requests.post('https://xsdb-temp.app.cern.ch/api/search', json={
                'orderBy': [],
                'pagination': { 'currentPage': 0, 'pageSize': 0 },
                'search': { 'DAS': self.mcm_dataset },
            }).text
            open(os.path.join(directory, 'xsdb'), 'w').write(xsdb)
            xsdb = json.loads(xsdb)
        self.xsdb = xsdb

        # Load cross section.
        try:
            xs = json.load(open(os.path.join(directory, 'xs')))
        except Exception:
            xs = self.generate_xs()
            open(os.path.join(directory, 'xs'), 'w').write(json.dumps(xs))
        self.xs = xs

    def __repr__(self):

        return '<%d files in %s>' % (len(self.filelist), self.dataset)

    def query(self, dataset):

        if dataset[:5] != 'file:':
            return os.popen("dasgoclient -json -query='file dataset=%s'" % dataset).read()

        # Special case: local directory.
        directory = dataset[5:]
        filelist = []
        import ROOT
        for file in os.listdir(directory):
            if file[-5:] != '.root': continue
            file = os.path.join(directory, file)
            if os.stat(file).st_size < 1024 * 1024: continue
            tfile = ROOT.TFile(file)
            nevents = tfile.Get('Events').GetEntriesFast()
            tfile.Close()
            filelist.append({'file': [{'name': 'file:' + file, 'nevents': nevents}]})
            print('%d root files found' % len(filelist))
        return json.dumps(filelist)

    def select(self, target_nevents=None, prefix='root://xrootd-cms.infn.it/'):

        if target_nevents is None: target_nevents = self.maxevent
        filelist = []
        nevents = 0
        for file in self.filelist:
            if target_nevents is not None and nevents >= target_nevents: break
            file = file['file'][0]
            name = file['name']
            if name[:5] != 'file:': name = prefix + name
            else: name = name[5:]
            nevents += file['nevents']
            filelist.append((file['nevents'], name))
        return filelist

    def count(self):
        return sum(file['file'][0]['nevents'] for file in self.filelist)

    def adjust_maxevent(self, maxevent):
        filelist = self.select(maxevent)
        return sum(file[0] for file in filelist)

    def generate_xs(self):
        xsdb = self.xsdb
        if len(xsdb) == 0: return
        if len(xsdb) == 1: return xsdb[0]
        for i, item in enumerate(xsdb):
            print('[%d]' % i, item['status'], item['MCM'], item['energy'],
                  item['cross_section'], item['total_uncertainty'], sep='\t')
        while True:
            try:
                return xsdb[int(input('Choice for %s: ' % self.mcm_prepid))]
            except Exception:
                pass

def list_samples(directory=None):  # directory: to the 'samples' DB

    directory = directory or os.path.join(basedir, 'samples')
    samples = { }

    # Directory level 1/2: MCM dataset names
    datasets = os.listdir(directory)
    for dataset in datasets:
        dataset_dir = os.path.join(directory, dataset)
        if not os.path.isdir(dataset_dir): continue

        dataset_samples = { }
        samples[dataset] = dataset_samples

        # Directory level 2/2: MCM prepids
        prepids = os.listdir(dataset_dir)
        for prepid in prepids:
            prepid_dir = os.path.join(dataset_dir, prepid)
            if not os.path.isdir(prepid_dir): continue

            dataset_samples[prepid] = Sample(prepid_dir)  # placeholder

    return samples
