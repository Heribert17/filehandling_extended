@echo off
rem ------------------------------------------------------------------------------------------------
rem
rem Create a virtual environment if it doesn't exist and start powershell with the virtual
rem environemnt
rem
rem Autor: Heribert Füchtenhans
rem
rem ------------------------------------------------------------------------------------------------

if not exist venv (
	echo venv doesn't exist so I create the virtual environment
	python -m venv venv

	echo Install requirements
    call .\venv\Scripts\Activate.bat
    set AllwaysArgs=--trusted-host files.pythonhosted.org --trusted-host pypi.org --retries 1 --upgrade
    python.exe -m pip install %AllwaysArgs% --upgrade pip
    pip3 install %AllwaysArgs% -r requirements.txt
) else (
	call venv\Scripts\activate.bat
)
cmd /K
