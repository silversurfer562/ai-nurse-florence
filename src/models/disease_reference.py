"""
Disease Reference Database Models

Two-tier diagnosis system:
- Tier 1: Full diagnosis library (500-1,000 curated conditions) -> DiagnosisContentMap
- Tier 2: Reference lookup (20,000+ conditions) -> DiseaseReference (this file)

The reference database provides lightweight lookup for rare/uncommon diseases
that don't warrant full clinical content, but users may need to search for.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Index
from datetime import datetime, timedelta

# Create a sync Base for disease reference (separate from async Base in src.models.database)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class DiseaseReference(Base):
    """
    Lightweight reference database for 20,000+ diseases from MONDO.

    This table provides quick lookup and external resource links for diseases
    not in the full clinical library. NO treatment/medication info stored here.

    Use cases:
    - User searches for rare disease -> show basic info + external links
    - Quick ICD-10/SNOMED lookup for documentation
    - "Promote to full library" workflow for frequently searched diseases
    """
    __tablename__ = "disease_reference"

    # Primary identifiers
    mondo_id = Column(String(50), primary_key=True)  # MONDO:0010526
    disease_name = Column(String(300), nullable=False, index=True)  # Primary name
    disease_synonyms = Column(JSON, nullable=True)  # ["Fabry disease", "Anderson-Fabry disease"]

    # Coding standards
    icd10_codes = Column(JSON, nullable=True)  # ["E75.21"] (some diseases have multiple)
    snomed_code = Column(String(20), nullable=True, index=True)  # 16652001
    umls_code = Column(String(20), nullable=True)  # C0002986
    orphanet_code = Column(String(20), nullable=True)  # For rare diseases

    # Brief clinical info (1-2 sentences only)
    short_description = Column(Text, nullable=True)  # "A rare X-linked lysosomal storage disorder..."
    disease_category = Column(String(100), nullable=True)  # "Metabolic", "Infectious", etc.

    # Prevalence flags
    is_rare_disease = Column(Boolean, default=False)  # <1 in 2,000 people
    estimated_prevalence = Column(String(100), nullable=True)  # "1 in 40,000 males"

    # External resource links (auto-generated)
    medlineplus_url = Column(String(500), nullable=True)
    pubmed_search_url = Column(String(500), nullable=True)
    mondo_url = Column(String(500), nullable=True)

    # Usage tracking (for "promote to full library" decision)
    search_count = Column(JSON, default=dict)  # {"2025-01": 5, "2025-02": 12}
    last_searched_at = Column(DateTime, nullable=True)

    # Admin flags
    promoted_to_full_library = Column(Boolean, default=False)
    promotion_date = Column(DateTime, nullable=True)

    # Billable code tracking (CMS guidelines)
    is_billable = Column(Boolean, default=True)  # Can this code be billed?
    billable_note = Column(String(200), nullable=True)  # Warning if not fully billable

    # Metadata
    data_source = Column(String(50), default="MONDO")  # Track where data came from
    imported_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for fast search
    __table_args__ = (
        Index('idx_disease_name_search', 'disease_name'),
        Index('idx_icd10_lookup', 'icd10_codes'),
        Index('idx_snomed_lookup', 'snomed_code'),
        Index('idx_category', 'disease_category'),
        Index('idx_rare_disease', 'is_rare_disease'),
    )

    def increment_search_count(self):
        """Track how often this disease is searched (for promotion decisions)"""
        current_month = datetime.utcnow().strftime("%Y-%m")

        if not self.search_count:
            self.search_count = {}

        self.search_count[current_month] = self.search_count.get(current_month, 0) + 1
        self.last_searched_at = datetime.utcnow()

    def get_total_searches(self):
        """Get total search count across all time"""
        if not self.search_count:
            return 0
        return sum(self.search_count.values())

    def get_recent_search_count(self, months=3):
        """Get search count for last N months"""
        if not self.search_count:
            return 0

        current_date = datetime.utcnow()
        count = 0

        for i in range(months):
            month_key = (current_date.replace(day=1) - timedelta(days=i*30)).strftime("%Y-%m")
            count += self.search_count.get(month_key, 0)

        return count

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "mondo_id": self.mondo_id,
            "disease_name": self.disease_name,
            "disease_synonyms": self.disease_synonyms or [],
            "icd10_codes": self.icd10_codes or [],
            "snomed_code": self.snomed_code,
            "short_description": self.short_description,
            "disease_category": self.disease_category,
            "is_rare_disease": self.is_rare_disease,
            "estimated_prevalence": self.estimated_prevalence,
            "billable_status": {
                "is_billable": self.is_billable,
                "note": self.billable_note
            },
            "external_resources": {
                "medlineplus": self.medlineplus_url,
                "pubmed": self.pubmed_search_url,
                "mondo": self.mondo_url or f"https://monarchinitiative.org/disease/{self.mondo_id}"
            },
            "search_stats": {
                "total_searches": self.get_total_searches(),
                "last_searched": self.last_searched_at.isoformat() if self.last_searched_at else None
            },
            "promoted_to_full_library": self.promoted_to_full_library
        }


class DiagnosisPromotionQueue(Base):
    """
    Staging table for promoting reference diseases to full clinical library.

    Workflow:
    1. User/admin marks disease for promotion
    2. Clinical team reviews and adds full content
    3. Promoted to DiagnosisContentMap
    4. Marked as completed
    """
    __tablename__ = "diagnosis_promotion_queue"

    id = Column(String(50), primary_key=True)
    mondo_id = Column(String(50), nullable=False, index=True)
    disease_name = Column(String(300), nullable=False)

    # Promotion justification
    requested_by = Column(String(100), nullable=True)  # User who requested
    request_reason = Column(Text, nullable=True)  # "Searched 50+ times in last month"
    search_frequency = Column(JSON, nullable=True)  # Copy of search_count at time of request

    # Workflow status
    status = Column(String(50), default="pending")  # pending, in_review, approved, rejected, completed
    assigned_to = Column(String(100), nullable=True)  # Clinical reviewer
    review_notes = Column(Text, nullable=True)

    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_promotion_status', 'status'),
        Index('idx_promotion_mondo', 'mondo_id'),
    )


# Migration script to create tables
if __name__ == "__main__":
    from sqlalchemy import create_engine

    # For development
    engine = create_engine('sqlite:///ai_nurse_florence.db')

    # Create tables
    Base.metadata.create_all(engine)
    print("✅ Created disease_reference and diagnosis_promotion_queue tables")
