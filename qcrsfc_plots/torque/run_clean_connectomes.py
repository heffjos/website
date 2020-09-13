import os
import pwd
import sys
import subprocess

from shlex import split
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import pandas as pd

SCRIPT_FILE = Path(sys.argv[0]).resolve()
SCRIPT_DIR = SCRIPT_FILE.parent
QSUB_SCRIPT = SCRIPT_DIR.joinpath('singularity_template.bash')
CONTAINER = Path('/rcc/stor1/depts/neurology/users/jheffernan/singularity_images/fmriprep-v20.1.0.simg')

EXPERIMENT_DIR = Path('/rcc/stor1/depts/neurology/users/jheffernan/hcp')
DATA_DIR = EXPERIMENT_DIR.joinpath('HCP_1200')
WORK_DIR = EXPERIMENT_DIR.joinpath('work_dir')
OUT_DIR = EXPERIMENT_DIR.joinpath('connectomes')
EXPERIMENT_SCRIPT_DIR = EXPERIMENT_DIR.joinpath('scripts')
SUBJECT_CSV = EXPERIMENT_DIR.joinpath('sample_subjects.csv')
CLEAN_SCRIPT_DIR = EXPERIMENT_SCRIPT_DIR.joinpath('cleaning')

SUBJECTS = pd.read_csv(str(SUBJECT_CSV)).subject.to_list()
PIPELINES = {
    'null': CLEAN_SCRIPT_DIR.joinpath('make_null_connectomes.py'),
    'burgess': CLEAN_SCRIPT_DIR.joinpath('make_burgess_connectomes.py'),
    'burgess+gordon': CLEAN_SCRIPT_DIR.joinpath('make_burgess+gordon_connectomes.py'),
}

if not CONTAINER.is_file():
    raise Exception(f'Container file does not exist: {CONTAINER}')

def user_name():
    return pwd.getpwuid(os.getuid()).pw_name

def make_readable_command(cmd):
    results = [cmd[0]] + ['    ' + x for x in cmd[1:]]
    return ' \\\n'.join(results)

def get_parser():
    """Define parser object"""

    parser = ArgumentParser(description='Queue clean regressors',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('pipeline', choices=list(PIPELINES), 
                        help='run this pipeline')

    # OPTIONAL
    parser.add_argument('--nthreads', action='store', type=int, default=1,
                        help='maximum number of threads across all processes')
    parser.add_argument('--participants', nargs='+', default=SUBJECTS,
                        help='cleanprep these participants')
    

    # OPTIONAL TORQUE
    parser.add_argument('--email', action='store', default=(user_name() + '@mcw.edu'),
                        help='email address')
    parser.add_argument('--mem', action='store', type=int, default=5,
                        help='qsub memory in gigabytes')
    parser.add_argument('--walltime', action='store', default='6:00:00',
                        help='qsub walltime')
    parser.add_argument('--testing', action='store_true',
                        help='do not run the command, only print information')

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    pipeline = args.pipeline
    
    nthreads = args.nthreads
    participants = args.participants

    email = args.email
    mem = args.mem
    walltime = args.walltime
    testing = args.testing

    log_dir = SCRIPT_DIR.joinpath('qsub_jobs', user_name())
    log_dir.mkdir(mode=int(0o775), exist_ok=True)

    python_script = PIPELINES[pipeline]

    # # squash this correction, because this is a short script
    # if mem > (5 * nthreads):
    #     print('Reducing memory from {}gb to {}gb'.format(mem, 5 * nthreads))
    #     mem = 5 * nthreads

    for participant in participants:
        singularity_cmd = [
            f'singularity exec',
            f'{CONTAINER} python {python_script}',
            f'{participant}']
        singularity_cmd = ' '.join(singularity_cmd)

        job_name = f'{pipeline}_{participant}'
        batch_file = log_dir.joinpath(job_name)
        variable_list = f'cmd="{singularity_cmd}",batch_file="{batch_file}"'

        cmd = [
            f'qsub -M {email}',
            f'-m abe',
            f'-j oe',
            f'-N {job_name}',
            f'-o {log_dir}',
            f'-V',
            f'-v {variable_list}',
            f'-l nodes=1:ppn={nthreads},walltime={walltime},mem={mem}gb',
            f'{QSUB_SCRIPT}'
        ]

        if not args.testing:
            results = subprocess.run(split(' '.join(cmd)), capture_output=True)
            print(results.stdout.decode().strip())
            if results.stderr:
                print(results.stderr.decode().strip())
        else:
            print('Here is your qsub command:')
            print(make_readable_command(cmd))

if __name__ == '__main__':
    main()

