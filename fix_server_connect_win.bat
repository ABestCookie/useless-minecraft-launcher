@echo off
powershell -command "Start-Process notepad $env:windir\System32\drivers\etc\hosts" -Verb runas