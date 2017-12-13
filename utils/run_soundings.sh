#!/bin/bash

prefix="sounding_dry"
suffix=".nc"

files=( ../data/soundings/dry/*.nc ) 
old="_blah"
for file in "${files[@]}"
do 
  filename="${file##*/}"
  trimmed="${filename%.*}"
  new=$(echo "$trimmed" | sed -e "s/^$prefix//") 
  echo $filename
  python sounding_to_rfm.py ../data/soundings/dry/$filename ../projects/atm/dry_co2$new.atm ../projects/outlevs.lev
  sed -i '' "s/dry_co2${old}/dry_co2${new}/" ../projects/rfm.drv
  old=$new 
  
  FILE=../projects/ncout/dry_co2${new}.nc
  if [ ! -f $FILE ]; then
      echo "File $FILE does not exist."
      cd ../projects/
      ./rfm
      cd ../utils/
      python rfm_to_netcdf.py ../projects/out/ ../projects/ncout/dry_co2${new}.nc  
  
  else
      echo "File $FILE exists, continuing"
      continue
  fi

done
# reset driver file
sed -i '' "s/dry_co2${old}/dry_co2_blah/" ../projects/rfm.drv
