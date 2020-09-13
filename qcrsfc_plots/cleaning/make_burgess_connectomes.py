import sys
import subprocess

from shlex import split
from pathlib import Path
from mimic_hcp import burgess_process

subject = sys.argv[1]
experiment_dir = Path('/rcc/stor1/depts/neurology/users/jheffernan/hcp')

out_dir = experiment_dir.joinpath('connectomes/burgess')
out_dir.mkdir(exist_ok=True)

parcellation = '/rcc/stor1/depts/neurology/users/jheffernan/repositories/ecp/ecp/data/glasser_conte.dlabel.nii'

hcp_dir = experiment_dir.joinpath('HCP_1200')
func_dir = hcp_dir.joinpath(subject, 'MNINonLinear', 'Results', 'rfMRI_REST1_LR')

motion_file = func_dir.joinpath('Movement_Regressors.txt')
nifti_scan = func_dir.joinpath('rfMRI_REST1_LR.nii.gz')
cifti_scan = func_dir.joinpath('rfMRI_REST1_LR_Atlas.dtseries.nii')
preclean_scan = func_dir.joinpath('Atlas_hp_preclean.dtseries.nii')

work_dir = experiment_dir.joinpath('work_dir', subject)
work_dir.mkdir(parents=True, exist_ok=True)

prefix = f'{subject}_REST1_LR'
clean_dtseries = out_dir.joinpath(f'{prefix}_cleaned.dtseries.nii')
ptseries = out_dir.joinpath(f'{prefix}_cleaned.ptseries.nii')
rvals = out_dir.joinpath(f'{subject}_rvals.pconn.nii')

# clean
burgess_process(str(preclean_scan),
                str(nifti_scan),
                str(motion_file),
                2000,
                str(work_dir),
                str(clean_dtseries))
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
        


