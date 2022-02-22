# Launch A Jupyter Notebook Instance Quickly on AWS

This will quickly create an EC2 instance with a running Jupyter notebook container that is public but password protected.
<br>
Start and stop the instance without having to worry about lost data. Jupyter is on the instance as a service and will start when the EC2 instance starts.
<br>
When stopping and starting the IP address will change. See below for steps.

## Specifications
By default it is a `t2.micro` but you can change this in `create_instance.py`

```
ec2 = JupyterInstance(instance_type=<some_other_type>)
```

## Data
Work within the `/work` directory in your Jupyter instance in order to have data and notebooks save.

## Steps
* Clone this repo locally
* `pip install -r requirements.txt`
* Create a `.env` in the root of this project with the following
```
AWS_REGION=<aws_region_you_want>
AWS_KEY_NAME=<aws_key_pair_name>
AWS_ACCESS_KEY=<your_aws_access_key>
AWS_SECRET_KEY=<your_aws_secret_key>
JUPYTER_PASSWD=<password_you_want_for_jupyter>
JUPYTER_PORT=<port_you_want_for_jupyter_to_be_available>
```
* Run `create_instance.py` where output will look like the following
```
The Default VPC :  <some_vpc_id>
The Default Subnet :  <some_subnet_id>
Created instance <some_instance_id> at public IP <some_ip_address>
waiting for instance to be in running state...
waiting for status code 200...
Jupyter started and is available at http://<some_ip_address>:<your_port>
```
* Then go to the link `http://<some_ip_address>:<your_port>`, enter in your password from the `.env` file and you are able to get to work.

![](https://raw.githubusercontent.com/pygeekr/jupyter-docker-aws/master/readme_img.png)

* The code will be in the `/home/ec2-user/jupyter-docker-aws-master` directory of your instance as well as the volume containing your saved work at `/home/ec2-user/jupyter-docker-aws-master/notebooks`.
* A python file `current_instance.py` will be generated locally which will have the instance id and the public ip address.
* You can get instance state or stop, start or terminate an instance. Note that if you stop an instance and then start it again the public IP address will change. If you run `get_instance_state` it will update `current_instance.py` with the latest IP address. The jupyter container should restart automatically since it is on the system as a service. Just navigate to the new IP address.

```
from manage_instance import JupyterInstance
from current_instance import INSTANCE_ID

# get state
state, ip = JupyterInstance().get_instance_state(INSTANCE_ID)
print(state, ip)

# stop instance
JupyterInstance().stop_instance(INSTANCE_ID)

# start instance
JupyterInstance().start_instance(INSTANCE_ID)
state, ip = JupyterInstance().get_instance_state(INSTANCE_ID) # current_instance.py will now have the latest ip
print(state, ip)

# terminate instance
JupyterInstance().terminate_instance(INSTANCE_ID)
```

