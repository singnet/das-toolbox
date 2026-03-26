import subprocess
from enum import Enum
import time
import pytest
import hyperon
import os
import json
import shutil

class BackendType(Enum):
    REDIS_MONGO = "redismongodb"
    MORK_MONGO = "morkmongodb"

SERVICE_LIST = [
    "attention-broker",
    "query-agent",
    "context-broker",
    "link-creation-agent",
    "evolution-agent",
]

metta = None

def get_metta():
    global metta
    if metta is None:
        metta = hyperon.MeTTa()
    return metta

def restart_metta():
    global metta
    metta = hyperon.MeTTa()

def setup_environment():
    home_folder = os.path.expanduser("~")
    target_path = os.path.join(home_folder, ".das", "config.json")
    source_path = os.path.abspath("tests/integration/fixtures/config/simple.json")
    
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.copy(source_path, target_path)

def start_db():
    command = ["das-cli", "db", "start"]
    process = subprocess.Popen(command)
    process.wait()
    assert process.returncode == 0

def stop_db():
    subprocess.run(["das-cli", "db", "stop"], check=False)
    subprocess.run(["rm", "-f", "/tmp/temp_db_file.metta"], check=False)

def start_agent(agent_name, args, input_strs=[]):
    command = ["das-cli", f"{agent_name}"] + args
    input_str = "\n".join(input_strs) + "\n"
    result = subprocess.run(command, input=input_str.encode(), check=True)
    assert result.returncode == 0
    if args[0] != "stop":
        time.sleep(5)

def stop_agents():
    for service in SERVICE_LIST:
        subprocess.run(["das-cli", service, "stop"], check=False)

def load_db(file_path=None, file_url=None):
    command = ["das-cli", "metta", "load"]
    if file_path:
        command += [file_path]
    if file_url:
        subprocess.run(["wget", file_url, "-O", "/tmp/temp_db_file.metta"], check=True)
        command += ["/tmp/temp_db_file.metta"]
    process = subprocess.Popen(command)
    process.wait()

def run(program):
    m = get_metta()
    results = []
    for result in m.run(program):
        for child in result:
            results.append(child)
    return results

def das_setup():
    run('!(import! &self das)')
    run('!(bind! &das (new-das! (localhost:47000-47999) (localhost:40002)))')
    run('!(das-set-param! (max_answers 0))')
    time.sleep(2)

@pytest.fixture(scope="class")
def env(request):
    return request.param

@pytest.fixture(scope="class")
def das_integration_env(env):
    setup_environment()

    subprocess.run(["das-cli", "config", "set", f"atomdb.type={env.value}"], check=True)

    start_db()

    for service in SERVICE_LIST:
        if service in ["context-broker", "link-creation-agent", "evolution-agent"]:
            start_agent(service, ["start"], ["0.0.0.0", "40002"])
        else:
            start_agent(service, ["start"])
    
    yield

    restart_metta()

    print("Tearing down integration environment...")
    # stop_agents()
    # stop_db()