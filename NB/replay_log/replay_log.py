#!/usr/bin/env python
# coding: utf-8

# # Rafal Load stress testing

# ## Connect to Rafal


# load connection script
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
import time

t0= time.time()

config_file= Path(Path(__file__).parent.parent.parent / 'etc' / 'config.json')

# open a new rafal session and connect
session= rafal.Session(verbose= True)

# check auto connect (no proxies)
env_url= environ.get('rf_url', None)
env_user= environ.get('rf_user', None)
env_pwd= environ.get('rf_pwd', None)
if env_url and env_user and env_pwd:
    user= env_user
    print(f'auto connect on {env_url} with user {env_user}')
    session.connect(url= env_url, login= env_user, pwd= env_pwd)
else:
    # config loading from config.json file
    config = json.load(open(config_file))
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
    uiConnect
    wServer.value= urls['frugal']
    on_button_clicked(1)

# ## Parse log file and look for rafal requests

# In[2]:


log_file= Path(__file__).parent / 'log.txt'


# In[4]:


def tokenize(line):
    return line.strip().split(' ')


# In[5]:


verbose= True


# In[6]:


read_request= False
requestsArgs= []
print(log_file)
with open(log_file, 'r') as fin:
    for i, line in enumerate(fin.readlines()):
        if read_request and (line[:3] == '202'):
            # end of endPoint request detected
            requestsArgs.append({'httpMethod': httpMethod,
                                 'endPoint':endPoint,
                                 'body': ''.join(body),
                                })
            if verbose:
                print(i, httpMethod, endPoint, len(body))
            read_request = False
            
        if read_request:
            # read body line
            body.append(line)
            
        if (line[:3] == '202') and ("DEBUG - TRAFFIC." in line):
            # new endPoint request detected
            read_request= True
            cmd= tokenize(line)
            httpMethod= cmd[6]
            endPoint= cmd[7]
            if len(cmd) > 8 and cmd[8] == '{':
                body= [cmd[8]]
            else:
                body= []


# ## replay rafal request
import json

for i, requestArgs in enumerate(requestsArgs):
    if requestArgs['endPoint'] == '/ping':
        print('/ping');continue
    print('\n', i, requestArgs['httpMethod'], requestArgs['endPoint'])
    ti= time.time()
    requestArgs['resp']= session.request(endPoint= requestArgs['endPoint'], 
                                         http= requestArgs['httpMethod'], 
                                         output= 'json',
                                         jsonText= json.loads(requestArgs['body']) if requestArgs['body'] else None)
    requestArgs['duration']= time.time() - ti

for requestArgs in requestsArgs:
    if 'resp' in requestArgs:
        print(requestArgs['httpMethod'], requestArgs['endPoint'], len(requestArgs['resp']) if requestArgs['resp'] else 0,
        f"{requestArgs['duration']:.3f} sec")

print(f"Total script duration : {time.time()-t0:.2f} sec.")