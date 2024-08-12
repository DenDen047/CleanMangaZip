#!/usr/bin/python
import os
import sys
import glob
import argparse
import shutil
from PIL import Image
from tqdm import tqdm
from pprint import pprint


argparser = argparse.ArgumentParser()
argparser.add_argument('--file_path', type=str, default='./list.txt')
argparser.add_argument('--crop_area', type=str, default=None, help='crop area in format of x1,y1,x2,y2')
args = argparser.parse_args()


# === MAIN ===
def main():
    with open(args.file_path, 'r') as f:
        dir_paths = f.readlines()

    for dir_path in tqdm(dir_paths):
        dir_path = os.path.abspath(dir_path.strip())

        # convert images to webp format if the folder having AVIF images
        avif_fpaths = glob.glob(os.path.join(dir_path, '*.avif'))
        if len(avif_fpaths) > 0:
            for image_fpath in avif_fpaths:
                with Image.open(image_fpath) as img:
                    img.save(image_fpath[:-4] + 'webp', format='WebP')
                os.remove(image_fpath)

        # remove url/db files
        redundant_fpaths = []
        for ext in ['url', 'db', 'ini']:
            redundant_fpaths += glob.glob(os.path.join(dir_path, f'*.{ext}'))
        for redundant_fpath in redundant_fpaths:
            os.remove(redundant_fpath)

        # crop images
        if args.crop_area is not None:
            crop_area = tuple(map(int, args.crop_area.split(',')))
            img_fpaths = glob.glob(os.path.join(dir_path, '*'))
            for image_fpath in img_fpaths:
                with Image.open(image_fpath) as img:
                    img.crop(crop_area).save(image_fpath)

        # make a zip
        shutil.make_archive(dir_path, format='zip', root_dir=dir_path)


if __name__ == "__main__":
    main()
