from celery import Celery
from kombu import Exchange, Queue
import logging
import json
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery('tasks', broker='amqp://guest@localhost:5672//', backend='rpc://', include=['tasks'])

# Define exchanges and queues
snapshots_exchange = Exchange('snapshots', type='direct')
dead_letters_exchange = Exchange('dead_letters', type='direct')

snapshot_queue = Queue(
    'snapshot_queue',
    exchange=snapshots_exchange,
    routing_key='snapshot.process',
    queue_arguments={'x-message-ttl': 60000, 'x-dead-letter-exchange': 'dead_letters'}
)

# Declare queue on startup
with app.connection_for_write() as conn:
    snapshot_queue.bind(conn).declare()

# Configure Celery settings
app.conf.task_queues = (snapshot_queue,)
app.conf.task_default_queue = 'snapshot_queue'
app.conf.task_default_exchange = 'snapshots'
app.conf.task_default_routing_key = 'snapshot.process'
app.conf.task_create_missing_queues = False
app.conf.broker_connection_retry_on_startup = True
app.conf.accept_content = ['json']
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.task_track_started = True
app.conf.task_time_limit = 30  # Task timeout in seconds

# Global counter for processed tasks
task_counter = Counter()

@app.task(queue='snapshot_queue', bind=True, max_retries=3, default_retry_delay=10)
def process_snapshot(self, payload):
    """Process and validate incoming snapshot data."""
    try:
        # Validate payload
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        
        required_keys = {'agent_id', 'snapshot_data'}
        if not all(key in payload for key in required_keys):
            missing = required_keys - set(payload.keys())
            raise ValueError(f"Missing required keys: {missing}")

        snapshot_data = payload.get('snapshot_data', {})
        if not isinstance(snapshot_data, dict):
            raise ValueError("snapshot_data must be a dictionary")

        # Extract and validate data
        agent_id = payload['agent_id']
        running_processes = snapshot_data.get('running_processes', [])
        if not isinstance(running_processes, list):
            raise ValueError("running_processes must be a list")

        # Log processed data
        process_count = len(running_processes)
        logger.info(f"Processed snapshot for agent_id: {agent_id}, Running processes: {process_count}")
        task_counter[agent_id] += 1
        logger.info(f"Total tasks processed for {agent_id}: {task_counter[agent_id]}")

        # Simulate additional processing
        return {"status": "success", "agent_id": agent_id, "process_count": process_count}

    except ValueError as e:
        logger.error(f"Validation error for payload {payload}: {str(e)}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Unexpected error processing payload {payload}: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=2 ** self.request.retries)