#!/usr/bin/python
import os
import socket
import MySQLdb


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
NGINX_CONF_DIR = "/etc/nginx/conf.d/netdata"
NGINX_SERVER_FILE = "/etc/nginx/conf.d/netdata.conf"
HOSTS_FILE = "/etc/nginx/hosts"
MYSQL_HOST='10.210.110.210'
MYSQL_PORT=3306
MYSQL_USER="ops"
MYSQL_DB="archery"
MYSQL_PASSWD="Ops$123$123"
MYSQL_TABLE="sql_netdata_monitor"



def sync_ip_info_to_db(ip,tport):
    host,port,user,db,passwd,table = MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_DB,MYSQL_PASSWD,MYSQL_TABLE
    try:
        conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,port=port,charset="utf8")
        cursor = conn.cursor()
        where_sql = 'select * from '+table+' where listen_address ="'+ip+'";'
        where_sql = 'select * from '+table+' where listen_address="'+ip+'";'
        insert_sql = 'use '+db+' ;insert into '+table+' (listen_address,listen_port) values ("'+ip+'",'+str(tport)+');'
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
    os.system("/usr/sbin/nginx -t &>/dev/null && /usr/sbin/nginx -s reload")
def main():
    hosts = HOSTS_FILE
    nginx_conf = NGINX_CONF_DIR
    template_upstream = TEMPLATE_UPSTREAM
    ip_port_list = list()
    if os.path.exists(hosts):
        with open(hosts,"r") as f:
            for line in f.readlines():
                line = line.replace("\n","").split(":")
                result = line if len(line) >1 else [line[0],19999]
                ip_port_list.append(result)

    nginx_server_file = NGINX_SERVER_FILE
    if not os.path.exists(nginx_server_file):
        write_server_http_file(nginx_server_file)
    for ip_port in ip_port_list:
        ip,port = ip_port
        if check_netdata_port(ip,port):
            ip_path = os.path.join(nginx_conf,ip+".conf")
            if not os.path.exists(ip_path):
                sync_ip_info_to_db(ip,port)
                with open(ip_path,"w") as f:
                    f.write(template_upstream.replace("xxxxxx",ip))
    reload_nginx()

if __name__ == "__main__":
    main()
            





