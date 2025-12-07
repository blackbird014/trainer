# MongoDB Setup Guide

This guide helps you set up MongoDB locally for testing JSON data storage.

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Run the setup script
./setup_mongodb.sh

# Or manually:
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest
```

### Option 2: Manual Installation

1. Download MongoDB Community Edition:
   - macOS: `brew install mongodb-community`
   - Linux: https://www.mongodb.com/try/download/community
   - Windows: https://www.mongodb.com/try/download/community

2. Start MongoDB:
   ```bash
   mongod --dbpath /path/to/data
   ```

## Verify MongoDB is Running

```bash
# Check Docker container
docker ps | grep mongodb

# Or test connection
docker exec -it mongodb mongosh --eval "db.version()"
```

## Install Python Package

```bash
pip install trainer-data-store[mongodb]
```

## Usage Examples

### Basic Example

```python
from data_store import create_store

# Connect to MongoDB
store = create_store(
    "mongodb",
    connection_string="mongodb://localhost:27017",
    database="trainer_data"
)

# Store JSON data
store.store(
    key="stock:AAPL",
    data={"price": 150.25, "volume": 1000000},
    metadata={"source": "yahoo_finance"}
)

# Query data
result = store.query({"source": "yahoo_finance"})
print(f"Found {result.total} items")
```

### Run Examples

```bash
# Basic usage (SQLite by default)
python examples/basic_usage.py

# MongoDB examples
python examples/basic_usage.py --mongodb

# JSON storage example (MongoDB)
python examples/mongodb_json_storage.py
```

## Why MongoDB for JSON?

- **Native JSON support**: Stores JSON documents natively
- **Flexible schema**: No need to define schema upfront
- **Nested queries**: Query nested JSON fields easily
- **Aggregation**: Powerful aggregation pipelines
- **Scalability**: Handles large datasets efficiently
- **Indexing**: Fast queries on any field

## Viewing Data

### Using MongoDB Shell

```bash
docker exec -it mongodb mongosh trainer_data

# List collections
show collections

# Query data
db.data_store.find().pretty()

# Query specific source
db.data_store.find({"source": "yahoo_finance"}).pretty()

# Count items
db.data_store.countDocuments({})
```

### Using MongoDB Compass (GUI)

1. Download: https://www.mongodb.com/try/download/compass
2. Connect to: `mongodb://localhost:27017`
3. Browse database: `trainer_data`
4. View collection: `data_store`

## Connection String

Default: `mongodb://localhost:27017`

For authentication:
```
mongodb://username:password@localhost:27017/database?authSource=admin
```

## Troubleshooting

### MongoDB not starting

```bash
# Check logs
docker logs mongodb

# Restart container
docker restart mongodb

# Remove and recreate
docker stop mongodb && docker rm mongodb
./setup_mongodb.sh
```

### Connection refused

- Make sure MongoDB is running: `docker ps | grep mongodb`
- Check port 27017 is not in use: `lsof -i :27017`
- Try connecting: `docker exec -it mongodb mongosh`

### Python can't connect

- Verify MongoDB is running
- Check connection string: `mongodb://localhost:27017`
- Install pymongo: `pip install trainer-data-store[mongodb]`

## Data Persistence

Data is stored in Docker volume `mongodb_data` and persists across container restarts.

To backup:
```bash
docker exec mongodb mongodump --out /backup
```

To restore:
```bash
docker exec mongodb mongorestore /backup
```

## Stop MongoDB

```bash
# Stop container (data persists)
docker stop mongodb

# Remove container and data
docker stop mongodb && docker rm mongodb && docker volume rm mongodb_data
```

