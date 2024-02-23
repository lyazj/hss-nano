#!/bin/bash

stdbuf -oL cmsDriver.py \
    --python_filename test_MiniAODv2_UL18.py \
    -n 1000 \
    --mc \
    --eventcontent NANOAODSIM \
    --datatier NANOAODSIM \
    --conditions 106X_upgrade2018_realistic_v15_L1v1 \
    --step NANO \
    --nThreads 1 \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
    --filein file:HIG-RunIISummer20UL18MiniAODv2-02334_15946930_1001_1.root \
    --fileout file:HIG-RunIISummer20UL18CustomizedNanoAODv9-02334_15946930_1001_1.root \
    2>&1 | tee test_MiniAODv2_UL18.log
