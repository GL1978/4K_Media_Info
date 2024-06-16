import json
from pathlib import Path

from pymediainfo import MediaInfo
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, and_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from globals import get_volume_label, format_duration, format_file_size, convert_bitrate_to_mbps, \
    convert_bitrate_to_kbps

volume_label = None
Base = declarative_base()


class MediaInfoModel(Base):
    __tablename__ = 'media_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    volume = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    duration = Column(Integer)
    formatted_duration = Column(String)
    file_size = Column(Integer)
    formatted_file_size = Column(String)
    overall_bit_rate = Column(Integer)
    formatted_overall_bit_rate = Column(String)
    video_format = Column(String)
    video_bit_rate = Column(Integer)
    formatted_video_bit_rate = Column(String)
    frame_rate = Column(Float)
    hdr_format = Column(String)
    color_primaries = Column(String)
    mastering_display_color_primaries = Column(String)
    mastering_display_luminance = Column(String)
    max_fall = Column(Integer)
    max_cll = Column(Integer)
    full_json = Column(Text, nullable=False)


def extract_media_info(file_path):
    media_info = MediaInfo.parse(file_path)
    return media_info.to_data()


def prepare_media_info(file_name, media_info_json):
    media_info = json.loads(media_info_json)
    general_info = next((track for track in media_info['tracks'] if track['track_type'] == 'General'), {})
    video_info = next((track for track in media_info['tracks'] if track['track_type'] == 'Video'), {})

    return MediaInfoModel(
        volume=media_info.get('volume'),
        file_name=file_name,
        duration=general_info.get('duration'),
        formatted_duration=format_duration(general_info.get('duration')),
        file_size=general_info.get('file_size'),
        formatted_file_size=format_file_size(general_info.get('file_size')),
        overall_bit_rate=general_info.get('overall_bit_rate'),
        formatted_overall_bit_rate=convert_bitrate_to_mbps(general_info.get('overall_bit_rate')),
        video_format=video_info.get('format'),
        video_bit_rate=video_info.get('bit_rate'),
        formatted_video_bit_rate=convert_bitrate_to_kbps(video_info.get('bit_rate')),
        frame_rate=video_info.get('frame_rate'),
        hdr_format=video_info.get('hdr_format'),
        color_primaries=video_info.get('color_primaries'),
        mastering_display_color_primaries=video_info.get('mastering_display_color_primaries'),
        mastering_display_luminance=video_info.get('mastering_display_luminance'),
        max_fall=video_info.get('maximum_frameaverage_light_level'),
        max_cll=video_info.get('maximum_content_light_level'),
        full_json=media_info_json
    )


def bulk_save_or_update(session, media_info_list, file_names):
    # Extract volume from the first media_info in the list
    volume = media_info_list[0].volume

    # Query existing file names based on volume and file_names
    existing_files = session.query(MediaInfoModel.file_name).filter(
        and_(
            MediaInfoModel.volume == volume,
            MediaInfoModel.file_name.in_(file_names)
        )
    ).all()

    # Create a set of existing file names
    existing_files = {file[0] for file in existing_files}

    update_list = []
    insert_list = []

    for media_info in media_info_list:
        if media_info.file_name in existing_files:
            update_list.append(media_info)
        else:
            insert_list.append(media_info)

    if update_list:
        for media_info in update_list:
            existing = session.query(MediaInfoModel).filter(
                MediaInfoModel.volume == media_info.volume,
                MediaInfoModel.file_name == media_info.file_name
            ).first()
            if existing:
                # Update existing object with new values
                existing.volume = media_info.volume
                existing.duration = media_info.duration
                existing.formatted_duration = media_info.formatted_duration
                existing.file_size = media_info.file_size
                existing.formatted_file_size = media_info.formatted_file_size
                existing.overall_bit_rate = media_info.overall_bit_rate
                existing.formatted_overall_bit_rate = media_info.formatted_overall_bit_rate
                existing.video_format = media_info.video_format
                existing.bit_rate = media_info.video_bit_rate
                existing.formatted_video_bit_rate = media_info.formatted_video_bit_rate
                existing.frame_rate = media_info.frame_rate
                existing.hdr_format = media_info.hdr_format
                existing.color_primaries = media_info.color_primaries
                existing.mastering_display_color_primaries = media_info.mastering_display_color_primaries
                existing.mastering_display_luminance = media_info.mastering_display_luminance
                existing.max_fall = media_info.max_fall
                existing.max_cll = media_info.max_cll
                existing.full_json = media_info.full_json

    if insert_list:
        session.bulk_save_objects(insert_list)

    session.commit()


def main(media_files_path, db_path, batch_size=100):
    volume = get_volume_label(media_files_path)
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    media_info_list = []
    file_names = set()

    file_count = 0
    for file_path in Path(media_files_path).rglob('*.mkv'):
        file_count += 1
        print(f'{file_count} Processing {file_path}')
        media_info = extract_media_info(file_path)
        media_info['volume'] = volume
        media_info_obj = prepare_media_info(file_path.name, json.dumps(media_info))
        media_info_list.append(media_info_obj)
        file_names.add(file_path.name)

        if len(media_info_list) >= batch_size:
            bulk_save_or_update(session, media_info_list, file_names)
            media_info_list.clear()
            file_names.clear()

    if media_info_list:
        bulk_save_or_update(session, media_info_list, file_names)

    session.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extract media info from MKV files and store in SQLite database.')
    parser.add_argument('media_files_volume', type=str,
                        help='Volume that has path to the directory containing MKV files.')
    parser.add_argument('media_files_path', type=str, help='Path to the directory containing MKV files.')
    parser.add_argument('database_path', type=str, help='Path to database which will contain the media info.')
    parser.add_argument('--batch_size', type=int, default=100, help='Number of records to insert in each batch.')
    #args = parser.parse_args()
    #main(args.media_files_volume, args.media_files_path, args.database_path, args.batch_size)
    main("G:/", "sqlite:///D:/MakeMKV/media_info/media_info_new.db", 100)

#select *, json_extract(full_json, '$.tracks[1].color_primaries') color_primaries from VW_4K_MEDIA_INFO where mastering_display_color_primaries NOT like '%2020%' AND mastering_display_color_primaries NOT like '%P3%'