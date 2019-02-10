#!/usr/bin/env python

import boto3
import requests
import json
import multiprocessing
from multiprocessing import Queue

#Initiate a Queue() class data structure as it's thread-safe, it's FIFO, as a way of
#sharing data between processes as multiprocessing doesn't share same memory space like threads
q = Queue()
processes = []
region = "us-east-1"

#Initiate ec2 low-level client instance
ec2 = boto3.client('ec2', region_name = region)
instances = ec2.describe_instances()


def add_host(url_post, header_post, host_object):
	create_post = requests.post(url_post, headers = header_post, data = host_object)
	q.put(create_post.text)


		
	
	
node_list = list()
node_dict = {}
#Loop through and append to python dictionary the Public IP address and Instance ID of only "running" instances in the region
for node in instances['Reservations']:
	if node['Instances'][0]['State']['Name'] == "running":
		print node['Instances'][0]['State']['Name'] + " " + node['Instances'][0]['InstanceId'] + " " +  node['Instances'][0]['PublicIpAddress']
		node_dict.update({ node['Instances'][0]['InstanceId'] : node['Instances'][0]['PublicIpAddress']  })


#Section for getting auth token from Opsview REST API for usage later when adding hosts
url = "http://localhost:3000/rest/login"
header = {'Content-Type': 'application/json'}
data = '{"username":"<your-opsview-username>","password":"<your-opsview-password>"}'

login = requests.post(url, headers=header,data=data)
token_json = json.loads(login.text)
token = token_json['token']


#Create object for AWS instance,replace all values starting with dummy_"
create_host='{ "alias":"", "check_attempts":"2", "check_command":null, "check_interval":"300", "check_period":"1", "enable_snmp":"0", "event_handler":"", "event_handler_always_exec":"0", "flap_detection_enabled":"1", "hostattributes":[ { "arg1":null, "arg2":null, "arg3":null, "arg4":null, "name":"aws_ec2_instance_id", "value":"dummy_instance_id" }, { "arg1":null, "arg2":"dummy_aws_access_key", "arg3":null, "arg4":"dummy_region", "name":"aws_cloudwatch_authentication", "value":"aws_creds" } ], "hostgroup":"2", "hosttemplates":[ { "id":"41" } ], "icon":"logo - opsview", "ip":"dummy_ip", "keywords":[], "monitored_by":"1", "name":"dummy_name", "notification_interval":"3600", "notification_options":"u,d,r", "notification_period":"1", "other_addresses":"", "parents":[], "rancid_autoenable":"0", "rancid_connection_type":"ssh", "rancid_username":"", "rancid_vendor": null, "retry_check_interval":"60", "servicechecks":[], "snmp_extended_throughput_data":"0", "snmp_max_msg_size":"0", "snmp_port":"161", "snmp_use_getnext":"0", "snmp_use_ifname":"0", "snmp_version":"2c", "snmpinterfaces":[], "snmptrap_tracing":"0", "tidy_ifdescr_level":"0", "use_rancid":"0" }'

url_create = "http://localhost:3000/rest/config/host"
header_create = {'Content-Type':'application/json', 'X-Opsview-Username':'admin', 'X-Opsview-Token' : token } 

#for loop starting multiprocessing of add API calls
for key in node_dict:
	modified_object = create_host.replace("dummy_name",key).replace("dummy_ip",node_dict[key]).replace("dummy_instance_id",key).replace("dummy_region",region)

	t = multiprocessing.Process(target=add_host, args=(url_create,header_create,modified_object,))
	processes.append(t)
	t.start()


for one_process in processes:
	one_process.join()


#Append all responses in Queue to a list to be displayed
response_list = [ ]
while not q.empty():
	response_list.append(q.get())


print "Done with all API calls"
print response_list

