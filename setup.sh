#!/usr/bin/bash

CONDA_ENV_NAME="geosmile"
ENV_FILE_PATH="environment.yml"
GIT_REPO_URL="https://github.com/GEOS-ESM/GEOSmie.git"
REPO_DIR_NAME="../GEOSmie"
HOSTNAME_CHECK="gatech.edu"

# --- Handle Git Repository ---
if [ -d "${REPO_DIR_NAME}" ]; then
    echo "--> Repository directory ${REPO_DIR_NAME} found. Updating..."
    cd "${REPO_DIR_NAME}" || { echo "Failed to cd into repo dir ${REPO_DIR_NAME}"; exit 1; }
    echo "    Current directory: $(pwd)"
    git pull
else
    echo "--> Cloning repository ${GIT_REPO_URL} into ${REPO_DIR_NAME}..."
    git clone "${GIT_REPO_URL}" "${REPO_DIR_NAME}"
    cd "${REPO_DIR_NAME}" || { echo "Failed to cd into repo dir ${REPO_DIR_NAME}"; exit 1; }
    echo "    Current directory: $(pwd)"
fi


cp "../VIP_PROJ2/${ENV_FILE_PATH}" .

echo "--> Checking for Conda environment: ${CONDA_ENV_NAME}"

HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"$HOSTNAME_CHECK"* ]]; then
    echo "--> Working on ICE"
    module load anaconda3
else
    echo "--> Working locally"
    which conda >/dev/null
    if [ $? -ne 0 ]; then echo "!!! conda has not been installed in this environment"; exit 1; fi
fi

CONDA_BASE_PATH=$(conda info --base)
if conda env list | grep -q "^${CONDA_ENV_NAME}\s"; then
    echo "--> Environment ${CONDA_ENV_NAME} exists. Activating and updating..."
    source activate base
    conda activate "${CONDA_ENV_NAME}"
    if [ $? -ne 0 ]; then echo "!!! Conda activate FAILED."; exit 1; fi
    echo "--> Updating environment from ${ENV_FILE_PATH}..."
    conda env update --name "${CONDA_ENV_NAME}" --file "${ENV_FILE_PATH}" --prune
else
    echo "--> Environment ${CONDA_ENV_NAME} does not exist. Creating from ${ENV_FILE_PATH}..."
    conda env create -f "${ENV_FILE_PATH}" -n "${CONDA_ENV_NAME}"
    if [ $? -ne 0 ]; then echo "!!! Conda create FAILED."; exit 1; fi
    echo "--> Activating newly created environment..."
    # Need to source again potentially before activating newly created env
    source "${CONDA_BASE_PATH}/etc/profile.d/conda.sh"
    source activate base
    conda activate "${CONDA_ENV_NAME}"
    if [ $? -ne 0 ]; then echo "!!! Conda activate FAILED."; exit 1; fi
fi

echo "--> Setting up pymiecoated"
cd pymiecoated
python setup.py install
cd ..