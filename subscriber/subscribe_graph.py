import grpc
import os
import lightning_pb2 as ln
import lightning_pb2_grpc as lnrpc
import mysql.connector
from mysql.connector import Error
import base64
import time
from google.protobuf.json_format import MessageToJson



'''
SELECT
    (SELECT COUNT(DISTINCT chan_id) FROM channel_updates)       AS UniqChannels,
    (SELECT COUNT(DISTINCT identity_key) FROM node_updates)     AS UniqNodes,
    
    
    (SELECT COUNT(*) FROM channel_updates)                      AS ChannelUpdates,
    (SELECT COUNT(*) FROM node_updates)                         AS NodeUpdates
'''





def get_macaroon():
    with open(os.path.expanduser('/root/.lnd/data/chain/bitcoin/mainnet/admin.macaroon'), 'rb') as f:
        macaroon_bytes = f.read()
    return grpc.metadata_call_credentials(
        lambda context, callback: callback([('macaroon', macaroon_bytes.hex())], None))





def connect_to_db():
    retries = 5
    for attempt in range(retries):
        try:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                database='lnd_data'
            )
            if connection.is_connected():
                print("Successfully connected to the database")
                return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            print(f"Retrying in 1 second ({attempt+1}/{retries})...")
            time.sleep(1)
    return None




def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_updates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chan_id BIGINT,
        chan_point TEXT,
        capacity BIGINT,
        time_lock_delta INT,
        min_htlc BIGINT,
        fee_base_msat BIGINT,
        fee_rate_milli_msat BIGINT,
        max_htlc_msat BIGINT,
        disabled BOOLEAN,
        advertising_node VARCHAR(66),
        connecting_node VARCHAR(66)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS node_updates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        identity_key VARCHAR(66),
        alias VARCHAR(32),
        color VARCHAR(7),
        features TEXT,
        addresses TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_edge_updates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chan_id BIGINT,
        chan_point TEXT,
        capacity BIGINT,
        routing_policy_1 TEXT,
        routing_policy_2 TEXT,
        advertising_node VARCHAR(66),
        connecting_node VARCHAR(66)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS closed_channels (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chan_id BIGINT,
        chan_point TEXT,
        capacity BIGINT,
        closed_height INT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_announcements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chan_id BIGINT,
        node1_pub VARCHAR(66),
        node2_pub VARCHAR(66),
        bitcoin_txid VARCHAR(64),
        output_index INT,
        node1_signature TEXT,
        node2_signature TEXT,
        timestamp BIGINT
    )
    """)





def insert_channel_update(cursor, update):
    query = """
    INSERT INTO channel_updates (
        chan_id, chan_point, capacity, time_lock_delta, min_htlc, fee_base_msat,
        fee_rate_milli_msat, max_htlc_msat, disabled, advertising_node, connecting_node
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        update.chan_id,
        str(update.chan_point),
        update.capacity,
        update.routing_policy.time_lock_delta if update.HasField('routing_policy') else None,
        update.routing_policy.min_htlc if update.HasField('routing_policy') else None,
        update.routing_policy.fee_base_msat if update.HasField('routing_policy') else None,
        update.routing_policy.fee_rate_milli_msat if update.HasField('routing_policy') else None,
        update.routing_policy.max_htlc_msat if update.HasField('routing_policy') else None,
        update.routing_policy.disabled if update.HasField('routing_policy') else None,
        update.advertising_node,
        update.connecting_node
    )
    cursor.execute(query, values)





def insert_node_update(cursor, update):
    query = """
    INSERT INTO node_updates (
        identity_key, alias, color, features, addresses
    ) VALUES (%s, %s, %s, %s, %s)
    """
    features = ', '.join([f"{feature.name}: {feature.is_known}" for feature in update.features.values()])
    addresses = ', '.join(update.addresses)
    values = (
        update.identity_key,
        update.alias,
        update.color,
        features,
        addresses
    )
    cursor.execute(query, values)





def insert_channel_edge_update(cursor, update):
    query = """
    INSERT INTO channel_edge_updates (
        chan_id, chan_point, capacity, routing_policy_1, routing_policy_2,
        advertising_node, connecting_node
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        update.chan_id,
        str(update.chan_point),
        update.capacity,
        str(update.routing_policy_1) if update.HasField('routing_policy_1') else None,
        str(update.routing_policy_2) if update.HasField('routing_policy_2') else None,
        update.advertising_node,
        update.connecting_node
    )
    cursor.execute(query, values)





def insert_closed_channel(cursor, update):
    query = """
    INSERT INTO closed_channels (
        chan_id, chan_point, capacity, closed_height
    ) VALUES (%s, %s, %s, %s)
    """
    values = (
        update.chan_id,
        str(update.chan_point),
        update.capacity,
        update.closed_height
    )
    cursor.execute(query, values)



def insert_channel_announcement(cursor, announcement):
    query = """
    INSERT INTO channel_announcements (
        chan_id, node1_pub, node2_pub, bitcoin_txid, output_index, node1_signature, node2_signature, timestamp
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        announcement.chan_id,
        announcement.node1_pub,
        announcement.node2_pub,
        announcement.bitcoin_txid,
        announcement.output_index,
        announcement.node1_signature.hex(),
        announcement.node2_signature.hex(),
        announcement.timestamp
    )
    cursor.execute(query, values)



def write_update_to_file(update, filename='updates.log'):
    timestamp = int(time.time())
    update_json = MessageToJson(update)
    update_base64 = base64.b64encode(update_json.encode('utf-8')).decode('utf-8')
    line_to_write = f"{timestamp}:{update_base64}\n"
    with open(filename, 'a') as f:
        f.write(line_to_write)



def main():
    while True:
        try:

            # Connect to database
            db_connection = connect_to_db()
            if db_connection is None:
                print("Failed to connect to the database. Exiting...")
                return
            cursor = db_connection.cursor()
            create_tables(cursor)

            # Read LND tls cert
            print("Loading TLS certificate...")
            with open('/root/.lnd/tls.cert', 'rb') as f:
                tls_cert = f.read()


            creds = grpc.ssl_channel_credentials(root_certificates=tls_cert)
            macaroon_creds = get_macaroon()
            composite_creds = grpc.composite_channel_credentials(creds, macaroon_creds)

            print("Creating gRPC secure channel...")
            channel = grpc.secure_channel(f'{os.getenv('LND_HOST')}:10009', composite_creds)
            print("Channel created. Creating stub...")
            stub = lnrpc.LightningStub(channel)
            print("Stub created. Subscribing to channel graph...")

            
            for update in stub.SubscribeChannelGraph(ln.GraphTopologySubscription()):
                try:
                    print("Received update...")
                    write_update_to_file(update)
                    print(MessageToJson(update))


                    # Handle Channel Updates
                    for channel_update in update.channel_updates:
                        try:
                            insert_channel_update(cursor, channel_update)
                        except Exception as e:
                            print(f"Error processing channel_update: {str(e)}")


                    # Handle Node Updates
                    for node_update in update.node_updates:
                        try:
                            print(f"Node update addresses attribute: {node_update.addresses}")
                            insert_node_update(cursor, node_update)
                        except Exception as e:
                            print(f"Error processing node_update: {str(e)}")


                    # Handle Channel Edge Updates
                    if hasattr(update, 'channel_edge_updates') and len(update.channel_edge_updates) > 0:
                        for edge_update in update.channel_edge_updates:
                            try:
                                insert_channel_edge_update(cursor, edge_update)
                            except Exception as e:
                                print(f"Error processing channel_edge_update: {str(e)}")


                    # Handle Closed Channel Updates
                    for closed_channel in update.closed_chans:
                        try:
                            insert_closed_channel(cursor, closed_channel)
                        except Exception as e:
                            print(f"Error processing closed_channel: {str(e)}")



                    # Handle Channel Announcements
                    if hasattr(update, 'channel_announcements') and len(update.channel_announcements) > 0:
                        for announcement in update.channel_announcements:
                            try:
                                insert_channel_announcement(cursor, announcement)
                            except Exception as e:
                                print(f"Error processing channel_announcement: {str(e)}")





                    db_connection.commit()



                except Exception as update_exception:
                    print(f"Error processing update: {str(update_exception)}")
        except grpc.RpcError as e:
            print(f"gRPC error: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
        finally:
            if db_connection and db_connection.is_connected():
                cursor.close()
                db_connection.close()
                print("MySQL connection is closed")
    sleep(0.2)





if __name__ == "__main__":
    main()

