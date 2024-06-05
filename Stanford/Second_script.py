import scipy
from PyEMD import EMD
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, kurtosis
import os
import glob
from Stanford.extract_name import extract_tokens


def calculate_vc(original_voltage):
    """
    Perform Empirical Mode Decomposition (EMD) on the voltage signal.

    :param original_voltage: The original voltage signal.
    :return: Vc values after decomposition.
    """
    emd = EMD()
    imf = emd(original_voltage)
    dynamic_array = np.array([])

    signal_sum = np.zeros(shape=original_voltage.shape)

    # Iterate through each Intrinsic Mode Function (IMF)
    for i, mode in enumerate(imf):
        for j, value in enumerate(imf[i, :]):
            signal_sum[j] += imf[i, j]
        corr, p_value = pearsonr(original_voltage, imf[i, :])
        dynamic_array = np.append(dynamic_array, corr)
    vc_values = original_voltage - imf[-1]
    return vc_values


def extract_features(buffer, vc_values):
    """
    Extract various statistical features from the voltage signal.

    :param buffer: The data buffer containing voltage values.
    :param vc_values: The Vc values from EMD.
    :return: A list of extracted features.
    """
    vc_values = np.array(vc_values)

    abs_voltage_value = np.abs(vc_values)
    peak_value = np.max(abs_voltage_value)
    mean_voltage = np.mean(vc_values)
    squared_voltage_values = vc_values ** 2
    mean_squared_voltage = np.mean(squared_voltage_values)
    rms_value = np.sqrt(mean_squared_voltage)
    skewness = scipy.stats.skew(vc_values)
    crest_factor = peak_value / rms_value
    kurtosis_value = kurtosis(vc_values)
    avg_abs_value = np.mean(abs_voltage_value)
    shape_factor = rms_value / avg_abs_value
    impulse_factor = peak_value / avg_abs_value
    noise_std = np.std(vc_values)
    snr = mean_voltage / noise_std

    def calculate_clearance_factor(voltage_values):
        avg_sqrt_voltage = np.mean(np.sqrt(voltage_values))
        clearance_factor = peak_value / (avg_sqrt_voltage ** 2)
        return clearance_factor

    clearance_factor = calculate_clearance_factor(abs_voltage_value)

    original_voltage_values = buffer['Voltage(V)']

    def calculate_sample_std_dev(original_voltage_values):
        original_voltage_values = np.array(original_voltage_values)
        original_voltage_mean = np.mean(original_voltage_values)
        sum_squared_deviations = np.sum((original_voltage_values - original_voltage_mean) ** 2)
        N = len(original_voltage_values)
        sample_std_dev = np.sqrt(sum_squared_deviations / (N - 1))
        return sample_std_dev

    sample_std_dev = calculate_sample_std_dev(original_voltage_values)

    features = [
        peak_value, mean_voltage, rms_value, skewness, crest_factor, kurtosis_value, shape_factor,
        impulse_factor, snr, sample_std_dev, clearance_factor
    ]
    return features


def extract_next_buffer(dataframe, buffer_length, current_time):
    """
    Extract a buffer of data from the dataframe based on the specified time window.

    :param dataframe: The dataframe containing the data.
    :param buffer_length: The length of the buffer in seconds.
    :param current_time: The starting time to extract the buffer.
    :return: The extracted buffer.
    """
    buffer = dataframe[(dataframe['Step_Time(s)'] >= current_time) &
                       (dataframe['Step_Time(s)'] < current_time + buffer_length)]
    if buffer.empty:
        print(current_time, buffer_length)
        print("Warning: Buffer is empty.")
    return buffer


def extract_features_for_battery(excel_files_directory, feature_files_directory, file_name_template,
                                 buffer_length_in_mins, starting_time):
    """
    Extract features from battery data and save them to CSV files.

    :param excel_files_directory: Directory containing the Excel files.
    :param feature_files_directory: Directory to save the feature CSV files.
    :param file_name_template: Template for the file names.
    :param buffer_length_in_mins: Length of each buffer in minutes.
    :param starting_time: Starting time in minutes.
    """
    excel_files = glob.glob(os.path.join(excel_files_directory, file_name_template))

    for i, excel_file in enumerate(excel_files, start=1):
        dataframe = pd.read_excel(excel_file)

        buffer_length_in_seconds = buffer_length_in_mins * 60
        buffer_start_time_in_seconds = starting_time * 60
        print(f"You chose a buffer of {buffer_length_in_seconds} seconds")
        print(f"Preparing file {i}")

        output_csv_file = os.path.join(feature_files_directory, f"features_{i}.csv")

        with open(output_csv_file, 'w') as file:
            file.write(
                "Peak Value,Mean Voltage,RMS,Skewness,Crest Factor,Kurtosis,Shape Factor,Impulse Factor,SNR,Sample Std Dev,Clearance Factor,Discharge_Capacity(Ah)\n")

        buffer_data = extract_next_buffer(dataframe, buffer_length_in_seconds, buffer_start_time_in_seconds)
        buffer_original_voltage = buffer_data["Voltage(V)"]
        buffer_original_voltage = np.array(buffer_original_voltage)

        while True:
            if buffer_data.empty:
                print("Buffer is empty. Exiting loop.")
                break

            vc_values = calculate_vc(buffer_original_voltage)
            features = extract_features(buffer_data, vc_values)

            # Extract the last value of the "Discharge Capacity (Ah)" column
            last_discharge_capacity = buffer_data.iloc[-1]['Discharge_Capacity(Ah)']

            with open(output_csv_file, 'a') as file:
                features_with_discharge_capacity = features + [last_discharge_capacity]
                file.write(",".join(map(str, features_with_discharge_capacity)) + "\n")

            buffer_start_time_in_seconds += buffer_length_in_seconds

            buffer_data = extract_next_buffer(dataframe, buffer_length_in_seconds, buffer_start_time_in_seconds)
            buffer_original_voltage = buffer_data["Voltage(V)"]
            buffer_original_voltage = np.array(buffer_original_voltage)


def list_subdirectories(input_folder, output_folder, buffer_length_in_mins, starting_time):
    """
    List subdirectories and process files within each.

    :param input_folder: Path to the main input directory.
    :param output_folder: Path to the main output directory.
    :param buffer_length_in_mins: Length of each buffer in minutes.
    :param starting_time: Starting time in minutes.
    """
    if os.path.exists(input_folder) and os.path.isdir(input_folder):
        print(f"Listing subdirectories in '{input_folder}':")
        # Get the list of all files and directories in the specified path
        cycling_list = os.listdir(input_folder)

        # Filter only directories
        cycling_folders_list = [c for c in cycling_list if os.path.isdir(os.path.join(input_folder, c))]

        # Print the list of directories, if present
        if cycling_folders_list:
            for input_cycles_path in cycling_folders_list:
                output_cycles_path = os.path.join(output_folder, input_cycles_path)
                os.makedirs(output_cycles_path, exist_ok=True)  # makedirs creates a folder if it doesn't exist.

                input_cycles_path = os.path.join(input_folder, input_cycles_path)
                print(input_cycles_path)

                battery_list = os.listdir(input_cycles_path)
                battery_folders = [
                    c for c in battery_list if os.path.isdir(os.path.join(input_cycles_path, c))
                    and c not in ['_processed_mat', '__MACOSX']
                ]
                for battery_folder in battery_folders:
                    output_battery_folder = os.path.join(output_cycles_path, battery_folder)
                    os.makedirs(output_battery_folder, exist_ok=True)

                    battery_folder = os.path.join(input_cycles_path, battery_folder)
                    print(battery_folder)
                    first_file = os.listdir(battery_folder)[0]
                    file_name_template, sheet_name = extract_tokens(first_file)
                    file_name_template = file_name_template + "out.*.xlsx"
                    print(file_name_template)
                    extract_features_for_battery(battery_folder, output_battery_folder, file_name_template, buffer_length_in_mins, starting_time)


def main():
    input_folder = "/home/haseeb/Data/Cycling_done"
    output_folder = "/home/haseeb/Data/features"
    buffer_length_in_mins = 60  # Adjust as needed
    starting_time = 0  # Adjust as needed

    list_subdirectories(input_folder, output_folder, buffer_length_in_mins, starting_time)


if __name__ == "__main__":
    main()