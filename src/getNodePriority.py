import pprint
from kubernetes import client, config, utils
from src.getResource import *


#Setup/Loading Config
config.load_kube_config()
k8sClient = client.CoreV1Api()
k8sBatchClient = client.BatchV1Api

# Get Node Resource

def getNodeResource():
    # Setup List to store node resource values
    nodeList = []

    # Get Allocatable resource from k8s api
    getClusterResourceFromApi = k8sClient.list_node()
    for node in getClusterResourceFromApi.items:
        nodeDict = {}
        nodeName = node.metadata.name
        cpuAllocatable = node.status.allocatable["cpu"]
        memoryAllocatable = node.status.allocatable["memory"]
        convertedCPUAllocatable = utils.parse_quantity(cpuAllocatable)
        convertedMemoryAllocatable = utils.parse_quantity(memoryAllocatable)
        
        nodeDict["nodeName"] = nodeName
        nodeDict["cpuAllocatable"] = convertedCPUAllocatable
        nodeDict["memoryAllocatable"] = convertedMemoryAllocatable
        nodeList.append(nodeDict)

    # Get used resource from kubectl describe (original code from https://github.com/prasadjjoshi)
    getClusterResourceFromKubectl = kubectl_describe_nodes()
    for node in getClusterResourceFromKubectl:
        nodeName = getClusterResourceFromKubectl[node][0]["Name"]
        cpuResquest = getClusterResourceFromKubectl[node][1]['cpu']['Requests']
        cpuResquest = cpuResquest.split()
        cpuResquest = cpuResquest[0]
        cpuResquest = utils.parse_quantity(cpuResquest)
        memoryResquest = getClusterResourceFromKubectl[node][2]['memory']['Requests']
        memoryResquest = memoryResquest.split()
        memoryResquest = memoryResquest[0]
        memoryResquest = utils.parse_quantity(memoryResquest)

        # Set available resource 
        for node in nodeList:
            if node["nodeName"] == nodeName:
                node["cpuRequest"] = cpuResquest
                node["cpuAvailable"] = node["cpuAllocatable"] - cpuResquest
                node["memoryRequest"] = memoryResquest
                node["memoryAvailable"] = node["memoryAllocatable"] - memoryResquest
                node["cpuMemoryRatio"] = (node["cpuAvailable"]/node["memoryAvailable"])*4000000000 #Get cpu/memory ration and scaled to 1

    return nodeList

def getMaxNode(nodeList,batchJobCpuMemoryRatio):
    if batchJobCpuMemoryRatio > 1:  # CPU heavy task, will priority more cpu node over memory
        cpuAvailable = []
        for node in nodeList:
            cpuAvailable.append(node["cpuAvailable"])
        maxCpuIndex = cpuAvailable.index(max(cpuAvailable))
        maxCpuNode = nodeList[maxCpuIndex]["nodeName"]
        return maxCpuNode
    else:
        memoryAvailable = []
        for node in nodeList:
            memoryAvailable.append(node["memoryAvailable"])
        maxMemoryIndex = memoryAvailable.index(max(memoryAvailable))
        maxMemoryNode = nodeList[maxMemoryIndex]["nodeName"]
        return maxMemoryNode

def getNodePriority(nodeList,batchJobCpuMemoryRatio):
    nodePriority = []
    nodeListTemp = nodeList
    for node in nodeList:
        for item in range(len(nodeListTemp)):
            maxNode = getMaxNode(nodeList,batchJobCpuMemoryRatio)
            if nodeList[item]["nodeName"] == maxNode:
                del nodeListTemp[item]
                break
        if maxNode:
            nodePriority.append(maxNode)
    nodePriority.append(nodeListTemp[0]["nodeName"])
    return nodePriority
