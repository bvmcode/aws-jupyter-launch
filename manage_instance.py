import os
import time
import boto3
from dotenv import load_dotenv
import requests
from bash_script import UserData

load_dotenv()

class JupyterInstance:

    def __init__(self, instance_type="t2.micro", sg_name='jupyter_sg'):
        self.client = boto3.client(
            "ec2",
            region_name=os.environ.get("AWS_REGION"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
        )
        self.instance_type = instance_type
        self.key_name = os.environ.get("AWS_KEY_NAME")
        self.jupyter_psswd = os.environ.get("JUPYTER_PASSWD")
        self.jupyter_port = os.environ.get("JUPYTER_PORT")
        self.UserData  = UserData.format(passwd=self.jupyter_psswd, port=self.jupyter_port)
        self.sg_name = sg_name
        self.jupyter_url = None
        self.sg_id = None
        self.instance_id = None
        self.instance_public_ip = None
        self.state = None
        self.vpc_id = None
        self.subnet_id = None

    def grep_vpc_subnet_id(self):
        response = self.client.describe_vpcs()
        for vpc in response["Vpcs"]:
            if vpc['IsDefault']:
                self.vpc_id = vpc["VpcId"]
                break
        print("The Default VPC : ", self.vpc_id)
        response = self.client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [self.vpc_id]}])
        self.subnet_id = response["Subnets"][0]["SubnetId"]
        print("The Default Subnet : ", self.subnet_id)

    def create_security_group(self):
        try:
            self.grep_vpc_subnet_id()
            response = self.client.create_security_group(
                GroupName=self.sg_name,
                Description="This is created using python",
                VpcId=self.vpc_id
            )
            self.sg_id = response["GroupId"]
            print(self.sg_id)
            sg_config = self.client.authorize_security_group_ingress(
                GroupId=self.sg_id,
                IpPermissions=[
                    {
                        'IpProtocol':'tcp',
                        'FromPort':22,
                        'ToPort': 22,
                        'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol':'tcp',
                        'FromPort':8888,
                        'ToPort': 8888,
                        'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
                    },                    
                ]
            )
            print(sg_config)


        except Exception as e:
            if str(e).__contains__("already exists"):
                response = self.client.describe_security_groups(GroupNames=[self.sg_name])
                self.sg_id = response["SecurityGroups"][0]["GroupId"]


    def create_ec2_instance(self):
        self.create_security_group()
        instance = self.client.run_instances(ImageId='ami-0a8b4cd432b1c3063',
                            MinCount=1,
                            MaxCount=1,
                            InstanceType=self.instance_type,
                            KeyName=self.key_name,
                            SecurityGroupIds=[self.sg_id],
                            SubnetId=self.subnet_id,
                            UserData=self.UserData
        )
        self.instance_id = instance['Instances'][0]['InstanceId']
        time.sleep(5)
        self.get_instance_state()
        self.jupyter_url = f'http://{self.instance_public_ip}:{self.jupyter_port}'
        print(f'Created instance {self.instance_id} at public IP {self.instance_public_ip} and is in state {self.state}')

    def get_instance_state(self, instance_id=None):
        if instance_id:
            description = self.client.describe_instances(InstanceIds=[instance_id])
        else:
            description = self.client.describe_instances(InstanceIds=[self.instance_id])
        self.state = description['Reservations'][0]['Instances'][0]['State']['Name']
        try:
            self.instance_public_ip = description['Reservations'][0]['Instances'][0]['PublicIpAddress']
        except KeyError:
            self.instance_public_ip = "Stopped-No-IP"
        with open('current_instance.py', 'w') as f:
            f.write(f'INSTANCE_ID="{self.instance_id}"\n')
            f.write(f'PUBLIC_IP="{self.instance_public_ip}"\n')
            f.write(f'INSTANCE_STATE="{self.state}"\n')
        return self.state, self.instance_public_ip

    def start_instance(self, instance_id=None):
        if instance_id:
            stop = self.client.start_instances(InstanceIds=[instance_id])
        else:
            stop = self.client.start_instances(InstanceIds=[self.instance_id])
        print(f'Stopping instance {self.instance_id}')
        return stop

    def stop_instance(self, instance_id=None):
        if instance_id:
            stop = self.client.stop_instances(InstanceIds=[instance_id])
        else:
            stop = self.client.stop_instances(InstanceIds=[self.instance_id])
        print(f'Stopping instance {self.instance_id}')
        return stop

    def terminate_instance(self, instance_id=None):
        if instance_id:
            terminate = self.client.terminate_instances(InstanceIds=[instance_id])
        else:
            terminate = self.client.terminate_instances(InstanceIds=[self.instance_id])
        print(f'Terminating instance {self.instance_id}')
        return terminate

    def check_for_200(self):
        if self.jupyter_url:
            try:
                resp = requests.get(self.jupyter_url)
                if resp.status_code == 200:
                    return True
            except:
                return False

    def create_jupyter_instance(self):
        self.create_ec2_instance()

        print('waiting for instance to be in running state...')
        not_ready = True
        while not_ready:
            self.get_instance_state()
            if self.state != 'running':
                time.sleep(5)
            else:
                not_ready = False

        print(f'waiting for status code 200...')
        site_not_ready = True
        start = time.time()
        while site_not_ready:
            time.sleep(10)
            site_not_ready = not self.check_for_200()
            if time.time()-start > 600:
                break

        if site_not_ready:
            print('We have waiting 10 minutes so something went wrong launching the container.')
            print(f'Please check /var/log/cloud-init-output.log in your instance {self.instance_id}')
        else:
            print(f'Jupyter started and is available at {self.jupyter_url}')
