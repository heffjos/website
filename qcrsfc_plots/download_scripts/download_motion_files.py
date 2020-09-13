import subprocess 

from shlex import split
from pathlib import Path

dest = Path('/rcc/stor1/depts/neurology/users/jheffernan/hcp')

with open('participants.txt') as f:
    participants = [x.strip() for x in f]

for participant in participants:
    
    movement_file = f'HCP_1200/{participant}/MNINonLinear/Results/rfMRI_REST1_LR/Movement_Regressors.txt'

    out_file = dest.joinpath(movement_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = f'aws s3 cp s3://hcp-openaccess/{movement_file} {out_file}'
    print(f'{cmd}')

    results = subprocess.run(split(cmd), capture_output=True)
    print(results.stdout.decode())
    if results.stderr:
        print('ERRORS:')
        print(results.stderr.decode())

    
