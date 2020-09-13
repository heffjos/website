import subprocess

import pandas as pd

from shlex import split
from pathlib import Path

dest = Path('/rcc/stor1/depts/neurology/users/jheffernan/hcp')

data = pd.read_csv('sample_subjects.csv')
subjects = data.subject

out_dir = dest.joinpath('connectomes/motion')
out_dir.mkdir(exist_ok=True)

parcellation = '/rcc/stor1/depts/neurology/users/jheffernan/repositories/ecp/ecp/data/glasser_conte.dlabel.nii'

for i, subject in enumerate(subjects):

    print('Working on {} / {}'.format(i, len(subjects)))

    dtseries = dest.joinpath(f'HCP_1200/{subject}/MNINonLinear/Results/rfMRI_REST1_LR/rfMRI_REST1_LR_Atlas.dtseries.nii')
    movement_regressors = dest.joinpath(f'HCP_1200/{subject}/MNINonLinear/Results/rfMRI_REST1_LR/Movement_Regressors.txt')

    prefix = f'{subject}_REST1_LR'
    nifti = out_dir.joinpath(f'{prefix}.nii.gz')
    clean_nifti = out_dir.joinpath(f'{prefix}_cleaned.nii.gz')
    clean_dtseries = out_dir.joinpath(f'{prefix}_cleaned.dtseries.nii')
    ptseries = out_dir.joinpath(f'{prefix}_cleaned.ptseries.nii')
    rvals = out_dir.joinpath(f'{subject}_rvals.pconn.nii')

    # convert to nifti
    cmd = [
        f'wb_command -cifti-convert',
        f'-to-nifti {dtseries} {nifti}',
    ]
    subprocess.run(split(' '.join(cmd)))

    # clean
    cmd = [
        f'3dTproject',
        f'-input {nifti}',
        f'-prefix {clean_nifti}',
        f'-polort 2',
        f'-ort {movement_regressors}',
        f'-passband 0.01 0.1',
        f'-dt 0.8',
    ]
    subprocess.run(split(' '.join(cmd)))

    # convert back to cifti
    cmd = [
        f'wb_command -cifti-convert',
        f'-from-nifti {clean_nifti} {dtseries} {clean_dtseries}'
    ]
    subprocess.run(split(' '.join(cmd)))

    # parcellate 
    cmd = [
        f'wb_command',
        f'-cifti-parcellate',
        f'{clean_dtseries}',
        f'{parcellation}',
        f'COLUMN',
        f'{ptseries}',
    ]
    subprocess.run(split(' '.join(cmd)))
    
    # create r connectome
    cmd = [
        f'wb_command',
        f'-cifti-correlation',
        f'{ptseries}',
        f'{rvals}',
    ]
    subprocess.run(split(' '.join(cmd)))
        

