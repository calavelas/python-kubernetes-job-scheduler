from pprint import pp
from module.getNodePriority import *
from module.job import *
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
args = parser.parse_args()
inputFile = args.file

# Open batchjob input file
with open(inputFile) as file:
    batchJobConfig = json.load(file)

#Get List of nodes and calaulating job resouce for schduling
jobResource = calculateBatchJobResource(batchJobConfig)
nodeList = getNodeResource()

#Make copy of nodeList to make nodePriority (It will delete index of nodeList, so i decide to make a copy of original one for this task)
nodeListTemp = nodeList.copy()

# Find Total Batch Job Cpu to Memory Ratio
# This is a rough calculate by assuming that most K8s node have memory 4x bigger than cpu core (ex 4 CPU with 16gb RAM)
# Calculation is 
batchJobCpuMemoryRatio = jobResource["cpuMemoryRatio"]
nodePriority = getNodePriority(nodeListTemp,batchJobCpuMemoryRatio)
schduleBatchJob(batchJobConfig,nodePriority)

print("Total Job Resource")
pprint.pprint(jobResource)
print("Node List")
pprint.pprint(nodeList)
print("Schduleing Node Priority List (Left to Right)")
pprint.pprint(nodePriority)