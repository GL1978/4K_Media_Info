import csv
import pandas as pd
import sqlite3


def get_query(table_name):
    columns = ['volume as Volume',
               'file_name as Title',
               'formatted_duration as Duration',
               'formatted_file_size as File_Size',
               'video_format Video_Format',
               'formatted_video_bit_rate as Video_BitRate',
               'frame_rate as Frame_Rate',
               'hdr_format as HDR_Format',
               'mastering_display_color_primaries as Mastering_Display_Color_Primaries',
               'mastering_display_luminance as Mastering_Display_Luminance',
               'max_mdl as MAX_MDL',
               'max_fall as MAX_FALL',
               'max_cll as MAX_CLL']

    return f"SELECT {','.join(columns)} FROM {table_name} ORDER by volume,id";


def export_to_csv_1(db_name, table_name, output_file, delimiter=','):
    print(f"Exporting data from table '{table_name}' to to '{output_file}'")

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Execute a query to retrieve all data from the table
    cursor.execute(get_query(table_name))
    rows = cursor.fetchall()

    # Get the column names from the cursor description
    column_names = [description[0] for description in cursor.description]

    # Write the data to a CSV file
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=delimiter)

        # Write the column names as the first row
        csv_writer.writerow(column_names)

        # Write the data rows
        csv_writer.writerows(rows)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(f"Exported data from table '{table_name}' to to '{output_file}'")


def export_to_csv_2(db_file, table_name, output_file, delimiter=','):
    print(f"Exporting data from table '{table_name}' to to '{output_file}'")

    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Use pandas to read the table data into a DataFrame
    df = pd.read_sql_query(get_query(table_name), conn)

    # Export the DataFrame to a CSV file
    df.to_csv(output_file, index=False, sep=delimiter)

    # Close the database connection
    conn.close()
    print(f"Exported data from table '{table_name}' to to '{output_file}'")


# Example usage
db_file = 'D:/MakeMKV/media_info/media_info_new.db'
table_name = 'VW_4K_MEDIA_INFO'
csv_file = 'D:/MakeMKV/media_info/media_info.csv'
delimiter = '#'

export_to_csv_1(db_file, table_name, csv_file, delimiter)
