## Install github repo
`git clone https://github.com/GEOS-ESM/GEOSmie.git`

## Zip file from teams chat
### environment.yml
move environment file into the root of GEOSmie directory

## Conda needs to be installed and activated
`conda init --all`
`conda env create --file environment.yml -n geosmile`
`conda activate geosmile`

## Install pymiecoated
`cd pymiecoated`
`python setup.py install`

## Run test
`cd ..` # go to root
`python ./runoptics.py --name geosparticles/bc.json`
This will run a test of particle bc

`python ./runbands.py --filename integ-bc-raw.nc`

`conda install conda-forge::ncview`

`ncview integ-bc-raw.RRTMG.nc`

## Timing of long test
Try to time 
`./generate_geos_optics.sh`
It runs multiple particle examples
We should time this for our local runtimes for our report

## Try to install on ICE