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
     ("root", "ERROR", "It has non numeric data on 1 row")),
    # (["a,0.2", "0.1,-0.5", "NaN,0.5", ",0.2"], [0.1], [-0.5],
    #  ("root", "ERROR", "It has non numeric data on 1 row"),
    #  ("root", "ERROR", "It has NaN data on 3 row"),
    #  ("root", "ERROR", "It has missing data on 4 row"))
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


@pytest.mark.parametrize("ECG, filename", [
    ([20, 42, 57, 89, 70], "test1.py"),
    ([-2.345, 6.203, -10.5, -50.5, 0.2], "test2.py"),
    ([100.56, 240.25, 70, 30.47], "test3.py")
])
def test_is_outside_range_with_warning(ECG, filename):
    from ecg import is_outside_range
    with LogCapture() as log_ecg:
        is_outside_range(ECG, filename)
    log_ecg.check()


@pytest.mark.parametrize("ECG, filename, logging_m", [
    ([20, 42, 400, 350, 70], "test1.py",
     ("root", "WARNING",
      "These ECG voltages in test1.py are out of range: [400, 350]")),
    ([-2.345, 6.203, -310.5, -450.5, 0.2], "test2.py",
     ("root", "WARNING",
      "These ECG voltages in test2.py are out of range: [-310.5, -450.5]")),
    ([510.56, 240.25, 70, 30.47], "test3.py",
     ("root", "WARNING",
      "These ECG voltages in test3.py are out of range: [510.56]"))
])
def test_is_outside_range_with_warning(ECG, filename, logging_m):
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


@pytest.mark.parametrize("Time, expected", [
    ([0.1, 0.2, 0.3], 0.2),
    ([0.2, 0.5, 0.6], 0.4),
    ([0.2, 0.3, 0.5, 0.8], 0.6)
])
def test_duration(Time, expected):
    """Test the function duration that calculates the time duration

    Args:
        Time (list): the list of time
        expected(float): the expected time duration

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import duration
    result = duration(Time)
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

# I found out that data 16-20 are quite clean. Can I just manually find
# the peaks in those signals and use those as my test signals?


def test_ECG():
    from ecg import read_data, convert_data, ave_sample_freq
    test_nor_filtered_ecg = []
    test_fs = []
    for i in range(3):
        filename = 'test_data{}.csv'.format(i+16)
        data_raw = read_data(filename)
        Time, ECG = convert_data(data_raw)
        fs = ave_sample_freq(Time)
        test_nor_filtered_ecg.append(ECG)
        test_fs.append(fs)
    return test_fs, test_nor_filtered_ecg


test_fs, test_nor_filtered_ecg = test_ECG()
manual_Rpeaks = np.asarray([32, 572, 1112, 1652, 2192, 2732, 3272, 3812,
                            4352, 4892, 5432, 5972, 6512, 7052, 7592, 8132,
                            8672, 9212, 9752])


@pytest.mark.parametrize("fs, nor_filtered_ecg, expected", [
    (test_fs[0], test_nor_filtered_ecg[0], manual_Rpeaks),
    (test_fs[1], test_nor_filtered_ecg[1], manual_Rpeaks),
    (test_fs[2], test_nor_filtered_ecg[2], manual_Rpeaks)
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
    assert result.tolist() == pytest.approx(expected.tolist(), abs=1)
