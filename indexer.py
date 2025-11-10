"""
LlamaIndex PgVector Indexer with Incremental Updates
"""
import logging
from typing import List, Optional, Type
from sqlalchemy.orm import Session
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from config import settings
from models import Job, TNNews, AIJob, NewsArticle, SessionLocal, Base

# Configure logging early
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Import embedding models based on provider
if settings.embedding_provider == "azure":
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
elif settings.embedding_provider == "openai":
    from llama_index.embeddings.openai import OpenAIEmbedding
else:
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except Exception as e:
        logger.warning(f"Failed to import HuggingFaceEmbedding: {e}")
        logger.warning("Falling back to Azure OpenAI embeddings")
        from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
        settings.embedding_provider = "azure"


class BaseIndexer:
    """Base class for indexing different data sources"""
    
    def __init__(
        self,
        table_name: str,
        model_class: Type[Base],
        collection_name: Optional[str] = None
    ):
        self.table_name = table_name
        self.model_class = model_class
        self.collection_name = collection_name or f"{settings.vector_table_prefix}_{table_name}"
        
        # Initialize embedding model
        self._setup_embeddings()
        
        # Initialize vector store
        self.vector_store = self._setup_vector_store()
        
        # Initialize storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
    
    def _setup_embeddings(self):
        """Setup embedding model and LLM based on configuration"""
        # Setup embeddings
        if settings.embedding_provider == "azure":
            logger.info(f"Using Azure OpenAI embeddings: {settings.azure_openai_embedding_deployment}")
            Settings.embed_model = AzureOpenAIEmbedding(
                model=settings.azure_openai_embedding_deployment,
                deployment_name=settings.azure_openai_embedding_deployment,
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
            
            # Also setup Azure OpenAI LLM globally for metadata extractors
            from llama_index.llms.azure_openai import AzureOpenAI
            logger.info(f"Using Azure OpenAI LLM: {settings.azure_openai_llm_model} (deployment: {settings.azure_openai_llm_deployment})")
            Settings.llm = AzureOpenAI(
                model=settings.azure_openai_llm_model,  # Actual model name (e.g., "gpt-4o")
                deployment_name=settings.azure_openai_llm_deployment,  # Azure deployment name
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
            
        elif settings.embedding_provider == "openai":
            logger.info(f"Using OpenAI embeddings: {settings.openai_embedding_model}")
            Settings.embed_model = OpenAIEmbedding(
                model=settings.openai_embedding_model,
                api_key=settings.openai_api_key
            )
            
            # Also setup OpenAI LLM globally
            from llama_index.llms.openai import OpenAI as OpenAILLM
            logger.info(f"Using OpenAI LLM: gpt-4")
            Settings.llm = OpenAILLM(
                model="gpt-4",
                api_key=settings.openai_api_key
            )
            
        else:
            logger.info(f"Using local embeddings: {settings.local_embedding_model}")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=settings.local_embedding_model
            )
            logger.warning("No LLM configured for local embeddings - metadata extraction will be limited")
    
    def _setup_vector_store(self) -> PGVectorStore:
        """Setup PgVector store"""
        logger.info(f"Setting up PgVector store for collection: {self.collection_name}")
        
        vector_store = PGVectorStore.from_params(
            database=settings.db_name,
            host=settings.db_host,
            password=settings.db_password,
            port=settings.db_port,        
            user=settings.db_user,
            table_name=self.collection_name,
            embed_dim=settings.vector_dimension,
        )
        
        return vector_store
    
    def get_unindexed_records(self, db: Session, limit: Optional[int] = None):
        """Get records that haven't been indexed yet (incremental update)"""
        query = db.query(self.model_class).filter(
            (self.model_class.index_status == None) | 
            (self.model_class.index_status != 1)
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def create_documents(self, records: List[Base]) -> List[Document]:
        """Convert database records to LlamaIndex Documents"""
        documents = []
        
        for record in records:
            doc_text = record.to_document_text()
            metadata = record.to_metadata()
            
            doc = Document(
                text=doc_text,
                metadata=metadata,
                id_=str(record.id)
            )
            documents.append(doc)
        
        return documents
    
    def index_records(
        self, 
        batch_size: int = 100,
        limit: Optional[int] = None
    ) -> dict:
        """
        Index records with incremental updates
        
        Args:
            batch_size: Number of records to process in each batch
            limit: Maximum number of records to index (None for all)
        
        Returns:
            Dictionary with indexing statistics
        """
        db = SessionLocal()
        stats = {
            "total_processed": 0,
            "total_indexed": 0,
            "errors": 0
        }
        
        try:
            logger.info(f"Starting indexing for {self.table_name}")
            
            # Get unindexed records
            records = self.get_unindexed_records(db, limit)
            total_records = len(records)
            
            if total_records == 0:
                logger.info(f"No new records to index for {self.table_name}")
                return stats
            
            logger.info(f"Found {total_records} unindexed records")
            
            # Process in batches
            for i in range(0, total_records, batch_size):
                batch = records[i:i + batch_size]
                
                try:
                    # Convert to documents
                    documents = self.create_documents(batch)
                    
                    # Create or update index
                    if i == 0:
                        # First batch - create index
                        self.index = VectorStoreIndex.from_documents(
                            documents,
                            storage_context=self.storage_context,
                            show_progress=True,
                            transformations=getattr(Settings, 'transformations', None)  # Use transformations if set
                        )
                    else:
                        # Subsequent batches - insert into existing index
                        for doc in documents:
                            self.index.insert(doc)
                    
                    # Mark records as indexed (status = 1)
                    for record in batch:
                        record.index_status = 1
                    
                    db.commit()
                    
                    stats["total_indexed"] += len(batch)
                    logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch)} records")
                
                except Exception as e:
                    logger.error(f"Error indexing batch: {str(e)}")
                    db.rollback()
                    stats["errors"] += len(batch)
                
                stats["total_processed"] += len(batch)
            
            logger.info(f"Indexing complete for {self.table_name}: {stats}")
            
        except Exception as e:
            logger.error(f"Fatal error during indexing: {str(e)}")
            raise
        finally:
            db.close()
        
        return stats
    
    def get_index(self) -> VectorStoreIndex:
        """Get or create index"""
        if not hasattr(self, 'index'):
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store,
                storage_context=self.storage_context
            )
        return self.index
    
    def reindex_all(self, batch_size: int = 100) -> dict:
        """
        Force reindex all records (not incremental)
        Use this when you need to rebuild the entire index
        """
        db = SessionLocal()
        
        try:
            # Reset all index_status
            db.query(self.model_class).update({"index_status": None})
            db.commit()
            
            # Now index all
            return self.index_records(batch_size=batch_size)
        
        finally:
            db.close()


class JobIndexer(BaseIndexer):
    """Indexer for Jobs table"""
    
    def __init__(self):
        super().__init__(
            table_name="jobs",
            model_class=Job,
            collection_name=f"{settings.vector_table_prefix}_jobs"
        )


class TNNewsIndexer(BaseIndexer):
    """Indexer for TN News table"""
    
    def __init__(self):
        super().__init__(
            table_name="tnnews",
            model_class=TNNews,
            collection_name=f"{settings.vector_table_prefix}_tnnews"
        )


class AIJobIndexer(BaseIndexer):
    """Indexer for AI Jobs table"""
    
    def __init__(self):
        super().__init__(
            table_name="aijobs",
            model_class=AIJob,
            collection_name=f"{settings.vector_table_prefix}_aijobs"
        )


class NewsArticleIndexer(BaseIndexer):
    """
    Indexer for News Articles table with transformation pipeline.
    
    Uses LlamaIndex transformations for:
    - SentenceSplitter: Intelligent chunking with paragraph awareness
    - TitleExtractor: Generate descriptive titles for chunks
    - KeywordExtractor: Extract relevant keywords (optional)
    """
    
    def __init__(self, use_keyword_extraction: bool = False, use_title_extraction: bool = False):
        """
        Initialize NewsArticleIndexer with optional transformation pipeline.
        
        Args:
            use_keyword_extraction: If True, extract keywords using LLM (slower, costs more, may trigger content filters)
            use_title_extraction: If True, generate titles using LLM (slower, costs more, may trigger content filters)
        """
        self.use_keyword_extraction = use_keyword_extraction
        self.use_title_extraction = use_title_extraction
        super().__init__(
            table_name="news_articles",
            model_class=NewsArticle,
            collection_name=f"{settings.vector_table_prefix}_news_articles"
        )
        
        # Setup transformation pipeline for news articles
        self._setup_transformations()
    
    def _setup_transformations(self):
        """Setup transformation pipeline for better chunking and metadata extraction"""
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.core.extractors import TitleExtractor, KeywordExtractor
        from llama_index.llms.azure_openai import AzureOpenAI
        
        logger.info("Setting up transformation pipeline for news articles")
        
        # Setup Azure OpenAI LLM for metadata extraction
        llm = AzureOpenAI(
            model=settings.azure_openai_llm_model,  # Actual model name (e.g., "gpt-4o")
            deployment_name=settings.azure_openai_llm_deployment,  # Azure deployment name
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )
        
        # Create transformations list
        transformations = [
            # 1. Split text intelligently with paragraph awareness
            SentenceSplitter.from_defaults(
                chunk_size=512,              # Smaller chunks for news (2-3 paragraphs)
                chunk_overlap=50,            # 10% overlap for context continuity
                paragraph_separator="\n\n",  # News typically uses double newlines
                include_metadata=True,       # Preserve metadata (category, source, date)
                include_prev_next_rel=True   # Maintain article flow
            ),
        ]
        
        # 2. Optionally generate descriptive titles for each chunk (uses Azure OpenAI LLM)
        if self.use_title_extraction:
            transformations.append(
                TitleExtractor(nodes=5, llm=llm)  # Use 5 surrounding nodes for context
            )
            logger.warning("Title extraction enabled - may trigger Azure content filters on some news articles")
        
        # 3. Optionally add keyword extraction (requires additional LLM calls)
        if self.use_keyword_extraction:
            transformations.append(
                KeywordExtractor(keywords=5, llm=llm)  # Extract 5 keywords per chunk
            )
            logger.warning("Keyword extraction enabled - may trigger Azure content filters on some news articles")
        
        # Set transformations in global settings
        # Note: This affects how documents are processed when creating the index
        Settings.transformations = transformations
        
        logger.info(f"Transformation pipeline configured with {len(transformations)} steps")
        if self.use_title_extraction or self.use_keyword_extraction:
            logger.info(f"Using Azure OpenAI LLM: {settings.azure_openai_llm_model} (deployment: {settings.azure_openai_llm_deployment})")
        else:
            logger.info("Using basic chunking only (no LLM-based metadata extraction)")


# Convenience function
def index_all_sources(batch_size: int = 100, limit: Optional[int] = None) -> dict:
    """Index all data sources"""
    results = {}
    
    indexers = [
        ("jobs", JobIndexer()),
        # Uncomment to index other sources
        # ("tnnews", TNNewsIndexer()),
        # ("aijobs", AIJobIndexer()),
    ]
    
    for name, indexer in indexers:
        logger.info(f"\n{'='*50}")
        logger.info(f"Indexing {name}")
        logger.info(f"{'='*50}")
        
        try:
            stats = indexer.index_records(batch_size=batch_size, limit=limit)
            results[name] = stats
        except Exception as e:
            logger.error(f"Failed to index {name}: {str(e)}")
            results[name] = {"error": str(e)}
    
    return results
