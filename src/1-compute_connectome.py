# INPUT:
# 1. working_dir: path to the directory to clone dataset
# 2. results_dir: path to the directory where to place results
# 3. subject: subject_id
# 
# DESCRIPTION:
# The script clones the HCP datadet (functional connectivity) and
# compute the whole-brain resting state connectome using schaefer's atlas
# with 100 parcels
# 
# OUTPUT:
# A file named {subject}_connectome.mat with the correlation matrix and 
# atlas labels in results_dir
# 

# %%
# Imports
import sys
from pathlib import Path
import nilearn.datasets

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
print('Atlas received')

# %% https://nilearn.github.io/auto_examples/03_connectivity/plot_signal_extraction.html
# #sphx-glr-auto-examples-03-connectivity-plot-signal-extraction-py

# Apply Atlas

masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, verbose=5)

full_rsfmri_fname = dataset_path / rsfmri_fname
full_confounds_fname = dataset_path / confounds_fname

print('Masking time series')
time_series = masker.fit_transform(full_rsfmri_fname.as_posix(), confounds=full_confounds_fname.as_posix())

# %%
# Compute FC
print('Computing connectivity')
correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrix = correlation_measure.fit_transform([time_series])[0]
print('Connectivity done')

# %%
# Plot the correlation matrix
# import numpy as np
# import matplotlib
# from nilearn import plotting
# # Make a large figure
# # Mask the main diagonal for visualization:

# labels = atlas.labels
# np.fill_diagonal(correlation_matrix, 0)
# # The labels we have start with the background (0), hence we skip the
# # first label
# # matrices are ordered for block-like representation
# plotting.plot_matrix(correlation_matrix, figure=(10, 8), labels=labels,
#                      vmax=0.8, vmin=-0.8, reorder=True)

# %%
# Save Connectome to mat file

print(f'Create results directory {results_dir.as_posix()}')

results_dir.mkdir(exist_ok=True, parents=True)
results_fname = results_dir / f'{subject}_connectome.mat'
to_save = {
    'connectome': correlation_matrix,
    'labels': atlas.labels
} # define dictionary to save as mat
sio.savemat(results_fname, to_save)

print ('ALL DONE')



