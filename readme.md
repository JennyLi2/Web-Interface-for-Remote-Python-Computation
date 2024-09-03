# A Web Interface For Remote Python Computations

This is a dissertation project carried out by Cheng Man Li under the supervision of Dr. Charles Grellois at the University of Sheffield.

## Introduction
This Python program allows you to give access to your own selection of Python scripts, hosted and executed on your own machine, via a web interface implemented with Flask.
Once installed and configured, a web server will run on your machine, allowing remote users to access a web page on which they will select one of the scripts you provide access to,
then enter relevant parameters through a dynamically generated web form. The computation will run on your machine and send back the result to the remote user on a web page.

Here is a demo of how a remote user will interact with the web interface:    

https://github.com/JennyLi2/Web-Interface-for-Remote-Python-Computation/assets/116062873/a73edca2-06fd-4bd2-8713-390a7c85248a


## Setup
Make sure [Python](https://www.python.org/downloads/) is installed before you proceed.

**1. Clone the repository ([Git](https://git-scm.com/downloads) required)**
```
cd path/to/your/folder
git clone https://github.com/JennyLi2/Web-Interface-for-Remote-Python-Computation.git
cd Web-Interface-for-Remote-Python-Computation
```
Alternatively, you can download this code as a zip file and extract it.

**2. Install Required Packages**

You may want to create a virtual environment before installing the packages. See the [official documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments) for more information.

To install:
```
pip install -r requirements.txt
```

If you would like to run the scikit-learn and PyTorch examples, uncomment the packages in requirements.txt to install the extra packages.

Check the installed packages:
```
pip list
```

**3. Start the web server**

Make sure you navigate to the project folder before running the command.
```
python app.py
```
This will start a waitress server. Once the server is running, you can access the web interface at:    
http://127.0.0.1:5000/

## Getting started

There are 2 Python scripts (`script1.py` and `script2.py` in the `modules` directory) with empty functions inside and a configuration file (`spec.json` in the `config` directory) provided as templates. You can modify/add new Python scripts and update the configuration file to observe how the web interface changes.

The 2 directories `scikitlearn_example` and `pytorch_example` contains the scripts of the scikit-learn and PyTorch models.

### 1. Adding new Python scripts   
The Python scripts have to be manually added to the `modules` directory. The entry point (main function to be called) has to use the name "validate". Details about the structure of its arguments will be given in the coming part.

```python
def validate([input parameters here]):
    # some operations to validate the inputs from the user
    ...
    
    # if the inputs are accepted
        # call other functions / perform some computation
        ...
        # return output
    # else
        # could be some error handling
        # or simply return False
```
It is intended that there will be some kind of measures to validate the user's input before performing the real computation. Therefore, this function is specified to be called first for the scripts.

The input parameters should have the same names and be in the same order as the input fields specified in the configuration file.

For example:
```python
# in the configuration file:
    ...
    "inputFields": [
        {
            ...
            "name": "input1",
            ...
        },
        {
            ...
            "name": "input2",
            ...
        }
    ]
    ...
    
# in the Python script:
def validate(input1: type, input2: type):
    ...
```

### 2. Updating the configuration file   
The configuration file `spec.json` is located in the `config` directory. The name and location of the file should not be changed.

The structure of the configuration file has to be as follows:
```javascript
{
  "scripts": {
    "[option 1]": {
      "inputFields": [
        {
          "label": "[field label]",
          "type": "[field type]",
          "name": "[field name]",
          "default": "[default value]",
            ...
        }, 
        ...
      ],
      "module": "[module name]",
      "output": "[output type]"
    },
    "[option 2]":{
        ...
    }
  }
}
```
The text in square brackets [ ] can be replaced accordingly, while the others are fixed terms and should not be changed.

"[option 1]" and "[option 2]" are the names of the scripts to be shown in the dropdown list for users to select. More options can be added following the above format. Each script should have an list of input fields that specify the inputs it needs for the computation.

An input field should have the following attributes:
* label
* name
* type
  * Available types: 
    * text
    * textarea
    * number
    * float
    * decimal
    * hidden
    * boolean (i.e. checkbox)
    * select (i.e. dropdown list)
    * radio
    * file
    * date
    * time 
  * check the input fields of `script1` in spec.json to see the examples


The following attributes are optional:
* choices (for types: 'select', 'radio')
* default
* description
* extension (for type: 'file')
* placeholder
* required
* readonly
* max (for types: 'number', 'float', 'decimal', 'text')
* min (for types: 'number', 'float', 'decimal', 'text')

This is an example of an input field:
```javascript
{
    "label": "Text input", 
    "type": "text",
    "name": "text_input",
    "placeholder": "Some text here.",
    "required": "true"
}
```

The configuration file has other examples for reference.

The "module" requires you to specify the name of your script (the module to be imported), and the "output" requires you to specify the type of output the script will return (in a list). For now, this program accepts `text`, `image`, and `images`.
