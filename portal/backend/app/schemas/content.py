"""
Pydantic schemas for content generation API
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ContentSearchRequest(BaseModel):
    """Request to search indexed content"""
    query: str = Field(..., description="Search query for semantic search")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    sources: List[str] = Field(
        default=["jobs", "news_articles"], 
        description="Sources to search (jobs, news_articles, tnnews, aijobs)"
    )


class ContentSearchResult(BaseModel):
    """Single search result"""
    source: str
    title: str
    content: str
    score: float
    metadata: dict


class ContentSearchResponse(BaseModel):
    """Response with search results"""
    query: str
    results: List[ContentSearchResult]
    total_found: int


class FilterOptionsResponse(BaseModel):
    """Available filter options"""
    news_categories: List[str]
    news_sources: List[str]
    job_sectors: List[str]


class TitleGenerationRequest(BaseModel):
    """Request to generate blog titles"""
    topic: Optional[str] = Field(None, description="Topic or keywords for title generation")
    source_type: str = Field(..., description="Source type: 'jobs' or 'news'")
    count: int = Field(default=5, ge=1, le=10, description="Number of titles to generate")
    
    # Filters for jobs
    sector: Optional[str] = Field(None, description="Job sector filter (only for jobs)")
    
    # Filters for news
    category: Optional[str] = Field(None, description="News category filter (only for news)")
    source: Optional[str] = Field(None, description="News source filter (only for news)")


class TitleGenerationResponse(BaseModel):
    """Response with generated titles"""
    topic: str
    source_type: str
    filters_applied: dict
    titles: List[str]


class BlogGenerationRequest(BaseModel):
    """Request to generate blog content"""
    title: str = Field(..., description="Blog title")
    context_query: Optional[str] = Field(None, description="Query to get relevant context from indexed data")
    tone: str = Field(default="professional", description="Writing tone (professional, casual, technical)")
    length: str = Field(default="medium", description="Content length (short, medium, long)")


class BlogGenerationResponse(BaseModel):
    """Response with generated blog content"""
    title: str
    content: str
    word_count: int
    sources_used: int


# Content Library Schemas

class SavedTitle(BaseModel):
    """Saved title from database"""
    id: int
    source_type: str
    source_id: Optional[int]
    filter_sector: Optional[str]
    filter_category: Optional[str]
    filter_source: Optional[str]
    topic: str
    title: str
    is_used: bool
    used_count: int
    created_at: str
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class SaveTitleRequest(BaseModel):
    """Request to save a generated title"""
    source_type: str
    topic: str
    title: str
    filter_sector: Optional[str] = None
    filter_category: Optional[str] = None
    filter_source: Optional[str] = None
    source_id: Optional[int] = None


class ListTitlesRequest(BaseModel):
    """Request to list saved titles with filters"""
    source_type: Optional[str] = None
    filter_sector: Optional[str] = None
    filter_category: Optional[str] = None
    filter_source: Optional[str] = None
    topic: Optional[str] = None
    is_used: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class SavedSocialContent(BaseModel):
    """Saved social media content from database"""
    id: int
    title_id: Optional[int]
    source_type: str
    filter_sector: Optional[str]
    filter_category: Optional[str]
    filter_source: Optional[str]
    topic: Optional[str]
    title: Optional[str]
    content: str
    tone: Optional[str]
    is_published: bool
    published_at: Optional[str]
    created_at: str
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class GenerateSocialContentRequest(BaseModel):
    """Request to generate social media content"""
    title_id: Optional[int] = None
    title: Optional[str] = None
    topic: str
    source_type: str
    tone: str = Field(default="professional", description="Tone: professional, casual, engaging, informative")
    filter_sector: Optional[str] = None
    filter_category: Optional[str] = None
    filter_source: Optional[str] = None


class SavedBlog(BaseModel):
    """Saved blog from database"""
    id: int
    title_id: Optional[int]
    source_type: str
    filter_sector: Optional[str]
    filter_category: Optional[str]
    filter_source: Optional[str]
    title: str
    content: str
    summary: Optional[str]
    tags: Optional[List[str]]
    word_count: Optional[int]
    tone: Optional[str]
    length: Optional[str]
    is_published: bool
    published_at: Optional[str]
    published_url: Optional[str]
    meta_description: Optional[str]
    keywords: Optional[List[str]]
    created_at: str
    updated_at: Optional[str]
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class GenerateBlogRequest(BaseModel):
    """Request to generate blog content"""
    title_id: Optional[int] = None
    title: str
    topic: str
    source_type: str
    tone: str = Field(default="professional", description="Tone: professional, casual, technical, engaging")
    length: str = Field(default="medium", description="Length: short, medium, long")
    filter_sector: Optional[str] = None
    filter_category: Optional[str] = None
    filter_source: Optional[str] = None


class ListContentRequest(BaseModel):
    """Request to list saved social content or blogs"""
    source_type: Optional[str] = None
    filter_sector: Optional[str] = None
    filter_category: Optional[str] = None
    filter_source: Optional[str] = None
    is_published: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
