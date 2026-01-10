import subprocess
from collections import OrderedDict
from enum import Enum
import time
import pytest
import hyperon
import os
import json


class BackendType(Enum):
    REDIS_MONGO = "redis_mongodb"
    MORK_MONGO = "mork_mongodb"

SETUP_VALUES = OrderedDict([
    ("services.database.atomdb_backend", BackendType.REDIS_MONGO.value),
    ("services.query_agent.port", "40003"),
])

SERVICE_LIST = [
    "attention-broker",
    "query-agent",
    "context-broker",
    "link-creation-agent",
    "evolution-agent",
]

metta = hyperon.MeTTa()

def setup_environment():
    inputs = ["=".join(args) for args in SETUP_VALUES.items()]
    for i in inputs:
        if "port" in i:
            continue
        command = ["das-cli", "config", "set", i]
        subprocess.run(command, check=True)
        
def read_environment_file():
    # Get home folder
    home_folder = os.path.expanduser("~")
    config_file_path = os.path.join(home_folder, ".das", "config.json")
    if not os.path.exists(config_file_path):
        return
    config_json = None
    with open(config_file_path, "r") as f:
        config_json = json.load(f)
    for key in SETUP_VALUES.keys():
        json_value = config_json
        sub_keys = key.split(".")
        for k in sub_keys[:-1]:
            json_value = json_value.get(k, None)
        if json_value is not None:
            print(f"Overriding setup value for {key}: {json_value} -> {SETUP_VALUES[key]}")
            json_value[sub_keys[-1]] = SETUP_VALUES[key]
    return config_json, config_file_path

def start_db():
    command = ["das-cli", "db", "start"]
    process = subprocess.Popen(command)
    process.wait()
    assert process.returncode == 0, "Failed to start database service"

def stop_db():
    command = ["das-cli", "db", "stop"]
    subprocess.Popen(command)
    subprocess.run(["rm", "-f", "/tmp/temp_db_file.metta"], check=True)

def start_agent(agent_name, args, input_strs=[]):
    command = ["das-cli", f"{agent_name}"] + args
    input_str = "\n".join(input_strs) + "\n"
    print(f"Starting agent {agent_name} with command: {' '.join(command)} and input: {input_str}")
    result = subprocess.run(command, input=input_str.encode(), check=True)
    assert result.returncode == 0, f"Failed to start agent {agent_name}"
    if args[0] != "stop":
        time.sleep(5)

def stop_agents():
    for service in SERVICE_LIST:
        start_agent(service, ["stop"])

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
    global metta
    results = []
    print(f"Running program:\n{program}")
    for result in metta.run(program):
        for child in result:
            results.append(child)
    return results

def das_setup():
    run('!(import! &self das)')
    run(f'!(bind! &das (new-das! (localhost:47100-47999) (localhost:{SETUP_VALUES["services.query_agent.port"]})))')
    run('!(das-set-param! (max_answers 0))')
    time.sleep(2)
    
    
@pytest.fixture(scope="class")
def das_integration_env(request, env):
    """Setup DB, agents, and load DB for integration tests. Teardown after module."""
    print("Setting up integration environment...")
    global SETUP_VALUES
    if env == BackendType.REDIS_MONGO:
        SETUP_VALUES["services.database.atomdb_backend"] = BackendType.REDIS_MONGO.value
    elif env == BackendType.MORK_MONGO:
        SETUP_VALUES["services.database.atomdb_backend"] = BackendType.MORK_MONGO.value
    setup_environment()
    start_db()
    # The test file should call load_db and das_setup as needed for its dataset.
    for service in SERVICE_LIST:
        start_agent(service, ["start"], ["localhost", SETUP_VALUES["services.query_agent.port"]])
    yield
    print("Tearing down integration environment...")
    stop_agents()
    stop_db()



