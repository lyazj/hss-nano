import os
import json

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Sample:

    def __init__(self, directory):  # directory: to the sample DB

        self.directory = directory

        # Load DAS dataset name.
        dataset = open(os.path.join(directory, 'dataset')).read().strip()
        self.dataset = dataset

        # Load DAS file list.
        try:
            filelist = json.load(open(os.path.join(directory, 'filelist')))
        except Exception:
            print('querying dataset %s' % dataset)
            filelist = os.popen("dasgoclient -json -query='file dataset=%s'" % dataset).read()
            if not filelist: raise RuntimeError('failed querying dataset %s' % dataset)
            open(os.path.join(directory, 'filelist'), 'w').write(filelist)
            filelist = json.loads(filelist)
        self.filelist = filelist

    def __repr__(self):

        return '<%d files in %s>' % (len(self.filelist), self.dataset)

    def select(self, target_nevents=None, prefix='root://xrootd-cms.infn.it/'):

        filelist = []
        nevents = 0
        for file in self.filelist:
            if target_nevents is not None and nevents >= target_nevents: break
            file = file['file'][0]
            nevents += file['nevents']
            filelist.append(prefix + file['name'])
        return filelist

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
