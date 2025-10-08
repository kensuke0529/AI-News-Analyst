# AI News Analyst - MVP-3 Summary

**Version:** 3.0  
**Date:** October 8, 2025  

---

## Executive Summary

MVP-3:  **decoupled architecture** that separates data extraction from query processing, resulting in faster response times, better scalability, and cleaner code organization.

**MVP-2:**
```
User Query → Fetch RSS → Embed → Store → Retrieve → Generate Response
(All in one request ~10s)
```

**MVP-3:**
```
Background Job (periodic):
  Fetch RSS → Embed → Store in DB

User Query (real-time):
  User Query → Retrieve from DB → Generate Response
  (Expected ~5-7s)
```

---

## Key Changes

### 1. **Background Extraction Job** (New)

**File:** `src/data_ingestion/extract_and_store.py`

- Runs independently from user queries
- Fetches from multiple sources (Techmeme, MIT)
- Handles deduplication automatically
- Stores with metadata (source, date, ingestion time)
- Can be scheduled via cron or the scheduler script

**Key Features:**
- Source attribution (tracks which RSS feed provided each article)
- Duplicate prevention (checks existing links before adding)
-  Rich metadata (title, link, pub_date, source, ingested_at)
-  Error resilience (continues if one source fails)
-  Detailed logging and statistics

### 2. **Query-Only Workflow** (Updated)

**File:** `src/workflow/news_analysis_workflow.py`

- **NO fetching during queries** - only reads from pre-populated DB
- **NO embedding during queries** - uses existing embeddings
- **Faster response times** - no waiting for RSS parsing
- **Better reliability** - queries never fail due to source timeouts


## Benefits

### Performance
-  **Faster queries** - No fetching/embedding overhead
- **Predictable latency** - Query time depends only on DB retrieval + LLM
- **Scalable** - Can handle multiple concurrent queries without hitting RSS feeds

### Maintainability
-  **Separation of concerns** - Extraction logic separate from query logic

## Performance Comparison

| Metric | MVP-2 | MVP-3 | Change |
|--------|-------|-------|--------|
| **Query Time** | 10.55s | ~5-7s (est.) | **-40%**  |
| **Extraction Time** | Per query | Background | **Decoupled**  |
| **Concurrent Queries** | Limited | High |  |


## Conclusion

MVP-3 establishes a **production-ready architecture** with clean separation of concerns. The decoupled extraction and query pipeline enables:

-  Faster, more predictable query times
-  Better reliability and error isolation
-  Richer metadata and source attribution
-  Foundation for advanced features in MVP-4
