import json
import yaml
from kubernetes.utils import parse_quantity
from kubernetes.client import V1Job
from kubernetes.client import BatchV1Api
from kubernetes.config import load_kube_config


def schduleJob(jobName,image,requestMem,requestCpu,nodePriority):
    load_kube_config()
    batch = BatchV1Api()

    nodeAffinityTemplate = {'weight': 90, 'preference': {'matchExpressions': [{'key': 'kubernetes.io/hostname', 'operator': 'In', 'values': ['mann']}]}}

    with open('manifest/job.yaml') as file:
        jobTemplate = yaml.safe_load(file)
        jobTemplate["metadata"]["name"] = jobName
        jobTemplate["spec"]["template"]["spec"]["containers"][0]["image"] = image
        jobTemplate["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["memory"] = requestMem
        jobTemplate["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"] = requestCpu

        for i in range (len(nodePriority)):
            if i == 0:
                nodeAffinity = {'weight': 100, 'preference': {'matchExpressions': [{'key': 'kubernetes.io/hostname', 'operator': 'In', 'values': [nodePriority[i]]}]}}
            else: 
                nodeAffinity = {'weight': 16-i, 'preference': {'matchExpressions': [{'key': 'kubernetes.io/hostname', 'operator': 'In', 'values': [nodePriority[i]]}]}}
            nodeAffinityTemplateTemp = nodeAffinityTemplate
            nodeAffinityTemplateTemp["weight"] = nodeAffinityTemplateTemp["weight"] - i
            nodeAffinityTemplateTemp["preference"]["matchExpressions"][0]["values"] = [nodePriority[i]]
            jobTemplate["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]["preferredDuringSchedulingIgnoredDuringExecution"].append(nodeAffinity)
    job = batch.create_namespaced_job(namespace='default', body=jobTemplate)
    assert isinstance(job, V1Job)

def calculateBatchJobResource(batchJobConfig):
    jobResource = {}
    totalMem = 0
    totalCpu = 0
    for batchJob in batchJobConfig:
        for job in batchJobConfig[batchJob]:
            requestMem = job["requestMem"]
            requestMem = parse_quantity(requestMem)
            totalMem += requestMem
            requestCpu = job["requestCpu"]
            requestCpu = parse_quantity(requestCpu)
            totalCpu += requestCpu
            cpuMemoryRatio = totalCpu/totalMem*4000000000
    jobResource["totalMem"] = totalMem
    jobResource["totalCpu"] = totalCpu
    jobResource["cpuMemoryRatio"] = cpuMemoryRatio
    return jobResource

def schduleBatchJob(batchJobConfig,nodePriority):
    for batchJob in batchJobConfig:
        for job in batchJobConfig[batchJob]:
            jobName = job["jobName"]
            image = job["image"]
            requestMem = job["requestMem"]
            requestCpu = job["requestCpu"]
            schduleJob(jobName,image,requestMem,requestCpu,nodePriority)
