# ecg.py
import os
import math
import logging
import scipy.signal as ss
import matplotlib.pyplot as plt
import numpy as np


def read_data(file_name):
    """Read the data from the original csv file

    Args:
        file_name (string): the entire file name of the data

    Returns:
        list: The raw file content
    """
    root = os.getcwd()
    csv_path = os.path.join(root, 'test_data', file_name)
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


def ave_sample_freq(Time):
    """Calculate the average sample frequency of the signal.

    Args:
        Time (list): the list of time

    Returns:
        float: The number of the sample frequency as fs
    """
    return (len(Time)-1)/(Time[-1]-Time[0])


def duration(Time):
    """The duration of the ECG signal

    Args:
        Time (list): the list of time

    Returns:
        float: The total time duration of the ECG signal
    """
    return Time[-1]-Time[0]


def freq(ECG, Time):
    """Return the zooming in frequency spectrum

    Args:
        ECG (list): the list of the eCG signal
        Time (list): the list of the time

    Returns:
        None
    """
    N = len(Time)
    fECG = np.fft.fftshift(abs(np.fft.fft(ECG)))
    axis_xf = np.linspace(-N / 2, N / 2 - 1, num=N)
    plt.plot(axis_xf, fECG)
    plt.axis([-100, 100, 0, 500])
    plt.show()
    return None


def butter_bp(lowcut, highcut, fs, order=5):
    """A butterworth bandpass filter

    Args:
        lowcut (float): the lower cutoff frequency
        highcut (float): the higher cutoff frequency
        fs (float): the sampling frequency
        order (int): the order for the filter

    Returns:
        ndarray: Numerator of the filter
        ndarray: Denominator
    """
    nyq = 0.5*fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = ss.butter(order, [low, high], 'bandpass')
    return b, a


def ecg_filter(fs, ECG):
    """A filter for the ECG signal

    Args:
        fs (float): the sampling frequency
        ECG (list) : the ECG signal

    Returns:
        ndarray: The filtered ECG signal

    """
    b, a = butter_bp(0.4, 75, fs)
    filtered_ecg = ss.filtfilt(b, a, ECG)
    return filtered_ecg


def normalize(filtered_ecg):
    """Normalize the filtered ECG signal

    Args:
        filtered_ecg (ndarray): the filtered ECG signal

    Returns:
        ndarray: The normalized filtered ECG signal

    """
    nor_filtered_ecg = filtered_ecg/(max(filtered_ecg)-min(filtered_ecg))
    return nor_filtered_ecg


def local_mean(fs, nor_filtered_ecg):
    """Compute the local means in the normalized filtered ECG signal

    Args:
        fs (float): the sampling frequency
        nor_filtered_ecg (ndarray): the normalized filtered ECG signal

    Returns:
        ndarray: The local means in the normalized filtered ECG signal

    """
    t = round(0.25*fs)
    kernal = np.ones(t)/t
    mean_nor_filtered_ecg = ss.convolve(nor_filtered_ecg, kernal, mode='same')
    return mean_nor_filtered_ecg


def R_detect(fs, nor_filtered_ecg):
    """R wave detection

    Args:
        fs (float): the sampling frequency of the ECG signal
        nor_filtered_ecg (ndarray): the normalized filtered ECG signal

    Returns:
        ndarray: The indices in signal that satisfy the given conditions

    """
    mean_nor_filtered_ecg = local_mean(fs, nor_filtered_ecg)+0.05
    # Assume that the regular human rate is 120 bpm.
    dis_min = (60/120)*fs
    # dis_max = (60/40)/ts
    # QRS duration: 0.06s - 0.1s
    # qrs_width = [None, 0.2/ts]
    peaks, _ = ss.find_peaks(nor_filtered_ecg,
                             height=(mean_nor_filtered_ecg, None),
                             distance=dis_min)
    return peaks


def main(filename):
    """The main function of the ecg.py

    Returns:
        None

    """
    filename = 'test_data30.csv'
    log_config(filename)
    data_raw = read_data(filename)
    Time, ECG = convert_data(data_raw)
    is_outside_range(ECG, filename)
    fs = ave_sample_freq(Time)
    T = duration(Time)
    freq(ECG, Time)
    filtered_ecg = ecg_filter(fs, ECG)
    nor_filtered_ecg = normalize(filtered_ecg)
    mean_nor_filtered_ecg = local_mean(fs, nor_filtered_ecg)
    peaks = R_detect(fs, nor_filtered_ecg)
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(Time, ECG)
    ax2.plot(Time, nor_filtered_ecg)
    ax2.plot(Time, mean_nor_filtered_ecg, color="red")
    ax2.plot([Time[peak] for peak in peaks], nor_filtered_ecg[peaks], "x")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main('test_data16.csv')
