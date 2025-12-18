# Development Guide

## Standard Patterns

### Running API Services

**Rule**: Always use `run_api.sh` scripts when available. They automatically handle virtual environment activation.

#### Pattern

Each module with an API service should have a `run_api.sh` script:

```bash
cd _dev/<module-name>
./run_api.sh
```

The script:
1. **Automatically activates venv** if `venv/` or `.venv/` exists (no manual activation needed)
2. Checks optional dependencies
3. Shows configuration status
4. Starts the API service

#### Example

```bash
# data-retriever
cd _dev/data-retriever
./run_api.sh  # ✅ Automatically uses venv if present

# data-store
cd _dev/data-store
./run_api.sh  # ✅ Automatically uses venv if present
```

#### Why This Pattern?

- **Consistency**: Same command across all modules
- **Convenience**: No need to remember to activate venv
- **Safety**: Ensures correct Python environment is used
- **Transparency**: Shows what's being used (venv, dependencies, config)

### Virtual Environments

#### Local Development

Each module can have its own `venv`:

```bash
cd _dev/data-retriever
python3 -m venv venv
source venv/bin/activate
pip install -e ".[yahoo]"  # Install with optional deps
```

The `run_api.sh` script will automatically detect and use it.

#### Production

In production (Docker, AWS Lambda, ECS/Fargate, EC2), dependencies are installed from `pyproject.toml` directly:

```dockerfile
# Dockerfile example
FROM python:3.11
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e ".[all]"
COPY . .
CMD ["python", "api_service.py"]
```

No `venv` needed in production - `pip install` handles isolation.

### Testing

Use `run_tests.sh` scripts (similar pattern):

```bash
cd _dev/<module-name>
./run_tests.sh
```

These also automatically activate venv if present.

### Configuration

#### Per-Module `.env` Files

Each module can have its own `.env` file:

```bash
_dev/data-retriever/.env
_dev/data-store/.env
```

These are:
- **Gitignored**: Not committed to repository
- **Loaded automatically**: Via `python-dotenv` in `api_service.py`
- **Mapped to AWS**: Environment variables in production

Example `.env`:
```bash
# _dev/data-retriever/.env
YAHOO_FINANCE_USE_MOCK=false

# _dev/data-store/.env
DATA_STORE_BACKEND=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=trainer_data
```

### Module Structure

Standard structure for modules with API services:

```
_dev/<module-name>/
├── api_service.py          # FastAPI service
├── run_api.sh             # ✅ Run script (auto venv)
├── run_tests.sh            # Test runner
├── .env                    # Local config (gitignored)
├── .env.example            # Config template (committed)
├── venv/                   # Optional: local venv
├── pyproject.toml          # Dependencies
├── src/                    # Source code
└── README.md               # Documentation
```

## Quick Reference

### Start a Module API

```bash
cd _dev/<module-name>
./run_api.sh
```

### Run Tests

```bash
cd _dev/<module-name>
./run_tests.sh
```

### Install Dependencies

```bash
cd _dev/<module-name>
python3 -m venv venv
source venv/bin/activate
pip install -e ".[all]"
```

### Check Configuration

```bash
cd _dev/<module-name>
cat .env  # Local config
cat .env.example  # Available options
```

