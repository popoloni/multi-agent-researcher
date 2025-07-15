@echo off
REM Wrapper script for backwards compatibility
REM Calls the actual start_all.bat in utils/ folder
%~dp0utils\start_all.bat %* 