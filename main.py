#!/usr/bin/python
import os
import sys
import glob
import shutil
from tqdm import tqdm
from pprint import pprint


FILE_PATH = './list.txt'


# === MAIN ===
def main():
    with open(FILE_PATH, 'r') as f:
        dir_paths = f.readlines()

    for dir_path in tqdm(dir_paths):
        dir_path = os.path.abspath(dir_path.strip())
        shutil.make_archive(dir_path, format='zip', root_dir=dir_path)


if __name__ == "__main__":
    main()
