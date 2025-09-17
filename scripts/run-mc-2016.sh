#!/bin/bash

# Avoid "input: $HOME/.root.mimes, output: $HOME/.root.mimes" error.
# REF: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCrabFaq
if [ -z "${HOME}" ]; then
    export HOME="$(pwd)"
fi

if [ $# -lt 3 ]; then
    >&2 echo "usage: $(basename "$0") <nevent> <nthread> <file-in> <file-out>"
    exit 1
fi
NEVENT="$1"
NTHREAD="$2"
FILEIN="$3"
FILEOUT="$4"
if [ -z "${FILEOUT}" ]; then
    FILEOUT="${FILEIN/MiniAODv2/CustomizedNanoAODv9}"
fi
if [ "${FILEIN:0:7}" != "root://" ]; then FILEIN="file:${FILEIN}"; fi
if [ "${FILEOUT:0:7}" != "root://" ]; then FILEOUT="file:${FILEOUT}"; fi

set -ev
voms-proxy-info  # early stop on proxy error
source /cvmfs/cms.cern.ch/cmsset_default.sh
[ -r CMSSW_13_2_2 ] || cmsrel CMSSW_13_2_2
cd CMSSW_13_2_2/src
cmsenv

scram b -j$(cat /proc/cpuinfo | grep MHz | wc -l)

cmsDriver.py  --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --conditions 106X_mcRun2_asymptotic_v17 --step NANO --era Run2_2016,run2_nanoAOD_106Xv2 --python_filename HIG-RunIISummer20UL16NanoAODv12-00528_1_cfg.py --fileout file:HIG-RunIISummer20UL16NanoAODv12-00528.root --filein "${FILEIN}" --mc -n "${NEVENT}" --nThreads "${NTHREAD}" --customise_commands 'process.genWeightsTable.keepAllPSWeights = True' || exit $?
xrdcp -f HIG-RunIISummer20UL16NanoAODv12-00528.root "${FILEOUT}" || exit $?
