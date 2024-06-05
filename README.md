
# Battery Data Processing and Feature Extraction

This repository contains scripts to process battery cycling test data from Excel files, extract statistical features, and save the results to CSV files. The repository includes the following Python scripts:

1. `First_script.py`: Processes Excel files to extract specific rows based on conditions and saves the results to new Excel files.
2. `Second_script.py`: Performs Empirical Mode Decomposition (EMD) on voltage data, extracts statistical features, and saves them to CSV files.
3. `extract_name.py`: Extracts tokens from file names to construct new file names and sheet names.

## Requirements

You can install the required packages using pip:

```bash
 pip install pandas numpy scipy openpyxl PyEMD
```

## Scripts Overview

### `First_script.py`

This script processes Excel files to extract specific rows based on certain conditions and saves the results to new Excel files.

#### Functions

- `process_cycle(file_number, start_row, output_file_number, file_base_name, sheet_name)`: Loads and processes data from an Excel file.
- `load_data(file_base_name, file_number, start_row, rows_to_add, sheet_name)`: Reads data from an Excel file and searches for specific conditions.
- `process_all_cycles(file_base_name, sheet_name)`: Iteratively processes multiple files to extract data based on conditions.
- `list_subdirectories(directory, file_name, sheet_name)`: Lists subdirectories and processes files within each.

#### Usage

```bash
python First_script.py
```

### `Second_script.py`

This script performs Empirical Mode Decomposition (EMD) on voltage data, extracts statistical features, and saves them to CSV files.

#### Functions

- `calculate_vc(original_voltage)`: Performs Empirical Mode Decomposition (EMD) on the voltage signal.
- `extract_features(buffer, vc_values)`: Extracts various statistical features from the voltage signal.
- `extract_next_buffer(dataframe, buffer_length, current_time)`: Extracts a buffer of data from the dataframe based on the specified time window.
- `extract_features_for_battery(excel_files_directory, feature_files_directory, file_name_template, buffer_length_in_mins, starting_time)`: Extracts features from battery data and saves them to CSV files.
- `list_subdirectories(input_folder, output_folder, buffer_length_in_mins, starting_time)`: Lists subdirectories and processes files within each.
- `main()`: Main function to set parameters and call `list_subdirectories`.

#### Usage

```bash
python Second_script.py
```

### `extract_name.py`

This script extracts tokens from file names to construct new file names and sheet names.

#### Functions

- `extract_tokens(input_string)`: Extracts tokens from the given input string to form a file name and sheet name.

#### Usage

This script is imported and used by both `First_script.py` and `Second_script.py`.

## Example

1. **Running `First_script.py`**:
   - Ensure your Excel files are in the specified directory.
   - Update the `file_base_name` and `sheet_name` variables as needed.
   - Run the script:
     ```bash
     python First_script.py
     ```

2. **Running `Second_script.py`**:
   - Ensure your input folder and output folder paths are correct.
   - Set the desired buffer length and starting time.
   - Run the script:
     ```bash
     python Second_script.py
     ```
