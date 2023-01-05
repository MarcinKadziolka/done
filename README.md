# Done
Minimalistic desktop application for managing tasks and projects in [todo.txt](http://todotxt.org/todo.txt) format

## Description
Application provides simplistic yet pretty graphical user interface for easier managment of tasks in provided text file formatted by the rules of the todo.txt.
Goal of this project is to provide the unnecessary functionality and smooth usage with addition of good looking themes.
Motivation was not being able to find a compromise between looks, functionality and keyboard-driven approach in other existing apps.

Application is written in Python with kivy and kivyMD library.

As of right now app, while providing full basic functionality, is not fully yet developed and there are possible features to add.

## Installation
To run the app you must have [Python](https://www.python.org/) installed on your computer.

### Step 1
Go to desired installation place
~~~
cd ~/Desktop
~~~
This command will create directory 'Done'
~~~
git clone https://github.com/MarcinKadziolka/Done
~~~
Enter this new directory
~~~
cd Done
~~~
Create new virtual environment
Using venv
~~~
python3 -m venv done_venv
~~~
Using virtualenv
~~~
python3 -m virtualenv done_venv
~~~
Activate the environment
On linux
~~~
source done_venv/bin/activate
~~~
On windows
~~~
windows activation here
~~~
After activating environment you should see name of your virtual environment preceeding command line
~~~
(done_venv) computer@ubuntu: ~/Desktop/Done$
~~~
Install all dependencies from requirements.txt file
~~~
pip install -r requirements.txt
~~~
Run the app
~~~
python3 done.py
~~~
