#!/usr/bin/python
import os
import sys
import glob
import subprocess
from tqdm import tqdm


FILE_PATH = './list.txt'


# === MAIN ===
def main():
    with open(FILE_PATH, 'r') as f:
        dir_paths = f.readlines()

    for dir_path in tqdm(dir_paths):
        dir_path = dir_path.strip()

        img_fpaths = glob.glob(os.path.join(dir_path, '*'))
        cmd = "zip -j {} {}".format(
            dir_path,
            ' '.join(img_fpaths)
        )
        subprocess.run(cmd.split(' '), stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
