import csv
import sqlite3
import pandas as pd
import util
import argparse


def extract_bold(conn, bold_tsv, marker, minlength):
    """
    Reads a TSV file with a snapshot of the BOLD database in chunks, selects rows that match the user's
    arguments for the desired marker, length, and kingdom, and writes them to two tables in the
    SQLite database (taxon_temp and barcode_temp) with a subset of their columns.
    :param conn: Connection object to the database.
    :param bold_tsv: Location of the unzipped BOLD TSV
    :param marker: String representing the desired marker
    :param minlength: Integer representing minimum length of sequences to include
    """
    logger.info("Going to import BOLD data TSV")
    for chunk in pd.read_csv(bold_tsv, quoting=csv.QUOTE_NONE,
                             low_memory=False, sep="\t", chunksize=10000):
        # Strip all '-' symbols out of the sequences, i.e. unalign them
        chunk['nuc'] = chunk['nuc'].str.replace('-', '', regex=False)

        # Keep rows that match user arguments
        if marker == "COI-5P":
            df = chunk.loc[
                (chunk['marker_code'] == marker) &
                (chunk["kingdom"] == "Animalia") &
                (chunk["nuc"].str.len() >= minlength) &
                (chunk["species"] is not None)
                ]

        else:
            # variable marker matk_rcbl is split into two separate markers
            marker_1 = marker.split('_')[0]
            marker_2 = marker.split('_')[1]
            df = chunk.loc[
                (
                    (chunk['marker_code'] == marker_1) &
                    (chunk["kingdom"] == "Plantae") &
                    (chunk[""].str.len() >= minlength) &
                    (chunk["species"] is not None)
                ) |
                (
                    (chunk['marker_code'] == marker_2) &
                    (chunk["kingdom"] == "Plantae") &
                    (chunk["nuc"].str.len() >= minlength) &
                    (chunk["species"] is not None)
                )
                ]

        # Keep stated columns, do not keep rows where NAs are present
        df_temp = df[['species', 'kingdom', 'class', 'order', 'family', 'genus', 'bin_uri']].dropna()
        df_temp.rename(columns={'order': 'ord'})

        # Add rows to SQLite table (makes table if not exist yet)
        df_temp.to_sql('taxon_temp', conn, if_exists='append', index=False)

        # Keep stated columns
        df_temp = df[['processid', 'marker_code', 'nuc', 'country', 'species', 'bin_uri']]

        # Add rows to SQLite table (makes table if not exist yet)
        df_temp.to_sql('barcode_temp', conn, if_exists='append', index=False)
        conn.commit()


def make_tables(conn, cursor):
    """Create taxon and barcode tables in the database.
    :param conn: Connection object to the database.
    :param cursor: Cursor object to execute SQL commands.
    """
    logger.info("Initializing database")

    # Create taxon table
    cursor.execute("""CREATE TABLE IF NOT EXISTS taxon (
            taxon_id INTEGER PRIMARY KEY,
            taxon TEXT NOT NULL,
            kingdom TEXT NOT NULL,
            ord TEXT NOT NULL,
            class TEXT NOT NULL,
            family TEXT NOT NULL,
            genus TEXT NOT NULL,
            bin_uri TEST NOT NULL,
            opentol_id INTEGER
            )
        """)

    # Create barcode table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS barcode (
        barcode_id INTEGER PRIMARY KEY,
        processid INTEGER NOT NULL,
        marker_code TEXT NOT NULL,
        nuc TEXT NOT NULL,
        country TEXT,
        taxon_id INTEGER NOT NULL,
        FOREIGN KEY (taxon_id) REFERENCES taxon(taxon_id)
    )""")

    # Commit the changes
    conn.commit()


def make_distinct(conn, cursor):
    """Inserts (the distinct) data from temporary tables into the main tables. Opentol_id column is added to taxon
     table and drops taxon_id to the barcode table as foreign keys. The temporary tables are dropped.
    :param conn: Connection object to the database.
    :param cursor: Cursor object to execute SQL commands.
    """
    logger.info("Post-processing database")
    # Select only the distinct taxon entries from taxon_temp, insert into taxon
    cursor.execute("""INSERT INTO taxon (taxon, kingdom, class, ord, family, genus, bin_uri)
     SELECT DISTINCT * FROM taxon_temp""")

    # Get taxon_id from taxon table as foreign key insert
    cursor.execute("""
     INSERT INTO barcode (processid, marker_code, nuc, country, taxon_id) 
     SELECT DISTINCT barcode_temp.processid, barcode_temp.marker_code,
     barcode_temp.nuc, barcode_temp.country, taxon.taxon_id
     FROM barcode_temp INNER JOIN taxon ON barcode_temp.bin_uri = taxon.bin_uri""")

    # Drop old tables
    cursor.execute("""DROP TABLE taxon_temp""")
    cursor.execute("""DROP TABLE barcode_temp""")

    # Commit the changes
    conn.commit()


if __name__ == '__main__':

    # Define command line arguments
    parser = argparse.ArgumentParser(description='Required command line arguments.')
    parser.add_argument('-d', '--database', required=True, help='Database file to create')
    parser.add_argument('-t', '--tsv', required=True, help='BOLD data dump TSV')
    parser.add_argument('-m', '--marker', required=True, help='Marker name (e.g. COI-5P)')
    parser.add_argument('-l', '--length', required=True, type=int, help='Minimum sequence length (e.g. 600)')
    parser.add_argument('-v', '--verbosity', required=True, help='Log level (e.g. DEBUG)')
    args = parser.parse_args()

    # Configure logger
    logger = util.get_formatted_logger('create_database', args.verbosity)

    # Make connection to the database
    connection = sqlite3.connect(args.database)

    # Create a cursor
    database_cursor = connection.cursor()

    # Dump BOLD data into DB in temporary tables
    extract_bold(connection, args.tsv, args.marker, args.length)

    # Make new tables with different names
    make_tables(connection, database_cursor)

    # Drop duplicates
    make_distinct(connection, database_cursor)

    # Close the connection
    connection.close()
