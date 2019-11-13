#!/usr/bin/python
import os
import socket
import MySQLdb
import ConfigParser
import io


HOSTS="""
[bigdata]
10.56.80.17
10.56.80.11
10.56.80.12
10.56.80.13
10.56.80.14
10.56.80.15
10.56.80.16
[ops]
10.57.0.31
"""


TEMPLATE_UPSTREAM = """
upstream backend-xxxxxx {
    server xxxxxx:19999;
    keepalive 64;
}
"""
TEMPLATE_SERVER = """
server {
    listen 80;
    location ~ /netdata/(?<behost>.*)/(?<ndpath>.*) {
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_pass_request_headers on;
        proxy_set_header Connection "keep-alive";
        proxy_store off;
        proxy_pass http://backend-$behost/$ndpath$is_args$args;
        gzip on;
        gzip_proxied any;
        gzip_types *;
    }
    # make sure there is a trailing slash at the browser
    # or the URLs will be wrong
    location ~ /netdata/(?<behost>.*) {
        return 301 /netdata/$behost/;
    }
}
"""
NGINX_CONF_DIR = "/usr/local/openresty/nginx/upstreams.d/netdata"
NGINX_SERVER_FILE = "/usr/local/openresty/nginx/vhosts/archery.yxzq.com.conf"
MYSQL_HOST='10.57.0.12'
MYSQL_PORT=3306
MYSQL_USER="db_archery"
MYSQL_DB="archery"
MYSQL_PASSWD="42"
MYSQL_TABLE="sql_netdata_monitor"






def parser_config():
    result = {}
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(HOSTS))
    groups = config.sections()
    for group in groups:
        result[group] = list()
        for item in config.items(section=group):
            result[group].append(item)
    return result
    
def sync_ip_info_to_db(ip,tport,group,delete=False):
    host,port,user,db,passwd,table = MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_DB,MYSQL_PASSWD,MYSQL_TABLE
    try:
        conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,port=port,charset="utf8")
        cursor = conn.cursor()
        if delete:
            delete_sql = "delete from "+table+" where listen_address='"+ip+"' and group_name = '"+group+"';"
            cursor.execute(delete_sql)
        else:
            where_sql = 'select * from '+table+' where listen_address="'+ip+'" and group_name = "' +group+'";'
            insert_sql = 'use '+db+' ;insert into '+table+' (listen_address,listen_port,group_name) values ("'+ip+'",'+str(tport)+',"'+group+'");'
            cursor.execute(where_sql)
            result = cursor.fetchone()
            if not result:
                cursor.execute(insert_sql)
    except Exception as e:
        print str(e)
    else:
        cursor.close()
        conn.commit()

def write_server_http_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path,"w") as f:
            f.wirte(TEMPLATE_SERVER)

def check_netdata_port(host,port):
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.settimeout(3)
    try:
        sk.connect((host,port))
        sk.close()
    except Exception as e:
        return False
    else:
        return True
    
def reload_nginx():
    os.system(" /usr/local/openresty/nginx/sbin/nginx -t &>/dev/null &&  /usr/local/openresty/nginx/sbin/nginx -s reload")

def main():
    nginx_conf = NGINX_CONF_DIR
    template_upstream = TEMPLATE_UPSTREAM
    result = parser_config()
    nginx_server_file = NGINX_SERVER_FILE
    if not os.path.exists(nginx_server_file):
        write_server_http_file(nginx_server_file)
    for group,ip_port_list in result.iteritems():
        for ip_port in ip_port_list:
            ip,port = ip_port
            port = 19999 if not port else int(port)
            if check_netdata_port(ip,port):
                ip_path = os.path.join(nginx_conf,ip+".conf")
                if not os.path.exists(ip_path):
                    sync_ip_info_to_db(ip,port,group)
                    with open(ip_path,"w") as f:
                        f.write(template_upstream.replace("xxxxxx",ip))
            else:
                sync_ip_info_to_db(ip,port,group,delete=True)
    reload_nginx()

if __name__ == "__main__":
    main()





