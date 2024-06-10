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