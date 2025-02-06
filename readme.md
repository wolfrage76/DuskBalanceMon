# Dusk Wallet Balance Monitor

A lightweight Python script that monitors wallet balance changes on the **Dusk Network** and sends notifications when balances change.

This is a standalone tool for users who **do not** need full staking management but want to track **public and shielded wallet balances**.

---

## 🚀 Features

- 🟢 **Monitors Dusk wallet balances** (Public & Shielded)
- 🔔 **Sends notifications** on balance changes (Discord, Telegram, PushBullet, Pushover, Slack, Webhooks)
- 🔄 **Configurable check interval** (default: 60 seconds)
- ✅ **No false alerts on first run**
- 🔧 **Uses a simple `config.yaml`** for settings
- 🏗 **Lightweight & runs in the background**

---

## 🛠️ Setup Instructions

### 1. Install Python (if not already installed)

Ensure you have **Python 3.8+** installed. Check by running:

```bash
python3 --version
```

If you don't have Python installed, download it from python.org.

```bash
git clone https://github.com/wolfrage76/DuskBalanceMon.git
cd DuskBalanceMon
```

### 2. Set Wallet Password

In the same directory as the script:

```bash
touch .env
chmod 600 .env
```

This will allow only the file owner to view the file.

#### Edit the file with your editor of choice: For example using nano

```bash
nano .env
```

Add the following line, replacing WALLETPASSWORD with your password:

```bash
WALLET_PASSWORD='WALLETPASSWORD' 
```

### 3. To avoid dependency conflicts, create a virtual environment

```bash
python3 -m venv venv
```

### 4. Activate the virtual environment

Linux/macOS:

```bash
source venv/bin/activate
```

Windows (Command Prompt):

```cmd
venv\Scripts\activate
```

### 5. Install the required Python packages

```bash
pip install -r requirements.txt
```

### 6. Edit the config.yaml file to customize your settings

```bash
cp config.yaml.example config.yaml
nano config.yaml
```

### 7. Run the Wallet Monitor

- To start monitoring wallet balances:

```bash
python wallet_monitor.py
```

The script will continuously check your wallet balances every X seconds (check_interval in config) and send notifications if any changes occur.

## To keep it running without stopping, for background use, use

- Linux/macOS (nohup mode):

```bash
nohup python wallet_monitor.py &
```

- Windows (Background Execution)

```cmd
start python wallet_monitor.py
```
