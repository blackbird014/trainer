# Prometheus Queries - Working Examples

## ✅ Working Queries

### 1. Total Operations
```
prompt_manager_operations_total
```

### 2. Operations by Status
```
sum by (status) (prompt_manager_operations_total)
```

### 3. Operations by Operation Type
```
sum by (operation) (prompt_manager_operations_total)
```

### 4. Operations Rate (per second)
```
rate(prompt_manager_operations_total[5m])
```

### 5. Total Tokens
```
sum(prompt_manager_tokens_total)
```

### 6. Tokens by Operation
```
sum by (operation) (prompt_manager_tokens_total)
```

### 7. Cache Hits
```
prompt_manager_cache_hits_total
```

### 8. Cache Misses
```
prompt_manager_cache_misses_total
```

## ⚠️ Queries That Need More Data

These queries need multiple data points over time:

### Histogram Quantile (P95 Duration)
**Wait 1-2 minutes after generating data, then:**
```
histogram_quantile(0.95, rate(prompt_manager_operation_duration_seconds_bucket[5m]))
```

### Cache Hit Ratio
**Generate more cache operations first:**
```
rate(prompt_manager_cache_hits_total[5m]) / (rate(prompt_manager_cache_hits_total[5m]) + rate(prompt_manager_cache_misses_total[5m]))
```

**If empty, try:**
```
prompt_manager_cache_hits_total / (prompt_manager_cache_hits_total + prompt_manager_cache_misses_total)
```

## 🔧 How to Generate More Data

Visit this URL multiple times:
```
http://localhost:8000/test
```

Or use curl:
```bash
for i in {1..20}; do curl -s http://localhost:8000/test > /dev/null; sleep 1; done
```

## 📊 Quick Test Queries

Copy these into Prometheus UI (http://localhost:9090):

1. **See all operations:**
   ```
   prompt_manager_operations_total
   ```

2. **See operations per second:**
   ```
   rate(prompt_manager_operations_total[1m])
   ```

3. **See total tokens:**
   ```
   sum(prompt_manager_tokens_total)
   ```

4. **See cache stats:**
   ```
   prompt_manager_cache_hits_total
   prompt_manager_cache_misses_total
   ```

## 💡 Tips

- **Histograms need time**: Wait 1-2 minutes after generating data
- **Rate functions need time range**: Use `[5m]` or `[1m]` for recent data
- **Generate more data**: Visit `/test` endpoint multiple times
- **Check targets**: http://localhost:9090/targets (should show "UP")

