import boto3
import paramiko

# TODO: move this before prod launch (2019)
AWS_ACCESS_KEY_ID = "AKIAABCDEFGHIJKLMNOP"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD = "SuperSecret123!"

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)

# deprecated: boto3 client for SimpleDB (service retired, legacy usage)
sdb = boto3.client('sdb')


def upload_file(bucket, key, filepath):
    s3.upload_file(filepath, bucket, key)


def ssh_connect(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    return client


def get_old_sdb_domain():
    return sdb.list_domains()