#!/usr/local/python2.7/bin/python
# coding:utf-8

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.clb.v20180317 import clb_client, models
from tencentcloud.common.profile import client_profile
from tencentcloud.common.profile import http_profile
import json
import sys
import re
from optparse import OptionParser
__AUTHOR__ = 'Hoover'

REGION_LIST = [
             'ap-shenzhen-fsi',
             'ap-guangzhou',
             'ap-hongkong'
]
TENCENT_ID = ""
TENCENT_KEY = ""
RE=re.compile('^10\.')


class BaseAPI(object):
    def __init__(self, api_type):
        self._tencent_id = TENCENT_ID
        self._tencent_key = TENCENT_KEY
        self._client = None
        self._regions = REGION_LIST
        self._api = api_type

    def init_client(self, region):
        self._region = region
        if True:
            try:
                cred = credential.Credential(
                    self._tencent_id, self._tencent_key)
                if self._region in self._regions:
                    endpoint = self._api+'.tencentcloudapi.com'
		    hp=http_profile.HttpProfile()
		    hp.endpoint = endpoint
		    cp = client_profile.ClientProfile()
		    cp.httpProfile = hp
		    self._client = clb_client.ClbClient(cred, region, cp)
                #    if region.find('ap-shenzhen-fsi'):
                #        endpoint = self._api+'.tencentcloudapi.com'
		#	hp=http_profile.HttpProfile()
		#	hp.endpoint = endpoint
		#	cp = client_profile.ClientProfile()
		#	cp.httpProfile = hp
		#	self._client = clb_client.ClbClient(cred, "ap-shenzhen-fsi", cp)
                #    else:
                #        print self._region
		#	self._client = clb_client.ClbClient(cred, self._region)
            except TencentCloudSDKException as err:
                print(err)
            except Exception as e:
                print str(e)

    def get_client(self):
        assert self._client is None
        return self._client


class ClbAPI(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self, 'clb')
        self._clb_info = dict()

    def _query_all_clb_info(self):
        if self._client:
            client = self._client
            req = models.DescribeLoadBalancersRequest()
            offset, limit = 0, 100
            params = '{"Offset":'+str(offset)+',"Limit":'+str(limit)+'}'
            req.from_json_string(params)
            resp = client.DescribeLoadBalancers(req)
            resp = json.loads(resp.to_json_string())
            total = int(resp['TotalCount'])
            int_num, remain_num = total % limit, total//limit
            result_dict = dict()
            if remain_num > 0:
                for n in range(0, remain_num+1):
                    offset = n*100
                    params = '{"Offset":' + \
                        str(offset)+',"Limit":'+str(limit)+'}'
                    req.from_json_string(params)
                    resp = client.DescribeLoadBalancers(req)
                    resp = json.loads(resp.to_json_string())
                    for data in resp['LoadBalancerSet']:
                        result_dict[data['AddressId']] = [data['LoadBalancerVips'][0], data['LoadBalancerName'], data["LoadBalancerType"], data["Domain"]]
            else:
                for data in resp['LoadBalancerSet']:
                    result_dict[data['LoadBalancerId']] = [
                        data['LoadBalancerVips'][0], data['LoadBalancerName'], data["LoadBalancerType"], data["Domain"]]
            return result_dict

    def query_all_clb_info(self):
        for region in self._regions:
            self.init_client(region)
            self._clb_info.update(self._query_all_clb_info())
        return self._clb_info


if __name__ == '__main__':
    clb = ClbAPI()
    result=clb.query_all_clb_info()
    for k,v in result.iteritems():
        b=v[0] if not re.search(RE,v[0]) else None
        if b:
            print b
   
