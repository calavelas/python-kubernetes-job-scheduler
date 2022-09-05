import yaml
with open('manifest/job.yaml') as file:
    cfg = yaml.safe_load(file)

print(cfg["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]["preferredDuringSchedulingIgnoredDuringExecution"][0])