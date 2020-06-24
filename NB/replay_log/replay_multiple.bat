echo OFF

title rafal batch
echo start batch rafal API to %rf_url%
for /L %%i IN (1,1,3) DO (
    START python %~dp0\replay_log.py
)