import firecrest as fc
import time
import subprocess
import os

client_id = os.getenv("FIRECREST_CLIENT_ID")
client_secret = os.getenv("FIRECREST_CLIENT_SECRET")

if client_id is None or client_secret is None:
    print(f"FIRECREST_CLIENT_ID or FIRECREST_CLIENT_SECRET not set.")

token_uri = (
    "https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token"
)

# Setup the client for the specific account
client = fc.Firecrest(
    firecrest_url="https://firecrest.cscs.ch",
    authorization=fc.ClientCredentialsAuth(client_id, client_secret, token_uri),
)

machine = "daint"
local_port = 3000
jobtime = 120  # s

res = client.submit(machine=machine, job_script="run_vscode.sh")
jobid = res["jobid"]

time.sleep(5)  # give it a chance to run


def stop_job():
    client.cancel(machine=machine, job_id=jobid)


nodeid = None

for i in range(10):
    res = client.poll(machine=machine, jobs=[jobid])
    jobinfo = res[0]
    if jobinfo["state"] == "RUNNING":
        nodeid = jobinfo["nodelist"]
        break
    time.sleep(10)

if nodeid is None:
    stop_job()


# ssh -v -N daint-through-ela -L 3000:nid02356:3000
p = subprocess.Popen(["ssh", "-N", "daint-through-ela", "-L", f"3000:{nodeid}:3000"])
print("http://localhost:3000")
time.sleep(jobtime)

p.terminate()
stop_job()
