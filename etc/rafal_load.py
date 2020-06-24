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


# open a new rafal session and connect
session= rafal.Session(verbose= True)

# check auto connect (no proxies)
env_url= environ.get('rf_url', None)
env_user= environ.get('rf_user', None)
env_pwd= environ.get('rf_pwd', None)
if env_url and env_user and env_pwd:
    user= env_user
    session.connect(url= env_url, login= env_user, pwd= env_pwd)
    uiConnect= widgets.Output()
else:
    # config loading from config.json file
    config = json.load(open(Path(__file__).parent / 'config.json'))
    config_user_file= Path('config_user.json') 
    if config_user_file.exists():
        config_user = json.load(open(config_user_file))
        if "Rafal.urls" in config_user:
            config["Rafal.urls"].update(config_user["Rafal.urls"])


    user= config['Rafal.user']
    urls = config['Rafal.urls']

    # UI connect
    myPwd= config.get('Rafal.password', environ.get('jpwd', None))
    pwd_exists = bool(myPwd)
    wUser = widgets.Text(
        value= user,
        disabled= False,)
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
            session.connect(url= wServer.value, login= wUser.value, pwd= pwd, proxies= proxies)
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
        widgets.HBox([widgets.Label(f'User :'), wUser]),
        widgets.HBox([widgets.Label(f'Password :'), wPwd, button,]),
        output,
        ])
