# test_ecg.py
import pytest


@pytest.mark.parametrize("data_raw, expected1, expected2", [
    (["2,-3", "4.2,2.3"], [2, 4.2], [-3, 2.3]),
    (["1.02,-2.345", "2.13,6.203", ""], [1.02, 2.13], [-2.345, 6.203]),
    ([""], [], []),
    ([",2.3", "1.3,0.6", "1.2,", "1.4,-0.2"], [1.3, 1.4], [0.6, -0.2]),
    (["NaN,1.2", "-0.2,1.1", "0.3,1.3", "0.4,NaN"], [-0.2, 0.3], [1.1, 1.3]),
    (["@,1.2", "0.3,v", "0.4,1.4"], [0.4], [1.4]),
    (["a,0.2", "0.1,-0.5", "NaN,0.5", ",0.2"], [0.1], [-0.5])
])
def test_convert_data(data_raw, expected1, expected2):
    """Test the function convert_data that converts the data style
    Args:
        data_raw (list): the raw file content
        expected1(list): the expected time
        expected2(list): the expected ecg signal
    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import convert_data
    result1, result2 = convert_data(data_raw)
    assert result1 == expected1 and result2 == expected2
