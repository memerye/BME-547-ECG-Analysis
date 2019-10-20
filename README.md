# ECG Analysis
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/bme547-fall2019/ecg-analysis-memerye/blob/master/LICENSE.txt)
[![Build Status](https://travis-ci.com/bme547-fall2019/ecg-analysis-memerye.svg?token=7FEBMaBYsSUBFsqKGuGE&branch=master)](https://travis-ci.com/bme547-fall2019/ecg-analysis-memerye)

## Background
[Electrocardiography](https://en.wikipedia.org/wiki/Electrocardiography) is the process of producing an electrocardiogram (**ECG** or **EKG**), a recording – a graph of voltage versus time – of the electrical activity of the heart using electrodes placed on the skin. These electrodes detect the small electrical changes that are a consequence of cardiac muscle depolarization followed by repolarization during each cardiac cycle (heartbeat). \
There are three main components to an ECG: 
* P wave: the depolarization of the atria
* QRS complex: the depolarization of the ventricles
* T wave: the repolarization of the ventricles

![ECG](https://github.com/bme547-fall2019/ecg-analysis-memerye/blob/master/readme_image/QRS.png)

An ECG conveys a large amount of information about the structure of the heart and the function of its electrical conduction system. Among other things, an ECG can be used to measure the rate and rhythm of heartbeats, the size and position of the heart chambers, the presence of any damage to the heart's muscle cells or conduction system, the effects of heart drugs, and the function of implanted pacemakers. As reference, if you’re sitting or lying and you’re calm, relaxed and aren’t ill, your [normal heart rate](https://www.heart.org/en/health-topics/high-blood-pressure/the-facts-about-high-blood-pressure/all-about-heart-rate-pulse) is normally between 60 beats per minute and 100 beats per minute (BPM). 

In this project, the code reads multiple ECG signals and then processes the data to get more information of these ECG signals. Ultimately these information is stored in the JSON output file.


## Environment
python 3


## Source
This data is originally from the [PhysioBank
Database](https://physionet.org/physiobank/database/#ecg) for ECG data.


## Test Files Description
* The data are given as `time, voltage` pairs.  `time` is in seconds, `voltage`
is in mV.
* **Tests 1-27** include variable forms of ECG data. Some files have peaks at a
constant voltage and period, while others have peaks at different voltages and
a change in heart rate within the data set. The time intervals between
measurements are vary per data set.
* **Tests 28-31** contain some non-numeric entries, missing data, or NaN in 
the time and voltage columns.  
* **Test 32** has values outside of the normal range of ECG data at a max of 
 +/- 300 mV.


## Functional Specifications
### Input
+ The `files_path` contains the path to all of the CSV files that you want to process in this program. The name of the ecg file should follow the format as: `test_data*.csv`, where * stands for the number of the file. The program would read the files in ascending order of that number in file name.
+ The program reads ECG data from the CSV file that will have lines with `time, voltage`. Example data can be found in the `test_data/` directory in this directory.
+ If either value in a `time, voltage` pair is missing, contains a non-numeric string, or is NaN, the program would recognize that it is missing, log an `error` to the log file, and skip to the next data pair. (See [test_data\README.md](test_data/README.md) for more details.)
+ If the file contains a voltage reading outside of the normal range of +/-300 mv, a `warning` entry would be added to the log file indicating the name of the test file and that voltages exceeded the normal range. This would be done only once per file. Analysis of the data would still be done as normal.
+ If the program reads an empty line in the data, then it regards this as the sign of stopping read and returns log `information` as finish reading.

### ECG Processing
+ The detection of a R peak would be considered as a heart beat. In order to easily detect those peaks, the ECG signals need some preprocessing.
    - **Butterworth bandpass filter**: By observing from the spectrum of each ECG signal, I found out that the passband of the signals is basically between around 0.4Hz - 75Hz. So I designed a butterworth bandpass filter with default order as 5 to filter the signal, removing the breath motion in low frequency and the noise in high frequency.
    - **Normalization**: The signal is then normalized so that the difference between the maximum value and the minimum value equals to 1.

+ Based on the preprocessing signal, I counted the beats by identifying the R wave. I defined the R wave as peaks with limitation of `dis_min` and `local_mean`, and then calculated the number of beats with the help of `stat_peaks`, where:
    - **`dis_min`** stands for an estimation of the minimum distance between peaks, which can be computed by knowing the sampling frequency and the predefined BPM as 150. Because in order to not miss any R peaks, the distance between each peak cannot be predefined so big, which is why I applied 150 BPM as it is considerable higher than normal BPM mentioned above.
    - **`Local mean`** is the result of a moving average adding with regularation on preprocessing signal using a window of 0.25 seconds. This operation smoothes the signal so that it gives a baseline to estimate the morphology of ECG signal. The peak should be higher than this local mean baseline, otherwise it won't considered as a R wave. The result of it is shown as read line on the image below.
    - **`stat_peaks`** is a function computing the distance between each couple of the peaks, and then remove the peak distance that is 2 times away from the median distance. It returns the peak distance with high reliable, whose mean is then used to calculate the mean BPM.

![processing_signal](https://github.com/bme547-fall2019/ecg-analysis-memerye/blob/master/readme_image/processing_signal.png)

+ More information: As I specified above, this program targets on the R wave to get the results. But R wave is not always the maximum peak during a heart beat. The image below shows multiple types of QRS complex. But as soon as there is a outstanding peak inside one heart beat, the program can always detect them. So this program may still effective when dealing with some abnormal ECGs.

![QRS complex](https://github.com/bme547-fall2019/ecg-analysis-memerye/blob/master/readme_image/QRS_nomenclature.png)

+ The following data would be saved as keys in a Python dictionary called `metrics`:
    - `duration`: time duration of the ECG strip  
    - `voltage_extremes`: tuple containing minimum and maximum lead voltages  
    - `num_beats`: number of detected beats in the strip
    - `mean_hr_bpm`: estimated average heart rate over the length of the strip  
    - `beats`: numpy array of times when a beat occurred

### Output
+ The `metrics` dictionary would be output as a [JSON](https://json.org/) 
  file in a folder named `json_outputs`. The json file would have the same name as the ECG data file, but with an extension of `.json`. Example: the dictionary 
  with results from the ECG data found in `test_data12.csv` should be saved in
  a json file called `test_data12.json`.
+ A logging text file would be created with the following log entries:  
   - log as `INFO` when starting and finishing analysis of a new ECG trace
   - log as `INFO` when assigning/calculating an attribute/dictionary entry
   - log as `WARNING` or `ERROR` when exceptions are generated
+ The following is an example of log for one ECG file.
```
INFO:root:----This is the log of file test_data32.csv----
INFO:root:Reading the data...
WARNING:root:The ECG voltage 331.25mv in test_data32.csv is out of range.
INFO:root:End of reading last line in file.
INFO:root:* Finish computing the sampling frequency as 720.03Hz
INFO:root:* Finish filtering the ECG signal
INFO:root:* Finish finding the R peaks in ECG signal
INFO:root:Calculating the information in dictionary...
INFO:root:* Finish calculating duration as float
INFO:root:                 ... voltage extremes as tuple
INFO:root:                 ... number of beats as int
INFO:root:                 ... mean bpm as int
INFO:root:                 ... time of beats as list
INFO:root:* Complete calculation.
INFO:root:Saving the information in json...
INFO:root:* Complete save the json file
INFO:root:----This is the end of file test_data32.csv----
```


## How to use
* Choose "clone with https" in your repository to your local computer.
* Open your `Git Bash` and input `git clone` adding with the http.
* Install the required code environment in the `requitements.txt` with the following command: `pip install -r requirements.txt`
* Ensure the existence of the files named `ecg.py` and `test_ecg.py`. 
* Run the command `pytest -v` in your bash window. It will automatically test the function in `ecg.py`. If all pass, we are expected to see the following output (just part of it).
```
========================================================================================================= test session starts =========================================================================================================
platform darwin -- Python 3.6.8, pytest-5.2.1, py-1.8.0, pluggy-0.13.0 -- /Users/liangyu/Documents/BME/BME547/Homework/ecg-analysis-memerye/myvenv/bin/python
cachedir: .pytest_cache
rootdir: /Users/liangyu/Documents/BME/BME547/Homework/ecg-analysis-memerye
plugins: pep8-1.0.6
collected 60 items

test_ecg.py::test_is_abnormal_data_no[time_and_ecg0-4-expected0] PASSED                                                                                                                                                         [  1%]
test_ecg.py::test_is_abnormal_data_no[time_and_ecg1-6-expected1] PASSED                                                                                                                                                         [  3%]
test_ecg.py::test_is_abnormal_data_no[time_and_ecg2-3-expected2] PASSED                                                                                                                                                         [  5%]
...
test_ecg.py::test_sort_files[ecg_files0-expected0] PASSED                                                                                                                                                                       [ 96%]
test_ecg.py::test_sort_files[ecg_files1-expected1] PASSED                                                                                                                                                                       [ 98%]
test_ecg.py::test_sort_files[ecg_files2-expected2] PASSED                                                                                                                                                                       [100%]

========================================================================================================= 60 passed in 0.70s ==========================================================================================================
```
* You can also change the testing arguments and expected results in the `test_ecg.py` and re-run the pytest command.
* The argument `files_path` in `ecg.py` can be changed to the path in your local that contains all of the CSV files that you want to read. Or it will read the default files in the `test_data/` directory in this repository. Then run the command `python ecg.py`. The json files for the those CSV files will automatically be created inside a folder named `json_outputs` at the current file path. The log for running `ecg.py` is also at the current file path.
* If you want to create the sphinx documentation, you shluld first run `cd docs` to get into the folder. Then run Makefile to generate documentation (e.g., `make html`). This will create `docs/_build/html` with the default webpage being `index.html`. Or the result of webpage that I ran is in the same path in the repository.


## Reference
https://github.com/dward2/BME547/blob/master/Assignments/ECG_Analysis/test_data/README.md
https://github.com/dward2/BME547/blob/master/Assignments/ECG_Analysis/README.md
