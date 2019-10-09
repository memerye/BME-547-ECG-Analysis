# test_ecg.py
import pytest


@pytest.mark.parametrize("data_raw, expected1, expected2", [
    (["2,-3", "", "4.2,2.3"], [2, 4.2], [-3, 2.3]),
    (["1.02,-2.345", "2.13,6.203", ""], [1.02, 2.13], [-2.345, 6.203]),
    ([""], [], []),
])
def test_end_read(data_raw, expected1, expected2):
    """Test the function convert_data that converts the data style

    Args:
        data_raw (list): the raw file content
        expected(list): the contents copied from the file

    Returns:
        Error if the test fails
        Pass if the test passes
    """
    from ecg import convert_data
    result1, result2 = convert_data(data_raw)
    assert result1 == expected1
    assert result2 == expected2
