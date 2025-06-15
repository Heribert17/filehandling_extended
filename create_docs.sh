#!/bin/bash

# ------------------------------------------------------------------------------------------------
#
# Create the documentation with mkdocs
#
# Autor: Heribert Füchtenhans
#
# ------------------------------------------------------------------------------------------------

source ./venv_linux/bin/activate

# echo Build documentation

# mkdocs build

#echo
#echo Upload documentation to github?
#read -p "Continue with return ..."
#
#mkdocs gh-deploy
#
#echo
echo Create local documentation that can be opend in local browser
#read -p "Continue with return ..."

mkdocs build --no-directory-urls --site-dir=documentation

echo
read -p "End with return ..."
