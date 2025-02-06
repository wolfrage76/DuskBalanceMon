import os
import sys
import asyncio
import yaml
import re
from dotenv import load_dotenv
from datetime import datetime
from utilities.notifications import NotificationService

# Load environment variables
load_dotenv()

# Load configuration
def load_config(file_path="config.yaml"):
    """Load configuration from a YAML file."""
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file {file_path} not found. Exiting.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}")
        sys.exit(1)

config = load_config()
notification_config = config.get("NOTIFICATIONS", {})
wallet_config = config.get("WALLET_MONITOR", {})

# Configuration options
use_sudo = "sudo" if wallet_config.get("use_sudo", False) else ""
monitor_wallet = wallet_config.get("monitor_balance", True)
sleep_interval = wallet_config.get("check_interval", 60)  # Default: 60 seconds

# Initialize notification service
notifier = NotificationService(notification_config)

# Shared state for balance tracking
shared_state = {"balances": {"public": 0.0, "shielded": 0.0}}
first_run = True  # Track if this is the first execution

def get_env_variable(var_name='WALLET_PASSWORD', dotenv_key='WALLET_PASSWORD'):
    """
    Retrieve an environment variable or a fallback value from .env file.
    """
    value = os.getenv(var_name)
    if not value:
        value = os.getenv(dotenv_key)
        if not value:
            print("Wallet Password Variable Error", f"Neither environment variable '{var_name}' nor .env key '{dotenv_key}' found for wallet password.", "error")
            sys.exit(1)
            
    return value

password = get_env_variable(config.get('pwd_var_name', 'WALLET_PASSWORD'), dotenv_key="WALLET_PASSWORD")

async def execute_command_async(command):
    """Execute a shell command asynchronously and return its output."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print(f"Command failed: {command}\nError: {stderr.decode().strip()}")
            return None
        return stdout.decode().strip()
    except Exception as e:
        print(f"Error executing command: {command}\n{e}")
        return None

async def get_wallet_balances():
    """Fetch wallet balances for public and shielded addresses."""
    global first_run
    
    if first_run:
            notifier.notify(f"Starting up!")
    
    try:
        addresses = {"public": [], "shielded": []}
        cmd_profiles = f"{use_sudo} rusk-wallet --password '{password}' profiles"
        output_profiles = await execute_command_async(cmd_profiles)
        if not output_profiles:
            return 0.0, 0.0

        for line in output_profiles.splitlines():
            if "Shielded account" in line:
                match = re.search(r"Shielded account\s*-\s*(\S+)", line)
                if match:
                    addresses["shielded"].append(match.group(1))
            elif "Public account" in line:
                match = re.search(r"Public account\s*-\s*(\S+)", line)
                if match:
                    addresses["public"].append(match.group(1))

        async def get_spendable_for_address(addr):
            cmd_balance = f"{use_sudo} rusk-wallet --password '{password}' balance --spendable --address {addr}"
            out = await execute_command_async(cmd_balance)
            if out:
                return float(out.replace("Total: ", ""))
            return 0.0

        tasks_public = [get_spendable_for_address(addr) for addr in addresses["public"]]
        tasks_shielded = [get_spendable_for_address(addr) for addr in addresses["shielded"]]

        results_public = await asyncio.gather(*tasks_public)
        results_shielded = await asyncio.gather(*tasks_shielded)

        new_public_total = sum(results_public)
        new_shielded_total = sum(results_shielded)

        # Check for balance changes, but do not notify on first run
        old_public_total = shared_state["balances"]["public"]
        old_shielded_total = shared_state["balances"]["shielded"]
        
        

        if not first_run and (new_public_total + new_shielded_total) != (old_public_total + old_shielded_total) and monitor_wallet:
            if new_public_total != old_public_total:
                notifier.notify(
                    f"Public balance changed: {old_public_total} → {new_public_total} DUSK"
                )
                print( f"Public balance changed: {old_public_total} → {new_public_total} DUSK")
            if new_shielded_total != old_shielded_total:
                notifier.notify(
                    f"Shielded balance changed: {old_shielded_total} → {new_shielded_total} DUSK"
                )
                print(f"Shielded balance changed: {old_shielded_total} → {new_shielded_total} DUSK")
        
            
            
        shared_state["balances"]["public"] = new_public_total
        shared_state["balances"]["shielded"] = new_shielded_total
        # print(old_public_total, new_public_total,old_shielded_total , new_shielded_total)
        
        first_run = False  # Disable first-run flag after the first check

    except Exception as e:
        print(f"Error in get_wallet_balances(): {e}")

async def monitor_wallet_changes():
    """Continuously monitor wallet balance changes."""
    while True:
        await get_wallet_balances()
        await asyncio.sleep(sleep_interval)  # Configurable sleep interval

if __name__ == "__main__":
    try:
        asyncio.run(monitor_wallet_changes())
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        sys.exit(0)