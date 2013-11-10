Eucalyptus Static mode installation scripts
-------------------------------------------

1. Files:
  - topo.ns: the topology specification for Emulab.
  - "output_files" folder: logs collected during installation.
  - DEPLOY.cc/DEPLOY.clc/DEPLOY.nc1: scripts to install and configure CC/CLC/NC1 respectively.
  - Other files: small scripts each does a specific task (refer to DEPLOY.xx for information). 
  Some are temporary logs/configuration files.
  
2. Installation:
  - Run DEPLOY.cc/DEPLOY.clc/DEPLOY.nc1 on CC/CLC/NC1 respectively.
  - The DEPLOY.xx scripts will invoke other scripts to do their task (DEPLOY.xx are readable).
  - Notes: 
    + The step "loading admin credentials" has to be execute in a real terminal 
  (by typing the command "source eucarc" mannually in a terminal). Please do so if the DEPLOY.clc 
  script fails to load the credential.
    + Since installations are running seperately on 3 different nodes, the order of installation 
    is maintained by USER (it means user has to decide which steps on which node have to be done 
    first before doing the other steps on other nodes). Refer to Eucalyptus installation guide.
    http://www.eucalyptus.com/docs/eucalyptus/3.3/install-guide/
  
