@echo off
chcp 65001 > nul 2>&1
title Stop Services
python "%~dp0stop.py"
timeout /t 2 > nul 2>&1
