#!/usr/local/python2.7/bin/python
#coding:utf-8
#腾讯云cvm信息查询

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.common.profile import client_profile
from tencentcloud.common.profile import http_profile
import json
import sys
from optparse import OptionParser

__AUTHOR__='Hoover'


REGION_LIST=[
             'ap-shenzhen-fsi',
             'ap-guangzhou',
	     'ap-hongkong'
	     ]
TENCENT_ID=""
TENCENT_KEY=""

class BaseAPI(object):
    def __init__(self):
	self._tencent_id=TENCENT_ID
	self._tencent_key=TENCENT_KEY
	self._client=None
	self._regions=REGION_LIST

    def init_client(self,region):
	self._region=region
	if True:
	    try:
		cred = credential.Credential(self._tencent_id, self._tencent_key)
		if self._region:
		    region=self._region
		    if region.find('fsi'):
			endpoint='cvm.'+region+'.tencentcloudapi.com'
			hp=http_profile.HttpProfile()
			hp.endpoint = endpoint
			cp=client_profile.ClientProfile()
			cp.httpProfile = hp
			self._client = cvm_client.CvmClient(cred,region,cp)
		    else:
			self._client = cvm_client.CvmClient(cred,self._region)
	    except TencentCloudSDKException as err:
		print(err)
	    except Exception as e:
		 print str(e)

    def get_client(self):
	assert self._client is None
	return self._client

class CvmAPI(BaseAPI):
    def __init__(self):
	BaseAPI.__init__(self)
	self._cvm_info=dict()

    def query_zone_info(self):
	self.init_client()
	if self._client:
	    client=self._client
	    req = models.DescribeZonesRequest()
	    resp = client.DescribeZones(req)
	    resp=json.loads(resp.to_json_string())
	    if 'ZoneSet' in resp:
		for  data in resp['ZoneSet']:
		    print data['ZoneName']

    def _query_cvm_info(self,ip):
	if self._client:
	    client=self._client
	    req=models.DescribeInstancesRequest()
	    #params='{"Offset":"0","Limit":1,"Filters.0.Name":"private-ip-address","Filters.0.Values.0":"'+ip+'"}'
	    params = '{"Filters":[{"Name":"private-ip-address","Values":["'+ip+'"]}],"Offset":0,"Limit":1}'
	    req.from_json_string(params)
	    resp = client.DescribeInstances(req)
	    resp=json.loads(resp.to_json_string())
	    if resp['TotalCount'] != 0:
		data=resp['InstanceSet'][0]
		return data['InstanceName'],data['Placement']['Zone'],data['InstanceId']
	    else:
		return None


    def _query_all_cvm_info(self):
	if self._client:
	    client=self._client
	    req=models.DescribeInstancesRequest()
	    offset,limit=0,100
	    params = '{"Offset":'+str(offset)+',"Limit":'+str(limit)+'}'
	    req.from_json_string(params)
	    resp = client.DescribeInstances(req)
	    resp=json.loads(resp.to_json_string())
	    total=int(resp['TotalCount'])
	    int_num,remain_num=total%limit,total//limit
	    result_dict=dict()
	    if remain_num > 0:
		for n in range(0,remain_num+1):
		    offset=n*100
	            params = '{"Offset":'+str(offset)+',"Limit":'+str(limit)+'}'
	            req.from_json_string(params)
	            resp = client.DescribeInstances(req)
	            resp=json.loads(resp.to_json_string())
		    for data in resp['InstanceSet']:
			result_dict[data['InstanceId']]=[data['PrivateIpAddresses'][0],data['InstanceName'],data['Placement']['Zone']]
	    else:
		for data in resp['InstanceSet']:
		    result_dict[data['InstanceId']]=[data['PrivateIpAddresses'][0],data['InstanceName'],data['Placement']['Zone']]
            return result_dict

    def query_all_cvm_info(self):
	for region in self._regions:
	    self.init_client(region)
	    self._cvm_info.update(self._query_all_cvm_info())
	return self._cvm_info

    def query_cvm_info(self,ip):
	for region in self._regions:
	    self.init_client(region)
	    result=self._query_cvm_info(ip)
	    if result:
		return result

def parser_option():
    parser = OptionParser()
    parser.add_option("-a", "--all",action='store_true',
	                      help="query tencent all cvm info and return python dict data type")
    parser.add_option("-i", "--private-ip",type='string',
	                      dest="ip",
			      help="tencent cvm private ip address")
    (options, args) = parser.parse_args()
    if not options.ip and not options.all:
	parser.print_help()
	sys.exit(1)
    return options.ip,options.all
	

def main():
    cvm=CvmAPI()
    ip,all=parser_option()
    if all:
	result=cvm.query_all_cvm_info()
        for k,v in result.iteritems():
            print v[0],v[1]
    else:
	res=cvm.query_cvm_info(ip)
        if res:
	    print res[0],res[1],res[2]


if __name__ == '__main__':
    main()
    
    
    





