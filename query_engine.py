"""
Query Engine for Content Generation using RAG
"""
import logging
from typing import List, Optional, Dict, Any
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response.schema import Response
from indexer import JobIndexer, TNNewsIndexer, AIJobIndexer
from config import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate blog content using RAG"""
    
    def __init__(self):
        self.job_indexer = JobIndexer()
        self.news_indexer = TNNewsIndexer()
        self.ai_job_indexer = AIJobIndexer()
        
        # Get indexes
        self.job_index = self.job_indexer.get_index()
        self.news_index = self.news_indexer.get_index()
        self.ai_job_index = self.ai_job_indexer.get_index()
    
    def _create_query_engine(
        self, 
        index: VectorStoreIndex,
        similarity_top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> RetrieverQueryEngine:
        """Create a query engine with optional metadata filters"""
        
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k,
        )
        
        query_engine = RetrieverQueryEngine(retriever=retriever)
        
        return query_engine
    
    def generate_blog_title(
        self,
        topic: str,
        source: str = "jobs",
        num_suggestions: int = 5
    ) -> List[str]:
        """
        Generate blog title suggestions based on indexed data
        
        Args:
            topic: The topic/keyword for the blog
            source: Data source (jobs, tnnews, aijobs)
            num_suggestions: Number of title suggestions
        
        Returns:
            List of blog title suggestions
        """
        index = self._get_index_by_source(source)
        query_engine = self._create_query_engine(index, similarity_top_k=10)
        
        prompt = f"""
        Based on the retrieved data about '{topic}', generate {num_suggestions} engaging blog post titles.
        Make them SEO-friendly, specific, and attention-grabbing.
        Format: Return only the titles, one per line, numbered 1-{num_suggestions}.
        """
        
        response = query_engine.query(prompt)
        
        # Parse titles from response
        titles = self._parse_titles(str(response), num_suggestions)
        
        return titles
    
    def generate_blog_content(
        self,
        title: str,
        source: str = "jobs",
        word_count: int = 800,
        style: str = "informative"
    ) -> Dict[str, Any]:
        """
        Generate complete blog content
        
        Args:
            title: Blog title
            source: Data source (jobs, tnnews, aijobs)
            word_count: Target word count
            style: Writing style (informative, listicle, analytical)
        
        Returns:
            Dictionary with title, content, tags, summary
        """
        index = self._get_index_by_source(source)
        query_engine = self._create_query_engine(index, similarity_top_k=15)
        
        prompt = f"""
        Write a comprehensive blog post with the title: "{title}"
        
        Requirements:
        - Style: {style}
        - Length: Approximately {word_count} words
        - Include relevant data points from the retrieved information
        - Add appropriate subheadings
        - Make it engaging and valuable for readers
        - Cite specific examples from the data where possible
        
        Format the response as:
        CONTENT:
        [Your blog content here]
        
        TAGS:
        [Comma-separated relevant tags]
        
        SUMMARY:
        [A 2-3 sentence summary]
        """
        
        response = query_engine.query(prompt)
        
        result = self._parse_blog_content(str(response), title)
        
        # Add metadata
        result["word_count"] = len(result["content"].split())
        result["source"] = source
        
        return result
    
    def generate_trend_analysis(
        self,
        topic: str,
        source: str = "jobs",
        time_period: Optional[str] = None
    ) -> str:
        """
        Generate trend analysis content
        
        Args:
            topic: Topic to analyze
            source: Data source
            time_period: Optional time period filter
        
        Returns:
            Trend analysis content
        """
        index = self._get_index_by_source(source)
        query_engine = self._create_query_engine(index, similarity_top_k=20)
        
        prompt = f"""
        Analyze trends related to '{topic}' based on the retrieved data.
        
        Include:
        1. Key patterns and trends
        2. Notable statistics
        3. Emerging themes
        4. Regional variations (if applicable)
        5. Salary trends (if applicable)
        6. Skills in demand (if applicable)
        
        Provide a data-driven analysis with specific examples.
        """
        
        if time_period:
            prompt += f"\nFocus on data from: {time_period}"
        
        response = query_engine.query(prompt)
        
        return str(response)
    
    def generate_comparison_content(
        self,
        item1: str,
        item2: str,
        source: str = "jobs"
    ) -> str:
        """
        Generate comparison content between two items
        
        Args:
            item1: First item to compare (e.g., "Data Scientist")
            item2: Second item to compare (e.g., "Data Engineer")
            source: Data source
        
        Returns:
            Comparison content
        """
        index = self._get_index_by_source(source)
        query_engine = self._create_query_engine(index, similarity_top_k=20)
        
        prompt = f"""
        Create a detailed comparison between '{item1}' and '{item2}' based on the retrieved data.
        
        Compare:
        - Key characteristics
        - Requirements
        - Salary ranges
        - Location availability
        - Skills needed
        - Career prospects
        
        Present in a clear, structured format.
        """
        
        response = query_engine.query(prompt)
        
        return str(response)
    
    def search_similar_content(
        self,
        query: str,
        source: str = "jobs",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content (for research/inspiration)
        
        Args:
            query: Search query
            source: Data source
            top_k: Number of results
        
        Returns:
            List of similar documents with metadata
        """
        index = self._get_index_by_source(source)
        
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=top_k,
        )
        
        nodes = retriever.retrieve(query)
        
        results = []
        for node in nodes:
            results.append({
                "text": node.text,
                "metadata": node.metadata,
                "score": node.score
            })
        
        return results
    
    # Helper methods
    
    def _get_index_by_source(self, source: str) -> VectorStoreIndex:
        """Get index by source name"""
        if source == "jobs":
            return self.job_index
        elif source == "tnnews":
            return self.news_index
        elif source == "aijobs":
            return self.ai_job_index
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def _parse_titles(self, response: str, num_suggestions: int) -> List[str]:
        """Parse titles from LLM response"""
        lines = response.strip().split('\n')
        titles = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                title = line.lstrip('0123456789.-) ').strip()
                if title:
                    titles.append(title)
        
        return titles[:num_suggestions]
    
    def _parse_blog_content(self, response: str, title: str) -> Dict[str, Any]:
        """Parse structured blog content from response"""
        result = {
            "title": title,
            "content": "",
            "tags": [],
            "summary": ""
        }
        
        # Simple parsing - you may want to improve this
        parts = response.split("TAGS:")
        
        if len(parts) >= 2:
            content_part = parts[0].replace("CONTENT:", "").strip()
            result["content"] = content_part
            
            tags_summary = parts[1].split("SUMMARY:")
            if len(tags_summary) >= 2:
                tags_str = tags_summary[0].strip()
                result["tags"] = [tag.strip() for tag in tags_str.split(',')]
                result["summary"] = tags_summary[1].strip()
            else:
                result["tags"] = [tag.strip() for tag in tags_summary[0].strip().split(',')]
        else:
            result["content"] = response.strip()
        
        return result
