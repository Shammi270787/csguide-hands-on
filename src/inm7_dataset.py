# %%
import sys
from pathlib import Path

import nest_asyncio
nest_asyncio.apply()

import datalad.api
from scipy import io as sio

# %%
# Variables

# Path to the working directory (relative to CWD)
working_dir = Path('../scratch')
# working_dir = sys.argv[1]
print(f'INPUT working_dir = {working_dir}')

# %%
# Install datalad dataset

# Path to datalad dataset (relative to CWD)
dataset_path = working_dir/'dataset_repo'

dataset_url = 'https://jugit.fz-juelich.de/inm7/datasets/datasets_repo.git'

print(f'Cloning dataset in {dataset_path}')
dataset = datalad.api.install(path=dataset_path, source=dataset_url)
print('Dataset cloned')

fcp_path = 'original/fcp'
dataset.get(fcp_path)

# %%
fcp_datset =  datalad.api.Dataset(dataset_path/ fcp_path)

fcp_datset.get('genetic')


