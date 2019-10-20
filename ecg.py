# ecg.py
import os
import math
import logging
import scipy.signal as ss
import matplotlib.pyplot as plt
import numpy as np
import json
import glob


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
                logging.error('It has missing data on {} row.'
                              .format(count))
                continue
            except ValueError:
                logging.error('It has non numeric data on {} row.'
                              .format(count))
                continue
            try:
                assert not math.isnan(time)
                assert not math.isnan(ecg)
            except AssertionError:
                logging.error('It has NaN data on {} row.'
                              .format(count))
                continue
            else:
                Time.append(time)
                ECG.append(ecg)
    assert len(Time) == len(ECG)
    return Time, ECG


def is_outside_range(ECG, file_name):
    """Test if the values in ECG are out of range of +/- 300 mv

    If the values in ECG are out of range of +/- 300 mv, a warning
    will be raised up to the log file indicating the name of the
    test file and that voltages exceeded the normal range.

    Args:
        ECG (list): the list of the ECG signals
        file_name (string): the entire file name of the data

    Returns:
        None
    """
    high_v = [ecg for ecg in ECG if abs(ecg) > 300]
    try:
        assert high_v == []
    except AssertionError:
        logging.warning('These ECG voltage {}mv in {} '
                        'is out of range.'.format(high_v[0], file_name))
    return None


def ave_sample_freq(Time):
    """Calculate the average sample frequency of the signal.

    Args:
        Time (list): the list of time

    Returns:
        float: The number of the sample frequency as fs
    """
    return (len(Time)-1)/(Time[-1]-Time[0])


def freq(filename, ECG, Time):
    """Return the zooming in frequency spectrum

    Args:
        filename (string): the name of the file
        ECG (list): the list of the eCG signal
        Time (list): the list of the time

    Returns:
        None
    """
    name = filename.split('.')
    N = len(Time)
    fECG = np.fft.fftshift(abs(np.fft.fft(ECG)))
    axis_xf = np.linspace(-N / 2, N / 2 - 1, num=N)
    plt.plot(axis_xf, fECG)
    plt.title("The frequency spectrum for ECG signal {}".format(name))
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
        ndarray: Denominator of the filter
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
        ndarray: the indices of R in signals

    """
    mean_nor_filtered_ecg = local_mean(fs, nor_filtered_ecg)+0.05
    # Assume that the maximum human rate (in regular range) is 150 bpm.
    dis_min = (60/150)*fs
    # dis_max = (60/40)/ts
    # QRS duration: 0.06s - 0.1s
    # qrs_width = [None, 0.2/ts]
    peaks, _ = ss.find_peaks(nor_filtered_ecg,
                             height=(mean_nor_filtered_ecg, None),
                             distance=dis_min)
    return peaks


def duration(Time):
    """The duration of the ECG signal

    Args:
        Time (list): the list of time

    Returns:
        float: The total time duration of the ECG signal
    """
    return Time[-1]-Time[0]


def voltage_extremes(ECG):
    """Compute the tuple containing minimum and maximum lead voltages

    Args:
        ECG (list): the list of the ECG signals

    Returns:
        tuple: minimum and maximum voltages
    """
    v_extremes = (min(ECG), max(ECG))
    return v_extremes


def stat_peaks(peaks):
    """Compute the removes the abnormal points in peak distance

    Compute the distance between each couple of the peaks. Remove the
    peak distance that is out of 2 times away from the median distance,
    which are considered as the wrong peaks.

    Args:
        peaks (ndarray): the indices of R in signals

    Returns:
        list: convinced distance between the peaks
    """
    peaks = peaks.tolist()
    peaks_ref = [0]+peaks[:-1]
    peaks_dis = [a-b for a, b in zip(peaks[1:], peaks_ref[1:])]
    dis_med = np.median(peaks_dis)
    dis_dev = np.abs(peaks_dis-dis_med)
    len_p = len(peaks_dis)
    peaks_dis_new = [peaks_dis[i] for i in range(len_p)
                     if dis_dev[i] <= dis_med]
    return peaks_dis_new


def num_beats(peaks):
    """Calculate the number of the peaks

    Args:
        peaks (ndarray): the indices of R in signals

    Returns:
        int: The number of the peaks
    """
    return len(peaks)


def mean_hr_bpm(peaks, fs):
    """Calculate the mean beats per minute

    Args:
        peaks (ndarray): the indices of R in signals
        fs (float): the sampling frequency of the ECG signal

    Returns:
        int: beats per minute
    """
    peaks_dis = stat_peaks(peaks)
    dis_mean_new = np.mean(peaks_dis)
    bpm = int(round(60/(dis_mean_new/fs)))
    return bpm


def beats(Time, peaks):
    """Record the times when beats occurred

    Args:
        Time (list): the list of time
        peaks (ndarray): the indices of R in signals

    Returns:
        ndarray: The numpy array of time sequence when beats occurred
    """
    t_beats = [Time[peak] for peak in peaks]
    t_beats_array = np.asarray(t_beats)
    return t_beats_array


def visual_result(filename, Time, ECG, nor_filtered_ecg,
                  mean_nor_filtered_ecg, peaks):
    """Visualize the ECG signals with peaks on it

    Args:
        filename (string): the name of the file
        Time (list): the list of time
        ECG (list): the list of the ECG signals
        nor_filtered_ecg (ndarray): the normalized filtered ECG signal
        mean_nor_filtered_ecg (ndarray): the local means in the
        normalized filtered ECG signal
        peaks (ndarray): the indices of R in signals

    Returns:
        None
    """
    name = filename.split('.')
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(Time, ECG)
    ax1.set_title("Original ECG signal {}".format(name))
    ax2.plot(Time, nor_filtered_ecg)
    ax2.plot(Time, mean_nor_filtered_ecg, color="red")
    ax2.plot([Time[peak] for peak in peaks], nor_filtered_ecg[peaks], "x")
    ax2.set_title("Filtered ECG signal with R peaks")
    plt.tight_layout()
    plt.show()


def create_dict(Time, ECG, peaks, fs):
    """Form the dictionary for each signal

    It basically only uses other functions so that it doesn't have
    test function for the outputs but have test for logging info.
    Each patient has a dictionary, which contains following information:
    duration: time duration of the ECG strip
    voltage_extremes: tuple containing minimum and maximum lead voltages
    num_beats: number of detected beats in the strip
    mean_hr_bpm: estimated average heart rate over the length of the strip
    beats: numpy array of times when a beat occurred

    Args:
        Time (list): the list of time
        ECG (list): the list of the ECG signals
        peaks (ndarray): the indices of R in signals
        fs (float): the sampling frequency of the ECG signal

    Returns:
        dict: The output dictionary of the ECG data
    """
    d = duration(Time)
    logging.info('* Finish calculating duration as float')
    v = voltage_extremes(ECG)
    logging.info('                 '
                 '... voltage extremes as tuple')
    n = num_beats(peaks)
    logging.info('                 '
                 '... number of beats as int')
    m = mean_hr_bpm(peaks, fs)
    logging.info('                 '
                 '... mean bpm as int')
    b = beats(Time, peaks).tolist()
    logging.info('                 '
                 '... time of beats as list')
    metrics = {"duration": d,
               "voltage_extremes": v,
               "num_beats": n,
               "mean_hr_bpm": m,
               "beats": b}
    return metrics


def json_output(metrics, file_name):
    """Create the json output files for each signal

    The json file have the same name as the ECG data file,
    but with an extension of .json.
    The file should contain the following information in JSON format:
    duration: time duration of the ECG strip
    voltage_extremes: tuple containing minimum and maximum lead voltages
    num_beats: number of detected beats in the strip
    mean_hr_bpm: estimated average heart rate over the length of the strip
    beats: numpy array of times when a beat occurred

    Args:
        metrics (dict): The output dictionary of the ECG data
        file_name (string): the entire file name of the data

    Returns:
        None
    """
    folder_name = "json_outputs"
    root = os.getcwd()
    try:
        os.mkdir(folder_name)
    except FileExistsError:
        pass
    json_name = file_name.split('.')[0]+'.json'
    path = os.path.join(root, folder_name, json_name)
    out_file = open(path, "w")
    json.dump(metrics, out_file)
    out_file.close()
    return


def sort_files(ecg_files):
    """Sort the ecg files in the folder

    The name of the ecg file should follow the format as:
    test_data*.csv, where * stands for the number of the file

    Args:
        ecg_files (list): The list of the path of ecg files
        in random order

    Returns:
        list: The list of the all of the ecg files
    """
    count = 0
    order = []
    for ecg_file in ecg_files:
        count = count + 1
        file_num = int(ecg_file.split('/')[-1].split('.')[0][9:])
        order.append(file_num)
    order_index = np.argsort(order)
    files = [ecg_files[i] for i in order_index]
    return files


def main(files_path):
    """The main function of the ecg.py

    Returns:
        None
    """
    logging.basicConfig(filename="ecg.log",
                        level=logging.INFO,
                        filemode='w')
    ecg_files = glob.glob(files_path)
    ecg_files_sorted = sort_files(ecg_files)
    for ecg_file in ecg_files_sorted:
        filename = ecg_file.split('/')[1]
        logging.info('----This is the log of file {}----'.format(filename))
        logging.info('Reading the data...')
        data_raw = read_data(filename)
        Time, ECG = convert_data(data_raw)
        is_outside_range(ECG, filename)
        logging.info('* Finish reading the ECG data as list.')
        fs = ave_sample_freq(Time)
        logging.info('* Finish computing the sampling frequency as '
                     '{0:.2f}Hz'.format(fs))
        filtered_ecg = ecg_filter(fs, ECG)
        logging.info('* Finish filtering the ECG signal')
        nor_filtered_ecg = normalize(filtered_ecg)
        mean_nor_filtered_ecg = local_mean(fs, nor_filtered_ecg)
        peaks = R_detect(fs, nor_filtered_ecg)
        logging.info('* Finish finding the R peaks in ECG signal')
        # freq(filename, ECG, Time)
        # visual_result(filename, Time, ECG, nor_filtered_ecg,
        #               mean_nor_filtered_ecg, peaks)
        logging.info('Calculating the information in dictionary...')
        metrics = create_dict(Time, ECG, peaks, fs)
        logging.info('* Complete calculation.')
        logging.info('Saving the information in json...')
        json_output(metrics, filename)
        logging.info('* Complete save the json file')
        logging.info('----This is the end of file {}----\n'.format(filename))


if __name__ == "__main__":
    files_path = 'test_data/*.csv'
    main(files_path)
