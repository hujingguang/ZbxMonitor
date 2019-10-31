#!/usr/local/python2.7/bin/python
#coding:utf-8

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile import client_profile
from tencentcloud.common.profile import http_profile
from tencentcloud.monitor.v20180724 import monitor_client, models 
import json
import sys
from optparse import OptionParser
import requests
from datetime import datetime
from datetime import timedelta
import time
__AUTHOR__='Hoover'

REGION_LIST=[
             'ap-shenzhen-fsi',
	     ]
TENCENT_ID=""
TENCENT_KEY=""
METRIC_LIST=["Connum","NewConn","Intraffic","Outtraffic","Inpkg","Outpkg"]

class BaseAPI(object):
    def __init__(self,api_type):
	self._tencent_id=TENCENT_ID
	self._tencent_key=TENCENT_KEY
	self._client=None
	self._regions=REGION_LIST
	self._api=api_type

    def init_client(self,region):
	self._region=region
	if True:
	    try:
		cred = credential.Credential(self._tencent_id, self._tencent_key)
		if self._region:
		    region=self._region
		    if region.find('fsi'):
			endpoint=self._api+'.'+region+'.tencentcloudapi.com'
			hp=http_profile.HttpProfile()
			hp.endpoint = endpoint
			cp=client_profile.ClientProfile()
			cp.httpProfile = hp
			self._client = monitor_client.MonitorClient(cred,region,cp)
		    else:
			self._client = monitor_client.MonitorClient(cred,self._region)
	    except TencentCloudSDKException as err:
		print(err)
	    except Exception as e:
		 print str(e)

    def get_client(self):
	assert self._client is None
	return self._client

class MonitorAPI(BaseAPI):
    def __init__(self):
	BaseAPI.__init__(self,'monitor')

    def _get_monitor_data(self,vip,startTime,endTime,dataType,period=300):
	for region in self._regions:
	    self.init_client(region)
	if self._client:
	    client=self._client
	    req=models.GetMonitorDataRequest()
	    params = '{"Namespace":"QCE/LB_PUBLIC","MetricName":"'+dataType+'","Period":'+str(period)+',"StartTime":"'+startTime+'","EndTime":"'+endTime+'","Instances":[{"Dimensions":[{"Name":"vip","Value":"'+vip+'"}]}]}'
	    req.from_json_string(params)
	    resp = client.GetMonitorData(req) 
	    resp=json.loads(resp.to_json_string())
	    if  "DataPoints" in resp:
		data=resp["DataPoints"][0]["Values"]
		timestamp=resp["DataPoints"][0]["Timestamps"]
		if data:
                    timestamp=str(int(timestamp[0])-180)
                    if dataType == "Intraffic" or dataType == "Outtraffic":
		        print "Zabbix_Tencent_Cloud_Tunnel_Info","tencent.clb.info["+sys.argv[1]+","+sys.argv[2]+"]",timestamp,data[0]*1000*1000
                    else:
		        print "Zabbix_Tencent_Cloud_Tunnel_Info","tencent.clb.info["+sys.argv[1]+","+sys.argv[2]+"]",timestamp,int(data[0])
                else:
		    print "Zabbix_Tencent_Cloud_Tunnel_Info","tencent.clb.info["+sys.argv[1]+","+sys.argv[2]+"]",str(time.time()).split('.')[0],0
            return 

    def get_monitor_data(self,vip,dataType):
	global METRIC_LIST
        now=datetime.now()
	begin_time=datetime.strftime(now+timedelta(minutes=-5),"%Y-%m-%dT%H:%M:%S+08:00")
	end_time=datetime.strftime(now+timedelta(minutes=-4),"%Y-%m-%dT%H:%M:%S+08:00")
	if dataType not in METRIC_LIST:
	    print "Error"
	else:
	    self._get_monitor_data(vip,begin_time,end_time,dataType)

  

if __name__ == '__main__':
    monitor=MonitorAPI()
    monitor.get_monitor_data(sys.argv[1],sys.argv[2])
    
    
    





