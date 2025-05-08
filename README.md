# 👀Nystagmus Analyser 

## Description

#### Dash application to analyse nystagmus eyetracking data.

Converts `.edf` files into interactive graphs, which can be recalibrated around a ±10° focal point.

Future features will include calculations for fast phase velocity and amplitude.

## Installation

#### 1. Clone the repository

#### 2. Create a virtual environment

```
python3 -m venv .venv
```

#### 3. Activate the virtual environment

##### Windows

```
.venv\Scripts\activate
```

##### macOS / Linux (Currently untested in either)

```
source .venv/bin/activate
```


#### 4. Install the package in editable mode

```
pip install -e .
```

#### 5. Once installed, run the application from the terminal:

```
nystagmus
```



## Requirements


- **Python**: 3.10 or later

### Dependencies:

- **dash**: 2.17.1
- **dash-bootstrap-components**: 1.6.0
- **numpy**: 2.1.0
- **pandas**: 2.2.2
- **plotly**: 5.23.0
- **ipywidgets**: 8.1.7

You can install all required dependencies by following the installation instructions in the **Installation** section above.

## Usage
- Upload a file to begin conversion
- Once converted, enable calibration for selected eye and drag lines on graph to desired point:

    ![demo](nystagmus_app/assets/nystagmus%20demo.gif)

- Currently to exit the program you must use either close the terminal or ctrl+c to interrupt  
<sub>(This will be fixed in later update)</sub>


