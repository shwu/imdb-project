#!/bin/bash

while true; do
  read -p "Are you sure you want to clean all files? " yn
  case $yn in
    [Yy]* ) 
      ./clean_train.sh
      ./clean_test.sh
      ./clean_xval.sh
      break;;
    [Nn]* ) exit;;
    * ) echo "Please answer yes or
    * no.";;
  esac
done
