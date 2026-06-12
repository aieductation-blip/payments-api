# ARCHITECTURE.md

# Project Overview
`payments-api` is a high-performance, maintainable web API written in Python using FastAPI. It facilitates payment processing through integration with Stripe and stores transaction data in a PostgreSQL database. The system adheres to layered architecture principles, separating routes, business logic, and data models. It employs environment variables for configuration and secrets management, and includes pytest-based testing scaffolds.

---

## Tech Stack & Rationale
- **FastAPI (Python):** Selected over Flask due to its native async support, enabling high concurrency for payment transactions. Its automatic OpenAPI documentation aids API management.
- **Stripe:** Chosen as a robust, PCI-compliant payment provider with comprehensive SDKs and webhooks, simplifying payment processing.
- **PostgreSQL:** Used for reliable, ACID-compliant transactional data storage. Its JSONB support and scalability suit payment data management.

---

## System Components

### 1. **API Routes Layer**
Handles HTTP requests, parses input, passes data to services, and returns responses with appropriate HTTP status and JSON payloads.

**Key endpoints:**
- `POST /charges`: Initiates a new payment (payload includes amount, currency, source, description)
- `GET /charges/{charge_id}`: Retrieves details of a specific charge
- `POST /webhooks/stripe`: Receives Stripe webhook events (e.g., payment succeeded, failed)

**Technology:**
- **FastAPI** handles routing with async endpoints for scalable request processing.
- Example route:  
  `POST /charges` with JSON body:
  ```json
  {
    "amount": 2000,
    "currency": "usd",
    "source": "tok_visa",
    "description": "Test charge"
  }
  ```

### 2. **Services Layer**
Encapsulates core business logic, including payment creation, webhook event processing, and database interactions.

**Example:**
- `create_charge()` calls Stripe's `charges.create()` API, then records transaction in the Postgres database.
- `process_stripe_event()` handles webhook payloads, verifies signatures, updates transaction status.

**Rationale for FastAPI-based async services:**  
Allows concurrent API call handling during payment processing, minimizing latency.

### 3. **Models Layer**
Defines Pydantic schemas for request validation and ORM models for database representation.

- **Pydantic schemas:**  
  `ChargeCreate`, `ChargeResponse`, `StripeWebhookEvent`
- **SQLAlchemy models (PostgreSQL):**  
  `charges` table:
  ```
  CREATE TABLE charges (
      id SERIAL PRIMARY KEY,
      stripe_charge_id VARCHAR(50),
      amount INTEGER,
      currency VARCHAR(8),
      status VARCHAR(20),
      description TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

---

## Data Flow & Interaction

Client → FastAPI `/charges` (POST)
  - Sends: {"amount": 2000, "currency": "usd", "source": "tok_visa", "description": "Test charge"}
  - Method: POST /charges

FastAPI Controller (`create_charge`) → Services (`create_charge`)
  - Calls Stripe API:
    POST https://api.stripe.com/v1/charges
    Headers: Authorization Bearer <STRIPE_SECRET_KEY>
    Body: amount=2000, currency=usd, source=tok_visa, description=Test charge

Stripe Response → Services
  - Receives charge ID, status, etc.
  - Stores record in `charges` Postgres table:
    INSERT INTO charges (stripe_charge_id, amount, currency, status, description)
    VALUES ('ch_1Example...', 2000, 'usd', 'succeeded', 'Test charge');

Service Response → Controller → Client
  - Responds with ChargeResponse schema containing transaction details and status.

Stripe Webhook (`/webhooks/stripe`) → FastAPI Endpoint
  - Receives POST payload from Stripe
  - Verifies signature with endpoint secret
  - Processes event (e.g., `charge.succeeded`)
  - Updates transaction status in `charges` table accordingly

Client retrieves charge status:
GET `/charges/{charge_id}`
  - FastAPI fetches from Postgres:
    SELECT * FROM charges WHERE id = {charge_id}
  - Responds with `ChargeResponse`.


---

## ASCII Architecture Diagram

+------------------+        HTTP        +-------------------+
|   Payment Client | -----------------> | FastAPI Routes     |
+------------------+                   +-------------------+
                                               |
                                               | Calls
                                               v
                                     +---------------------------+
                                     | Services Layer            |
                                     | (Async with Stripe SDK)   |
                                     +---------------------------+
                                               |
                                   ______________|_______________
                                  |                                |
       +------------------> +---------------------+   +----------------------+
       | Stripe Webhook  | | PostgreSQL Database |   | Environment Variables |
       +------------------+ +---------------------+   +----------------------+

---

## Configuration & Secrets Management
- All sensitive data, especially `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`, are read from environment variables.
- `.env` files or Docker secrets are used in deployment environments.
- Example variable usage:
  - `export STRIPE_SECRET_KEY=sk_test_XXXX`
  - `export STRIPE_WEBHOOK_SECRET=whsec_XXXX`

---

## Additional Development & Testing Tools
- **Makefile**:
  - `make run`: Run the FastAPI server
  - `make test`: Execute pytest with coverage
  - `make lint`: Run flake8 or black checks
- **Pytest setup**:
  - Fixtures for test database setup
  - Mocks for external Stripe API calls

---

## Documentation & API Specification
- Auto-generated using FastAPI's integrated OpenAPI support
- Docstrings detail each route's purpose, parameters, and responses
- `README.md` includes setup instructions, environment variable configuration, and API usage examples.

---

*This document provides a comprehensive, concrete overview of the `payments-api` system architecture based on the specified stack and architectural rules.*