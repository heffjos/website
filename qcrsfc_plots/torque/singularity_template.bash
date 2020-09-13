#!/bin/bash

module load singularity/2.6.1

echo "cmd           : ${cmd}"
echo "batch_file    : ${batch_file}"

echo "Start singularity: `date`"

${cmd}

echo "End singularity:   `date`"

chmod g+rw,o+r ${batch_file}.o*
