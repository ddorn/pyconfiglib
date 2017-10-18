# configlib

A bit desesperate by the lack of good and easy to use configuration libraries in python, 
I decided to write this one. The two main goals are:
- Make it easy for the you to describe the data you use to configurate your project and be able 
to save and load it in one line
- Make it easy for the user of your code to modify his configuration through the command line

### User interface

The end user can easily see his configuration with

    python config.py -s

That will print in colors (if availaible) his config:

![See your configuration in colors](assets/show%20config.PNG)

He is able to see what are all the fields easily with

    python config.py --help

or for a simpler list

    python config.py -l
    
![--help](assets/help.PNG)

### Developper interface

*Documentation needs to be done*


### Install

There are a few requirements that you can download with pip:

    pip install click pygments
    
For windows users, you will need pyreadline because readline isn't in the stdlib.

    pip install pyreadline
