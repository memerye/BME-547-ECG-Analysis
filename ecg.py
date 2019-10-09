# ecg.py
import os


def read_data(file_name):
    """Read the data from the original csv file

    Args:
        file_name (string): the entile file name of the data

    Returns:
        list: The raw file content
    """
    csv_path = os.path.join('test_data', file_name)
    f = open(csv_path, 'r')
    data_raw = f.read().split('\n')
    f.close()
    return data_raw


def convert_data(data_raw):
    """Convert the data from raw string style to the list numbers

    The raw data is the list of the strings with mixed time and ecg
    signals. This function converts the strings to numbers. It can
    tolerate the empty row inside or at the end of the csv file.

    Args:
        data_raw (list): the raw file content

    Returns:
        list: The list of the time
        list: The list of the ECG signals
    """
    Time = []
    ECG = []
    for row in data_raw:
        time_and_ecg = row.split(',')
        if time_and_ecg != ['']:
            time = float(time_and_ecg[0])
            ecg = float(time_and_ecg[1])
            Time.append(time)
            ECG.append(ecg)
    return Time, ECG


if __name__ == "__main__":
    data_raw = read_data('test_data1.csv')
    Time, ECG = convert_data(data_raw)
