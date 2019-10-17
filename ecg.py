# ecg.py
import os
import math
import logging


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
    count = 0
    for row in data_raw:
        count = count + 1
        time_and_ecg = row.split(',')
        if time_and_ecg != ['']:
            try:
                assert time_and_ecg[0] != '' and time_and_ecg[1] != ''
                time = float(time_and_ecg[0])
                ecg = float(time_and_ecg[1])
            except AssertionError:
                logging.error('It has missing data on {} row'
                              .format(count))
                continue
            except ValueError:
                logging.error('It has non numeric data on {} row'
                              .format(count))
                continue
            try:
                assert not math.isnan(time)
                assert not math.isnan(ecg)
            except AssertionError:
                logging.error('It has NaN data on {} row'
                              .format(count))
                continue
            else:
                Time.append(time)
                ECG.append(ecg)
    assert len(Time) == len(ECG)
    return Time, ECG


def is_outside_range(ECG, filename):
    # the name of the test file?
    try:
        high_v = [ecg for ecg in ECG if abs(ecg) > 300]
        assert high_v == []
    except AssertionError:
        logging.warning('These ECG voltages in {} '
                        'are out of range: {}'.format(filename, high_v))
    return None


def log_config(filename, level=logging.WARNING):
    log_name = filename.split('.')[0]+'.log'
    try:
        os.mkdir('log')
    except FileExistsError:
        pass
    logging.basicConfig(filename="./log/{}".format(log_name),
                        level=level,
                        datefmt='%b %d %Y %H:%M',
                        filemode='w')
    return None


def main():
    filename = 'test_data30.csv'
    log_config(filename)
    data_raw = read_data(filename)
    Time, ECG = convert_data(data_raw)
    is_outside_range(ECG, filename)


if __name__ == "__main__":
    main()
