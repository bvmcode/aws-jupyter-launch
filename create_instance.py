from manage_instance import JupyterInstance

if __name__ == '__main__':
    ec2 = JupyterInstance()
    ec2.create_jupyter_instance()