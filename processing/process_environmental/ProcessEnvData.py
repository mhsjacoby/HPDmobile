"""
ProcessEnvData.py
Author: Maggie Jacoby, October 2020

This is script to run the data cleaning on env params
Use in combination with HomeDataClasses.py and cleanData.py
"""




import os
import sys
import csv
import ast
import json
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from my_functions import *
from gen_argparse import *

from cleanData import *
import HomeDataClasses as HD


if __name__ == '__main__':

    # root_path = path.strip('/').split('/')[:-1]

    data = HD.ReadEnv(house_entry=home_system, pi=pi_env, root_dir=path)
    data.main()
    data.clean_data()