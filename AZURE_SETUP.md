# Azure OpenAI Setup Guide

## Quick Setup Steps

### 1. Get Your Azure OpenAI Credentials

From Azure Portal (https://portal.azure.com):

1. Go to your **Azure OpenAI resource**
2. Navigate to **Keys and Endpoint** (left sidebar)
3. Copy:
   - **KEY 1** or **KEY 2** → This is your `AZURE_OPENAI_API_KEY`
   - **Endpoint** → This is your `AZURE_OPENAI_ENDPOINT`

### 2. Get Your Deployment Names

1. Go to **Azure OpenAI Studio** (https://oai.azure.com)
2. Click on **Deployments** (left sidebar)
3. Find your deployments:
   - **Embedding model deployment** (usually `text-embedding-ada-002`)
   - **LLM deployment** (usually `gpt-4o-mini`, `gpt-4`, or `gpt-35-turbo`)

### 3. Update Your .env File

Open `.env` and fill in these values:

```env
# Azure OpenAI Settings
AZURE_OPENAI_API_KEY=your-actual-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure OpenAI LLM (for content generation)
AZURE_OPENAI_LLM_DEPLOYMENT=gpt-4o-mini
```

### 4. Example Values

Here's what they might look like:

```env
AZURE_OPENAI_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
AZURE_OPENAI_ENDPOINT=https://my-openai-resource.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_LLM_DEPLOYMENT=gpt-4o-mini
```

## Vector Dimension

Azure OpenAI's `text-embedding-ada-002` produces **1536-dimensional** vectors.

The `.env` file is already configured with:
```env
VECTOR_DIMENSION=1536
```

## Testing Your Setup

After updating `.env`, test the connection:

```powershell
# Install Azure OpenAI package
pip install llama-index-embeddings-azure-openai

# Run indexing
python example_index.py
```

## Common Issues

### "Authentication failed"
- Double-check your `AZURE_OPENAI_API_KEY`
- Make sure there are no extra spaces

### "Deployment not found"
- Verify `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` matches your actual deployment name
- Go to Azure OpenAI Studio → Deployments to confirm

### "Endpoint not found"
- Ensure `AZURE_OPENAI_ENDPOINT` includes `https://` and ends with `/`
- Format: `https://YOUR-RESOURCE-NAME.openai.azure.com/`

## API Versions

Current recommended version: `2024-02-15-preview`

If you get version errors, try these alternatives:
- `2024-02-01`
- `2023-12-01-preview`
- `2023-05-15`

## Cost Estimation

### Embeddings (text-embedding-ada-002)
- **Price**: ~$0.0001 per 1,000 tokens
- **Example**: Indexing 10,000 job descriptions (~5M tokens) ≈ $0.50

### LLM (gpt-4o-mini)
- **Price**: ~$0.150 per 1M input tokens, ~$0.600 per 1M output tokens
- **Example**: Generating 100 blog posts ≈ $2-5

## Need Help?

1. Check Azure OpenAI documentation: https://learn.microsoft.com/en-us/azure/ai-services/openai/
2. Verify your deployments in Azure OpenAI Studio
3. Test with a simple API call first

## Ready to Go!

Once your `.env` is configured, run:

```powershell
python example_index.py
```

This will:
1. Connect to your Azure OpenAI
2. Generate embeddings for your job data
3. Store vectors in PostgreSQL
4. Enable semantic search and content generation!
