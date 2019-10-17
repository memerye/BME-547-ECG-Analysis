# test_ecg.py
import pytest
from testfixtures import LogCapture


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
