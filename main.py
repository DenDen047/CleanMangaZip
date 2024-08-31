#!/usr/bin/python
import os
import sys
import glob
import argparse
import shutil
import time
from PIL import Image
from tqdm import tqdm
from pprint import pprint
import pillow_avif


argparser = argparse.ArgumentParser()
argparser.add_argument('--file_path', type=str, default='./list.txt')
argparser.add_argument('--crop_area', type=str, default=None, help='crop area in format of x1,y1,x2,y2')
args = argparser.parse_args()


def update_file_timestamps(directory):
    min_timestamp = time.mktime((1980, 1, 1, 0, 0, 0, 0, 0, 0))
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_time = os.path.getmtime(file_path)
            if file_time < min_timestamp:
                os.utime(file_path, (min_timestamp, min_timestamp))


# === MAIN ===
def main():
    with open(args.file_path, 'r') as f:
        dir_paths = f.readlines()

    for dir_path in tqdm(dir_paths):
        dir_path = os.path.abspath(dir_path.strip())

        # convert images to webp format if the folder having AVIF images
        avif_fpaths = sorted(glob.glob(os.path.join(dir_path, '*.avif')))
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
        try:
            shutil.make_archive(dir_path, format='zip', root_dir=dir_path)
        except ValueError as e:
            if "ZIP does not support timestamps before 1980" in str(e):
                print(f"Warning: {dir_path} contains files with timestamps before 1980. Updating timestamps...")
                update_file_timestamps(dir_path)
                shutil.make_archive(dir_path, format='zip', root_dir=dir_path)
            else:
                raise e


if __name__ == "__main__":
    main()
