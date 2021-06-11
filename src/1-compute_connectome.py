# INPUT:
# 
# DESCRIPTION:
# The script clones the HCP datadet (functional connectivity) and
# compute the whole-brain resting state connectome using schaefer's atlas
# with 100 parcels
# OUTPUT:
# 

# %%
# Imports
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
working_dir = Path('../scratch')

# Path to the results directory (relative to CWD)
results_dir = Path('../scratch')

# subject to compute
subject = '100206'

# %%
# Install datalad dataset

# Path to datalad dataset (relative to CWD)
dataset_path = working_dir/'dataset'

dataset_url = 'https://github.com/datalad-datasets/hcp-functional-connectivity.git'

print('Cloning dataset in {dataset_path}')
dataset = datalad.api.install(path=dataset_path, source=dataset_url)
print('Dataset cloned')
# %% 
# Get rsFMRI

# Path to thee subject RS  data (relative to datalad dataset)
subject_data_path = Path(subject) / 'MNINonLinear' / 'Results' / 'rfMRI_REST1_LR'

# Path to the RS Nifti (relative to datalad dataset)
rsfmri_fname = subject_data_path / 'rfMRI_REST1_LR_hp2000_clean.nii.gz'
dataset.get(rsfmri_fname)

# get confound
confounds_fname = subject_data_path / 'Movement_Regressors.txt'
dataset.get(confounds_fname)

# %%
# Get Atlas
atlas = nilearn.datasets.fetch_atlas_schaefer_2018(n_rois=100,resolution_mm=2)
atlas_filename = atlas.maps

# %% https://nilearn.github.io/auto_examples/03_connectivity/plot_signal_extraction.html
# #sphx-glr-auto-examples-03-connectivity-plot-signal-extraction-py

# Apply Atlas

masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, verbose=5)

full_rsfmri_fname = dataset_path / rsfmri_fname
full_confounds_fname = dataset_path / confounds_fname
time_series = masker.fit_transform(full_rsfmri_fname.as_posix(), confounds=full_confounds_fname.as_posix())

# %%
# Compute FC
correlation_measure = ConnectivityMeasure(kind='correlation')
correlation_matrix = correlation_measure.fit_transform([time_series])[0]

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

results_dir.mkdir(exist_ok=True, parents=True)
results_fname = results_dir / f'{subject}_connectome.mat'
to_save = {
    'connectome': correlation_matrix,
    'labels': atlas.labels
} # define dictionary to save as mat
sio.savemat(results_fname, to_save)

