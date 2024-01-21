#!/usr/bin/python
import os
import sys
import glob
import shutil
from PIL import Image
import pillow_avif
from tqdm import tqdm
from pprint import pprint


FILE_PATH = './list.txt'


# === MAIN ===
def main():
    with open(FILE_PATH, 'r') as f:
        dir_paths = f.readlines()

    for dir_path in tqdm(dir_paths):
        dir_path = os.path.abspath(dir_path.strip())

        # convert images to webp format if the folder having AVIF images
        image_fpaths = glob.glob(os.path.join(dir_path, '*.avif'))
        if len(image_fpaths) > 0:
            for image_fpath in image_fpaths:
                with Image.open(image_fpath) as img:
                    img.save(image_fpath[:-4] + 'webp', format='WebP')
                os.remove(image_fpath)

        # remove url/db files
        redundant_fpaths = []
        for ext in ['url', 'db', 'ini']:
            redundant_fpaths += glob.glob(os.path.join(dir_path, f'*.{ext}'))
        for redundant_fpath in redundant_fpaths:
            os.remove(redundant_fpath)

        # make a zip
        shutil.make_archive(dir_path, format='zip', root_dir=dir_path)


if __name__ == "__main__":
    main()
