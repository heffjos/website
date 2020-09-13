import subprocess

import pandas as pd

from shlex import split
from pathlib import Path

dest = Path('/rcc/stor1/depts/neurology/users/jheffernan/hcp')

data = pd.read_csv('sample_subjects.csv')
subjects = data.subject

out_dir = dest.joinpath('connectomes/no_clean')
out_dir.mkdir(exist_ok=True)

parcellation = '/rcc/stor1/depts/neurology/users/jheffernan/repositories/ecp/ecp/data/glasser_conte.dlabel.nii'

for subject in subjects:

    dtseries = dest.joinpath(f'HCP_1200/{subject}/MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR_Atlas.dtseries.nii')
    ptseries = out_dir.joinpath(f'{subject}_REST1_LR.ptseries.nii')

    # parcellate 
    cmd = [
        f'wb_command',
        f'-cifti-parcellate',
        f'{dtseries}',
        f'{parcellation}',
        f'COLUMN',
        f'{ptseries}',
    ]
    subprocess.run(split(' '.join(cmd)))
    
    rvals = out_dir.joinpath(f'{subject}_rvals.pconn.nii')

    # create r connectome
    cmd = [
        f'wb_command',
        f'-cifti-correlation',
        f'{ptseries}',
        f'{rvals}',
    ]

    subprocess.run(split(' '.join(cmd)))
        
