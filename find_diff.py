import os
import shutil
from pprint import pprint
from tqdm import tqdm


def get_mkv_files(directory):
    """Recursively get all .mkv files from the directory."""
    mkv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.mkv'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                mkv_files.append(relative_path)
    return set(mkv_files)


def print_differences(dir1_files, dir2_files, dir1_name, dir2_name):
    """Print the differences between two sets of files, including directory names."""
    only_in_dir1 = dir1_files - dir2_files
    only_in_dir2 = dir2_files - dir1_files

    if only_in_dir1:
        print(f"\nFiles only in {dir1_name}:")
        pprint(sorted(only_in_dir1), width=80)
    else:
        print(f"\nNo unique files in {dir1_name}.")

    if only_in_dir2:
        print(f"\nFiles only in {dir2_name}:")
        pprint(sorted(only_in_dir2), width=80)
    else:
        print(f"\nNo unique files in {dir2_name}.")

    return only_in_dir1, only_in_dir2


def copy_large_file(source_path, dest_path, buffer_size=1024 * 1024):
    """Copy a large file using a buffer."""
    print(f'Copying {source_path} to {dest_path}')
    with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
        while True:
            buffer = src.read(buffer_size)
            if not buffer:
                break
            dst.write(buffer)
        print(f'Copied {source_path} to {dest_path}')


def copy_files(files, source_dir, dest_dir):
    """Copy files from source_dir to dest_dir with a progress bar."""
    for file in tqdm(files, desc="Copying files", unit="file"):
        source_path = os.path.join(source_dir, file)
        dest_path = os.path.join(dest_dir, file)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        copy_large_file(source_path, dest_path)


def main(dir1, dir2):
    dir1_files = get_mkv_files(dir1)
    dir2_files = get_mkv_files(dir2)

    only_in_dir1, only_in_dir2 = print_differences(dir1_files, dir2_files, dir1, dir2)

    if only_in_dir1:
        prompt = input(f"\nDo you want to copy missing files from {dir1} to {dir2}? (y/n): ")
        if prompt.lower() == 'y':
            copy_files(only_in_dir1, dir1, dir2)

    if only_in_dir2:
        prompt = input(f"\nDo you want to copy missing files from {dir2} to {dir1}? (y/n): ")
        if prompt.lower() == 'y':
            copy_files(only_in_dir2, dir2, dir1)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python script.py <directory1> <directory2>")
        sys.exit(1)

    dir1 = sys.argv[1]
    dir2 = sys.argv[2]

    main(dir1, dir2)
