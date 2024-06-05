import pandas as pd
import os
from Stanford.extract_name import extract_tokens
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_cycle(file_number, start_row, output_file_number, file_base_name, sheet_name):
    """
    Loads data from an Excel file, processes it, and saves the results.

    :param file_number: Current file number to be processed.
    :param start_row: Row to start processing from.
    :param output_file_number: Output file identifier.
    :param file_base_name: Base name of the file.
    :param sheet_name: Sheet name in the Excel file.
    :return: Updated file number, ending row, and continuation condition.
    """
    # Initialize an empty list to collect rows
    rows_to_add = []

    ending_row, rows_to_add, continue_condition = load_data(file_base_name, file_number, start_row, rows_to_add,
                                                            sheet_name)

    if ending_row < 0:
        logger.info("Row not found, trying next file")
        start_row = 0
        file_number += 1

        ending_row, rows_to_add, continue_condition = load_data(file_base_name, file_number, start_row, rows_to_add,
                                                                sheet_name)

        if ending_row < 0:
            file_number += 1
            start_row = 0

            ending_row, rows_to_add, continue_condition = load_data(file_base_name, file_number, start_row, rows_to_add,
                                                                    sheet_name)

    # Create a new DataFrame from collected rows
    new_df = pd.DataFrame(rows_to_add).reset_index(drop=True)
    logger.info(f"Ending row: {ending_row}, File number: {file_number}")
    output_path = f"{file_base_name}out.{output_file_number}.xlsx"
    new_df.to_excel(output_path, index=False)
    return file_number, ending_row, continue_condition


def load_data(file_base_name, file_number, start_row, rows_to_add, sheet_name):
    """
    Reads data from an Excel file and searches for specific conditions.

    :param file_base_name: Base name for the Excel file.
    :param file_number: Current file number.
    :param start_row: Row to start processing from.
    :param rows_to_add: List to collect rows of interest.
    :param sheet_name: Sheet name in the Excel file.
    :return: Ending row, updated list of rows, and continuation condition.
    """
    step_index_end = 14
    step_index_start = 7
    search_column = 'Step_Index'
    file_path = f"{file_base_name}{file_number}.xlsx"
    logger.info(f"Processing file: {file_path}")

    if not os.path.exists(file_path):
        return -1, rows_to_add, False

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return -1, rows_to_add, False

    ending_row = -1
    # Since we are looking for pairs of values in consecutive rows,
    # we need to iterate up to the second last row to compare each row with the next one
    for i in range(start_row, len(df) - 1):  # len(df) - 1 to not go beyond the last row
        # Check if the current row has value1 and the next row has value2
        if df.iloc[i][search_column] == step_index_end and df.iloc[i + 1][search_column] == step_index_start:
            ending_row = i
            rows_to_add.append(df.iloc[i])
            break
        elif df.iloc[i][search_column] == step_index_end:
            rows_to_add.append(df.iloc[i])
    return ending_row, rows_to_add, True


def process_all_cycles(file_base_name, sheet_name):
    """
    Iteratively processes multiple files to extract data based on conditions.

    :param file_base_name: Base name for the Excel files.
    :param sheet_name: Sheet name in the Excel files.
    """
    continue_condition = True
    ending_row = 0
    file_number = 1
    start_row = 0
    output_file_number = 1
    while continue_condition:
        logger.info(
            f"Processing - File number: {file_number}, Starting row: {start_row}, Output file number: {output_file_number}")
        file_number, ending_row, continue_condition = process_cycle(file_number, start_row, output_file_number,
                                                                    file_base_name, sheet_name)
        start_row = ending_row + 1
        output_file_number += 1


def list_subdirectories(directory, file_name, sheet_name):
    """
    Lists subdirectories and processes files within each.

    :param directory: Path to the main directory.
    :param file_name: Base name of the files.
    :param sheet_name: Sheet name in the Excel files.
    """
    if os.path.exists(directory) and os.path.isdir(directory):
        logger.info(f"Listing subdirectories in '{directory}'")
        contents = os.listdir(directory)
        subdirectories = [c for c in contents if os.path.isdir(os.path.join(directory, c))]
        if subdirectories:
            for subdirectory in subdirectories:
                subdirectory_path = os.path.join(directory, subdirectory)
                logger.info(f"Processing folder: {subdirectory_path}")
                contents = os.listdir(subdirectory_path)
                battery_folders = [c for c in contents if
                                   os.path.isdir(os.path.join(subdirectory_path, c)) and c not in ['_processed_mat',
                                                                                                   '__MACOSX']]
                for battery_folder in battery_folders:
                    battery_folder_path = os.path.join(subdirectory_path, battery_folder)
                    first_file = os.listdir(battery_folder_path)[0]
                    file_name, sheet_name = extract_tokens(first_file)
                    process_all_cycles(os.path.join(battery_folder_path, file_name), sheet_name)
                    logger.info(f"\tProcessed folder: {battery_folder_path}")
        else:
            logger.info("No subdirectories found.")
    else:
        logger.error("Specified path does not exist or is not a directory.")


if __name__ == "__main__":
    sheet_name = "Channel_4_1"
    file_base_name = "INR21700_M50T_T23_Aging_UDDS_SOC20_80_CC_0_5C_N25_W8_Channel_4."
    main_directory = "C:\\Users\\ayazh\\Desktop\\Master stage\\Cycling_tests"
    list_subdirectories(main_directory, file_base_name, sheet_name)
