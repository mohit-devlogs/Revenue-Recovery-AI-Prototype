# Revenue-Recovery-AI-Prototype

An AI Revenue Recovery agent prototype built for the Razorpay Buildathon 2026.

The system detects payment provider degradation, identifies revenue at risk, determines bounded recovery actions, executes recovery decisions, and maintains an audit trail of every intervention.

It supports both:

- **Simulation Mode** for demonstrating provider degradation and recovery
- **Razorpay Test Mode** for ingesting real payment data through the Razorpay API

## Architecture

```text
Frontend (HTML/CSS/JS)
        |
        | HTTP
        v
FastAPI Backend
        |
        +----------------------+
        |                      |
        v                      v
Simulation Engine       Razorpay Test API
        |                      |
        +----------+-----------+
                   |
                   v
          Revenue Detection
                   |
                   v
          Recovery Decision
                   |
                   v
       Bounded Recovery Execution
                   |
                   v
              Audit Trail
                   |
                   v
             JSON Response
                   |
                   v
             Frontend Dashboard
```

## How It Works

1. **Detect degradation**

   The system compares payment failure rates across providers and identifies significant degradation.

2. **Identify revenue at risk**

   It calculates the failed payment value during the degraded period and estimates the recoverable portion.

3. **Determine recovery action**

   Recoverable failures are classified into bounded actions:

   - Payment timeout → **Retry**
   - Provider error → **Route to alternative provider**
   - Non-recoverable failures → **No action**

4. **Execute recovery**

   The prototype simulates the outcome of each recommended recovery action using predefined success probabilities.

5. **Escalate failures**

   Recovery attempts that fail are escalated rather than retried indefinitely.

6. **Maintain an audit trail**

   Every recovery recommendation records the payment, provider, action, result, and amount involved.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **Payment Integration:** Razorpay Test Mode API
- **Data & Analysis:** Python
- **API Server:** Uvicorn

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/mohit-devlogs/Revenue-Recovery-AI-Prototype.git
cd Revenue-Recovery-AI-Prototype
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure Razorpay

Create a `.env` file inside the `backend` directory:

```text
backend/.env
```

Add your Razorpay Test Mode credentials:

```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

**Never commit your `.env` file or expose your API credentials publicly.**

### 4. Start the backend

From the project root:

```bash
python -m uvicorn backend.app.api:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### 5. Start the frontend

Open another terminal:

```bash
cd frontend
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500
```

## API Endpoints

### `GET /analyze`

Runs the simulated revenue recovery analysis.

It:

- Generates payment events
- Detects provider degradation
- Calculates revenue at risk
- Determines recovery recommendations
- Simulates recovery execution
- Generates an audit trail

### `GET /analyze/razorpay`

Fetches eligible payment data from Razorpay Test Mode and runs it through the revenue recovery analysis pipeline.

### `GET /razorpay/payments`

Fetches payment data from the Razorpay Test Mode API.

## Recovery Policy

The prototype uses bounded recovery rules to avoid uncontrolled retry behavior.

| Failure Cause | Action |
|---|---|
| Payment Timeout | Retry |
| Provider Error | Route to Alternative Provider |
| Bank Declined | No Action |
| Unknown Failure | No Action |

Recovery attempts that fail are escalated instead of being retried indefinitely.

## Demo Metrics

In Simulation Mode, the system demonstrates:

- Provider failure-rate degradation
- Failed revenue during the degraded period
- Estimated recoverable revenue
- Recovery recommendations
- Retry and rerouting decisions
- Successful and failed recovery attempts
- Escalated recoveries
- Complete recovery audit trail

The displayed recovery outcomes are simulated to demonstrate the decision and execution workflow.

## Razorpay Integration

The prototype integrates with the **Razorpay Test Mode API** to ingest payment data.

The integration:

1. Fetches payment records from Razorpay
2. Normalizes Razorpay payment data
3. Converts payments into the internal payment-event model
4. Runs the revenue-risk detection pipeline
5. Displays the resulting analysis in the dashboard

The current prototype uses real Razorpay Test Mode data for ingestion. Recovery execution itself is simulated and does not claim to perform real payment retries or provider rerouting through Razorpay.

## Project Structure

```text
Revenue-Recovery-AI-Prototype/
│
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   ├── generator.py
│   │   │   └── simulation.py
│   │   │
│   │   ├── models/
│   │   │   └── payment.py
│   │   │
│   │   ├── api.py
│   │   ├── detector.py
│   │   └── razorpay_client.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   └── index.html
│
├── .gitignore
└── README.md
```

## Key Design Principles

### Provider Agnostic

The detection and recovery pipeline operates on the internal payment-event model rather than being tightly coupled to a single provider.

### Bounded Recovery

The system only acts on failure types classified as recoverable and avoids unlimited retries.

### Explainable Decisions

Every recovery recommendation is based on an explicit failure cause and recovery policy.

### Auditability

Each recovery action records the payment, provider, action, result, and amount involved.

### Safe Integration

Razorpay credentials are stored locally through environment variables and excluded from version control.

## Status

**Prototype / Buildathon Submission**

The project demonstrates an end-to-end revenue recovery workflow:

**Detect → Quantify → Decide → Recover → Escalate → Audit**
