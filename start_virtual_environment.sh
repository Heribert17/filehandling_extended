#!/bin/bash

# ------------------------------------------------------------------------------------------------
#
# Create a virtual environment if it doesn't exist and start powershell with the virtual
# environment
#
# Autor: Heribert Füchtenhans
#
# ------------------------------------------------------------------------------------------------

if [ ! -d ./venv_linux ]; then
	echo "venv_linux doesn't exist so I create the virtual environment"
	python3.13 -m venv ./venv_linux

	if [ -d ./venv_linux ]; then
		echo "Install requirements"
		source ./venv_linux/bin/activate
		AllwaysArgs='--trusted-host files.pythonhosted.org --trusted-host pypi.org --retries 1 --upgrade'
		python3.13 -m pip install $AllwaysArgs --upgrade pip
		python3.13 -m pip install $AllwaysArgs -r requirements.txt
    	pip3.13 install $AllwaysArgs -r requirements_other.txt
	fi
fi
bash --rcfile "./venv_linux/bin/activate" -i

