
# Setup Instructions
### Prerequisites

## Kali linux users

- **WSL (Ubuntu)**: Install via Windows Features or Microsoft Store
- **Docker**: For running RabbitMQ
- **Python 3.10+**: With pip and venv
- **Git**: For cloning and version control

## Window users


- **WSL (Ubuntu)**: Required for running Celery and Supervisor  
  Install from Microsoft Store or enable via Windows Features:
  - Open PowerShell (as Administrator):
    ```powershell
    wsl --install
    ```
  - Restart your computer if needed
  - Open Ubuntu and finish setup

- **Docker Desktop**: Required for running RabbitMQ  
  - Download and install from: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
  - Enable **WSL 2 backend** and ensure Docker is available in Ubuntu by running:
    ```bash
    docker --version
    ```

 - **Python 3.10+ (in WSL Ubuntu)**  
   Use Ubuntu terminal, not Windows command prompt:
   ```bash
   sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
    ```


### Step-by-Step Setup

#### Clone the Repository

```bash
git clone https://github.com/your-username/async-worker-prototype.git
cd async-worker-prototype

```

## installing Supervisor 
```bash 
sudo apt install supervisor
```


### Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Install Docker

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

```

Log out and back in to apply Docker group changes.

### Run RabbitMQ in Docker
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
docker ps
```

Access the management UI at http://localhost:15672
Username: guest, Password: guest

Configure Supervisor
Ensure supervisord.conf is in the project / directory.

Create log files:

```bash
touch src/supervisord.log src/celery.out.log src/celery.err.log
chmod -R 755 src
chown -R $USER:$USER src
```


## Running the Project

### Start Supervisor

```bash 
sudo supervisord -c src/supervisord.conf

sudo supervisorctl -c src/supervisord.conf status
```

Expected output: celery_worker RUNNING


### Send Test Messages

```
python src/sender.py
```

### Monitor logs
```
tail -f src/celery.out.log
tail -f src/celery.err.log
```

### Stop Supervisor

```
sudo supervisorctl -c src/supervisord.conf shutdown
```


Testing
Manual Testing: Use sender.py to send sample JSON messages and verify logs

Validation: Ensure the worker handles invalid payloads with retries

Concurrency: Test with concurrency=2 in supervisord.conf