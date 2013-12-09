#!/bin/zsh
sdate=$1
if [ -z "$sdate" ];
then
  sdate="-7h -30min"
fi
export sdate
date=`/usr/bin/php << 'EOF'
<?php
date_default_timezone_set("Etc/GMT+2");
$date = strtotime(GETENV("sdate"));
echo "\r".$date;
EOF`
echo $sdate
echo $date
/usr/sbin/rtcwake -m mem -t $date
