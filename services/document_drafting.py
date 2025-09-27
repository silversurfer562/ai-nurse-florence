"""
AI Nurse Florence - Document Drafting System
Provides editable document generation with version control and approval workflow
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json

class DocumentStatus(str, Enum):
    """Document lifecycle status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SENT = "sent"
    ARCHIVED = "archived"

class DocumentDraft(BaseModel):
    """Document draft with editing capabilities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    document_type: str
    original_content: str  # Generated content
    edited_content: Optional[str] = None  # User-edited version
    status: DocumentStatus = DocumentStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class DocumentRevision(BaseModel):
    """Document revision history"""
    revision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    content: str
    changed_by: Optional[str] = None
    changed_at: datetime = Field(default_factory=datetime.now)
    change_summary: Optional[str] = None
    diff_stats: Dict[str, int] = Field(default_factory=dict)  # lines added/removed

class DocumentDraftingSystem:
    """
    Document drafting system with editing, version control, and approval workflow
    Supports nurses in creating professional documents they can edit before use
    """
    
    def __init__(self):
        self.drafts: Dict[str, DocumentDraft] = {}
        self.revisions: Dict[str, List[DocumentRevision]] = {}
    
    def create_draft(
        self,
        title: str,
        document_type: str,
        generated_content: str,
        created_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Create a new document draft from generated content"""
        
        draft = DocumentDraft(
            title=title,
            document_type=document_type,
            original_content=generated_content,
            created_by=created_by,
            metadata=metadata or {},
            tags=tags or []
        )
        
        self.drafts[draft.id] = draft
        self.revisions[draft.id] = []
        
        # Create initial revision
        initial_revision = DocumentRevision(
            document_id=draft.id,
            content=generated_content,
            changed_by=created_by,
            change_summary="Initial draft created"
        )
        self.revisions[draft.id].append(initial_revision)
        
        return draft.id
    
    def edit_draft(
        self,
        draft_id: str,
        new_content: str,
        edited_by: Optional[str] = None,
        change_summary: Optional[str] = None
    ) -> bool:
        """Edit an existing draft and track changes"""
        
        if draft_id not in self.drafts:
            return False
        
        draft = self.drafts[draft_id]
        old_content = draft.edited_content or draft.original_content
        
        # Calculate diff stats
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        diff_stats = {
            "lines_added": len(new_lines) - len(old_lines),
            "total_lines": len(new_lines),
            "characters_changed": len(new_content) - len(old_content)
        }
        
        # Update draft
        draft.edited_content = new_content
        draft.last_modified = datetime.now()
        
        # Create revision
        revision = DocumentRevision(
            document_id=draft_id,
            content=new_content,
            changed_by=edited_by,
            change_summary=change_summary or "Content edited",
            diff_stats=diff_stats
        )
        self.revisions[draft_id].append(revision)
        
        return True
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a draft with its current content and metadata"""
        
        if draft_id not in self.drafts:
            return None
        
        draft = self.drafts[draft_id]
        current_content = draft.edited_content or draft.original_content
        
        return {
            "id": draft.id,
            "title": draft.title,
            "document_type": draft.document_type,
            "content": current_content,
            "original_content": draft.original_content,
            "has_edits": draft.edited_content is not None,
            "status": draft.status.value,
            "created_at": draft.created_at.isoformat(),
            "last_modified": draft.last_modified.isoformat(),
            "created_by": draft.created_by,
            "metadata": draft.metadata,
            "tags": draft.tags,
            "notes": draft.notes,
            "revision_count": len(self.revisions.get(draft_id, []))
        }
    
    def list_drafts(
        self,
        created_by: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[DocumentStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List drafts with optional filtering"""
        
        filtered_drafts = []
        
        for draft in self.drafts.values():
            # Apply filters
            if created_by and draft.created_by != created_by:
                continue
            if document_type and draft.document_type != document_type:
                continue
            if status and draft.status != status:
                continue
            if tags and not any(tag in draft.tags for tag in tags):
                continue
            
            # Add summary info
            current_content = draft.edited_content or draft.original_content
            filtered_drafts.append({
                "id": draft.id,
                "title": draft.title,
                "document_type": draft.document_type,
                "status": draft.status.value,
                "created_at": draft.created_at.isoformat(),
                "last_modified": draft.last_modified.isoformat(),
                "created_by": draft.created_by,
                "has_edits": draft.edited_content is not None,
                "content_preview": current_content[:200] + "..." if len(current_content) > 200 else current_content,
                "tags": draft.tags,
                "revision_count": len(self.revisions.get(draft.id, []))
            })
        
        # Sort by last modified (newest first)
        filtered_drafts.sort(key=lambda x: x["last_modified"], reverse=True)
        return filtered_drafts
    
    def update_status(
        self,
        draft_id: str,
        new_status: DocumentStatus,
        updated_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Update document status (draft -> review -> approved -> sent)"""
        
        if draft_id not in self.drafts:
            return False
        
        draft = self.drafts[draft_id]
        old_status = draft.status
        draft.status = new_status
        draft.last_modified = datetime.now()
        
        if notes:
            draft.notes = notes
        
        if new_status == DocumentStatus.APPROVED:
            draft.reviewed_by = updated_by
        
        # Create revision for status change
        revision = DocumentRevision(
            document_id=draft_id,
            content=draft.edited_content or draft.original_content,
            changed_by=updated_by,
            change_summary=f"Status changed from {old_status.value} to {new_status.value}"
        )
        self.revisions[draft_id].append(revision)
        
        return True
    
    def get_revision_history(self, draft_id: str) -> List[Dict[str, Any]]:
        """Get complete revision history for a document"""
        
        if draft_id not in self.revisions:
            return []
        
        return [
            {
                "revision_id": rev.revision_id,
                "changed_at": rev.changed_at.isoformat(),
                "changed_by": rev.changed_by,
                "change_summary": rev.change_summary,
                "diff_stats": rev.diff_stats
            }
            for rev in self.revisions[draft_id]
        ]
    
    def compare_versions(self, draft_id: str, revision_1: str, revision_2: str) -> Dict[str, Any]:
        """Compare two versions of a document"""
        
        if draft_id not in self.revisions:
            return {"error": "Document not found"}
        
        revisions = self.revisions[draft_id]
        rev_1 = next((r for r in revisions if r.revision_id == revision_1), None)
        rev_2 = next((r for r in revisions if r.revision_id == revision_2), None)
        
        if not rev_1 or not rev_2:
            return {"error": "Revision not found"}
        
        # Simple diff calculation
        lines_1 = rev_1.content.split('\n')
        lines_2 = rev_2.content.split('\n')
        
        return {
            "revision_1": {
                "id": rev_1.revision_id,
                "date": rev_1.changed_at.isoformat(),
                "lines": len(lines_1)
            },
            "revision_2": {
                "id": rev_2.revision_id,
                "date": rev_2.changed_at.isoformat(),
                "lines": len(lines_2)
            },
            "changes": {
                "lines_added": len(lines_2) - len(lines_1),
                "total_changes": abs(len(lines_2) - len(lines_1))
            }
        }
    
    def export_document(
        self,
        draft_id: str,
        format_type: Literal["text", "html", "json"] = "text"
    ) -> Optional[Dict[str, Any]]:
        """Export document in different formats for use in emails, records, etc."""
        
        draft_data = self.get_draft(draft_id)
        if not draft_data:
            return None
        
        content = draft_data["content"]
        
        if format_type == "text":
            return {
                "format": "text",
                "content": content,
                "filename": f"{draft_data['title'].replace(' ', '_')}.txt"
            }
        
        elif format_type == "html":
            # Convert to HTML with basic formatting
            html_content = content.replace('\n', '<br>\n')
            html_content = f"""
            <html>
            <head><title>{draft_data['title']}</title></head>
            <body>
            <h1>{draft_data['title']}</h1>
            <p><em>Generated: {draft_data['created_at']}</em></p>
            <div>{html_content}</div>
            </body>
            </html>
            """
            return {
                "format": "html",
                "content": html_content,
                "filename": f"{draft_data['title'].replace(' ', '_')}.html"
            }
        
        elif format_type == "json":
            return {
                "format": "json",
                "content": json.dumps(draft_data, indent=2),
                "filename": f"{draft_data['title'].replace(' ', '_')}.json"
            }
    
    def get_statistics(self, created_by: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics for the drafting system"""
        
        all_drafts = list(self.drafts.values())
        if created_by:
            all_drafts = [d for d in all_drafts if d.created_by == created_by]
        
        total_drafts = len(all_drafts)
        status_counts = {}
        type_counts = {}
        
        for draft in all_drafts:
            status_counts[draft.status.value] = status_counts.get(draft.status.value, 0) + 1
            type_counts[draft.document_type] = type_counts.get(draft.document_type, 0) + 1
        
        return {
            "total_documents": total_drafts,
            "status_breakdown": status_counts,
            "document_types": type_counts,
            "total_revisions": sum(len(revs) for revs in self.revisions.values()),
            "active_drafts": len([d for d in all_drafts if d.status == DocumentStatus.DRAFT])
        }

# Global instance
document_drafting_system = DocumentDraftingSystem()
