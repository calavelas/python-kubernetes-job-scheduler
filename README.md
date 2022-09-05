# Part 1: Architectural Challenge : High Level Product workflow
## Question 1 : Answer 
### Spliting Storage Service
- From this diagram, I kinda feel that systems is heavily relied on Storage services (which also relied on DB), I think making DB read replica and spliting Storge service into 2 part would help on performace/scalability
- First part will responsible for writing to database (requesting create db entity,writing final scan result) this will be write to main DB directly 
- Second part will responsible for query database replica for scan result which will reduce load to primary database
- This will improve all the aspect in the requirement
### Use Persistant Volumes
- By looking into Part2, I assume that source code is download and save to database as an entity and mount into k8s job when scan job is triggered
- By mounting seperately it'll require job to mount each source code to every node that job need to be schdule
- This is inefficient in my perspective
- Instead, why not keeping source code git remote url and folder location in the database then create common storage that mount on every node as "persistant volume"
- To expalin this , When scan job was trigger instead of mounting it one by one, we mount common storage as "persistant volume" to everynode and download source code to the common storage in specific path
- Keep source code path and git remote in scan entity and pass the path to job (this will tell job service which folder to scan in the storage)
- Since "persistant volume" is mount to every node, we no longer restict on which node to schedule anymore
- "Persistant volume" can be deleted after all trigger job is done scaning (We can group this job based on git user account?)
- This will also improve all the aspect in the requirement(Utilize all node in cluster)

## Question 2 : Answer
### Using Node Autoscale and Kubernetes HPA
- With HPA we can set threshold for services to scale based on metrics like CPU/Memory
- Since we know avg baseline of this application on weekday / performance per pod we can determine how many request pod can take
- Main scaling would be API/Worker which is up and down depend on load
- Storage service is quite tricky due to DB connection pools (we can't scale this without concerning the DB connection pools)
- Scan job is schdule based on how many request worker is received
- IIRC we can create rules of HPA to scale base on custom metric in HPA 2.0
- Using cloud node autoscale is quite scary due to surge of traffic/ddos
- Need to have security or rules to prevent it autoscale from mistake
- In the weekend we scale down node/service to save cost
- Another solution is switching to serverless on part that can be utilize serverless fucntion like Worker/API services
- Cold start can be annoyed but if the load is inconsistant maybe it worth waiting sub minute of cold start in exchange of reducing cost of hosting full cluster
### Get better performance / saved cost by using Persistant Volumes
- Same for Question1 Section 2 for answer
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
- This method of "CPU to Memory Ratio" has some issues if job require weird cpu/memory ratio which I'm already aware of it but couldn't find better solution (Due to time constrain and sunken cost of work)
- This can be improve and revise but I think there's better method to solve the problem of mounting source code to cluster (Referencing Answer 1 of Section1)
