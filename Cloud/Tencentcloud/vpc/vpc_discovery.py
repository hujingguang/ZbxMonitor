#!/usr/local/python2.7/bin/python
#coding:utf-8

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models
from tencentcloud.common.profile import client_profile
from tencentcloud.common.profile import http_profile
import json
import sys
from optparse import OptionParser
import requests
__AUTHOR__='Hoover'

REGION_LIST=[
             'ap-shenzhen-fsi',
             'ap-guangzhou',
	     'ap-hongkong'
	     ]
TENCENT_ID=""
TENCENT_KEY=""

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
			self._client = vpc_client.VpcClient(cred,region,cp)
		    else:
			self._client = vpc_client.VpcClient(cred,self._region)
	    except TencentCloudSDKException as err:
		print(err)
	    except Exception as e:
		 print str(e)

    def get_client(self):
	assert self._client is None
	return self._client

class VpcAPI(BaseAPI):
    def __init__(self):
	BaseAPI.__init__(self,'vpc')
	self._vpc_info=dict()

    def _query_all_vpc_info(self):
	if self._client:
	    client=self._client
	    req=models.DescribeAddressesRequest()
	    offset,limit=0,100
	    params = '{"Offset":'+str(offset)+',"Limit":'+str(limit)+'}'
	    req.from_json_string(params)
	    resp = client.DescribeAddresses(req)
	    resp=json.loads(resp.to_json_string())
	    total=int(resp['TotalCount'])
	    int_num,remain_num=total%limit,total//limit
	    result_dict=dict()
	    if remain_num > 0:
		for n in range(0,remain_num+1):
		    offset=n*100
	            params = '{"Offset":'+str(offset)+',"Limit":'+str(limit)+'}'
	            req.from_json_string(params)
	            resp = client.DescribeAddresses(req)
	            resp=json.loads(resp.to_json_string())
		    for data in resp['AddressSet']:
			result_dict[data['AddressId']]=[data['AddressIp'],data['AddressType'],data["AddressStatus"],data["IsBlocked"]]
	    else:
		for data in resp['AddressSet']:
		    result_dict[data['AddressId']]=[data['AddressIp'],data['AddressType'],data["AddressStatus"],data["IsBlocked"]]
            return result_dict

    def query_all_vpc_info(self):
	for region in self._regions:
	    self.init_client(region)
	    self._vpc_info.update(self._query_all_vpc_info())
	return self._vpc_info

    def query_used_vpc_info(self):
	result=list()
	for region in self._regions:
	    self.init_client(region)
	    result.append({k:v for k,v in self._query_all_vpc_info().iteritems() if v[3] != "False" and v[2] == "BIND"})
	return [v for v in result if v != {} ]

    def print_used_vpc_info(self):
	print_data={"data":[]}
	for vpc_info in self.query_used_vpc_info():
	    for k,v in vpc_info.iteritems():
		info={"{#EIP_ID}":k,
		      "{#EIP_IP}":v[0]
			}
		print_data["data"].append(info)
	return json.dumps(print_data)



    def query_vpc_info(self,ip):
	for region in self._regions:
	    self.init_client(region)
	    result=self._query_vpc_info(ip)
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
    vpc=VpcAPI()
    ip,all=parser_option()
    if all:
	result=vpc.query_all_vpc_info()
	for k,v in result.iteritems():
	    print k,v
    else:
	res=cvm.query_vpc_info(ip)
	if res:
	    print res[0],res[1],res[2]



if __name__ == '__main__':
    vpc=VpcAPI()
    print vpc.print_used_vpc_info()
    sys.exit(1)
    main()
    
    
    





