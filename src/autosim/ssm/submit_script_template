#!/bin/bash

# module purge
# module load sierra
# module load seacas

# previously ran with 16 processors
# PROCS=16
#
# skybridge has 16 cores per node
# 10 nodes = 160 processors
#
# eclipse has 36 cores per node
# 10 nodes = 360 processors
#
# attaway has 36 cores per node
# 10 nodes = 360 processors
#
# [PROCS]
# PROCS=160
# PROCS=320
# PROCS=336

# geometry and mesh file
# GFILE="../geometry/bob-1mm-5kg-helmet2-hemi.g"
# GFILE="/projects/sibl/data/bob-1mm-5kg-helmet-hemi/bob-1mm-5kg-helmet2-hemi.g"
# GFILE="/projects/sibl/data/bob-1mm-5kg-helmet-hemi/bob-1mm-5kg-helmet2-hemi.g"
# GFILE="../../geometry/bob-1mm-5kg-helmet2-hemi.g"
# GFILE="../../geometry/a001/a001.e"
# GFILE="../../geometry/sphere/spheres_resolution_2.exo"
# decomp --processors $PROCS $GFILE

# sierra solid mechanics input file
# IFILE="bob-1mm-5kg-helmet2-0305-hemi-066b.i"
# IFILE="bob067.i"
# IFILE="bob068.i"
# IFILE="a001.i"
# IFILE="sr4c.i"
IFILE="ssm_input.i"

# queues
# https://wiki.sandia.gov/pages/viewpage.action?pageId=1359570410#SlurmDocumentation-Queues
# short can be used for nodes <= 40 and wall time <= 4:00:00 (4 hours)
# batch, the default queue, wall time <= 48 h
# long, wall time <= 96 h, eclipse 256 nodes

# https://wiki.sandia.gov/display/OK/Slurm+Documentation
# over 4 hours, then need to remove 'short' from the --queue-name
#
#sierra -T 00:05:00 --queue-name batch,short --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 00:10:00 --queue-name batch,short --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 00:20:00 --queue-name batch,short --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 00:40:00 --queue-name batch,short --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
sierra -T 04:00:00 --queue-name batch,short --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 06:00:00 --queue-name batch --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 15:00:00 --queue-name batch --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 18:00:00 --queue-name batch --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
#sierra -T 24:00:00 --queue-name batch --account FY180042 -j $PROCS --job-name $IFILE --run adagio -i $IFILE
