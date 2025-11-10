"""
API endpoints for indexing statistics and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
import sys

from core.database import get_db
from core.config import settings
from schemas.indexing import (
    IndexingStats,
    IndexingStatsResponse,
    CrawlerStatusResponse,
    CrawlerStatus,
    DashboardStats
)

# Add indexer path to import models
sys.path.insert(0, settings.indexer_path)
from models import Job, NewsArticle, TNNews, AIJob

router = APIRouter(prefix="/indexing", tags=["Indexing"])


@router.get("/stats", response_model=IndexingStatsResponse)
async def get_indexing_stats(db: Session = Depends(get_db)):
    """
    Get indexing statistics for all tables
    """
    tables_config = [
        {"name": "jobs", "model": Job, "vector_table": f"{settings.vector_table_prefix}_jobs"},
        {"name": "news_articles", "model": NewsArticle, "vector_table": f"{settings.vector_table_prefix}_news_articles"},
        {"name": "tnnews", "model": TNNews, "vector_table": f"{settings.vector_table_prefix}_tnnews"},
        {"name": "aijobs", "model": AIJob, "vector_table": f"{settings.vector_table_prefix}_aijobs"},
    ]
    
    stats = {}
    total_records = 0
    total_indexed = 0
    
    for table_config in tables_config:
        table_name = table_config["name"]
        model = table_config["model"]
        
        # Get total count
        total = db.query(func.count(model.id)).scalar() or 0
        
        # Get indexed count (where index_status = 1)
        indexed = db.query(func.count(model.id)).filter(model.index_status == 1).scalar() or 0
        
        # Get last updated
        last_updated = db.query(func.max(model.updated_at)).scalar()
        
        # Calculate percentage
        percentage = (indexed / total * 100) if total > 0 else 0.0
        
        stats[table_name] = IndexingStats(
            table_name=table_name,
            total_records=total,
            indexed_records=indexed,
            unindexed_records=total - indexed,
            index_percentage=round(percentage, 2),
            last_updated=last_updated,
            vector_table=table_config["vector_table"]
        )
        
        total_records += total
        total_indexed += indexed
    
    overall_percentage = (total_indexed / total_records * 100) if total_records > 0 else 0.0
    
    return IndexingStatsResponse(
        stats=stats,
        total_records=total_records,
        total_indexed=total_indexed,
        overall_percentage=round(overall_percentage, 2)
    )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get overall dashboard statistics
    """
    # Count records in each table
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    total_news = db.query(func.count(NewsArticle.id)).scalar() or 0
    total_tnnews = db.query(func.count(TNNews.id)).scalar() or 0
    total_aijobs = db.query(func.count(AIJob.id)).scalar() or 0
    
    # Count indexed today (you can modify this logic based on your needs)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    indexed_today = db.query(func.count(Job.id)).filter(
        func.date(Job.updated_at) == today,
        Job.index_status == 1
    ).scalar() or 0
    
    # Calculate overall indexing success rate
    total_records = total_jobs + total_news + total_tnnews + total_aijobs
    total_indexed = (
        db.query(func.count(Job.id)).filter(Job.index_status == 1).scalar() or 0
    ) + (
        db.query(func.count(NewsArticle.id)).filter(NewsArticle.index_status == 1).scalar() or 0
    ) + (
        db.query(func.count(TNNews.id)).filter(TNNews.index_status == 1).scalar() or 0
    ) + (
        db.query(func.count(AIJob.id)).filter(AIJob.index_status == 1).scalar() or 0
    )
    
    success_rate = (total_indexed / total_records * 100) if total_records > 0 else 0.0
    
    return DashboardStats(
        total_jobs=total_jobs,
        total_news=total_news,
        total_tnnews=total_tnnews,
        total_aijobs=total_aijobs,
        indexed_today=indexed_today,
        crawlers_active=0,  # TODO: Implement crawler status tracking
        indexing_success_rate=round(success_rate, 2)
    )


@router.get("/crawlers", response_model=CrawlerStatusResponse)
async def get_crawler_status():
    """
    Get status of all crawlers
    Note: This is a placeholder. Implement based on your crawler architecture.
    """
    # TODO: Implement actual crawler status tracking
    # For now, return mock data
    crawlers = [
        CrawlerStatus(
            name="Jobs Crawler",
            status="scheduled",
            last_run=None,
            next_run=None,
            records_crawled=0,
            success_rate=0.0
        ),
        CrawlerStatus(
            name="News Crawler",
            status="scheduled",
            last_run=None,
            next_run=None,
            records_crawled=0,
            success_rate=0.0
        ),
    ]
    
    return CrawlerStatusResponse(crawlers=crawlers)
