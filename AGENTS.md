# AGENTS.md — Codex Memory for Interceptr

This file provides guidance to OpenAI Codex when working in this repository.
For full project context, architecture decisions, and conventions, read CLAUDE.md.

## Critical rules for this codebase
- Python 3.12, FastAPI, SQLAlchemy sync (never async)
- All imports absolute (from app.models.audit_log import ...)
- Every new file needs a one-line comment as first line in English
- Never modify config.py or database.py without explicit instruction
- Tests use SQLite in-memory, never PostgreSQL directly
- Run pytest tests/ -v after every change to verify nothing broke
- policy.yaml is gitignored — policy.example.yaml is the reference

## Read before starting
Read CLAUDE.md for the complete project context including stack, architecture,
completed files, API endpoints, data models, and week-by-week status.