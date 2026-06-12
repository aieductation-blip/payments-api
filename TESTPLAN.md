# TESTPLAN.md

## 1. Test Strategy
- **Layered testing approach**: Focus on unit testing core business logic and models, integration testing API endpoints with the database and external Stripe API, and end-to-end testing user transaction flows.
- **Mock external dependencies**: Use `pytest-mock` or `unittest.mock` to mock Stripe API responses and database interactions where appropriate.
- **Test environment**: Isolate tests using a separate Postgres test database. Use environment variables for all secrets (Stripe API keys, DB credentials).
- **Coverage goals**: Achieve 80% coverage on service layer functions and critical route handlers, ensuring core transaction paths are tested thoroughly.
- **Continuous integration**: Integrate with CI pipeline to run all tests on each push, enforce passing before merge.

## 2. Test Levels

### Unit Tests
- Test `models.py`:
  - `Transaction` model creation and validation
- Test `services.py`:
  - `create_transaction()` logic with mock data
  - `refund_transaction()` processes with mock Stripe responses
- Test utility functions like `calculate_total_amount()`

### Integration Tests
- Test `/transactions/create` API endpoint (POST):
  - Submit valid transaction request, expect 201 Created with correct response
  - Submit invalid request with missing fields, expect 422 Unprocessable Entity
- Test `/transactions/{transaction_id}` GET endpoint:
  - Retrieve existing transaction, expect 200 with correct data
  - Request non-existent transaction, expect 404
- Test Stripe charge creation via mocked Stripe API:
  - Successful charge creation, verify database recorded transaction
  - Stripe API failure, verify proper error handling and response

### E2E Tests
- User payment flow:
  - POST `/transactions/create` with valid payment details, verify atomic success: payment through Stripe, transaction record created, confirmation response.
  - Refund flow:
    - POST `/transactions/{id}/refund`, ensures refund is initiated in Stripe, record updated.
  - Handle failed payment:
    - Simulate Stripe decline, verify proper error message returned and no transaction recorded.

## 3. Test Cases Table

| ID   | Test Case                                        | Type            | Priority | Expected Result                                                   |
|-------|--------------------------------------------------|-----------------|----------|-------------------------------------------------------------------|
| TC001 | Create transaction with valid amount and card   | Unit/API       | High     | Stripe charge succeeded, 201 response, transaction stored        |
| TC002 | Fetch existing transaction by ID                | API            | High     | 200 OK with correct transaction details                           |
| TC003 | Create transaction with missing amount          | API            | High     | 422 Unprocessable Entity, validation error                        |
| TC004 | Refund a validated transaction                  | API            | Medium   | Refund initiated via Stripe, status updated in DB               |
| TC005 | Simulate Stripe decline during charge           | API            | High     | 402 Payment Required with error message                         |
| TC006 | Verify transaction model validation              | Unit           | Medium   | Model raises validation error for missing required fields      |
| TC007 | End-to-end payment flow with successful transaction | E2E       | High     | Payment processed, transaction recorded, confirmation returned  |
| TC008 | End-to-end refund flow for existing transaction | E2E         | Medium   | Refund processed, status updated, confirmation returned         |
| TC009 | Fetch non-existent transaction ID               | API            | Medium   | 404 Not Found                                                    |
| TC010 | Test database connection reliability             | Integration    | Low      | Database responds correctly, can query transactions             |

## 4. Edge Cases
- Transaction amount = 0 (zero)
- Transaction amount exceeds maximum allowed (e.g., API limit)
- Payment method token is invalid or malformed
- Attempt to refund a transaction that is already refunded
- Rapid consecutive transaction requests for the same payment details

## 5. Test Data Requirements
- Seeds of `transactions` with known IDs for retrieval tests
- Mock Stripe test card tokens (e.g., `tok_visa`, `tok_chargeDeclined`)
- Valid and invalid payment method tokens
- Sample transaction data with edge case parameters (zero amount, large amount)
- Environment variables:
  - `STRIPE_SECRET_KEY`
  - `DATABASE_URL` for test database
- Fixtures for users, payment methods, and transactions as necessary

## 6. Tools & Setup
- **Testing Framework**: `pytest`
- **HTTP Client for API**: `httpx` or FastAPI’s built-in `TestClient`
- **Mocking**: `pytest-mock` or `unittest.mock`
- **Setup commands**:
  - Install dependencies:
    ```bash
    pip install pytest pytest-mock httpx
    ```
  - Run tests:
    ```bash
    make test
    ```
  - Run API locally:
    ```bash
    make run
    ```
- **Makefile snippets**:
  ```Makefile
  test:
      pytest --maxfail=1 --disable-warnings -q

  run:
      uvicorn app.main:app --reload
  ```
- **Environment setup**:
  - Use `.env.test` with test secrets
  - Load environment variables before running tests

---

**End of TESTPLAN.md**