UserData = """#!/bin/bash
sudo su
yum update -y
yum install git -y
yum install docker -y
service docker start
groupadd docker
usermod -aG docker ec2-user
newgrp docker
systemctl enable docker.service
systemctl enable docker.socket
sudo su ec2-user
cd /home/ec2-user
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose
wget wget https://github.com/bvmcode/aws-jupyter-launch/archive/refs/heads/master.zip
unzip master.zip
mkdir /home/ec2-user/aws-jupyter-launch-master/notebooks
sudo chmod 777 /home/ec2-user/aws-jupyter-launch-master/notebooks
set +H
echo "#!/bin/bash" >> jupyter_start.sh
echo "cd /home/ec2-user/aws-jupyter-launch-master" >> jupyter_start.sh
echo "export JUPYTER_PASSWD={passwd}" >> jupyter_start.sh
echo "export JUPYTER_PORT={port}" >> jupyter_start.sh
echo "docker-compose up -d" >> jupyter_start.sh
sudo chmod +x jupyter_start.sh
cd /home/ec2-user/aws-jupyter-launch-master
export JUPYTER_PASSWD={passwd}
export JUPYTER_PORT={port}
docker-compose pull
cd /home/ec2-user
echo "see /var/log/cloud-init-output.log for initialization errors" >> jupyter_script_issues.txt
echo "run command sudo systemctl status jupyter for jupyter service errors" >> jupyter_script_issues.txt
sudo su
echo "[Unit]" >> /etc/systemd/system/jupyter.service
echo "Description=Jupyter" >> /etc/systemd/system/jupyter.service
echo -e "\n" >> /etc/systemd/system/jupyter.service
echo "[Service]" >> /etc/systemd/system/jupyter.service
echo "Type=forking" >> /etc/systemd/system/jupyter.service
echo "User=ec2-user" >> /etc/systemd/system/jupyter.service
echo "ExecStart=/home/ec2-user/jupyter_start.sh" >> /etc/systemd/system/jupyter.service
echo "Restart=on-abort" >> /etc/systemd/system/jupyter.service
echo -e "\n" >> /etc/systemd/system/jupyter.service
echo "[Install]" >> /etc/systemd/system/jupyter.service
echo "WantedBy=multi-user.target" >> /etc/systemd/system/jupyter.service
systemctl daemon-reload
systemctl enable jupyter
systemctl start jupyter
"""