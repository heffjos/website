import subprocess

import pandas as pd

from shlex import split
from pathlib import Path

dest = Path('/rcc/stor1/depts/neurology/users/jheffernan/hcp')

data = pd.read_csv('sample_subjects.csv')
to_download = data.subject

for subject in to_download:

    atlas_file = f'HCP_1200/{subject}/MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR_Atlas.dtseries.nii'

    out_file = dest.joinpath(atlas_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = f'aws s3 cp s3://hcp-openaccess/{atlas_file} {out_file}'
    print(f'{cmd}')

    results = subprocess.run(split(cmd), capture_output=True)
    print(results.stdout.decode())
    if results.stderr:
        print('ERRORS:')
        print(results.stderr.decode())

    

    

