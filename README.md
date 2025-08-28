# TelekDados

## IMPORTANT LEGAL NOTICE

**Recommendation:** Test only in channels/groups you control or where you have explicit permission. Example: your own channels or with the owner’s consent.

---

### Features:

* Support for videos, photos, audio, documents, and messages via Telegram API (Telethon).
* Authentication via a Telegram user account (no bot needed, just membership in the source channel/group).
* Copies comments from linked discussion groups if you are a member.
* Rate limiting to avoid Telegram bans.
* Redis-based communication for managing message/media queues.
* Metrics export to Grafana (auto dashboards) and interactive charts with Chart.js.
* Deployable via Docker or Kubernetes for scalable simulation.
* Optional: AWS S3 integration for backup storage.

The goal is to preserve important content that could be lost due to Telegram failures or malicious actions, always with ethical use.

---

## Requirements

* **Python 3.8+**
* Libraries: `telethon`, `requests`, `redis`, `grafana-api`, `boto3` (AWS), `tkinter`
  Install via:

  ```bash
  pip install telethon requests redis grafana-api boto3
  ```
* **Docker** and **Docker Compose** (for local testing)
* **Kubernetes** (e.g., Minikube or cloud cluster like EKS/GKE)
* **kubectl** for Kubernetes management
* **Redis**:

  ```bash
  docker run -d -p 6379:6379 redis
  ```
* **Grafana**:

  ```bash
  docker run -d -p 3000:3000 grafana/grafana
  ```
* **Telegram API ID and Hash**: Obtain from [my.telegram.org](https://my.telegram.org)

---

## How to Use

### Clone the repository:

```bash
git clone https://github.com/hygark/telekdados.git
```

### Obtain API credentials:

* Get API ID and Hash at [my.telegram.org](https://my.telegram.org).

### Prepare test environments:

* Create a test channel/group (e.g., `t.me/my_test`) with media (videos, photos, audio, documents, messages).
* Create an empty channel/group for backups (e.g., `t.me/my_backup`) and ensure your account has posting permissions (e.g., admin).

### Configure Grafana:

* Access `http://localhost:3000`
* Create an API key for integration.

---

### Local Testing (Docker)

* Configure `docker-compose.yml` with:

  * `API_ID`, `API_HASH`, `PHONE`, `SOURCE_CHANNEL`, `DEST_CHANNEL`
* Run:

  ```bash
  docker-compose up --build --scale worker=3
  ```
* Log in using the verification code sent to your number.
* View results in `output.json`, `chart.html`, or Grafana.

---

### Local Testing (GUI)

* Run:

  ```bash
  python gui.py
  ```
* Enter:

  * Source and destination channel/group links (e.g., `t.me/my_test` → `t.me/my_backup`)
  * API ID and Hash
  * Phone number
  * Grafana API key (optional)
* Log in with the verification code.
* Check results at `t.me/my_backup`, `chart.html`, and Grafana.

---

### Deploy with Kubernetes

* Install Minikube (`minikube start`) or use a cloud cluster (EKS/GKE).
* Configure `k8s/configmap.yaml` with:

  * `API_ID`, `API_HASH`, `PHONE`, `SOURCE_CHANNEL`, `DEST_CHANNEL`
* Apply configurations:

  ```bash
  kubectl apply -f k8s/configmap.yaml
  kubectl apply -f k8s/deployment.yaml
  kubectl apply -f k8s/service.yaml
  ```
* Log in using the verification code (may appear in terminal or require manual interaction).
* Access Grafana via:

  ```bash
  minikube service grafana-service
  ```
* Check results in `t.me/my_backup` and `chart.html`.

---

## Example Output

* JSON logs
* Interactive charts (`chart.html`)
* Grafana dashboards

---

## Code Structure

* **main.py** → Core logic, Telegram, Redis, Grafana integration
* **worker.py** → Processes queued messages/media
* **Dockerfile** → For containerization
* **docker-compose.yml** → Orchestrates workers, Redis, Grafana (local testing)
* **k8s/**

  * `configmap.yaml`: Environment configs
  * `deployment.yaml`: Deployments for GUI and workers
  * `service.yaml`: Services for Redis and Grafana
* **chart.html** → Interactive Chart.js visualization
* **README.md** → This file

---

## Limitations

* **only**: Works only with channels/groups you have access to (member or public).
* **Telegram API**: Subject to rate limits (respected by the tool).
* **Performance**: Limited by host machine. Kubernetes improves scalability.
* **Login**: Requires authentication with phone number on first run.
