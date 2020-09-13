This folder contains the scripts and data files I created to attempt to recreate supplementary figure S2 A in [Burgess et al 2016](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5105353/). The original plot sampled 183 resting state fMRI scans from participants in the HCP 500 data set. The samples were split into three motion groups: low, medium, and high. The motion groups were defined by the proportion of time points that surpassed either the FD or DVARS thresholds. Demographics (age, years of education, race, or ethnicity) were controlled for the samples so there were no significant differences between motion groups. Only the rFMRI_REST1_RL grayordinate scan was included for all participants. Due to hard drive constraints, I included only 120 HCP resting state scans from the HCP 1200 data set. I picked only rFMRI_RESET1_RL grayordinate scans. I did not have the demographic information at the time, so I did not control for it when selecting my samples. I defined motion groups using mean FD. I simply picked the top 40, middle 40, and bottom 40 scans when sorted by mean FD. My data selection is probably different enough so that I do not exactly recreate figure S2 A plot. I should get the demographic information and pick samples while controlling for demographics. That will be a future project.

All files are a copy, so hardcoded paths will not be correct. My initial workflow and directory structure is not ideal. Here is the summarized workflow to use these scripts:

1. Download all motion parameters (**download_scripts/download_motion_files.py**).
2. Calculate framewise displacement (FD). (**commands/MotionCalculate.py**).
3. Gather FD for all participants into one tsv file. (**rscripts/generate_fd_files.R***).
4. Pick samples (**rscripts/get_subjects_from_fd_summary.R**).
5. Download sample data. (**download_scripts/**)
6. Make connectomes using different methods of confound removal (**cleaning/**).
7. Extract the upper triangle for each connectome and save all of them in an RDS file (**rscripts/get_hcp_data.Rmd**).
8. Make plots.
