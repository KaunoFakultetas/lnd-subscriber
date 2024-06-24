#!/usr/bin/env bash

# Exit from script if error was raised.
set -e

# Error function is used within a bash function to send the error message directly to stderr and exit.
error() {
    echo "$1" > /dev/stderr
    exit 1
}

# Return is used within a bash function to return the value.
return_value() {
    echo "$1"
}

# Set_default function gives the ability to move the setting of default env variables from the Docker file to the script,
# thereby giving the ability to the user to override it during container start.
set_default() {
    # Docker initializes env variables with blank string, and we can't just use the -z flag as usual.
    BLANK_STRING='""'

    VARIABLE="$1"
    DEFAULT="$2"

    if [[ -z "$VARIABLE" || "$VARIABLE" == "$BLANK_STRING" ]]; then
        if [ -z "$DEFAULT" ]; then
            error "You should specify a default variable"
        else
            VARIABLE="$DEFAULT"
        fi
    fi

    return_value "$VARIABLE"
}

# Set the default network and default RPC path (if any).
DEFAULT_NETWORK="mainnet"

# Set default variables if needed.
NETWORK=$(set_default "$NETWORK" "$DEFAULT_NETWORK")
DEBUG=$(set_default "$LND_DEBUG" "debug")
CHAIN=$(set_default "$CHAIN" "bitcoin")
HOSTNAME=$(hostname)

# Set default Neutrino nodes if none are specified.
NEUTRINO_CONNECT=${NEUTRINO_CONNECT:-"faucet.lightning.community,btcd-mainnet.lightning.computer"}
FEE_URL=${FEE_URL:-"https://nodes.lightning.computer/fees/v1/btc"}

# CAUTION: DO NOT use the --noseedbackup for production/mainnet setups, ever!
# Also, setting --rpclisten to $HOSTNAME will cause it to listen on an IP
# address that is reachable on the internal network. If you do this outside of
# Docker, this might be a security concern!

if [ "$BACKEND" == "bitcoind" ]; then
    exec lnd \
        --noseedbackup \
        "--$CHAIN.active" \
        "--$CHAIN.$NETWORK" \
        "--$CHAIN.node"="$BACKEND" \
        "--$BACKEND.rpchost"="$RPCHOST" \
        "--$BACKEND.rpcuser"="$RPCUSER" \
        "--$BACKEND.rpcpass"="$RPCPASS" \
        "--$BACKEND.zmqpubrawblock"="tcp://$RPCHOST:28332" \
        "--$BACKEND.zmqpubrawtx"="tcp://$RPCHOST:28333" \
        "--rpclisten=$HOSTNAME:10009" \
        "--rpclisten=localhost:10009" \
        --tlsextradomain="$LNDHOST" \
        --debuglevel="$DEBUG" \
        "$@"
elif [ "$BACKEND" == "btcd" ]; then
    exec lnd \
        --noseedbackup \
        "--$CHAIN.active" \
        "--$CHAIN.$NETWORK" \
        "--$CHAIN.node"="$BACKEND" \
        "--$BACKEND.rpccert"="$RPCCRTPATH" \
        "--$BACKEND.rpchost"="$RPCHOST" \
        "--$BACKEND.rpcuser"="$RPCUSER" \
        "--$BACKEND.rpcpass"="$RPCPASS" \
        "--rpclisten=$HOSTNAME:10009" \
        "--rpclisten=localhost:10009" \
        --tlsextradomain="$LNDHOST" \
        --debuglevel="$DEBUG" \
        "$@"
elif [ "$BACKEND" == "neutrino" ]; then
    # Split the comma-separated list of Neutrino nodes into separate --neutrino.connect flags
    NEUTRINO_CONNECT_FLAGS=()
    IFS=',' read -ra ADDR <<< "$NEUTRINO_CONNECT"
    for NODE in "${ADDR[@]}"; do
        NEUTRINO_CONNECT_FLAGS+=(--neutrino.connect="$NODE")
    done

    exec lnd \
        --noseedbackup \
        "--$CHAIN.active" \
        "--$CHAIN.$NETWORK" \
        "--$CHAIN.node=neutrino" \
        "${NEUTRINO_CONNECT_FLAGS[@]}" \
        "--fee.url=$FEE_URL" \
        "--rpclisten=$HOSTNAME:10009" \
        "--rpclisten=localhost:10009" \
        --tlsextradomain="$LNDHOST" \
        --debuglevel="$DEBUG" \
        "$@"
else
    echo "Unknown backend: $BACKEND"
    exit 1
fi
