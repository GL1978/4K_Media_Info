import os
import re
import subprocess

media_info_table_columns_def = [
    ('title', 'VARCHAR(1000)'),
    ('duration', 'VARCHAR(20)'),
    ('file_size_gb', 'VARCHAR(50)'),
    ('overall_bitrate', 'VARCHAR(50)'),
    ('video_codec', 'VARCHAR(20)'),
    ('video_bitrate', 'VARCHAR(50)'),
    ('video_framerate', 'VARCHAR(10)'),
    ('hdr_format', 'VARCHAR(4000)'),
    ('masteringdisplay_color_primaries', 'TEXT'),
    ('masteringdisplay_luminance', 'VARCHAR(1000)'),
    ('maxfall', 'INTEGER'),
    ('maxcll', 'INTEGER')
]

media_info_table_columns = [column[0] for column in media_info_table_columns_def]


def coalesce(*args):
    return next((arg for arg in args if arg is not None and len(str(arg).strip()) > 0), None)


def format_file_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def convert_bitrate_to_mbps(bitrate):
    if bitrate:
        return f"{int(bitrate) / 1_000_000:.2f} Mbps"
    return None


def convert_bitrate_to_kbps(bitrate):
    if bitrate:
        return f"{int(bitrate) / 1_000:.2f} Kbps"
    return None


def format_duration(duration_ms):
    if duration_ms:
        duration_ms_str = str(duration_ms)
        duration_ms = int(duration_ms_str.replace('.', '') if "." in duration_ms_str else duration_ms)
        seconds = int(duration_ms) / 1000
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return None


def is_4k_resolution(width, height):
    # Check if the resolution qualifies as 4K
    return (width == 3840 and height == 2160) or (width == 4096 and height == 2160)


def dict_to_delimited_string(dictionary, delimiter=','):
    delimited_string = delimiter.join([f"{value}" for key, value in dictionary.items()])
    return delimited_string


def extract_after_pattern(input_string):
    # Create a regular expression pattern to match "anytoken is " and capture everything after it
    regex = re.compile(r".*? is (.*)")

    # Search for the pattern in the input string
    match = regex.search(input_string)

    if match:
        # Extract the captured group which is everything after "anytoken is "
        result = match.group(1).strip()
        return result


def get_drive_letter(path):
    drive_letter = os.path.splitdrive(path)[0]
    return drive_letter


def get_volume_label(drive_path):
    try:
        # Use subprocess to run the 'vol' command
        drive_path = get_drive_letter(drive_path)
        result = subprocess.run(['vol', drive_path], capture_output=True, text=True, shell=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Split the output by lines and find the line with the volume label
            lines = result.stdout.splitlines()
            print(lines)
            for line in lines:
                if "Volume in drive" in line and "has no label" not in line:
                    # Extract the volume label from the line
                    parts = line.split(' ')
                    volume_label = ' '.join(parts[4:])
                    return extract_after_pattern(volume_label)
        return "No volume label found"
    except Exception as e:
        return str(e)
