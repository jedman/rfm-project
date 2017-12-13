#!/bin/bash

FILE=$1     
if [ ! -f $FILE ]; then
     echo "File $FILE does not exist."
   else
        echo "File $FILE exists."
      fi
