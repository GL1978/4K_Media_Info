from globals import media_info_table_columns, media_info_table_columns_def
import os
import pandas as pd
import sqlite3


def import_media_info_into_db(directory_path, file_name_pattern, delimiter, db_path, table_name):
    # Initialize an empty list to store DataFrames
    dataframes = []

    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(file_name_pattern):
            file_path = os.path.join(directory_path, filename)
            try:
                # Read the delimited file into a DataFrame
                df = pd.read_csv(filepath_or_buffer=file_path, delimiter=delimiter, header=None, engine='python', on_bad_lines=lambda error: print("Bad line detected in", file_path, error))
                # Assign the column names to the DataFrame
                df.columns = media_info_table_columns
                dataframes.append(df)
            except pd.errors.ParserError as e:
                print(f"Error parsing {file_path}: {e}")
            except Exception as e:
                print(f"An error occurred with {file_path}: {e}")

        # Optionally, concatenate all DataFrames into a single DataFrame
    if dataframes:
        df = pd.concat(dataframes, ignore_index=True)
    else:
        print("No data files found matching the pattern.")
        return

        # Ensure the DataFrame has all expected columns and in the correct order
    for col in media_info_table_columns:
        if col not in df.columns:
            df[col] = None  # Add missing columns with None values

        # Reorder columns to match the expected schema
    df = df[media_info_table_columns]

    # Check the DataFrame content before writing to SQLite
    print("DataFrame content before inserting into database:")
    print(df.head())

    # Create a connection to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    cursor = conn.cursor()

    # Create the SQL table schema string
    columns_schema = ', '.join([f"{col_name} {col_type}" for col_name, col_type in media_info_table_columns_def])
    create_table_sql = f'''
      CREATE TABLE IF NOT EXISTS {table_name} (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          {columns_schema}
      )
      '''

    # Create the table
    cursor.execute(create_table_sql)

    # Write the DataFrame to an SQLite table
    df.to_sql(table_name, conn, if_exists='replace', index=False)

    # Close the connection
    conn.close()


if __name__ == "__main__":
    directory_path = 'D:/MakeMKV/media_info'
    file_name_pattern = '_final.txt'
    delimiter = '#'
    db_path = 'D:/MakeMKV/media_info/media_info.db'
    table_name = 'media_info'
    import_media_info_into_db(directory_path, file_name_pattern, delimiter, db_path, table_name);
