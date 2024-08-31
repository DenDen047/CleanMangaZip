# Clean Manga Zip

This is a simple script to clean up a folder of images, and convert them to a single zip file.

## Usage

1. Create a file named `list.txt`.
```txt
/home/username/manga_dir/v01
/home/username/manga_dir/v02
/home/username/manga_dir/v03
```

2. Run the script.

```bash
python main.py --file_path list.txt
```

### Options

You can specify the crop area of the image (default is `None`, no crop).

```bash
python main.py <directory> --crop-area <x1,y1,x2,y2>
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
