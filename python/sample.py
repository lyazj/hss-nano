#!/usr/bin/env python3

import os

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Sample:

    xrootd_domain = 'xrootd-cms.infn.it'

    def __init__(self, directory):  # directory: to the sample DB

        self.directory = directory

        # Load DAS dataset name.
        dataset = open(os.path.join(directory, 'dataset')).read().strip()
        self.dataset = dataset

        # Load DAS file list.
        try:
            filelist = open(os.path.join(directory, 'filelist')).read().strip().split('\n')
        except FileNotFoundError:
            filelist = os.popen(f"dasgoclient -query='file dataset={dataset}'").read()
            if not filelist: raise RuntimeError(f'failed querying dataset {dataset}')
            open(os.path.join(directory, 'filelist'), 'w').write(filelist)
            filelist = filelist.strip().split('\n')
        self.filelist = filelist

class SampleManager:

    def __init__(self, directory=None):  # directory: to the 'samples' DB

        directory = directory or os.path.join(basedir, 'samples')
        self.directory = directory
        samples = { }
        self.samples = samples

        # Directory level 1/2: MCM dataset names
        datasets = os.listdir(self.directory)
        for dataset in datasets:
            dataset_dir = os.path.join(self.directory, dataset)
            if not os.path.isdir(dataset_dir): continue

            dataset_samples = { }
            samples[dataset] = dataset_samples

            # Directory level 2/2: MCM prepids
            prepids = os.listdir(dataset_dir)
            for prepid in prepids:
                prepid_dir = os.path.join(dataset_dir, prepid)
                if not os.path.isdir(prepid_dir): continue

                dataset_samples[prepid] = Sample(prepid_dir)  # placeholder

print(SampleManager().samples)
