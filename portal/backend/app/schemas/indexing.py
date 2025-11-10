"""
Pydantic schemas for indexing-related API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class IndexingStats(BaseModel):
    """Statistics for a single table's indexing status"""
    table_name: str
    total_records: int
    indexed_records: int
    unindexed_records: int
    index_percentage: float
    last_updated: Optional[datetime] = None
    vector_table: str


class IndexingStatsResponse(BaseModel):
    """Response with indexing statistics for all tables"""
    stats: Dict[str, IndexingStats]
    total_records: int
    total_indexed: int
    overall_percentage: float


class CrawlerStatus(BaseModel):
    """Status of a crawler"""
    name: str
    status: str  # "running", "stopped", "scheduled", "error"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    records_crawled: int = 0
    success_rate: float = 0.0


class CrawlerStatusResponse(BaseModel):
    """Response with all crawler statuses"""
    crawlers: list[CrawlerStatus]


class DashboardStats(BaseModel):
    """Overall dashboard statistics"""
    total_jobs: int
    total_news: int
    total_tnnews: int
    total_aijobs: int
    indexed_today: int
    crawlers_active: int
    indexing_success_rate: float
