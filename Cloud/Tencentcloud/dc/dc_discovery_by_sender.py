#!/usr/local/python2.7/bin/python
#coding:utf-8

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dc.v20180410 import dc_client, models
from tencentcloud.common.profile import client_profile
from tencentcloud.common.profile import http_profile
import json
import sys
from optparse import OptionParser
import requests
__AUTHOR__='Hoover'

REGION_LIST=[
             'ap-shenzhen-fsi',
             #'ap-guangzhou',
#	     'ap-hongkong'
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
			self._client = dc_client.DcClient(cred,region,cp)
		    else:
			self._client = dc_client.DcClient(cred,self._region)
	    except TencentCloudSDKException as err:
		print(err)
	    except Exception as e:
		 print str(e)

    def get_client(self):
	assert self._client is None
	return self._client

class DcAPI(BaseAPI):
    def __init__(self):
	BaseAPI.__init__(self,'dc')
	self._dc_info=dict()

    def _query_all_dc_info(self):
	if self._client:
	    client=self._client
	    req=models.DescribeDirectConnectTunnelsRequest()
	    offset,limit=0,100
	    params = '{"Offset":'+str(offset)+',"Limit":'+str(limit)+'}'
	    req.from_json_string(params)
	    resp = client.DescribeDirectConnectTunnels(req)
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
		    for data in resp['DirectConnectTunnelSet']:
			#result_dict[data['DirectConnectTunnelId']]=[data['CustomerAddress'],data['Vlan'],data["Bandwidth"],data["State"],data["RouteFilterPrefixes"],data["NetworkType"],data["DirectConnectTunnelName"],data["TencentAddress"],data["RouteType"]]
		        result_dict[data['DirectConnectTunnelId']]={"CustomerAddress":data['CustomerAddress'],"Vlan":data['Vlan'],"Bandwidth":data["Bandwidth"],"State":data["State"],"NetworkType":data["NetworkType"],"DirectConnectTunnelName":data["DirectConnectTunnelName"],"TencentAddress":data["TencentAddress"],"RouteType":data["RouteType"]}
	    else:
		for data in resp['DirectConnectTunnelSet']:
		    result_dict[data['DirectConnectTunnelId']]={"CustomerAddress":data['CustomerAddress'],"Vlan":data['Vlan'],"Bandwidth":data["Bandwidth"],"State":data["State"],"NetworkType":data["NetworkType"],"DirectConnectTunnelName":data["DirectConnectTunnelName"],"TencentAddress":data["TencentAddress"],"RouteType":data["RouteType"]}
            return result_dict

    def query_all_dc_info(self):
	for region in self._regions:
	    self.init_client(region)
	    return self._query_all_dc_info()

    def print_used_dc_info(self):
	print_data={"data":[]}
	for k in self.query_all_dc_info().iteritems():
	    print k[0]
	return json.dumps(print_data)

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
    dc=DcAPI()
    ip,all=parser_option()
    if all:
	result=dc.query_all_dc_info()
	for k,v in result.iteritems():
	    print k,v
    else:
	res=cvm.query_dc_info(ip)
	if res:
	    print res[0],res[1],res[2]



if __name__ == '__main__':
    dc=DcAPI()
    #print dc.query_all_dc_info()
    dc.print_used_dc_info()
    sys.exit(1)
    main()
    
    
    





