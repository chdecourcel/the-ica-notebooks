import sys
from os import environ
from pathlib import Path
import json
import pandas as pd
from uuid import uuid4

import ipywidgets as widgets
from IPython.display import display
from IPython.core.display import Markdown

import rafal

# config loading from config.json file
config = json.load(open(Path(__file__).parent / 'config.json'))

# open a new rafal session and connect
session= rafal.Session(verbose= True)

user= config['Rafal.user']
urls = config['Rafal.urls']

# UI connect
myPwd= config.get('Rafal.password', environ.get('jpwd', None))
pwd_exists = bool(myPwd) 
wPwd= widgets.Password(value= '',
                      placeholder= 'from config' if pwd_exists else 'Enter password',
                      disabled= pwd_exists
                     )

# proxy parameters
proxies = (config['proxies'] if config['proxies']['http'] or config['proxies']['https'] 
           else None)

wServer = widgets.Dropdown(
    options= urls.items(),
    value= urls['review_master'],
    disabled= False,)
button = widgets.Button(description='Connect', button_style='info',)
output = widgets.Output()

modules= []

def on_button_clicked(b):
    output.clear_output()
    with output:
        # get password
        pwd= myPwd if pwd_exists else wPwd.value
        if not pwd:
            print('Please write your password first !')
            return

        # connect to rafal
        session.connect(url= wServer.value, login= user, pwd= pwd, proxies= proxies)
        environ['jpwd']= pwd
        del pwd

        # Python version
        print (f'Python version: {sys.version}')
        print (f'Pandas version: {pd.__version__}')

        swagger_link= Markdown(f"[Swagger on {session.url}]({session.url}/docs/swagger-ui/index.html?url=/assets/swagger.json#/)")
        display(swagger_link)
        # list all modules
        modules= session.request(endPoint= '/modules', http= 'GET', verbose= True)
        print('Modules found :\n', modules)

button.on_click(on_button_clicked)

uiConnect = widgets.VBox([
    widgets.HBox([widgets.Label(f'Rafal API :'), wServer]),
    widgets.Label(f'User : {user}'),
    widgets.HBox([widgets.Label(f'Password :'), wPwd, button,]),
    
    output,
    ])
