#!/bin/bash
while true; do
  read -p "Are you sure you want to clean all files? " yn
  case $yn in
    [Yy]* ) 
      ./clean_train_svm.sh
      ./clean_test_svm.sh
      break;;
    [Nn]* ) exit;;
    * ) echo "Please answer yes or
    * no.";;
  esac
done
