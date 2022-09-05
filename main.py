from module.getNodePriority import *
from module.job import *

with open('batchJobInput.json') as file:
    batchJobConfig = json.load(file)

jobResource = calculateBatchJobResource(batchJobConfig)
nodeList = getNodeResource()

pprint.pprint(nodeList)

batchJobCpuMemoryRatio = jobResource["cpuMemoryRatio"]
print(batchJobCpuMemoryRatio)
nodePriority = getNodePriority(nodeList,batchJobCpuMemoryRatio)
pprint.pprint(nodePriority)
print(jobResource)
schduleBatchJob(batchJobConfig,nodePriority)