"""
API endpoints for content generation using LlamaIndex + Azure OpenAI
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.content import (
    FilterOptionsResponse,
    TitleGenerationRequest,
    TitleGenerationResponse,
    SaveTitleRequest,
    SavedTitle,
    ListTitlesRequest,
    GenerateSocialContentRequest,
    SavedSocialContent,
    GenerateBlogRequest,
    SavedBlog,
    ListContentRequest,
)
from services.query_engine import PortalQueryEngine
from typing import List

router = APIRouter(prefix="/content", tags=["Content Generation"])

# Initialize query engine (singleton)
query_engine = PortalQueryEngine()


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_filter_options():
    """
    Get available filter options for content generation
    
    Returns:
        - news_categories: List of unique categories from news_articles
        - news_sources: List of unique sources from news_articles
        - job_sectors: List of unique sectors from jobs
    """
    try:
        categories = query_engine.get_news_categories()
        sources = query_engine.get_news_sources()
        sectors = query_engine.get_job_sectors()
        
        return FilterOptionsResponse(
            news_categories=categories,
            news_sources=sources,
            job_sectors=sectors
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")


@router.post("/generate-titles", response_model=TitleGenerationResponse)
async def generate_titles(request: TitleGenerationRequest):
    """
    Generate blog titles using RAG with metadata filters
    
    Filters:
    - For jobs: sector
    - For news: category, source
    
    Process:
    1. Apply metadata filters to narrow down content
    2. Perform vector similarity search in PgVector
    3. Retrieve top-k similar documents
    4. Send to Azure OpenAI LLM to generate titles
    """
    try:
        # Track applied filters
        filters_applied = {}
        
        # Use empty string if topic is None
        topic = request.topic or ""
        
        if request.source_type == "jobs":
            # Generate from job postings
            if request.sector:
                filters_applied["sector"] = request.sector
            
            titles = query_engine.generate_titles_from_jobs(
                topic=topic,
                sector=request.sector,
                num_titles=request.count
            )
        
        elif request.source_type == "news":
            # Generate from news articles
            if request.category:
                filters_applied["category"] = request.category
            if request.source:
                filters_applied["source"] = request.source
            
            titles = query_engine.generate_titles_from_news(
                topic=topic,
                category=request.category,
                source=request.source,
                num_titles=request.count
            )
        
        else:
            raise HTTPException(status_code=400, detail="source_type must be 'jobs' or 'news'")
        
        return TitleGenerationResponse(
            topic=topic,
            source_type=request.source_type,
            filters_applied=filters_applied,
            titles=titles
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Title generation failed: {str(e)}")


# ========== Content Library Endpoints ==========

@router.post("/titles/save", response_model=dict)
async def save_title(request: SaveTitleRequest):
    """Save a generated title to the database"""
    try:
        title_id = query_engine.save_title(
            source_type=request.source_type,
            topic=request.topic,
            title=request.title,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source,
            source_id=request.source_id
        )
        return {"id": title_id, "message": "Title saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save title: {str(e)}")


@router.post("/titles/list", response_model=List[SavedTitle])
async def list_titles(request: ListTitlesRequest):
    """Get saved titles with optional filters"""
    try:
        titles = query_engine.get_titles(
            source_type=request.source_type,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source,
            topic=request.topic,
            is_used=request.is_used,
            limit=request.limit,
            offset=request.offset
        )
        
        # Convert to Pydantic models
        return [
            SavedTitle(
                id=t.id,
                source_type=t.source_type,
                source_id=t.source_id,
                filter_sector=t.filter_sector,
                filter_category=t.filter_category,
                filter_source=t.filter_source,
                topic=t.topic,
                title=t.title,
                is_used=t.is_used,
                used_count=t.used_count,
                created_at=t.created_at.isoformat() if t.created_at else None,
                created_by=t.created_by
            )
            for t in titles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list titles: {str(e)}")


@router.post("/social/generate", response_model=dict)
async def generate_social_content(request: GenerateSocialContentRequest):
    """Generate and save social media content"""
    try:
        # Generate content
        content = query_engine.generate_social_content(
            topic=request.topic,
            title=request.title or "",
            source_type=request.source_type,
            tone=request.tone,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source
        )
        
        # Save to database
        content_id = query_engine.save_social_content(
            content=content,
            source_type=request.source_type,
            topic=request.topic,
            title=request.title or "",
            tone=request.tone,
            title_id=request.title_id,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source
        )
        
        return {
            "id": content_id,
            "content": content,
            "message": "Social content generated and saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate social content: {str(e)}")


@router.post("/social/list", response_model=List[SavedSocialContent])
async def list_social_content(request: ListContentRequest):
    """Get saved social media content with optional filters"""
    try:
        content_list = query_engine.get_social_content(
            source_type=request.source_type,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source,
            is_published=request.is_published,
            limit=request.limit,
            offset=request.offset
        )
        
        return [
            SavedSocialContent(
                id=c.id,
                title_id=c.title_id,
                source_type=c.source_type,
                filter_sector=c.filter_sector,
                filter_category=c.filter_category,
                filter_source=c.filter_source,
                topic=c.topic,
                title=c.title,
                content=c.content,
                tone=c.tone,
                is_published=c.is_published,
                published_at=c.published_at.isoformat() if c.published_at else None,
                created_at=c.created_at.isoformat() if c.created_at else None,
                created_by=c.created_by
            )
            for c in content_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list social content: {str(e)}")


@router.post("/blogs/generate", response_model=dict)
async def generate_blog(request: GenerateBlogRequest):
    """Generate and save blog content"""
    try:
        # Generate blog
        result = query_engine.generate_blog(
            title=request.title,
            topic=request.topic,
            source_type=request.source_type,
            tone=request.tone,
            length=request.length,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source
        )
        
        # Save to database
        blog_id = query_engine.save_blog(
            title=request.title,
            content=result["content"],
            source_type=request.source_type,
            tone=request.tone,
            length=request.length,
            word_count=result["word_count"],
            summary=result["summary"],
            title_id=request.title_id,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source
        )
        
        return {
            "id": blog_id,
            "content": result["content"],
            "word_count": result["word_count"],
            "summary": result["summary"],
            "message": "Blog generated and saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate blog: {str(e)}")


@router.post("/blogs/list", response_model=List[SavedBlog])
async def list_blogs(request: ListContentRequest):
    """Get saved blogs with optional filters"""
    try:
        blogs = query_engine.get_blogs(
            source_type=request.source_type,
            filter_sector=request.filter_sector,
            filter_category=request.filter_category,
            filter_source=request.filter_source,
            is_published=request.is_published,
            limit=request.limit,
            offset=request.offset
        )
        
        return [
            SavedBlog(
                id=b.id,
                title_id=b.title_id,
                source_type=b.source_type,
                filter_sector=b.filter_sector,
                filter_category=b.filter_category,
                filter_source=b.filter_source,
                title=b.title,
                content=b.content,
                summary=b.summary,
                tags=b.tags,
                word_count=b.word_count,
                tone=b.tone,
                length=b.length,
                is_published=b.is_published,
                published_at=b.published_at.isoformat() if b.published_at else None,
                published_url=b.published_url,
                meta_description=b.meta_description,
                keywords=b.keywords,
                created_at=b.created_at.isoformat() if b.created_at else None,
                updated_at=b.updated_at.isoformat() if b.updated_at else None,
                created_by=b.created_by
            )
            for b in blogs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list blogs: {str(e)}")
