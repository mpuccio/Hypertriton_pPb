import os

if not os.path.exists("Trees"):
        os.makedirs("Trees")

if not os.path.exists("Tables"):
        os.makedirs("Tables")

if not os.path.exists("Utils"):
        os.makedirs("Utils")

if not os.path.exists("Trees/HyperTritonTree_13bc.root"):
    os.system("scp lxplus.cern.ch:/eos/user/h/hypertriton/trees/2Body/HyperTritonTree_13bc.root  Trees/.")

if not os.path.exists("Trees/HyperTritonTree_16qt.root"):
    os.system("scp lxplus.cern.ch:/eos/user/h/hypertriton/trees/2Body/HyperTritonTree_16qt.root  Trees/.")

if not os.path.exists("Trees/HyperTritonTree_16qt_LS.root"):
    os.system("scp lxplus.cern.ch:/eos/user/h/hypertriton/trees/2Body/HyperTritonTree_16qt_LS.root  Trees/.")

if not os.path.exists("Trees/HyperTritonTree_17d.root"):
    os.system("scp lxplus.cern.ch:/eos/user/h/hypertriton/trees/2Body/HyperTritonTree_17d.root  Trees/.")

if not os.path.exists("Utils/AnalysisResults_pPb.root"):
    os.system("scp lxplus.cern.ch:/eos/user/h/hypertriton/trees/2Body/AnalysisResults_pPb.root  Utils/.")