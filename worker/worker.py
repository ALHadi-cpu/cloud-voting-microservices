import redis
import psycopg2
import json
import time

# Connect to the Redis container
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Resilient connection to the PostgreSQL container
def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                host="db",
                dbname="votesdb",
                user="postgres",
                password="password"
            )
            print("Connected to PostgreSQL!")
            return conn
        except psycopg2.OperationalError:
            print("Waiting for PostgreSQL to start...")
            time.sleep(2)

conn = connect_db()
cursor = conn.cursor()

# Ensure our table exists before we start inserting data
cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id VARCHAR(255) PRIMARY KEY,
        vote VARCHAR(255) NOT NULL
    )
""")
conn.commit()

print("Worker ready! Blocking and waiting for votes in Redis...")

while True:
    try:
        # BRPOP blocks (waits) until an item is available in the queue
        _, data = redis_client.brpop('votes')
        payload = json.loads(data.decode('utf-8'))
        
        voter_id = payload['voter_id']
        vote = payload['vote']
        
        # Insert the vote, or update it if this user already voted (UPSERT)
        cursor.execute("""
            INSERT INTO votes (id, vote) VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET vote = EXCLUDED.vote
        """, (voter_id, vote))
        conn.commit()
        
        print(f"Processed vote for {vote} by {voter_id}")
        
    except Exception as e:
        print(f"Error processing vote: {e}")
        time.sleep(1)
