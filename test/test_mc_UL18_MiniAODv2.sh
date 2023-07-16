#!/bin/bash

stdbuf -oL cmsDriver.py \
    --python_filename test_mc_UL18_MiniAODv2.py \
    -n 1000 \
    --mc \
    --eventcontent NANOAODSIM \
    --datatier NANOAODSIM \
    --conditions 106X_upgrade2018_realistic_v15_L1v1 \
    --step NANO \
    --nThreads 1 \
    --era Run2_2018,run2_nanoAOD_106Xv2 \
    --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
    --filein /store/mc/RunIISummer20UL18MiniAODv2/WplusH_HToCC_WToLNu_M-125_TuneCP5_13TeV-powheg-pythia8/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/A4FFC5A7-79DF-FE4B-A515-1F3EA0513509.root \
    --fileout file:HIG-RunIISummer20UL18CustomizedNanoAOD-mc-A4FFC5A7-79DF-FE4B-A515-1F3EA0513509.root \
    2>&1 | tee test_mc_UL18_MiniAODv2.log
