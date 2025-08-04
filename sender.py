from tasks import process_snapshot
import time
import random

# Sample payloads
sample_payloads = [
    {
        "agent_id": "host-789",
        "snapshot_data": {
            "running_processes": ["nginx", "redis", "python"],
            "timestamp": 1678901234
        }
    },
    {
        "agent_id": "host-123",
        "snapshot_data": {
            "running_processes": ["apache", "mysql"],
            "timestamp": 1678901235
        }
    },
    {
        "agent_id": "host-456",  # Invalid payload for testing
        "snapshot_data": "invalid"
    }
]

def send_messages():
    """Send multiple sample messages to the snapshot_queue."""
    for payload in sample_payloads:
        try:
            process_snapshot.apply_async(args=[payload])
            print(f"Sent message for agent_id: {payload.get('agent_id', 'unknown')}")
        except Exception as e:
            print(f"Failed to send message {payload}: {str(e)}")
        time.sleep(random.uniform(0.1, 1.0))  # Simulate delay between messages

if __name__ == "__main__":
    send_messages()