#!/bin/bash
discovery_script="/usr/local/bin/scripts/clb_discovery_by_sender.py"
clb_info_script="/usr/local/bin/scripts/clb_info_by_sender.py"
metric_info="Connum NewConn Intraffic Outtraffic Inpkg Outpkg"

[ -e "$discovery_script" ] || exit 1
[ -e "$clb_info_script" ] || exit 1

for vip in `$discovery_script`
do
   for metric in $metric_info
   do
      result=`$clb_info_script $vip $metric`
      if [ "$result" != "" ]
      then
       echo $result > /tmp/.clb_info.tmp
       /opt/zabbix/bin/zabbix_sender -c /opt/zabbix/etc/zabbix_agentd.conf  -i /tmp/.clb_info.tmp -T
      fi
   done
done


