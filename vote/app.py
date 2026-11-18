from flask import Flask, render_template, request, make_response
import redis
import json
import uuid

app = Flask(__name__)

# Connect to Redis using the Docker container name as the host
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/', methods=['POST', 'GET'])
def vote():
    # Assign a unique ID to the voter if they don't have one
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = str(uuid.uuid4())

    if request.method == 'POST':
        vote = request.form.get('vote')
        # Create the payload and push it to the Redis 'votes' list
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        redis_client.lpush('votes', data)
        
    resp = make_response(render_template('index.html'))
    resp.set_cookie('voter_id', voter_id)
    return resp

if __name__ == "__main__":
    # Listen on all network interfaces (0.0.0.0) so Docker can map the port
    app.run(host='0.0.0.0', port=5000)
