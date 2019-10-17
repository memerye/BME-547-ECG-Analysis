# ecg.py
import os
import math


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
    signals. This function converts the strings to numbers. It
    regards the empty row as the end of the csv file. It can also
    print the corresponding error message when the data contain some
    non-numeric entries, missing data, or NaN.

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
            try:
                assert time_and_ecg[0] != '' and time_and_ecg[1] != ''
                time = float(time_and_ecg[0])
                ecg = float(time_and_ecg[1])
            except AssertionError:
                print('It has missing data')
                continue
            except ValueError:
                print('It has non numeric data')
                continue
            try:
                assert not math.isnan(time)
                assert not math.isnan(ecg)
            except AssertionError:
                print('It has NaN data')
                continue
            else:
                Time.append(time)
                ECG.append(ecg)
    assert len(Time) == len(ECG)
    return Time, ECG


if __name__ == "__main__":
    data_raw = read_data('test_data32.csv')
    Time, ECG = convert_data(data_raw)
