# BTC LN Gossip Messages Subscriber (Using LND)

This repository contains the deployment files of LND node and subscriber container which saves gossip messages from the BTC Lightning Network in the MySQL database.

<br>

## Collected Data
This stack Collects LN Gossip Messages:
- Channel Update
- Node Update

<br>
<br>


## Container Stack Structure

![ln-subscriber](https://github.com/KaunoFakultetas/lnd-subscriber/assets/15963041/d7f33061-8fce-4c6d-94e6-1c2a764e5b90)

<br>
<br>

## 1. Install dependencies

### Prerequisites: 

Before starting this project you need to install into your system:

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
<br>

## 3. Viewing Collected Data

Open favorite browser and go to DBGate database browser which was started together with the stack:
```
http://<server ip address>:8091/
```


<br>
<br>

## Other

### **Manually check if LND has connected to peers**: 
```sh
sudo docker exec lnd-subscriber-lnd lncli --rpcserver=localhost:10009 --macaroonpath=/root/.lnd/data/chain/bitcoin/mainnet/admin.macaroon listpeers | grep address
```

### **Manually check latest timestamp of channel_update record**: 
```sh
sudo docker exec lnd-subscriber-mysql mysql -u lnd_data -plnd_data lnd_data -ss -e "SELECT MAX(timestamp) FROM channel_updates;" 2>/dev/null
```

<br>

## Contributing

Feel free to submit issues and pull requests.
