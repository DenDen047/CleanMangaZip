#!/usr/bin/python
import os
import glob
import argparse
import shutil
import time
from collections import Counter
import numpy as np
from PIL import Image
from tqdm import tqdm
import pillow_avif  # noqa: F401  # side-effect import: registers AVIF plugin in Pillow


IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


argparser = argparse.ArgumentParser(
    description="Clean and zip manga folders.",
)
argparser.add_argument(
    "paths",
    nargs="*",
    help="manga folder path(s). If omitted, falls back to -f/--file_path.",
)
argparser.add_argument(
    "-f",
    "--file_path",
    type=str,
    default=None,
    help="path to a file listing one folder per line (batch mode)",
)
argparser.add_argument(
    "--crop_area",
    type=str,
    default=None,
    help='"auto" (auto-detect), "none" (skip), or "x1,y1,x2,y2" (manual)',
)
argparser.add_argument(
    "--auto_samples",
    type=int,
    default=8,
    help="number of pages to sample for auto crop detection",
)
argparser.add_argument(
    "--padding",
    type=int,
    default=0,
    help="extra pixels to keep around auto-detected bbox (negative = crop tighter)",
)
args = argparser.parse_args()


def _list_images(dir_path: str) -> list[str]:
    return sorted(
        p
        for p in glob.glob(os.path.join(dir_path, "*"))
        if p.lower().endswith(IMAGE_EXTS)
    )


def _stack_grayscale_samples(
    fpaths: list[str],
    n_samples: int,
) -> np.ndarray | None:
    """Sample n_samples images evenly, load as grayscale, and stack only
    those that share the most common (H, W) shape.

    Returns a (K, H, W) uint8 array, or None if fewer than 2 usable samples.
    """
    if len(fpaths) < 2:
        return None
    indices = np.linspace(0, len(fpaths) - 1, num=min(n_samples, len(fpaths)))
    sampled = [fpaths[int(i)] for i in indices]

    arrays: list[np.ndarray] = []
    for fp in sampled:
        try:
            with Image.open(fp) as img:
                arrays.append(np.asarray(img.convert("L")))
        except Exception:
            continue

    if len(arrays) < 2:
        return None
    most_common_shape, _ = Counter(a.shape for a in arrays).most_common(1)[0]
    arrays = [a for a in arrays if a.shape == most_common_shape]
    if len(arrays) < 2:
        return None
    return np.stack(arrays, axis=0)


def _mask_to_bbox(
    mask: np.ndarray,
    padding: int = 0,
) -> tuple[int, int, int, int] | None:
    """Convert a 2D boolean mask to a bounding box (x1, y1, x2, y2).

    PIL Image.crop expects (x1, y1, x2, y2) where x2/y2 are EXCLUSIVE.
    Apply `padding` outward, clipped to mask bounds.
    Returns None if the mask has no True pixels.
    """
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any() or not cols.any():
        return None

    H, W = mask.shape
    y_idx = np.where(rows)[0]
    x_idx = np.where(cols)[0]
    y1, y2 = int(y_idx[0]), int(y_idx[-1]) + 1
    x1, x2 = int(x_idx[0]), int(x_idx[-1]) + 1

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(W, x2 + padding)
    y2 = min(H, y2 + padding)
    return x1, y1, x2, y2


def detect_crop_area(
    dir_path: str,
    n_samples: int = 8,
    std_threshold: float = 8.0,
    padding: int = 0,
) -> tuple[int, int, int, int] | None:
    """Auto-detect crop area by finding pixels that VARY across pages.

    Decorative borders are identical on every page → low std.
    Manga content varies page to page → high std.
    The bounding box of high-std pixels is the content region.
    """
    fpaths = _list_images(dir_path)
    stack = _stack_grayscale_samples(fpaths, n_samples)
    if stack is None:
        return None

    # Per-pixel std across the K sampled pages → (H, W)
    std = stack.std(axis=0)
    mask = std > std_threshold
    return _mask_to_bbox(mask, padding=padding)


def update_file_timestamps(directory):
    min_timestamp = time.mktime((1980, 1, 1, 0, 0, 0, 0, 0, 0))
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_time = os.path.getmtime(file_path)
            if file_time < min_timestamp:
                os.utime(file_path, (min_timestamp, min_timestamp))


def _resolve_dir_paths() -> list[str]:
    if args.paths:
        return [p.strip() for p in args.paths if p.strip()]
    if args.file_path:
        with open(args.file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    argparser.error(
        "no folders given. Pass folder path(s) as positional arguments or use -f <list.txt>."
    )


# === MAIN ===
def main():
    dir_paths = _resolve_dir_paths()

    for dir_path in tqdm(dir_paths):
        dir_path = os.path.abspath(dir_path)

        # convert images to webp format if the folder having AVIF images
        avif_fpaths = sorted(glob.glob(os.path.join(dir_path, "*.avif")))
        if len(avif_fpaths) > 0:
            for image_fpath in avif_fpaths:
                with Image.open(image_fpath) as img:
                    img.save(image_fpath[:-4] + "webp", format="WebP")
                os.remove(image_fpath)

        # remove url/db files
        redundant_fpaths = []
        for ext in ["url", "db", "ini"]:
            redundant_fpaths += glob.glob(os.path.join(dir_path, f"*.{ext}"))
        for redundant_fpath in redundant_fpaths:
            os.remove(redundant_fpath)

        # crop images
        crop_area: tuple[int, int, int, int] | None = None
        if args.crop_area in (None, "none"):
            pass
        elif args.crop_area == "auto":
            crop_area = detect_crop_area(
                dir_path,
                n_samples=args.auto_samples,
                padding=args.padding,
            )
            if crop_area is None:
                print(
                    f"Warning: auto crop detection failed for {dir_path}; skipping crop."
                )
            else:
                print(f"Auto-detected crop {crop_area} for {dir_path}")
        else:
            crop_area = tuple(map(int, args.crop_area.split(",")))

        if crop_area is not None:
            img_fpaths = _list_images(dir_path)
            for image_fpath in img_fpaths:
                with Image.open(image_fpath) as img:
                    img.crop(crop_area).save(image_fpath)

        # make a zip
        try:
            shutil.make_archive(dir_path, format="zip", root_dir=dir_path)
        except ValueError as e:
            if "ZIP does not support timestamps before 1980" in str(e):
                print(
                    f"Warning: {dir_path} contains files with timestamps before 1980. Updating timestamps..."
                )
                update_file_timestamps(dir_path)
                shutil.make_archive(dir_path, format="zip", root_dir=dir_path)
            else:
                raise e


if __name__ == "__main__":
    main()
