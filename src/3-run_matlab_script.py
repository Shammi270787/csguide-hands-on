
# %%
# Imports
import sys
from pathlib import Path
import nilearn.datasets
import subprocess

import nest_asyncio
nest_asyncio.apply()

import datalad.api
from scipy import io as sio
from nilearn.input_data import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure

# %%
# Variables

# Path to the working directory (relative to CWD)
# working_dir = Path('../scratch')
working_dir = sys.argv[1]

# Path to the results directory (relative to CWD)
# results_dir = Path('../scratch')
results_dir = sys.argv[2]

# subject to compute
# subject = '100206'
subject = sys.argv[3]

# matlab_bin = '/Application' # Path to matlab
matlab_bin = sys.argv[4]

print(f'INPUT working_dir = {working_dir}')
print(f'INPUT results_dir = {results_dir}')
print(f'INPUT subject = {subject}')

working_dir = Path(working_dir)
results_dir = Path(results_dir)

# %%
# Install datalad dataset

# Path to datalad dataset (relative to CWD)
dataset_path = working_dir/'dataset'

dataset_url = 'https://github.com/datalad-datasets/hcp-functional-connectivity.git'

print(f'Cloning dataset in {dataset_path}')
dataset = datalad.api.install(path=dataset_path, source=dataset_url)
print('Dataset cloned')

# %% 
# Get rsFMRI

# Path to thee subject RS  data (relative to datalad dataset)
subject_data_path = Path(subject) / 'MNINonLinear' / 'Results' / 'rfMRI_REST1_LR'

# Path to the RS Nifti (relative to datalad dataset)
print('Getting data')
rsfmri_fname = subject_data_path / 'rfMRI_REST1_LR_hp2000_clean.nii.gz'
dataset.get(rsfmri_fname)
print('Data received')

# get confound
print('Getting confounds file')
confounds_fname = subject_data_path / 'Movement_Regressors.txt'
dataset.get(confounds_fname)
print('confound file received')

# %%
# Get Atlas
print('Getting atlas')
atlas = nilearn.datasets.fetch_atlas_schaefer_2018(n_rois=100,resolution_mm=2)
atlas_filename = atlas.maps
print(f'Atlas loacted in {atlas_filename}')

# %%
# For local
# exec_string = f'matlab compute_connectome.m {subject}'

# For remote
# exec_string = f'/usr/bin/matlab99 -singleCompThread compute_connectome.m {subject}'
# exec_string = f'{matlab_bin} -singleCompThread compute_connectome.m {subject}'

exec_string = f'fslinfo{atlas_filename}'

process = subprocess.run(exec_string, shell=True)

# %%
