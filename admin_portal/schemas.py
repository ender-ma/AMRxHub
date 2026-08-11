from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ResearchOutput(BaseModel):
    title: Optional[str]
    summary: Optional[str]
    authors: Optional[List[str]] = []
    publication_date: Optional[str]
    doi: Optional[str]
    license: Optional[str]
    institution: Optional[str]
    website: Optional[str]
    screenshots: Optional[List[str]] = []
    missing_fields: Optional[List[str]] = []
    raw: Optional[Dict[str, Any]] = None


class ClassificationOutput(BaseModel):
    object_type: Optional[str]
    tool_type: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    organisms: Optional[List[str]] = []
    research_functions: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    confidence_score: float = 0.0
    classification_rationale: Optional[str]
    taxonomy_review_required: bool = False
    suggested_taxonomy_change: Optional[str]
    raw: Optional[Dict[str, Any]] = None


class ToolMetadata(BaseModel):
    name: Optional[str]
    short_description: Optional[str]
    detailed_description: Optional[str]
    category: Optional[str]
    url: Optional[str]
    tool_type: Optional[str]
    institution: Optional[str]
    author: Optional[str]
    version: Optional[str]
    license: Optional[str]
    logo: Optional[str]
    screenshot: Optional[str]
    features: Optional[List[str]] = []
    requirements: Optional[List[str]] = []
    raw: Optional[Dict[str, Any]] = None


class ResourceMetadata(BaseModel):
    category: Optional[str]
    title: Optional[str]
    description: Optional[str]
    link: Optional[str]
    link_text: Optional[str]
    link_icons: Optional[List[str]] = []
    pdf_file: Optional[str]
    image: Optional[str]
    raw: Optional[Dict[str, Any]] = None


class QualityOutput(BaseModel):
    overall_quality_score: float = 0.0
    evidence_quality_score: float = 0.0
    metadata_completeness_score: float = 0.0
    classification_confidence: float = 0.0
    issues: Optional[List[str]] = []
    final_recommendation: Optional[str]
    raw: Optional[Dict[str, Any]] = None


class PipelineOutput(BaseModel):
    research: Optional[ResearchOutput]
    classification: Optional[ClassificationOutput]
    metadata: Optional[Dict[str, Any]]
    quality: Optional[QualityOutput]
    raw: Optional[Dict[str, Any]] = None
