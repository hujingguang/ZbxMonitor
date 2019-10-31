#!/bin/bash
discovery_script="/usr/local/bin/scripts/dc_discovery_by_sender.py"
dc_info_script="/usr/local/bin/scripts/dc_info_by_sender.py"
metric_info="OutBandwidth InBandwidth OutPkg InPkg PkgDrop"

[ -e "$discovery_script" ] || exit 1
[ -e "$dc_info_script" ] || exit 1

for tunnel_id in `$discovery_script`
do
   for metric in $metric_info
   do
      result=`$dc_info_script $tunnel_id $metric`
      if [ "$result" != "" ]
      then
       echo $result > /tmp/.dc_info.tmp
       /opt/zabbix/bin/zabbix_sender -c /opt/zabbix/etc/zabbix_agentd.conf  -i /tmp/.dc_info.tmp -T
      fi
   done
done


