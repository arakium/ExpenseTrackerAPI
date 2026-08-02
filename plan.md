# Expense Tracker API plan

## Problem
The repository currently has only the data/config layer: PostgreSQL connection config, table bootstrap code, and dataclass models. There is no API server, auth flow, expense endpoints, filtering logic, or tests yet.

## Proposed approach
Build the backend in the same Python/PostgreSQL stack already started here, using the Python standard library HTTP server as the API layer. Add JWT auth, user-scoped expense CRUD, and date-based filtering around the existing `users`, `categories`, and `expenses` tables.

## Layer interaction
The request flow should be `HTTP layer -> validation/auth -> service layer -> repository layer -> database`.

- **HTTP layer** parses requests, query params, and JSON, then returns status codes and JSON responses.
- **Validation/auth** checks required fields and verifies JWTs before business logic runs.
- **Service layer** enforces rules like ownership, allowed categories, JWT creation, password hashing, and date-range logic.
- **Repository layer** contains only SQL/database access.
- **Models** are shared data shapes passed between layers.

Typical request flow:
`POST /expenses` -> parse JSON -> validate -> verify JWT -> apply service rules -> save via repository -> return response

`GET /expenses?filter=month` -> read auth + query params -> translate filter to dates -> query repository -> return list

## Suggested folder structure
```text
ExpenseTracker/
  config/
    config.py
    database.ini
    settings.py
  database/
    database.py
    models.py
    repositories/
      user_repository.py
      expense_repository.py
      category_repository.py
  services/
    auth_service.py
    expense_service.py
  api/
    server.py
    router.py
    handlers/
      auth_handler.py
      expense_handler.py
    middleware/
      auth.py
    responses.py
  utils/
    jwt.py
    password.py
    validators.py
    dates.py
  tests/
    test_auth.py
    test_expenses.py
    test_filters.py
  main.py
```

## Todo list
1. Create the bare-Python API entrypoint and project structure.
2. Add user signup/login with password hashing and JWT issue/validation.
3. Add protected expense CRUD endpoints scoped to the authenticated user.
4. Add expense list filters for week, month, 3 months, and custom ranges.
5. Seed/validate the allowed categories and tighten request/response validation.
6. Add tests for auth, authorization, CRUD, and filtering behavior.

## Notes
- Keep secrets out of source and move database/JWT settings to environment variables.
- Reuse the existing schema where possible; only adjust it if a missing constraint blocks a feature.
- Make all expense reads and writes user-owned by default so one user cannot access another user’s data.
