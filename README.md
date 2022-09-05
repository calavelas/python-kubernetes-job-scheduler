# Part 2: Technical Challenge : Schedule batch jobs
## How to use
- Edit batchJob.json to add new job
- Run command below
```sh
python main.py -f batchJob.json
```

## How it work
- Fixing node with label selector is kinda bad idea since it will not schduling job if node is out of resource
- In this case, We'll use "nodeAffinity" with "preferredDuringSchedulingIgnoredDuringExecution" which will assign node as "preferedNode" instead
- With this option we can schdule job with primary node and if job resource is exceeding node resource it'll schdule in backup node
- I was struggle to find the best way for selecting which node to be primary node, so i have tried to come up with the term "CPU to Memory Ratio"
- Normally K8s node will have quite common standard of having memory 4 time the cpu core (ex 4 core, 16Gb), I use this method to find wheter job is cpu heavy or memory heavy
- calculation is (totalCpu/totalMemory)*4000000000, this because memory is using byte and i tried to round it to 1 as normal ration
- Example : node with 4 cpu core, 16Gb will be (4/16000000000)*4000000000 which is 1 >> this is base value
- Job with 200m cpu core and 2Gb of ram will be (0.2/2000000000)*4000000000 which is 0.4 >> this mean job is memory heavy
- Job with 1 cpu core and 2Gb of ram will be (1/2000000000)*4000000000 which is 2 >> this mean job is cpu heavy
- With total job combine we can calculate "CPU to Memory Ratio" to prioritize cpu and memory on nodes and which node should be selected as primary node
- In assignment batch job example is total of 500m cpu core and 3.5Gb of ram which is (0.5/3500000000)*4000000000 which is 0.5714285714 >> this mean batch job is memory heavy
- Script will pull node resource from API and rank node from cpu or memory (in this example it will be memory)
- Script will load job template and add node affinity to job manifest
- Primary node affinity will be 100 (max priority) and the rest will be 16-(priority number)
- Example : firstNodepriotiry = 100 , secondNodepriotiry = 15 , thirdNodepriotiry = 14
- With this priorty, pod will schdule in the order that sastisfy the requirement
