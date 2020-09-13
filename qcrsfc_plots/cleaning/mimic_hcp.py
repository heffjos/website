import subprocess

import numpy as np
import nibabel as nib

from shlex import split
from pathlib import Path
from nilearn import image, signal

'''
hptr=$(echo "scale = 10; $hp / (2 * $tr)" | bc -l)

fix_cmd=("${FSL_FIXDIR}/fix" "${fmrihp}.ica" "${TrainingData}" "${FixThresh}" -m -h "${hp}")
    feature extraction
    classify features (predict for a melodic folder)
    "clean" input

This line below is the command for cleaning data with fix.
${FSL_FIXDIR}/call_matlab.sh -l .fix.log -f fix_3_clean .fix $aggressive $domot $HP
aggressive is false
domot is true
HP is 2000

DOvol = 1
Atlas.dtseries.nii is a link to REST_atlas_hp2000.dtseries.nii

% read and prepare motion confounds
confounds = functionmotionconfounds(TR,hp);
BO.cdata = BO.cdata - (confounds * (pinv(confounds,1e-6) * BO.cdata'))';
BO.cdata = BO.cdata - (ICA(:,DDremove) * betaICA(DDremove,:))';    % cleanup
'''
def fsl_bptf(img, hp_sigma, lp_sigma, out_img):
    """filter img with fslmaths -bptf"""

    cmd = [
        f'fslmaths {img}',
        f'-bptf {hp_sigma} {lp_sigma}',
        f'{out_img}',
    ]
    print(' '.join(cmd))
    subprocess.run(split(' '.join(cmd)))

def normalize(x, axis=0):
    """Standardizes x along axis"""

    y = x - x.mean(axis=axis)
    y = y / np.fmax(y.std(axis=axis, ddof=1), 0.00001)

    return y

def motion_confounds(motion, hp, ref_img, work_dir):
    """Preprocess motion confounds"""

    work_dir = Path(work_dir).resolve()
    ref_img = image.load_img(ref_img)
    TR = ref_img.header['pixdim'][4]

    confounds = np.vstack((np.zeros((1, 6)), 
                           motion[1:, :6] - motion[0:-1, :6]))
    confounds = normalize(confounds)
    confounds = normalize(np.hstack((confounds, confounds * confounds)))

    (tp, xdim) = confounds.shape
    confounds = confounds.T.reshape((xdim, 1, 1, tp))

    confounds_img = image.new_img_like(ref_img, confounds, copy_header=True)
    motion_file = str(work_dir.joinpath('motion.nii.gz'))
    confounds_img.to_filename(motion_file)

    if hp > 0:
        filtered_file = str(work_dir.joinpath('filtered_motion.nii.gz'))
        fsl_bptf(motion_file, 0.5 * hp / TR, -1, filtered_file)
        confounds = image.load_img(filtered_file).get_fdata()
        confounds = normalize(confounds.reshape((xdim, tp)).T)

    return confounds

def burgess_process(cifti_file, nifti_file, motion_file, hp, work_dir, out_file):
    """regress out motion from a cifti and filter"""

    cii = nib.load(cifti_file)
    data = cii.get_fdata()
    tr = cii.header.matrix.get_index_map(0).series_step

    motion = np.loadtxt(motion_file)
    confounds = motion_confounds(motion, hp, nifti_file, work_dir)
    data = data - confounds.dot(np.linalg.pinv(confounds, 1e-6).dot(data))
    data = signal.butterworth(data, 1 / tr, high_pass=0.009, copy=True)

    out_cii = nib.cifti2.cifti2.Cifti2Image(data, cii.header, cii.nifti_header)
    out_cii.to_filename(out_file)

    return data

    

    

    
    

    
    
