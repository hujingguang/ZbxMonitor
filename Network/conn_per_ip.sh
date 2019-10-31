#!/bin/bash
#获取主机单个IP连接数,返回类型：text . 触发器 regexp(^OK.*)}=1
DEFAULT=1000
if [ x"$1" != "x" ]
then
  if [ `echo "$1"| awk '{print($0~/^[-]?([0-9])+[.]?([0-9])+$/)?"n":"s"}'` = "n" ] 
  then
     FLAG=$1
  fi
else
     FLAG=$DEFAULT
fi
RETURN_STRING_PREFIX="OK"
RETURN_STRING_CONTENT=""
ss -ant4|egrep -v '^LISTEN|Address'|awk '{print $5}'|cut -d: -f1|sort -n -k1|uniq -c |sort -n -k1 -r|head -n 5|awk '{print $1":"$2}'  >/tmp/.ip_counts
for line in `cat /tmp/.ip_counts`
do
   count=`echo $line|awk -F':' '{print $1}'`
   ip=`echo $line|awk -F':' '{print $2}'`
   [ "$FLAG" != "" ] && res=`echo "$count > $FLAG"|bc`
   [ "$res" = "1" ] && RETURN_STRING_CONTENT="IP:"$ip" 连接数:"$count" "$RETURN_STRING_CONTENT" "
done
rm -f /tmp/.ip_counts
[ "$RETURN_STRING_CONTENT" != "" ] && echo "$RETURN_STRING_PREFIX-$RETURN_STRING_CONTENT"
[ "$?" != "0" ] && echo NULL 
