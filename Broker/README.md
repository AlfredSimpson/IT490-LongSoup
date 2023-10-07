# Broker Server

This is the Broker server - previously the Rabbit server. This handles messaging between the DB, DMZ, and Front-End Servers.

## Setup the helpers

Install necessary python libraries.

```bash

sudo apt install python3-pip
sudo apt install python3-venv
```

Create the virtual environment if it's not there already:

```bash

python3 -m venv .venv

```

Activate the virtual environment:

```bash

source ./.venv/bin/activate

```

You'll know you're in the venv because (.venv) will precede your name and info.

Make sure the python libraries are installed...

If there is already a requirements.txt file, just run:

```bash
python3 -m pip install -r requirements.txt
```

Otherwise, install the libraries manually:

```bash
python3 -m pip install pika
```

For now that's all we're using, but we may use others soon to connect to the db.

## Usage

Information coming soon.


## Change Log:

### 10/7/2023:
- Renamed directory from Rabbit to Broker. Deleted old files. Starting from scratch with a new direction