#!/usr/bin/env python
#assumes that boto3 is installed "pip install boto3"
import boto3

#Initialize the boto3 STS client
client = boto3.client('sts')

#Assuming the role, requires role ARN which has been provisioned on the account the user wants to assume access in

assumed_role_object = client.assume_role(RoleArn = 'arn:aws:iam::<account-id>:role/<rolename-in-other-account>', RoleSessionName = 'random-string', DurationSeconds = 3600)

#we assign response of client.assume_role to credentials, as it contains the temp access, secret keys as well as session token for assumed role

credentials = assumed_role_object['Credentials']

#we pass the temp access,secret key and session token to the initilization of ec2 client boto3 resource

ec2 = boto3.client('ec2',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],aws_session_token=credentials['SessionToken'])



#make a sample call , in my case the role only allow EC2 read only perms and displays if defined for an instance public dns
reservation = ec2.describe_instances()

for i in reservation['Reservations']:
    if i['Instances'][0]['InstanceId']:
        print i['Instances'][0]['InstanceId'] + " " + i['Instances'][0]['InstanceType'] + " " + i['Instances'][0]['State']['Name']
