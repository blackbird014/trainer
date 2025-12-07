# Simple ETL Pipeline Examples

Simple ETL utilities demonstrating file system polling and mock database extraction, storing data in MongoDB.

## Overview

This directory contains simple ETL utilities that demonstrate:
1. **File Poller**: Watches a directory for JSON files and processes them
2. **Mock DB Extractor**: Simulates extracting data from an external database
3. **Simple Pipeline**: Combines both and stores everything in MongoDB

## Quick Start

### 1. Setup MongoDB

```bash
cd ../../
./setup_mongodb.sh
```

### 2. Install Dependencies

```bash
pip install trainer-data-store[mongodb]
```

### 3. Create Input Directory

```bash
mkdir -p ../../data/input
```

### 4. Run the Pipeline

```bash
# Run once
python simple_pipeline.py

# Run continuously (watches for new files)
python simple_pipeline.py --continuous
```

## Components

### File Poller (`file_poller.py`)

Watches a directory for JSON files and processes them.

```python
from file_poller import FilePoller

def process_data(data, metadata):
    print(f"Processing: {metadata['file_name']}")
    print(f"Data: {data}")

poller = FilePoller("data/input", poll_interval=5)
poller.poll_once(process_data)
```

### Mock DB Extractor (`mock_db_extractor.py`)

Simulates extracting data from an external database.

```python
from mock_db_extractor import MockDBExtractor

extractor = MockDBExtractor()
records = extractor.extract_all()
print(f"Found {len(records)} records")
```

### Simple Pipeline (`simple_pipeline.py`)

Combines file polling and DB extraction, stores in MongoDB.

```bash
# Run once
python simple_pipeline.py

# Run continuously
python simple_pipeline.py --continuous
```

## Visualization

### View Pipeline Results

After running the pipeline, visualize what's stored:

```bash
python visualize_pipeline.py
```

This shows:
- All items stored by source
- Data previews (tickers, prices, etc.)
- Storage timestamps
- Statistics and summaries

### Console Logs

The pipeline itself shows detailed logs:
- File processing status
- Database extraction progress
- Storage confirmations
- Data store visualization

Run with verbose logging:
```bash
python simple_pipeline.py
```

## Testing

### Test File Poller

1. Create a JSON file in `data/input/`:
```json
{
  "ticker": "TEST",
  "price": 100.50,
  "volume": 1000000
}
```

2. Run the pipeline - it will process the file automatically.

3. Visualize results:
```bash
python visualize_pipeline.py
```

### Test Mock DB

The mock DB generates sample stock data automatically. Just run the pipeline and visualize:

```bash
python simple_pipeline.py
python visualize_pipeline.py
```

## Example Data Flow

```
File System (data/input/*.json)
    ↓
File Poller → Reads JSON → Stores in MongoDB

Mock External DB
    ↓
Mock DB Extractor → Generates sample data → Stores in MongoDB

MongoDB (trainer_data.etl_data)
    ↓
Queryable via data-store module
```

## Next Steps

This is a simple implementation to demonstrate the concept. To make it production-ready:

1. **Replace Mock DB**: Connect to real database
2. **Add Transformations**: Transform data before storing
3. **Add Scheduling**: Run on schedule (cron, etc.)
4. **Add Error Handling**: Better error recovery
5. **Add Monitoring**: Track pipeline execution

## Integration with Other Modules

This ETL pipeline uses:
- **data-store**: For MongoDB storage
- Can integrate with **data-retriever**: For real data sources
- Can integrate with **prompt-manager**: For data-driven prompts

## Notes

- Files are processed once (tracked by modification time)
- Mock DB generates fresh data each time
- All data stored in MongoDB with metadata
- Easy to extend with real data sources

