import pandas as pd
import sqlite3


def export_to_csv(db_file, table_name, csv_file, delimiter=','):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    columns = ['volume', 'file_name',
               'formatted_duration as duration', 'formatted_file_size as file_size',
               'formatted_file_size as file_size', 'video_format',
               'formatted_video_bit_rate as video_bit_rate', 'frame_rate',
               'hdr_format', 'mastering_display_color_primaries',
               'mastering_display_luminance', 'max_fall', 'max_cll']

    # Use pandas to read the table data into a DataFrame
    df = pd.read_sql_query(f"SELECT {','.join(columns)} FROM {table_name} ORDER by volume,id", conn)

    # Export the DataFrame to a CSV file
    df.to_csv(csv_file, index=False, sep=delimiter)

    # Close the database connection
    conn.close()
    print(f"Data exported successfully to {csv_file}")


# Example usage
db_file = 'D:/MakeMKV/media_info/media_info_new.db'
table_name = 'media_info'
csv_file = 'D:/MakeMKV/media_info/media_info.csv'
delimiter = '#'

export_to_csv(db_file, table_name, csv_file, delimiter)
