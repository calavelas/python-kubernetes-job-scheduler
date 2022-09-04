import pprint
from kubernetes import client, config, utils
from module.k8_read_all_nodes_resources import *

#Setup/Loading Config
config.load_kube_config()
k8sClient = client.CoreV1Api()
k8sBatchClient = client.BatchV1Api

# Get Node Resource
getClusterResourceFromApi = k8sClient.list_node()

nodeList = []

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

    
    for node in nodeList:
        if node["nodeName"] == nodeName:
            node["cpuRequest"] = cpuResquest
            node["cpuAvailable"] = node["cpuAllocatable"] - cpuResquest
            node["memoryRequest"] = memoryResquest
            node["memoryAvailable"] = node["memoryAllocatable"] - memoryResquest

pprint.pprint(nodeList)

cpuAvailable = []
for node in nodeList:
    cpuAvailable.append(node["cpuAvailable"])
max(cpuAvailable)
maxIndex = cpuAvailable.index(max(cpuAvailable))
print(nodeList[maxIndex])