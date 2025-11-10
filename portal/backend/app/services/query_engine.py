"""
Portal Query Engine - Simplified for Blog Title Generation
Uses LlamaIndex + PgVector with metadata filters
"""
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
sys.path.insert(0, str(PathLib(__file__).parent.parent.parent))
from app.models.content import GeneratedTitle, GeneratedSocialContent, GeneratedBlog, GenerationHistory

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortalQueryEngine:
    """Query engine for portal with filtering capabilities"""
    
    def __init__(self):
        """Initialize connection to PgVector and Azure OpenAI"""
        
        # Database connection
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        self.db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Azure OpenAI Embedding
        self.embed_model = AzureOpenAIEmbedding(
            model="text-embedding-3-large",
            deployment_name=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
        )
        
        # Azure OpenAI LLM
        self.llm = AzureOpenAI(
            model=os.getenv('AZURE_OPENAI_LLM_MODEL'),
            deployment_name=os.getenv('AZURE_OPENAI_LLM_DEPLOYMENT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
        )
        
        # Initialize indexes (lazy loading)
        self._jobs_index = None
        self._news_index = None
    
    def _get_jobs_index(self) -> VectorStoreIndex:
        """Get or create jobs vector index"""
        if self._jobs_index is None:
            vector_store = PGVectorStore.from_params(
                database=os.getenv('DB_NAME'),
                host=os.getenv('DB_HOST'),
                password=os.getenv('DB_PASSWORD'),
                port=int(os.getenv('DB_PORT')),
                user=os.getenv('DB_USER'),
                table_name="llamaindex_embedding_jobs",
                embed_dim=3072,
            )
            
            self._jobs_index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=self.embed_model,
            )
            logger.info("Jobs index initialized")
        
        return self._jobs_index
    
    def _get_news_index(self) -> VectorStoreIndex:
        """Get or create news vector index"""
        if self._news_index is None:
            vector_store = PGVectorStore.from_params(
                database=os.getenv('DB_NAME'),
                host=os.getenv('DB_HOST'),
                password=os.getenv('DB_PASSWORD'),
                port=int(os.getenv('DB_PORT')),
                user=os.getenv('DB_USER'),
                table_name="llamaindex_embedding_news_articles",
                embed_dim=3072,
            )
            
            self._news_index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=self.embed_model,
            )
            logger.info("News index initialized")
        
        return self._news_index
    
    def get_news_categories(self) -> List[str]:
        """Get unique categories from news_articles table"""
        query = "SELECT DISTINCT category FROM news_articles WHERE category IS NOT NULL ORDER BY category"
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            categories = [row[0] for row in result]
        return categories
    
    def get_news_sources(self) -> List[str]:
        """Get unique sources from news_articles table"""
        query = "SELECT DISTINCT source FROM news_articles WHERE source IS NOT NULL ORDER BY source"
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            sources = [row[0] for row in result]
        return sources
    
    def get_job_sectors(self) -> List[str]:
        """Get unique sectors from jobs table"""
        query = "SELECT DISTINCT sector FROM jobs WHERE sector IS NOT NULL ORDER BY sector"
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            sectors = [row[0] for row in result]
        return sectors
    
    def generate_titles_from_jobs(
        self,
        topic: str,
        sector: Optional[str] = None,
        num_titles: int = 5
    ) -> List[str]:
        """
        Generate blog titles using job data with optional sector filter
        
        Args:
            topic: Topic for blog titles
            sector: Optional sector filter (e.g., "Technology", "Healthcare")
            num_titles: Number of titles to generate
        
        Returns:
            List of blog titles
        """
        index = self._get_jobs_index()
        
        # Build filters
        filters = None
        if sector:
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="sector",
                        value=sector,
                        operator=FilterOperator.EQ
                    )
                ]
            )
        
        # Create query engine with filters
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            filters=filters,
            llm=self.llm
        )
        
        # Create prompt
        prompt = f"""Based on the job postings retrieved, generate {num_titles} engaging blog post titles about: {topic}

Requirements:
- Make titles catchy and SEO-friendly
- Base titles on the actual job data provided
- Focus on trends, insights, or valuable information
- Each title should be unique and interesting
{f"- Focus on the {sector} sector" if sector else ""}

Return only the titles, one per line, without numbering."""

        # Generate titles
        response = query_engine.query(prompt)
        
        # Debug logging
        logger.info(f"Raw LLM Response (Jobs): {response}")
        logger.info(f"Response type: {type(response)}")
        
        # Parse titles
        titles = self._parse_titles(str(response), num_titles)
        
        if not titles:
            logger.warning(f"No titles parsed from response: {response}")
        
        return titles
    
    def generate_titles_from_news(
        self,
        topic: str,
        category: Optional[str] = None,
        source: Optional[str] = None,
        num_titles: int = 5
    ) -> List[str]:
        """
        Generate blog titles using news data with optional category/source filters
        
        Args:
            topic: Topic for blog titles
            category: Optional category filter
            source: Optional source filter
            num_titles: Number of titles to generate
        
        Returns:
            List of blog titles
        """
        index = self._get_news_index()
        
        # Build filters
        filter_list = []
        if category:
            filter_list.append(
                MetadataFilter(
                    key="category",
                    value=category,
                    operator=FilterOperator.EQ
                )
            )
        if source:
            filter_list.append(
                MetadataFilter(
                    key="source",
                    value=source,
                    operator=FilterOperator.EQ
                )
            )
        
        filters = MetadataFilters(filters=filter_list) if filter_list else None
        
        # Create query engine with filters
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            filters=filters,
            llm=self.llm
        )
        
        # Create prompt
        prompt = f"""Based on the news articles retrieved, generate {num_titles} engaging blog post titles about: {topic}

Requirements:
- Make titles catchy and SEO-friendly
- Base titles on the actual news data provided
- Focus on trends, insights, or valuable information
- Each title should be unique and interesting
{f"- Focus on the {category} category" if category else ""}
{f"- Use insights from {source}" if source else ""}

Return only the titles, one per line, without numbering."""

        # Generate titles
        response = query_engine.query(prompt)
        
        # Debug logging
        logger.info(f"Raw LLM Response: {response}")
        logger.info(f"Response type: {type(response)}")
        
        # Parse titles
        titles = self._parse_titles(str(response), num_titles)
        
        if not titles:
            logger.warning(f"No titles parsed from response: {response}")
        
        return titles
    
    def _parse_titles(self, response: str, num_titles: int) -> List[str]:
        """Parse titles from LLM response"""
        # Handle empty response
        if not response or response.strip() == "" or response.strip().lower() == "empty response":
            logger.error("Empty response from LLM")
            return []
        
        lines = response.strip().split('\n')
        titles = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip common header/footer lines
            skip_phrases = ['based on', 'here are', 'titles:', 'blog post', 'engaging']
            if any(phrase in line.lower() for phrase in skip_phrases):
                continue
            
            # Remove numbering/bullets
            if line[0].isdigit() or line.startswith('-') or line.startswith('•'):
                title = line.lstrip('0123456789.-•) ').strip()
            else:
                title = line
            
            if title:
                titles.append(title)
        
        logger.info(f"Parsed {len(titles)} titles from response")
        return titles[:num_titles]
    
    def save_title(
        self,
        source_type: str,
        topic: str,
        title: str,
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None,
        source_id: Optional[int] = None,
        created_by: Optional[str] = None
    ) -> int:
        """Save a generated title to database"""
        session = self.Session()
        try:
            title_obj = GeneratedTitle(
                source_type=source_type,
                source_id=source_id,
                filter_sector=filter_sector,
                filter_category=filter_category,
                filter_source=filter_source,
                topic=topic,
                title=title,
                created_by=created_by
            )
            session.add(title_obj)
            session.commit()
            title_id = title_obj.id
            logger.info(f"Saved title with ID: {title_id}")
            return title_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving title: {e}")
            raise
        finally:
            session.close()
    
    def get_titles(
        self,
        source_type: Optional[str] = None,
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None,
        topic: Optional[str] = None,
        is_used: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[GeneratedTitle]:
        """Get saved titles with filters"""
        session = self.Session()
        try:
            query = session.query(GeneratedTitle)
            
            if source_type:
                query = query.filter(GeneratedTitle.source_type == source_type)
            if filter_sector:
                query = query.filter(GeneratedTitle.filter_sector == filter_sector)
            if filter_category:
                query = query.filter(GeneratedTitle.filter_category == filter_category)
            if filter_source:
                query = query.filter(GeneratedTitle.filter_source == filter_source)
            if topic:
                query = query.filter(GeneratedTitle.topic.ilike(f"%{topic}%"))
            if is_used is not None:
                query = query.filter(GeneratedTitle.is_used == is_used)
            
            query = query.order_by(GeneratedTitle.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            return query.all()
        finally:
            session.close()
    
    def generate_social_content(
        self,
        topic: str,
        title: str,
        source_type: str,
        tone: str = "professional",
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None
    ) -> str:
        """Generate social media content based on title and filters"""
        # Choose index based on source type
        if source_type == "jobs":
            index = self._get_jobs_index()
        else:
            index = self._get_news_index()
        
        # Build filters
        filter_list = []
        if source_type == "jobs" and filter_sector:
            filter_list.append(MetadataFilter(key="sector", value=filter_sector, operator=FilterOperator.EQ))
        elif source_type == "news":
            if filter_category:
                filter_list.append(MetadataFilter(key="category", value=filter_category, operator=FilterOperator.EQ))
            if filter_source:
                filter_list.append(MetadataFilter(key="source", value=filter_source, operator=FilterOperator.EQ))
        
        filters = MetadataFilters(filters=filter_list) if filter_list else None
        
        # Create query engine
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            filters=filters,
            llm=self.llm
        )
        
        # Create prompt based on tone
        prompt = f"""Based on the retrieved content about "{topic}", create engaging social media content with the title: "{title}"

Tone: {tone}
Topic: {topic}

Requirements:
- Create concise, engaging content suitable for social media platforms
- Use a {tone} tone
- Include relevant insights from the retrieved data
- Keep it between 150-250 characters
- Make it shareable and engaging
- Do NOT include hashtags or emojis

Return only the social media content text."""

        response = query_engine.query(prompt)
        return str(response).strip()
    
    def save_social_content(
        self,
        content: str,
        source_type: str,
        topic: str,
        title: str,
        tone: str,
        title_id: Optional[int] = None,
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> int:
        """Save generated social media content to database"""
        session = self.Session()
        try:
            social_obj = GeneratedSocialContent(
                title_id=title_id,
                source_type=source_type,
                filter_sector=filter_sector,
                filter_category=filter_category,
                filter_source=filter_source,
                topic=topic,
                title=title,
                content=content,
                tone=tone,
                created_by=created_by
            )
            session.add(social_obj)
            session.commit()
            content_id = social_obj.id
            logger.info(f"Saved social content with ID: {content_id}")
            return content_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving social content: {e}")
            raise
        finally:
            session.close()
    
    def get_social_content(
        self,
        source_type: Optional[str] = None,
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None,
        is_published: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[GeneratedSocialContent]:
        """Get saved social content with filters"""
        session = self.Session()
        try:
            query = session.query(GeneratedSocialContent)
            
            if source_type:
                query = query.filter(GeneratedSocialContent.source_type == source_type)
            if filter_sector:
                query = query.filter(GeneratedSocialContent.filter_sector == filter_sector)
            if filter_category:
                query = query.filter(GeneratedSocialContent.filter_category == filter_category)
            if filter_source:
                query = query.filter(GeneratedSocialContent.filter_source == filter_source)
            if is_published is not None:
                query = query.filter(GeneratedSocialContent.is_published == is_published)
            
            query = query.order_by(GeneratedSocialContent.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            return query.all()
        finally:
            session.close()
    
    def generate_blog(
        self,
        title: str,
        topic: str,
        source_type: str,
        tone: str = "professional",
        length: str = "medium",
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate blog content based on title and filters"""
        # Choose index based on source type
        if source_type == "jobs":
            index = self._get_jobs_index()
        else:
            index = self._get_news_index()
        
        # Build filters
        filter_list = []
        if source_type == "jobs" and filter_sector:
            filter_list.append(MetadataFilter(key="sector", value=filter_sector, operator=FilterOperator.EQ))
        elif source_type == "news":
            if filter_category:
                filter_list.append(MetadataFilter(key="category", value=filter_category, operator=FilterOperator.EQ))
            if filter_source:
                filter_list.append(MetadataFilter(key="source", value=filter_source, operator=FilterOperator.EQ))
        
        filters = MetadataFilters(filters=filter_list) if filter_list else None
        
        # Create query engine
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            filters=filters,
            llm=self.llm
        )
        
        # Determine target word count based on length
        word_counts = {"short": 500, "medium": 1000, "long": 1500}
        target_words = word_counts.get(length, 1000)
        
        # Create prompt
        prompt = f"""Based on the retrieved content, write a comprehensive blog post with the title: "{title}"

Topic: {topic}
Tone: {tone}
Target Length: {target_words} words

Requirements:
- Write in a {tone} tone
- Create well-structured content with clear sections
- Base the content on the retrieved data
- Include insights, trends, and valuable information
- Make it informative and engaging
- Aim for approximately {target_words} words

Return the blog content in markdown format with proper headings."""

        response = query_engine.query(prompt)
        content = str(response).strip()
        
        # Count words
        word_count = len(content.split())
        
        # Generate summary (first 200 chars)
        summary = content[:200] + "..." if len(content) > 200 else content
        
        return {
            "content": content,
            "word_count": word_count,
            "summary": summary
        }
    
    def save_blog(
        self,
        title: str,
        content: str,
        source_type: str,
        tone: str,
        length: str,
        word_count: int,
        summary: Optional[str] = None,
        title_id: Optional[int] = None,
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> int:
        """Save generated blog to database"""
        session = self.Session()
        try:
            blog_obj = GeneratedBlog(
                title_id=title_id,
                source_type=source_type,
                filter_sector=filter_sector,
                filter_category=filter_category,
                filter_source=filter_source,
                title=title,
                content=content,
                summary=summary,
                word_count=word_count,
                tone=tone,
                length=length,
                created_by=created_by
            )
            session.add(blog_obj)
            session.commit()
            blog_id = blog_obj.id
            logger.info(f"Saved blog with ID: {blog_id}")
            return blog_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving blog: {e}")
            raise
        finally:
            session.close()
    
    def get_blogs(
        self,
        source_type: Optional[str] = None,
        filter_sector: Optional[str] = None,
        filter_category: Optional[str] = None,
        filter_source: Optional[str] = None,
        is_published: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[GeneratedBlog]:
        """Get saved blogs with filters"""
        session = self.Session()
        try:
            query = session.query(GeneratedBlog)
            
            if source_type:
                query = query.filter(GeneratedBlog.source_type == source_type)
            if filter_sector:
                query = query.filter(GeneratedBlog.filter_sector == filter_sector)
            if filter_category:
                query = query.filter(GeneratedBlog.filter_category == filter_category)
            if filter_source:
                query = query.filter(GeneratedBlog.filter_source == filter_source)
            if is_published is not None:
                query = query.filter(GeneratedBlog.is_published == is_published)
            
            query = query.order_by(GeneratedBlog.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            return query.all()
        finally:
            session.close()
