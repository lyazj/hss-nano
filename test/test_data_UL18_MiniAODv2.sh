#!/bin/bash

stdbuf -oL cmsDriver.py \
    --python_filename test_data_UL18_MiniAODv2.py \
    -n 1000 \
    --data \
    --eventcontent NANOAOD \
    --datatier NANOAOD \
    --conditions 106X_dataRun2_v37 \
    --step NANO \
    --nThreads 1 \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
    --filein /store/data/Run2018A/SingleMuon/MINIAOD/UL2018_MiniAODv2_GT36-v1/2820000/000EE25A-A8E8-1444-8A0B-0DBEBE5634FB.root \
    --fileout file:HIG-RunIISummer20UL18CustomizedNanoAOD-data-000EE25A-A8E8-1444-8A0B-0DBEBE5634FB.root \
    2>&1 | tee test_data_UL18_MiniAODv2.log
