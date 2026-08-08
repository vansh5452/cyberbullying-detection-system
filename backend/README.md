# CyberGuard AI API

**AI-Powered Cyberbullying Detection System — FastAPI Backend**

This is the backend service for the CyberGuard AI Class 12 AI Capstone
project. It wraps the project's original TF-IDF + Logistic Regression
model (`model.py`) and safety-guide content (`utils.py`) behind a
production-shaped REST API, so the Streamlit frontend no longer imports
the ML pipeline directly.

## 1. Project Overview

CyberGuard AI detects cyberbullying in text messages using a classic
NLP pipeline (TF-IDF vectorization + Logistic Regression), and pairs the
detector with student-facing safety tooling: a chat simulator, a social
feed simulator, a toxic-word highlighter, a "detox" rewriter, and an
Indian cyber-law / helpline reference guide.

## 2. Architecture

```
Frontend (Streamlit)
   |  HTTP (api_client.py)
   v
REST API (FastAPI, /api/v1/*)
   v
Service layer (prediction_service, model_service, analytics_service, safety_service)
   v
Existing ML Model (TF-IDF + Logistic Regression, loaded once at startup)
   v
SQLite / PostgreSQL (users, predictions, chat messages)
```

The model and vectorizer are loaded **once**, at application startup,
from `models/cyberbullying_model.pkl`, and kept in memory by
`ModelService`. No request re-loads the pickle file.

## 3. Features

- `POST /api/v1/predict` — TF-IDF + Logistic Regression prediction with
  confidence, matched toxic words, category, and severity.
- Lexicon-based fallback when the trained model file is unavailable.
- JWT authentication (register/login), with `user` and `admin` roles.
- Prediction history, paginated, isolated per user.
- Chat Simulator (`/simulator/message`) and simulated social feed
  (`/simulator/posts`).
- Safety Guide API: cyber laws, helplines, coping tips
  (`/safety/laws`, `/safety/helplines`, `/safety/tips`).
- Toxic-word highlighting + "detox" safe-rewrite (`/safety/detox`).
- Model status, model analytics (accuracy, confusion matrix,
  classification report, top toxic words), and an admin-only retrain
  endpoint.
- Dashboard statistics computed from real stored prediction rows —
  not session counters.
- Consistent `{success, data}` / `{success: false, error: {code, message}}`
  response envelope, structured logging, CORS, and configurable
  privacy controls.

## 4. Technology Stack

Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy, SQLite (dev) /
PostgreSQL-compatible (prod), JWT (python-jose), Passlib (bcrypt),
python-dotenv, pytest, scikit-learn, pandas.

## 5. Folder Structure

```
backend/
├── app/
│   ├── main.py
│   ├── api/v1/            # auth, predictions, analytics, safety, simulator, model, health
│   ├── core/               # config, security, logging, deps
│   ├── db/                 # database session, SQLAlchemy models
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # prediction_service, model_service, analytics_service, safety_service
│   └── utils/               # error/pagination helpers
├── models/cyberbullying_model.pkl
├── dataset.csv
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

## 6. Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 7. Environment Configuration

```bash
cp .env.example .env
# then edit .env — at minimum, change SECRET_KEY before deploying anywhere real
```

Key variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | `sqlite:///./cyberguard.db` for dev, a `postgresql://...` URL for production |
| `SECRET_KEY` | JWT signing key — must be changed in production |
| `MODEL_PATH` | Path to the trained pickle file |
| `DATASET_PATH` | Path to `dataset.csv`, used by `/model/retrain` |
| `ALLOWED_ORIGINS` | Comma-separated list of frontend origins allowed by CORS |
| `STORE_PREDICTION_TEXT` | `true`/`false` — if `false`, only prediction metadata is stored, not the raw submitted text |

## 8. How to Run Locally

```bash
uvicorn app.main:app --reload --port 8000
```

## 9. API Documentation

Once running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

### Full endpoint list

| Method | URL | Purpose | Auth |
|---|---|---|---|
| GET | `/api/v1/health` | Liveness check | none |
| POST | `/api/v1/auth/register` | Create an account | none |
| POST | `/api/v1/auth/login` | Get a JWT | none |
| GET | `/api/v1/auth/me` | Current user profile | user |
| POST | `/api/v1/predict` | Analyze a message | optional (works anonymously) |
| GET | `/api/v1/predictions` | Paginated prediction history | user |
| GET | `/api/v1/predictions/{id}` | Single prediction (own only) | user |
| GET | `/api/v1/analytics/dashboard` | Dashboard stats | none |
| GET | `/api/v1/analytics/model` | Accuracy / confusion matrix / report | none |
| GET | `/api/v1/analytics/top-toxic-words` | Top LR coefficients | none |
| GET | `/api/v1/model/status` | Model loaded? accuracy? fallback? | none |
| POST | `/api/v1/model/retrain` | Retrain from dataset.csv | **admin** |
| POST | `/api/v1/simulator/message` | Chat Simulator moderation | optional |
| GET | `/api/v1/simulator/posts` | Simulated social feed | none |
| GET | `/api/v1/safety/tips` | Coping strategies | none |
| GET | `/api/v1/safety/helplines` | Emergency helplines (India) | none |
| GET | `/api/v1/safety/laws` | Cyber law reference (educational only) | none |
| POST | `/api/v1/safety/detox` | Safe-rewrite a toxic message | none |

### Example calls

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "You are so stupid and ugly"}'

curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"SuperSecret123"}'
```

To make a user an **admin** (required for `/model/retrain`), register
normally, then update that row's `role` column to `admin` directly in
the database (there's no self-service "become admin" endpoint, by
design).

## 10. Connecting the Streamlit Frontend

The frontend (`../frontend/app.py` + `api_client.py`) no longer imports
`model.py` or `utils.py`. Set:

```bash
export BACKEND_URL=http://localhost:8000
streamlit run app.py
```

## 11. Running Tests

```bash
pytest -v
```

Tests use a separate SQLite file (`test_cyberguard.db`), created and
torn down automatically, so they never touch your dev database. They
exercise the real trained model bundled in `models/cyberbullying_model.pkl`.

> **Note on this delivery:** this sandbox environment has no outbound
> network access, so the test suite and `pip install` could not be
> executed here. Every file was syntax-checked (`python -m py_compile`),
> but please run `pip install -r requirements.txt && pytest -v` yourself
> to confirm runtime behavior before relying on it.

## 12. Retraining the Model

```bash
curl -X POST http://localhost:8000/api/v1/model/retrain \
  -H "Authorization: Bearer <admin JWT>"
```

**⚠️ Known issue with the uploaded `dataset.csv`:** the file you
provided is not actually a CSV — it contains Python source
(`import pandas as pd ... new_entries = [...]`), i.e. a script that
*appends* rows to a dataset, not the dataset itself. `/model/retrain`
expects a real CSV with `text` and `label` columns (matching what the
original `train_cyberbullying_model()` expected). Retraining will fail
with `INVALID_DATASET` until a proper CSV is supplied at `DATASET_PATH`.
The bundled `cyberbullying_model.pkl` (your existing trained model,
93.5% accuracy) is unaffected and works today.

## 13. Docker

```bash
docker build -t cyberguard-api .
docker run -p 8000:8000 --env-file .env cyberguard-api
```

## 14. Deployment (beginner-friendly)

1. Push this `backend/` folder to a Git repo.
2. On a platform like Render, Railway, or Fly.io: create a new "Web
   Service" from the repo, using the included `Dockerfile`.
3. Set environment variables in the platform's dashboard (same keys as
   `.env.example`) — especially `SECRET_KEY`, `DATABASE_URL` (point it
   at a managed Postgres instance for production), and `ALLOWED_ORIGINS`
   (your deployed Streamlit URL).
4. The container listens on `0.0.0.0:$PORT` — most platforms inject
   `$PORT` automatically; the `CMD` in the Dockerfile already reads it.
5. Once deployed, set `BACKEND_URL=https://your-backend-domain.com` in
   the frontend's environment before running `streamlit run app.py`.

## 15. Security Notes

- Passwords are hashed with bcrypt (via Passlib) — never stored or
  logged in plaintext.
- JWTs are never logged.
- All list/detail prediction endpoints check `user_id` ownership before
  returning data.
- `/model/retrain` is restricted to the `admin` role.
- Unhandled exceptions return a generic `INTERNAL_ERROR` message —
  stack traces are never sent to clients (they're only written to
  server-side logs).
- CORS origins are explicit (`ALLOWED_ORIGINS`), not `*`, once you're
  running authenticated endpoints in production.

## 16. Privacy Notes

- `STORE_PREDICTION_TEXT` controls whether raw submitted text is
  persisted. When set to `false`, only prediction metadata (label,
  confidence, category, severity, text length) is stored — the actual
  message content is discarded after the prediction is made.
- Predictions can be made anonymously (no `Authorization` header) —
  in that case `user_id` is stored as `NULL` and the record is not
  retrievable through the history endpoints.
- The `/safety/laws` endpoint explicitly returns a disclaimer marking
  its content as educational reference material, not personalized
  legal advice.
- Confidence scores are explicitly labeled as statistical estimates,
  not guarantees, in every prediction response (`disclaimer` field).
