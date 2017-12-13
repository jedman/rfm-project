#!/bin/bash

prefix="sounding_lineartau"
suffix=".nc"

files=( ../data/soundings/dry/lineartau/*.nc ) 
old="_blah"
for file in "${files[@]}"
do 
  filename="${file##*/}"
  trimmed="${filename%.*}"
  new=$(echo "$trimmed" | sed -e "s/^$prefix//") 
  echo $filename
  python sounding_to_rfm.py ../data/soundings/dry/lineartau/$filename ../projects/atm/dry_lineartau$new.atm ../projects/outlevs.lev
  sed -i '' "s/dry_lineartau${old}/dry_lineartau${new}/" ../projects/rfm.drv
  old=$new 
  
  FILE=../projects/ncout/dry_lineartau${new}.nc
  if [ ! -f $FILE ]; then
      echo "File $FILE does not exist."
      cd ../projects/
      ./rfm
      cd ../utils/
      python rfm_to_netcdf.py ../projects/out/ ../projects/ncout/dry_lineartau${new}.nc  
  
  else
      echo "File $FILE exists, continuing"
      continue
  fi

done
# reset driver file
sed -i '' "s/dry_lineartau${old}/dry_lineartau_blah/" ../projects/rfm.drv
