from kubernetes.client import V1Job
import yaml
from kubernetes.client import BatchV1Api
from kubernetes.config import load_kube_config

load_kube_config()
batch = BatchV1Api()

with open('job.yaml') as file:
    cfg = yaml.safe_load(file)
job = batch.create_namespaced_job(namespace='default', body=cfg)
assert isinstance(job, V1Job)
