# Contributing to UBSI API

Thank you for your interest in contributing to UBSI API! Please review the guidelines below to maintain stability, security, and consistent code quality.

---

## 1. Development Setup

This project uses Python 3.12+ and `uv` for fast environment and dependency management.

```bash
# Clone the repository
git clone https://github.com/Curzyori/UBSI-API.git
cd UBSI-API

# Create virtual environment and install dependencies
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# Setup local environment configuration
cp .env.example .env
# Edit .env with your credentials if testing private endpoints
```

---

## 2. Testing Guidelines (TDD Mandatory)

- **Pure Parser Isolation**: Unit tests for HTML parsers must strictly test against offline snapshot fixtures in `tests/fixtures/`. Never make live network requests inside pytest suites.
- **Directory Structure of `tests/`**:
  ```text
  tests/
  ├── fixtures/                 # Offline snapshot HTML fixtures (sv2_*.html, el_*.html)
  ├── test_config.py            # Settings, env loading, and tiered TTLs
  ├── test_envelope.py          # Response envelope standardization (clean JSON)
  ├── test_cache.py             # Two-tier Redis cache (fresh + LGG) and mutex
  ├── test_limiter.py           # Sliding-window rate limiter (60 req/min)
  ├── test_main.py              # Base FastAPI app, /health, and middleware
  ├── test_studentv2_parser.py  # Pure parsers for schedule, grades, news, announcements
  ├── test_studentv2_router.py  # StudentV2 endpoint integration tests
  ├── test_elearning_parser.py  # Pure parsers for MyBest courses, captcha, presence, tasks
  ├── test_elearning_router.py  # Elearning endpoint integration tests
  ├── test_elibrary_parser.py   # Elibrary OPAC search & book detail parsers
  ├── test_elibrary_router.py   # Elibrary endpoint integration & retry tests
  ├── test_public_modules.py    # News (WP REST API), Repository, and EJournal parsers
  ├── test_public_routers.py    # Public endpoints integration tests
  └── test_integration.py       # End-to-end full pipeline integration test
  ```
- **Run the Test Suite**:
  ```bash
  .venv/bin/pytest -v
  ```
- All pull requests and changes must have 100% passing tests before submission.

---

## 3. Code Standards & Architecture

1. **Clean Minimalist JSON**: All endpoints must return standard responses via `app.envelope`:
   ```json
   {
     "success": true,
     "data": [...],
     "cached": false
   }
   ```
2. **Resilience & Fault Tolerance**:
   - Cache operations must fail gracefully if Redis is temporarily unreachable (safe cache miss and fail-open rate limiting).
   - Upstream network errors should fall back to Last-Known-Good (`lgg`) cached data when available.
3. **Anti-Ban Protections**:
   - Always reuse session cookies in client instances; never submit login credentials unnecessarily on every request.
   - Respect tiered cache TTLs and maintain the single-flight mutex on upstream requests.
4. **Data Sanitization**:
   - Pervasively sanitize strings (remove extraneous newlines and spaces).
   - Ensure clean typing (`int` for SKS/counts, `float` for grades, ISO-8601 strings for dates, `null` for absent values).

---

## 4. Git & Commit Message Discipline

We follow **Conventional Commits**:
- `feat(scope): ...` for new features or endpoints.
- `fix(scope): ...` for bug fixes.
- `refactor(scope): ...` for code refactoring without behavior changes.
- `test(scope): ...` for adding or updating tests.
- `docs(scope): ...` for documentation changes.

**Zero Secrets Rule**:
- Never stage or commit `.env`, session files, credentials, or personal tokens. Always verify `git status` and `git diff` before committing.

---

## 5. Submitting a Pull Request (PR)

1. Create a dedicated feature branch from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feat/your-feature-name
   ```
2. Make your targeted code changes and write corresponding unit tests.
3. Ensure all tests pass:
   ```bash
   .venv/bin/pytest -v
   ```
4. Commit your changes with Conventional Commits message:
   ```bash
   git add <modified-files>
   git commit -m "feat(scope): your descriptive change"
   ```
5. Push the branch and open a Pull Request:
   ```bash
   git push -u origin feat/your-feature-name
   gh pr create --base main --head feat/your-feature-name --title "feat: ..." --body "Summary of changes"
   ```
