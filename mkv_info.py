import shutil
import subprocess
import json
import os
import traceback
from pathlib import Path


def coalesce(*args):
    return next((arg for arg in args if arg is not None and len(str(arg).strip()) > 0), None)


def dict_to_delimited_string(dictionary, delimiter=','):
    delimited_string = delimiter.join([f"{value}" for key, value in dictionary.items()])
    return delimited_string


def is_4k_resolution(width, height):
    # Check if the resolution qualifies as 4K
    return (width == 3840 and height == 2160) or (width == 4096 and height == 2160)


def format_file_size(size_bytes):
    # Convert bytes to a human-readable format (KB, MB, GB)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024


def convert_bitrate_to_mbps(bitrate):
    # Convert bit rate from bps to Mbps
    if bitrate:
        return f"{int(bitrate) / 1_000_000:.2f} Mbps"
    return None


def convert_bitrate_to_kbps(bitrate):
    # Convert bit rate from bps to Kbps
    if bitrate:
        return f"{int(bitrate) / 1_000:.2f} Kbps"
    return None


def format_duration(duration_ms):
    # Convert duration from ms to HH:MM:SS format
    if duration_ms:
        duration_ms_str = str(duration_ms)
        duration_ms = int(duration_ms_str.replace('.', '') if "." in duration_ms_str else duration_ms)
        seconds = int(duration_ms) / 1000
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return None


def get_mediainfo(file_path):
    try:
        # Run the mediainfo command and capture the output
        result = subprocess.run(
            ['mediainfo', '--Output=JSON', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check for errors
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None

        # Parse the JSON output
        media_info = json.loads(result.stdout)
        return media_info
    except Exception as ex:
        print(f'Exception while getting media_info for {file_path}')
        traceback.print_exc();
        return None


def extract_and_write_media_info(media_info_json_dump_input_file_path, media_info_output_file_path):
    with open(media_info_output_file_path, 'w') as media_info_output_file:
        print('Writing sanitised media_info to', media_info_output_file_path)
        with open(media_info_json_dump_input_file_path, 'r') as media_info_json_dump_file:
            for media_info in media_info_json_dump_file:
                try:
                    media_info = eval(media_info.strip())
                    if not media_info:
                        continue
                    final_media_info = extract_fields_from_media_info(media_info)
                    if final_media_info:
                        media_info_output_file.write(dict_to_delimited_string(final_media_info, '#'))
                        media_info_output_file.write('\n')
                except Exception as ex:
                    print(f'Exception while writing sanitised media_info from {media_info_json_dump_input_file_path}')
                    print(media_info)
                    traceback.print_exc();
        print('Wrote sanitised media_info to', media_info_output_file_path)


def extract_fields_from_media_info(media_info):
    media_details = dict()

    media_details["Title"] = os.path.basename(media_info['media']['@ref'])
    # print(media_info)
    # Extract user supplied file name

    # Extract general track information
    general_track = next((track for track in media_info['media']['track'] if track['@type'] == 'General'), None)
    if general_track:
        duration = general_track.get('Duration')
        media_details["Duration"] = format_duration(duration) if duration else None
        file_size = general_track.get('FileSize')
        media_details["File_size"] = format_file_size(int(file_size)) if file_size else None
        media_details["OverallBitRate"] = convert_bitrate_to_mbps(general_track.get('OverallBitRate'))

    # Extract video track information
    video_track = next((track for track in media_info['media']['track'] if track['@type'] == 'Video'), None)
    if video_track:
        media_details["Video_Codec"] = video_track.get('Format')
        if media_details["Video_Codec"] not in ['HEVC']:
            return None
        video_bitrate = video_track.get('BitRate')
        media_details["Video_Bit_Rate"] = convert_bitrate_to_mbps(video_bitrate)
        media_details["FrameRate"] = video_track.get('FrameRate')
        media_details["HDR_Format"] = video_track.get('HDR_Format')
        media_details["MasteringDisplay_ColorPrimaries"] = video_track.get('MasteringDisplay_ColorPrimaries')
        media_details["MasteringDisplay_Luminance"] = video_track.get('MasteringDisplay_Luminance')
        val = str(video_track.get('MaxFALL'))
        media_details["MaxFALL"] = val.replace("cd/m2", "").strip()
        val = str(video_track.get('MaxCLL'))
        media_details["MaxCLL"] = val.replace("cd/m2", "").strip()

    # # Extract audio track information
    # audio_track = next((track for track in media_info['media']['track'] if track['@type'] == 'Audio'), None)
    # if audio_track:
    #     audio_bitrate = audio_track.get('BitRate')
    #     media_details["Audio bit rate"] = convert_bitrate_to_kbps(audio_bitrate)
    #     media_details["Audio format"] = audio_track.get('Format')

    return media_details


def main():
    dir_path = 'F:\\'
    media_info_file_name = 'WD8A_10TB'
    media_info_json_dump_file_path = f'D:/MakeMKV/media_info/{media_info_file_name}.txt'
    media_info_final_dump_file_path = f'D:/MakeMKV/media_info/{media_info_file_name}_final.txt'
    option = 3

    if option not in [1, 2, 3]:
        print("Unsupported option selected")
        return

    # Create media info json dump file
    if option in [1, 3]:
        directory_path = Path(dir_path)

        if not directory_path.is_dir():
            print(f"The directory {dir_path} does not exist.")
            return

        pattern = '**/*.mkv'

        # Create a backup of the file
        if os.path.isfile(media_info_json_dump_file_path):
            media_info_json_dump_backup_file_path = Path(media_info_json_dump_file_path)
            media_info_json_dump_backup_file_path = Path(media_info_json_dump_backup_file_path.parent, media_info_json_dump_backup_file_path.stem + ".bkp")
            shutil.copy2(media_info_json_dump_file_path, media_info_json_dump_backup_file_path)
            print(f"Backup created at {media_info_json_dump_backup_file_path}")

        # Create media_info json dump file
        with open(media_info_json_dump_file_path, 'w') as media_info_json_dump_file:
            paths = directory_path.glob(pattern, )
            if not paths:
                print(f"Found no files in {dir_path} matching pattern {pattern}")
                return
            print(f"Dumping media info to {media_info_json_dump_file_path}")
            file_count = 1
            error_list = list()
            for path in paths:
                path = str(path)
                print(f'[{file_count}] Dumping media info for {path}')
                media_info = get_mediainfo(path)
                if media_info:
                    media_info_json_dump_file.write(str(media_info) + '\n')
                    print(f'[{file_count}] Dumped media info for {path}')
                    file_count += 1
                else:
                    print(f'[{file_count}] Got empty media info for {path}')
                    error_list.append(path)
            print(f"Dumped media info for {file_count} file(s) to {media_info_json_dump_file_path}")
            print('Error list', error_list)
            print('Error count', len(error_list))
    # Create media_info final dump file from media info json dump file
    if option in [2, 3]:
        if not os.path.isfile(media_info_json_dump_file_path):
            print(f'Media info dump file {media_info_json_dump_file_path} not found')
            return
        extract_and_write_media_info(media_info_json_dump_file_path, media_info_final_dump_file_path)


if __name__ == "__main__":
    main()
