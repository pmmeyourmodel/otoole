# -*- coding: utf-8 -*-
import zipfile
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def run(file):
    """
    Input: file --> any scenario download as a zip package
    Will unzip package and clean dir.
    """
    # Set Time
    start_time = time.time()
    # Preparation
    file = file.split('.')[0]
    # Create folder
    if not os.path.exists(file):
        os.makedirs(file)
    # Unzip package
    with zipfile.ZipFile(file+'.zip') as zip_ref:
        zip_ref.extractall(file)
    print('Unzipped to \\{}'.format(file))

    # clean directory
    if os.path.isfile(os.path.join(file, 'RunSimulation.exe')):
        os.remove(os.path.join(file, 'RunSimulation.exe'))
    if os.path.isfile(os.path.join(file, 'metadata.txt')):
        os.remove(os.path.join(file, 'metadata.txt'))
    print('Files: {}'.format(os.listdir(os.path.join(file))))
    # print('Time since start: {:10.2f} s'.format(time.time()-start_time))

    # Create LP file
    os.system('glpsol -m ' +
              file +
              '\\model.txt -d ' +
              file+'\\data.txt --wlp ' +
              file+'\\problem.lp --check')
    if os.path.isfile(os.path.join(file, 'problem.lp')):
        print('Sucessfully created problem.lp')
        # print('Time since start: {:10.2f} s'.format(time.time()-start_time))

    # Solve LP file
    os.system('cplex -c read ' +
              file +
              '\\problem.lp -c optimize -c write ' +
              file +
              '\\solution.sol')
    if os.path.isfile(os.path.join(file, 'problem.sol')):
        print('Sucessfully solved problem.')

    # Transform data to txt
    cwd = os.getcwd()
    os.chdir(file)
    finput = 'solution.sol'
    foutput = 'solution.txt'
    exec(open(os.path.join(cwd, 'transform.py')).read())
    os.chdir(cwd)
    return print('All done. Took {:1.2f} mins'.format(
                (time.time()-start_time)/60))


def read_soltxt(file, pickle=True):
    """
    Converts solution text file to a dataframe and pickles it by default.
    Note:
    file must be path to solution.txt
    All data are stored as objects within df
    """
    # Read
    df = pd.read_csv(file, sep='\t',
                     header=None, names=range(0, 100),
                     low_memory=False)
    # Sort and drop empry columns
    df = df.sort_values(0).dropna(how='all', axis=1).reset_index(drop=True)
    # Pickle if True
    if pickle:
        df.to_pickle(file.split('.')[0]+'.pkl')
    return df
