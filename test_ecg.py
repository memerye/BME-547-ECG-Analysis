# test_ecg.py
import pytest
from testfixtures import LogCapture
import numpy as np


@pytest.mark.parametrize("data_raw, expected1, expected2", [
    (["2,-3", "4.2,2.3"], [2, 4.2], [-3, 2.3]),
    (["1.02,-2.345", "2.13,6.203", ""], [1.02, 2.13], [-2.345, 6.203]),
    ([""], [], [])
])
def test_convert_data_no_abnormal_data(data_raw, expected1, expected2):
    """Test the function convert_data that converts the data style

    The input data are all without abnormal data such as missing data,
    non numeric data and NaN data.

    Args:
        data_raw (list): the raw file content
        expected1(list): the expected time
        expected2(list): the expected ecg signal

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import convert_data
    with LogCapture() as log_ecg:
        result1, result2 = convert_data(data_raw)
        assert result1 == expected1 and result2 == expected2
    log_ecg.check()


@pytest.mark.parametrize("data_raw, expected1, expected2, logging_m", [
    ([",2.3", "1.3,0.6", "1.4,-0.2"], [1.3, 1.4], [0.6, -0.2],
     ("root", "ERROR", "It has missing data on 1 row")),
    (["-0.2,1.1", "0.3,1.3", "0.4,NaN"], [-0.2, 0.3], [1.1, 1.3],
     ("root", "ERROR", "It has NaN data on 3 row")),
    (["@,1.2", "0.4,1.4"], [0.4], [1.4],
     ("root", "ERROR", "It has non numeric data on 1 row"))
])
def test_convert_data_abnormal_data(data_raw, expected1, expected2, logging_m):
    """Test the function convert_data that converts the data style

    The input data are all with abnormal data such as missing data,
    non numeric data and NaN data.

    Args:
        data_raw (list): the raw file content
        expected1(list): the expected time
        expected2(list): the expected ecg signal
        logging_m(tuple): the expected logging message

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import convert_data
    with LogCapture() as log_ecg:
        result1, result2 = convert_data(data_raw)
        assert result1 == expected1 and result2 == expected2
    log_ecg.check(logging_m)


@pytest.mark.parametrize("data_raw, expected1, expected2", [
    (["a,0.2", "0.1,-0.5", "NaN,0.5", ",0.2"], [0.1], [-0.5]),
    (["0.3,@", "1.5,1.3", "NaN,0.7", "0.6,"], [1.5], [1.3]),
    (["0.1,`", "-0.3,-0.1", "NaN,1.2", "1.1,"], [-0.3], [-0.1])
])
def test_convert_data_multi_abnormal_data(data_raw, expected1, expected2):
    """Test the function convert_data that converts the data style

    Each element in input data is along with abnormal data such as missing
    data, non numeric data and NaN data. In order to have the same logging
    record, I purposely set the data with the same type of error in the
    same place.

    Args:
        data_raw (list): the raw file content
        expected1(list): the expected time
        expected2(list): the expected ecg signal

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import convert_data
    with LogCapture() as log_ecg:
        result1, result2 = convert_data(data_raw)
        assert result1 == expected1 and result2 == expected2
    log_ecg.check(("root", "ERROR", "It has non numeric data on 1 row"),
                  ("root", "ERROR", "It has NaN data on 3 row"),
                  ("root", "ERROR", "It has missing data on 4 row"))


@pytest.mark.parametrize("ECG, file_name", [
    ([20, 42, 57, 89, 70], "test1.py"),
    ([-2.345, 6.203, -10.5, -50.5, 0.2], "test2.py"),
    ([100.56, 240.25, 70, 30.47], "test3.py")
])
def test_is_outside_range_no_warning(ECG, file_name):
    """Test the function is_outside_range that test the ECG values' range

    This function has no warning in the log file.

    Args:
        ECG (list): the list of the ECG signals
        file_name (string): the entire file name of the data

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import is_outside_range
    with LogCapture() as log_ecg:
        is_outside_range(ECG, file_name)
    log_ecg.check()


@pytest.mark.parametrize("ECG, filename, logging_m", [
    ([20, 42, 400, 350, 70], "test1.py",
     ("root", "WARNING",
      "These ECG voltage 400mv in test1.py is out of range.")),
    ([-2.345, 6.203, -310.5, -450.5, 0.2], "test2.py",
     ("root", "WARNING",
      "These ECG voltage -310.5mv in test2.py is out of range.")),
    ([510.56, 240.25, 70, 30.47], "test3.py",
     ("root", "WARNING",
      "These ECG voltage 510.56mv in test3.py is out of range."))
])
def test_is_outside_range_with_warning(ECG, filename, logging_m):
    """Test the function is_outside_range that test the ECG values' range

    This function has warnings in the log file.

    Args:
        ECG (list): the list of the ECG signals
        file_name (string): the entire file name of the data
        logging_m (tuple): the warning messages

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import is_outside_range
    with LogCapture() as log_ecg:
        is_outside_range(ECG, filename)
    log_ecg.check(logging_m)


@pytest.mark.parametrize("Time, expected", [
    ([0.1, 0.2, 0.3], 10),
    ([0.2, 0.5, 0.6], 5),
    ([0.2, 0.3, 0.5, 0.8], 5)
])
def test_ave_sample_freq(Time, expected):
    """Test the function ave_sample_freq that calculates the average sampling time

    Args:
        Time (list): the list of time
        expected(float): the expected average sampling frequency

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import ave_sample_freq
    result = ave_sample_freq(Time)
    assert result == pytest.approx(expected)


def test_signal():
    """Create six signals to test the filter function

    Returns:
        list: A list of six signals which contains three signals
        inside the cutoff frequency and three signals outside the
        cutoff frequency

    """
    test_signals = []
    t = np.linspace(0, 10, 2000)
    # outside the cutoff frequency
    for i in range(1, 4):
        signal = np.sin(2*np.pi*0.01*i*t)/np.sqrt(2)
        signal = signal+np.sin(2*np.pi*(10*i+80)*t)/np.sqrt(2)
        signal.tolist()
        test_signals.append(signal)
    # inside the cutoff frequency
    for i in range(1, 4):
        signal = np.sin(2*np.pi*(i+10)*t)
        signal.tolist()
        test_signals.append(signal)
    return test_signals


test_signals = test_signal()


@pytest.mark.parametrize("fs, ECG, expected", [
    (200, test_signals[0], np.zeros_like(test_signals[0])),
    (200, test_signals[1], np.zeros_like(test_signals[0])),
    (200, test_signals[2], np.zeros_like(test_signals[0])),
    (200, test_signals[3], np.asarray(test_signals[3])),
    (200, test_signals[4], np.asarray(test_signals[4])),
    (200, test_signals[5], np.asarray(test_signals[5]))
])
def test_ecg_filter(fs, ECG, expected):
    """Test the function ecg_filter that filters the signal

    Args:
        fs (float): the sampling frequency
        ECG (list):  the ECG signal
        expected(ndarray): the expected filtered signals

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import ecg_filter
    filtered_signal = ecg_filter(fs, ECG)
    result = np.sqrt(np.mean((filtered_signal-expected)**2))
    assert result == pytest.approx(0, abs=0.1)


@pytest.mark.parametrize("filtered_ecg, expected", [
    (np.asarray([0.1, 0.2, 0.3]), np.asarray([0.5, 1, 1.5])),
    (np.asarray([0.2, 0.5, 0.6]), np.asarray([0.5, 1.25, 1.5])),
    (np.asarray([0.2, 0.3, 0.5, 1.0]), np.asarray([0.25, 0.375, 0.625, 1.25]))
])
def test_normalize(filtered_ecg, expected):
    """Test the function normalize that normalizes the signal

    Args:
        filtered_ecg (ndarray): the filtered ECG signal
        expected (ndarray): the expected normalized signals

    Returns:
        Error if the test fails
        Pass if the test passes

    """
    from ecg import normalize
    result = normalize(filtered_ecg)
    assert result.tolist() == pytest.approx(expected.tolist())


@pytest.mark.parametrize("fs, nor_filtered_ecg, expected", [
    (12, np.asarray([0.1, 0.2, 0.3]), np.asarray([0.1, 0.2, 0.5/3])),
    (12, np.asarray([0.2, 0.5, 0.6]), np.asarray([0.7/3, 1.3/3, 1.1/3])),
    (12, np.asarray([0.2, 0.3, 0.5, 1.0]), np.asarray([0.5/3, 1/3, 0.6, 0.5]))
])
def test_local_mean(fs, nor_filtered_ecg, expected):
    """Test the function local_mean that gets the local mean of the signal

    Args:
        fs (float): the sampling frequency
        nor_filtered_ecg (ndarray): the normalized filtered ECG signal
        expected (ndarray): the expected local means of the input signal

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import local_mean
    result = local_mean(fs, nor_filtered_ecg)
    assert result.tolist() == pytest.approx(expected.tolist())


def test_ECG():
    """Import the test ECG signals for testing R detection

    Returns:
        float: the sampling frequency
        list: the test normalized ECG signals
    """
    from ecg import read_data, convert_data, ave_sample_freq, normalize
    test_nor_filtered_ecg = []
    test_fs = []
    for i in range(3):
        filename = 'test_data{}.csv'.format(i+16)
        data_raw = read_data(filename)
        Time, ECG = convert_data(data_raw)
        ECG = np.asarray(ECG)
        nor_filtered_ecg = normalize(ECG)
        fs = ave_sample_freq(Time)
        test_nor_filtered_ecg.append(nor_filtered_ecg)
        test_fs.append(fs)
    return test_fs, test_nor_filtered_ecg


test_fs, test_nor_filtered_ecg = test_ECG()
# python starts counting from 0
manual_R_peaks = np.asarray([31, 571, 1111, 1651, 2191, 2731, 3271, 3811,
                            4351, 4891, 5431, 5971, 6511, 7051, 7591, 8131,
                            8671, 9211, 9751])


@pytest.mark.parametrize("fs, nor_filtered_ecg, expected", [
    (test_fs[0], test_nor_filtered_ecg[0], manual_R_peaks),
    (test_fs[1], test_nor_filtered_ecg[1], manual_R_peaks),
    (test_fs[2], test_nor_filtered_ecg[2], manual_R_peaks)
])
def test_R_detect(fs, nor_filtered_ecg, expected):
    """Test the function R_detect that detects the R wave of the signal

    Args:
        fs (float): the sampling frequency
        nor_filtered_ecg (ndarray): the normalized filtered ECG signal
        expected (ndarray): the expected indices of R peaks in signal

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import R_detect
    result = R_detect(fs, nor_filtered_ecg)
    assert result.tolist() == pytest.approx(expected.tolist())


@pytest.mark.parametrize("Time, expected", [
    ([0.1, 0.2, 0.3], 0.2),
    ([0.2, 0.5, 0.6], 0.4),
    ([0.2, 0.3, 0.5, 0.8], 0.6)
])
def test_duration(Time, expected):
    """Test the function duration that calculates the time duration

    Args:
        Time (list): the list of time
        expected (float): the expected time duration

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import duration
    result = duration(Time)
    assert result == pytest.approx(expected)


@pytest.mark.parametrize("Time, expected", [
    ([0.1, 0.2, 0.3], (0.1, 0.3)),
    ([0.2, 0.5, 0.6], (0.2, 0.6)),
    ([0.2, 0.3, 0.5, 0.8], (0.2, 0.8))
])
def test_voltage_extremes(Time, expected):
    """Test the function voltage_extremes that calculates min and max voltages

    Args:
        Time (list): the list of time
        expected (tuple): the expected time voltage extremes

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import voltage_extremes
    result = voltage_extremes(Time)
    assert result == expected


@pytest.mark.parametrize("peaks, expected", [
    (np.asarray([0.1, 0.2, 0.3, 0.4, 1.5, 1.65, 1.8]),
     [0.1, 0.1, 0.1, 0.15, 0.15]),
    (np.asarray([0.2, 0.4, 0.7, 1.0, 2.1, 2.2]),
     [0.2, 0.3, 0.3, 0.1]),
    (np.asarray([0.2, 0.6, 1.1, 1.4, 2.0, 2.4]),
     [0.4, 0.5, 0.3, 0.6, 0.4])
])
def test_stat_peaks(peaks, expected):
    """Test the function stat_peaks that removes the abnormal
    points in peak distance and return the peak distance

    Args:
        peaks (ndarray): the indices of R in signals
        expected (list): the expected peaks distance

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import stat_peaks
    result = stat_peaks(peaks)
    assert result == pytest.approx(expected)


@pytest.mark.parametrize("peaks, expected", [
    (np.asarray([0.1, 0.2, 0.3, 0.4]), 4),
    (np.asarray([0.2, 0.4, 0.7, 1.0, 2.1, 2.2]), 6),
    (np.asarray([0.2, 0.6, 1.1, 1.4, 2.0]), 5)
])
def test_num_beats(peaks, expected):
    """Test the function num_beats that calculates the number of the peaks

    Args:
        peaks (ndarray): the indices of R in signals
        expected (list): the expected number of the peaks

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import num_beats
    result = num_beats(peaks)
    assert result == expected


@pytest.mark.parametrize("peaks_dis, fs, expected", [
    (np.asarray([0.1, 0.2, 0.3, 0.4, 1.5, 1.65, 1.8]), 10, 5000),
    (np.asarray([0.2, 0.4, 0.7, 1.0, 2.1, 2.2]), 10, 2667),
    (np.asarray([0.2, 0.6, 1.1, 1.4, 2.0, 2.4]), 10, 1364)
])
def test_mean_hr_bpm(peaks_dis, fs, expected):
    """Test the function mean_hr_bpm that calculates the mean beats per minute

    Args:
        peaks (ndarray): the indices of R in signals
        expected (list): the expected mean beats per minute

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import mean_hr_bpm
    result = mean_hr_bpm(peaks_dis, fs)
    assert result == expected


@pytest.mark.parametrize("Time, peaks, expected", [
    ([0.1, 0.2, 0.3, 0.4, 0.5],
     np.asarray([0, 1, 3]), np.asarray([0.1, 0.2, 0.4])),
    ([1.7, 1.8, 1.9, 2.0, 2.1, 2.2],
     np.asarray([0, 2, 3]), np.asarray([1.7, 1.9, 2.0])),
    ([0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
     np.asarray([3, 5, 6]), np.asarray([1.2, 1.6, 1.8]))
])
def test_beats(Time, peaks, expected):
    """Test the function beats that records the times when beats occurred

    Args:
        Time (list): the list of time
        peaks (ndarray): the indices of R in signals
        expected (list): the expected times of beats

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import beats
    result = beats(Time, peaks)
    assert result.tolist() == expected.tolist()


@pytest.mark.parametrize("ecg_files, expected", [
    (["test_data3.csv", "test_data7.csv", "test_data5.csv"],
     ["test_data3.csv", "test_data5.csv", "test_data7.csv"]),
    (["test_data9.csv", "test_data6.csv", "test_data1.csv"],
     ["test_data1.csv", "test_data6.csv", "test_data9.csv"]),
    (["test_data2.csv", "test_data11.csv", "test_data3.csv"],
     ["test_data2.csv", "test_data3.csv", "test_data11.csv"])
])
def test_sort_files(ecg_files, expected):
    """Test the function sort_files that sorts the ecg files in the folder

    Args:
        ecg_files (list): The list of the ecg files in random order
        expected (list): the expected ecg files in the folder

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import sort_files
    result = sort_files(ecg_files)
    assert result == expected
