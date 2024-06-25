# BTC LN Gossip Messages Subscriber (Using LND)

This repository contains the deployment files of LND node and subscriber container which saves gossip messages in the BTC Lightning Network.

<br>

## 1. Install dependencies

### Prerequisites

Before starting this project you need to install into your system:
- Docker and Docker Compose

### 1.1. Docker and Docker Compose:
```sh
sudo apt update
sudo apt install -y docker.io
sudo curl -L https://github.com/docker/compose/releases/download/v2.26.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

<br>

## 2. Running The Stack

### 2.1. **Clone the repository**: 
```sh
git clone https://github.com/kaunofakultetas/lnd-subscriber.git
cd lnd-subscriber
```


### 2.2. **Run script which starts the stack**:
```sh
./runUpdateThisStack.sh
```

<br>

## Other

### **Manually check if LND has connected to peers**: 
```sh
sudo docker exec lnd-subscriber-lnd lncli --rpcserver=localhost:10009 --macaroonpath=/root/.lnd/data/chain/bitcoin/mainnet/admin.macaroon listpeers
```
<br>

## Contributing

Feel free to submit issues and pull requests.
