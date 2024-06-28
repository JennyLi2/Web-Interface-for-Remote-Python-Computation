# A Web Interface For Remote Python Computations

This is a dissertation project carried out by Cheng Man Li under the supervision of Dr. Charles Grellois at the University of Sheffield.

## Introduction

https://github.com/JennyLi2/Web-Interface-for-Remote-Python-Computation/assets/116062873/792a68e5-24f4-48aa-8086-a52dabdccea8


## Setup
Make sure Python is installed before you proceed.

1. Clone the repository
```
git clone https://github.com/JennyLi2/Web-Interface-for-Remote-Python-Computation.git
```
Alternatively, you can download this code as a zip file.

2. Install Flask
```
pip install flask
```
3. Start the web server
```
flask run
```
Once the server is running, you can access the web interface at:    
http://127.0.0.1:5000/ or http://localhost:5000/

## Getting started

There is a Python script (`script.py` in the `modules` directory) with an empty function inside and a configuration file (`spec.json` in the `config` directory) provided as templates. You can modify/add new Python scripts and update the configuration file to observe how the web interface changes.

### 1. Adding new Python scripts   
The Python scripts have to be manually added to the `modules` directory. The entry point (main function to be called) has to use the name "validate".

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

The input parameters should have the same name and be in the same order as the input fields specified in the configuration file.

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
          "value": "[value name]",
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

"[option 1]" and "[option 2]" are the names of the scripts to be shown in the dropdown list for users to select. More options can be added following the above format. Each script should have an array of input fields that specifies the inputs it needs for the computation.

An input field should have the following attributes:
* label
* type (All types can be found [here](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types). Commonly used ones are `text` and `number`, the use of other types in this program is still under experimentation.)
* name


The following attributes are optional:
* value
* placeholder
* required
* readonly

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

The "module" requires you to specify the name of your script (the module to be imported), and the "output" requires you to specify the type of output the script will return. For now, this program accepts `number`, `text`, and `image`.
