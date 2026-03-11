# Contributing to Interceptr

Thanks for your interest in contributing. Here's everything you need to get started.

## Setting up the development environment

**Prerequisites:** Python 3.12+, Docker, pipx

```bash
# Clone the repo
git clone https://github.com/trykelink/interceptr
cd interceptr

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL

# Start the database
docker compose up db -d

# Run the server
uvicorn main:app --reload --port 8000

# Verify it's running
curl http://localhost:8000/health
```

## Running the tests

Tests use an in-memory SQLite database — no running server or Docker needed.

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_policy_engine.py -v
```

As of v0.1.0, all 192 tests should pass.

## Reporting bugs

Check [existing issues](https://github.com/trykelink/interceptr/issues) before opening a new one.

When filing a bug report, include:
- Interceptr version (`interceptr --version`)
- OS and Docker version
- Steps to reproduce
- Expected vs. actual behavior
- Relevant logs (`interceptr logs` or `docker compose logs interceptr`)

**Security vulnerabilities:** do NOT open a public issue. Follow the process in [SECURITY.md](SECURITY.md) instead.
