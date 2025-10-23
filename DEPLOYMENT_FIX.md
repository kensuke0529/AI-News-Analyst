# RAG Response Fix - Deployment Guide

## Issue Identified
The RAG system was returning "no information" responses even though the database contained relevant articles. This was due to:
1. **State passing issue**: Lambda functions in the workflow weren't reliably capturing state
2. **Overly restrictive prompt**: The LLM was being too cautious about using context
3. **No error checking**: Empty context wasn't being handled gracefully

## What Was Fixed

### 1. Improved State Management
**File**: `src/workflow/news_analysis_workflow.py`

**Before**:
```python
chain = (
    {
        "context": lambda x: state['retrieved_docs'], 
        "question": lambda x: state['prompt']
    }
    | prompt_template
    | llm
    | StrOutputParser()
)
response = chain.invoke({})
```

**After**:
```python
# Get context and question directly from state
context = state.get('retrieved_docs', '')
question = state.get('prompt', '')

# Direct invocation with explicit parameters
chain = prompt_template | llm | StrOutputParser()
final_response = chain.invoke({"context": context, "question": question})
```

### 2. Enhanced Prompt Template
- Made instructions clearer about using the provided context
- Emphasized that SOURCE, TITLE, DATE, LINK, and CONTENT fields contain valid information
- Reduced over-cautious behavior while maintaining accuracy

### 3. Added Debug Logging
```python
print(f"\n[DEBUG] Question: {question[:100]}...")
print(f"[DEBUG] Context length: {len(context)} characters")
print(f"[DEBUG] Context preview: {context[:300]}...")
```

### 4. Empty Context Detection
```python
if not context or len(context.strip()) < 10:
    return {"response": "I apologize, but I couldn't retrieve any relevant information..."}
```

## Test Results

### Before Fix:
```
Query: "what is the tiktok related news?"
Response: "The provided context does not contain any specific information regarding TikTok-related news."
```

### After Fix:
```
Query: "what is the tiktok related news?"
Context: 1937 characters (with TikTok articles)
Response: Detailed news about TikTok's ad-buying tool with proper citations
```

## Deployment Steps

### Option 1: Quick Deploy (Recommended)
```bash
# 1. Commit and push the changes
git add src/workflow/news_analysis_workflow.py
git commit -m "Fix: Improve RAG context passing and prompt template"
git push origin main

# 2. Railway will auto-deploy (if enabled)
# Or manually redeploy in Railway dashboard
```

### Option 2: Manual Testing Before Deploy
```bash
# 1. Test locally first
python3 -c "
from src.workflow.news_analysis_workflow import run_news_analysis
result = run_news_analysis('what is the tiktok related news?')
print(result)
"

# 2. If test passes, commit and push
git add .
git commit -m "Fix: Improve RAG response reliability"
git push origin main
```

### Option 3: Test on Staging (if available)
```bash
# Deploy to staging environment first
# Test thoroughly
# Then deploy to production
```

## Verification

After deployment, verify the fix by:

1. **Check Logs**: Look for DEBUG output in Railway logs
   ```
   [DEBUG] Question: what is the tiktok related news?...
   [DEBUG] Context length: 1937 characters
   [DEBUG] Response length: 810 characters
   ```

2. **Test via UI**: 
   - Visit your deployed site
   - Search for: "what is the tiktok related news?"
   - Expected: Detailed response with citations

3. **Test via API**:
   ```bash
   curl -X POST https://your-app.railway.app/api/news/rag \
     -H "Content-Type: application/json" \
     -d '{"query":"what is the tiktok related news?"}'
   ```

## Database Verification

If issues persist, verify the database:

```bash
# Run diagnostic script
python3 scripts/diagnose_database.py

# Expected output:
# ✅ Database is working correctly!
# Total documents: 101
# Total TikTok documents: 2
```

If database is empty:
```bash
# Populate database
python3 scripts/populate_database.py
```

## Environment Variables to Check

Make sure these are set correctly in Railway:

- `OPENAI_API_KEY`: Your OpenAI API key
- `USE_CHROMA_CLOUD`: `true` (if using cloud ChromaDB)
- `CHROMA_API_KEY`: Your ChromaDB API key (if using cloud)
- `CHROMA_TENANT`: Your ChromaDB tenant (if using cloud)
- `CHROMA_DATABASE`: `news-ai` (or your database name)

## Rollback Plan

If something goes wrong:

```bash
# Revert the commit
git revert HEAD
git push origin main

# Or checkout previous version
git checkout <previous-commit-hash> src/workflow/news_analysis_workflow.py
git commit -m "Rollback: Revert to previous workflow version"
git push origin main
```

## Additional Improvements Made

### New Diagnostic Script
**File**: `scripts/diagnose_database.py`

Run this script to check:
- Database configuration (local vs cloud)
- Document count
- TikTok article presence
- Vector search functionality

```bash
python3 scripts/diagnose_database.py
```

## Support

If you encounter issues:

1. Check Railway logs for DEBUG output
2. Run `diagnose_database.py` locally
3. Verify environment variables
4. Test locally before deployment
5. Check that cloud ChromaDB is accessible (if using cloud)

## Performance Impact

- **Latency**: No significant change (direct parameter passing is equally fast)
- **Reliability**: Much improved (explicit state handling)
- **Debugging**: Enhanced (debug logging helps identify issues)

## Next Steps

After successful deployment:

1. **Monitor logs** for the first few queries
2. **Test multiple query types** (AI news, tech companies, etc.)
3. **Remove debug logging** once confident (optional):
   - Comment out or remove the `print()` statements in `response_generation_node`
4. **Consider adding**:
   - Response caching for common queries
   - Query analytics
   - User feedback mechanism

---

**Last Updated**: October 23, 2025  
**Status**: ✅ Tested and Ready for Deployment

