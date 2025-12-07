# Embeddings and MongoDB: Explained Simply

## What are Embeddings?

**Embeddings** are numerical representations of text that capture **semantic meaning**.

Think of it like this:
- **Text**: "What is the price of Apple stock?"
- **Embedding**: `[0.123, -0.456, 0.789, ..., 0.234]` (a list of ~1536 numbers)

The embedding model (like OpenAI's `text-embedding-3-small`) converts text into these numbers.

## Why Embeddings?

**Problem**: How do you find similar questions without exact text matching?

**Example**:
- Question 1: "What is the price of Apple stock?"
- Question 2: "How much does AAPL cost?"
- Question 3: "Show me Tesla stock price"

Questions 1 and 2 are **semantically similar** (both ask about Apple stock price), but text matching won't find them.

**Solution**: Embeddings capture meaning, so similar questions have similar embedding vectors!

## How Embeddings Work with MongoDB

### Current MongoDB Document (without embeddings):
```json
{
  "key": "prompt:stock:apple",
  "data": {
    "prompt": "What is the price of Apple stock?",
    "json_data": {"ticker": "AAPL", "price": 150.25}
  },
  "source": "prompt_manager"
}
```

### MongoDB Document WITH Embeddings:
```json
{
  "key": "prompt:stock:apple",
  "data": {
    "prompt": "What is the price of Apple stock?",
    "json_data": {"ticker": "AAPL", "price": 150.25}
  },
  "source": "prompt_manager",
  "embedding": [0.123, -0.456, 0.789, ..., 0.234]  // ← NEW: Vector of numbers
}
```

## The Workflow

### Step 1: Generate Embedding
```python
from openai import OpenAI
client = OpenAI()

# Your prompt
prompt = "What is the price of Apple stock?"

# Generate embedding (converts text → numbers)
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=prompt
)
embedding = response.data[0].embedding  # List of ~1536 numbers
```

### Step 2: Store in MongoDB
```python
from data_store import create_store

store = create_store("mongodb", connection_string="mongodb://localhost:27017")

# Store with embedding
store.store(
    key="prompt:stock:apple",
    data={
        "prompt": "What is the price of Apple stock?",
        "json_data": {"ticker": "AAPL", "price": 150.25}
    },
    metadata={
        "source": "prompt_manager",
        "embedding": embedding  # ← Store the vector!
    }
)
```

### Step 3: Search Using Embeddings (Vector Search)

**Traditional MongoDB Query** (exact match only):
```python
# Only finds EXACT matches
result = store.query({"data.prompt": "What is the price of Apple stock?"})
```

**Vector Search** (semantic similarity):
```python
# Finds SIMILAR questions!
query = "How much does AAPL cost?"
query_embedding = generate_embedding(query)  # Convert query to embedding

# MongoDB Vector Search finds documents with similar embeddings
similar_docs = store.vector_search(
    query_embedding=query_embedding,
    limit=5
)
# Returns: "What is the price of Apple stock?" (even though text is different!)
```

## MongoDB Vector Search

MongoDB (Atlas or with vector search extension) can:
1. **Index embeddings** for fast similarity search
2. **Find similar documents** using cosine similarity
3. **Return results** ranked by similarity

### Example: MongoDB Vector Search Query
```javascript
// MongoDB query for vector search
db.collection.aggregate([
  {
    $vectorSearch: {
      index: "embedding_index",
      path: "embedding",
      queryVector: [0.123, -0.456, ...],  // Your query embedding
      numCandidates: 100,
      limit: 10
    }
  }
])
```

## Real-World Example

### Scenario: User asks a question

**Without Embeddings**:
```
User: "How much does AAPL cost?"
System: Searches MongoDB for exact text "How much does AAPL cost?"
Result: ❌ Not found (even though we have "What is the price of Apple stock?")
```

**With Embeddings**:
```
User: "How much does AAPL cost?"
System: 
  1. Convert query to embedding: [0.120, -0.450, ...]
  2. Vector search in MongoDB
  3. Finds: "What is the price of Apple stock?" (similarity: 0.95)
  4. Returns: {"ticker": "AAPL", "price": 150.25} ✅
```

## Embedding Models

### 1. OpenAI `text-embedding-3-small`
- **Cost**: ~$0.02 per 1M tokens
- **Dimensions**: 1536 numbers
- **Quality**: Excellent
- **Requires**: API key

### 2. Sentence Transformers (Free!)
- **Cost**: FREE (runs locally)
- **Dimensions**: 384-768 numbers
- **Quality**: Very good
- **Example**: `sentence-transformers/all-MiniLM-L6-v2`

### 3. Cohere Embed
- **Cost**: Similar to OpenAI
- **Dimensions**: 1024 numbers
- **Quality**: Excellent
- **Requires**: API key

## Implementation Options

### Option 1: MongoDB Atlas Vector Search (Cloud)
- MongoDB Atlas (cloud) has built-in vector search
- Just add embedding field and create vector index
- **Cost**: MongoDB Atlas subscription

### Option 2: Local MongoDB + Vector Search Extension
- Use local MongoDB
- Add vector search extension
- **Cost**: Free (self-hosted)

### Option 3: Separate Vector Database
- Store embeddings in Pinecone, Weaviate, or Chroma
- Keep original data in MongoDB
- **Cost**: Varies by service

## Summary

**Embeddings** = Numbers that represent text meaning
**MongoDB** = Database that stores your data
**Vector Search** = Finding similar documents using embedding similarity

**The Connection**:
1. Generate embedding from text (using OpenAI, Sentence Transformers, etc.)
2. Store embedding in MongoDB document
3. Use MongoDB vector search to find similar documents
4. Return results without calling LLM!

This enables **semantic search** - finding answers based on meaning, not exact text matching.

