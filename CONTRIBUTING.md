# Contributing

Thanks for taking a look. This is a private, single-tenant personal automation API (one student account on your own localhost / VPS), so most contributions are campus parser fixes, new endpoint additions, or test coverage.

Local setup, configuration, and architectural design live in [README.md](README.md) and [docs/superpowers/specs/2026-09-25-ubsi-api-design.md](docs/superpowers/specs/2026-09-25-ubsi-api-design.md) — one place, so they cannot drift apart.

## Development setup

```bash
# Clone and setup environment (Python 3.12+)
git clone https://github.com/Curzyori/UBSI-API.git
cd UBSI-API

uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

## Pull requests

- One logical change per PR, conventional-commit title (`fix(elearning): …`, `feat(studentv2): …`).
- Say what you changed and why in the body; include the failing fixture or upstream HTML change you fixed when there is one.
- **TDD Mandatory**: Parser unit tests must test against offline snapshot fixtures in `tests/fixtures/`. Never make live network requests to campus servers inside pytest. All 46+ tests must pass (`.venv/bin/pytest -v`).
- **Zero Secrets Rule**: Never stage or commit `.env`, session cookies, credentials, or personal tokens. Always verify `git status` and `git diff` before pushing.
- Upstream changes: mention which campus service was tested (`studentv2`, `elearning`, `elibrary`, `news`, `repository`, `ejournal`) and provide anonymized snapshot proof if layout changed.
- **Student Contributor Attribution**: If you are a UBSI student, you are encouraged to mention your student metadata (Full Name, NIM, Faculty, Study Program, Class, Semester) in the PR body so your contribution is recognized in the `README.md` Contributors table.

## Tests structure

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

## Security

Please do not open a public issue for vulnerabilities or credential leaks — see [SECURITY.md](SECURITY.md).

## Intellectual property & DMCA

All university trademarks, materials, and portal assets belong to Universitas Bina Sarana Informatika — see [DMCA.md](DMCA.md).

## License

By contributing you agree that your work is licensed under the [MIT License](LICENSE).
