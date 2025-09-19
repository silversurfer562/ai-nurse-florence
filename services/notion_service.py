"""
Notion integration service for GitHub webhook events.

This service handles the creation and updating of Notion pages based on
GitHub events, providing a structured way to track repository activity.
"""
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx

from utils.config import get_settings
from utils.logging import get_logger
from utils.exceptions import ExternalServiceException

logger = get_logger(__name__)


class NotionService:
    """Service for interacting with Notion API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.settings.NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test the connection to Notion API."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/databases/{self.settings.NOTION_DATABASE_ID}",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
        except Exception as e:
            raise ExternalServiceException(
                message=f"Failed to connect to Notion: {str(e)}",
                service_name="notion",
                details={"database_id": self.settings.NOTION_DATABASE_ID}
            )
    
    async def create_page(self, properties: Dict[str, Any], children: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new page in the Notion database."""
        try:
            page_data = {
                "parent": {"database_id": self.settings.NOTION_DATABASE_ID},
                "properties": properties,
            }
            
            if children:
                page_data["children"] = children
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            raise ExternalServiceException(
                message=f"Notion API error: {e.response.status_code} - {e.response.text}",
                service_name="notion",
                status_code=e.response.status_code,
                details={"operation": "create_page"}
            )
        except Exception as e:
            raise ExternalServiceException(
                message=f"Failed to create Notion page: {str(e)}",
                service_name="notion",
                details={"operation": "create_page"}
            )
    
    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing page in Notion."""
        try:
            update_data = {"properties": properties}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    json=update_data
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            raise ExternalServiceException(
                message=f"Notion API error: {e.response.status_code} - {e.response.text}",
                service_name="notion",
                status_code=e.response.status_code,
                details={"operation": "update_page", "page_id": page_id}
            )
        except Exception as e:
            raise ExternalServiceException(
                message=f"Failed to update Notion page: {str(e)}",
                service_name="notion",
                details={"operation": "update_page", "page_id": page_id}
            )
    
    def _create_rich_text(self, text: str) -> List[Dict[str, Any]]:
        """Create a rich text object for Notion."""
        return [{"type": "text", "text": {"content": text}}]
    
    def _create_text_block(self, text: str) -> Dict[str, Any]:
        """Create a text block for Notion page content."""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": self._create_rich_text(text)
            }
        }
    
    def _create_code_block(self, code: str, language: str = "text") -> Dict[str, Any]:
        """Create a code block for Notion page content."""
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": self._create_rich_text(code),
                "language": language
            }
        }
    
    async def handle_push_event(self, data: Dict[str, Any]):
        """Handle a GitHub push event."""
        repository = data.get("repository", {})
        commits = data.get("commits", [])
        pusher = data.get("pusher", {})
        ref = data.get("ref", "")
        
        # Create a summary of the push
        commit_count = len(commits)
        branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref
        
        # Prepare page properties
        properties = {
            "Title": {
                "title": self._create_rich_text(
                    f"Push to {repository.get('name', 'Unknown')} ({branch})"
                )
            },
            "Type": {
                "select": {"name": "Push"}
            },
            "Repository": {
                "rich_text": self._create_rich_text(repository.get("full_name", ""))
            },
            "Branch": {
                "rich_text": self._create_rich_text(branch)
            },
            "Author": {
                "rich_text": self._create_rich_text(pusher.get("name", "Unknown"))
            },
            "Commit Count": {
                "number": commit_count
            },
            "Date": {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            "URL": {
                "url": data.get("compare", repository.get("html_url", ""))
            }
        }
        
        # Create page content with commit details
        children = [
            self._create_text_block(f"Push with {commit_count} commit(s) to {branch}")
        ]
        
        for commit in commits[:10]:  # Limit to first 10 commits
            children.append(
                self._create_text_block(
                    f"• {commit.get('message', '').split('\n')[0]} - {commit.get('author', {}).get('name', 'Unknown')}"
                )
            )
        
        if len(commits) > 10:
            children.append(
                self._create_text_block(f"... and {len(commits) - 10} more commits")
            )
        
        await self.create_page(properties, children)
        logger.info(f"Created Notion page for push to {repository.get('full_name')}")
    
    async def handle_pull_request_event(self, data: Dict[str, Any]):
        """Handle a GitHub pull request event."""
        action = data.get("action", "")
        pr = data.get("pull_request", {})
        repository = data.get("repository", {})
        
        # Prepare page properties
        properties = {
            "Title": {
                "title": self._create_rich_text(
                    f"PR #{pr.get('number', 0)}: {pr.get('title', 'Unknown')}"
                )
            },
            "Type": {
                "select": {"name": "Pull Request"}
            },
            "Repository": {
                "rich_text": self._create_rich_text(repository.get("full_name", ""))
            },
            "Action": {
                "select": {"name": action.title()}
            },
            "Author": {
                "rich_text": self._create_rich_text(pr.get("user", {}).get("login", "Unknown"))
            },
            "State": {
                "select": {"name": pr.get("state", "unknown").title()}
            },
            "Date": {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            "URL": {
                "url": pr.get("html_url", "")
            }
        }
        
        # Create page content
        children = [
            self._create_text_block(f"Pull request #{pr.get('number')} {action}"),
            self._create_text_block(f"From: {pr.get('head', {}).get('ref', 'unknown')}"),
            self._create_text_block(f"To: {pr.get('base', {}).get('ref', 'unknown')}"),
        ]
        
        if pr.get("body"):
            children.append(self._create_text_block("Description:"))
            children.append(self._create_text_block(pr.get("body", "")[:1000]))
        
        await self.create_page(properties, children)
        logger.info(f"Created Notion page for PR #{pr.get('number')} ({action})")
    
    async def handle_issue_event(self, data: Dict[str, Any]):
        """Handle a GitHub issue event."""
        action = data.get("action", "")
        issue = data.get("issue", {})
        repository = data.get("repository", {})
        
        # Prepare page properties
        properties = {
            "Title": {
                "title": self._create_rich_text(
                    f"Issue #{issue.get('number', 0)}: {issue.get('title', 'Unknown')}"
                )
            },
            "Type": {
                "select": {"name": "Issue"}
            },
            "Repository": {
                "rich_text": self._create_rich_text(repository.get("full_name", ""))
            },
            "Action": {
                "select": {"name": action.title()}
            },
            "Author": {
                "rich_text": self._create_rich_text(issue.get("user", {}).get("login", "Unknown"))
            },
            "State": {
                "select": {"name": issue.get("state", "unknown").title()}
            },
            "Date": {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            "URL": {
                "url": issue.get("html_url", "")
            }
        }
        
        # Create page content
        children = [
            self._create_text_block(f"Issue #{issue.get('number')} {action}"),
        ]
        
        if issue.get("body"):
            children.append(self._create_text_block("Description:"))
            children.append(self._create_text_block(issue.get("body", "")[:1000]))
        
        # Add labels if present
        labels = issue.get("labels", [])
        if labels:
            label_names = [label.get("name", "") for label in labels]
            children.append(self._create_text_block(f"Labels: {', '.join(label_names)}"))
        
        await self.create_page(properties, children)
        logger.info(f"Created Notion page for issue #{issue.get('number')} ({action})")
    
    async def handle_issue_comment_event(self, data: Dict[str, Any]):
        """Handle a GitHub issue comment event."""
        action = data.get("action", "")
        comment = data.get("comment", {})
        issue = data.get("issue", {})
        repository = data.get("repository", {})
        
        # Prepare page properties
        properties = {
            "Title": {
                "title": self._create_rich_text(
                    f"Comment on Issue #{issue.get('number', 0)}"
                )
            },
            "Type": {
                "select": {"name": "Comment"}
            },
            "Repository": {
                "rich_text": self._create_rich_text(repository.get("full_name", ""))
            },
            "Action": {
                "select": {"name": action.title()}
            },
            "Author": {
                "rich_text": self._create_rich_text(comment.get("user", {}).get("login", "Unknown"))
            },
            "Date": {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            "URL": {
                "url": comment.get("html_url", "")
            }
        }
        
        # Create page content
        children = [
            self._create_text_block(f"Comment {action} on issue #{issue.get('number')}: {issue.get('title', '')}"),
        ]
        
        if comment.get("body"):
            children.append(self._create_text_block("Comment:"))
            children.append(self._create_text_block(comment.get("body", "")[:1000]))
        
        await self.create_page(properties, children)
        logger.info(f"Created Notion page for comment on issue #{issue.get('number')} ({action})")
    
    async def handle_pr_review_event(self, data: Dict[str, Any]):
        """Handle a GitHub pull request review event."""
        action = data.get("action", "")
        review = data.get("review", {})
        pr = data.get("pull_request", {})
        repository = data.get("repository", {})
        
        # Prepare page properties
        properties = {
            "Title": {
                "title": self._create_rich_text(
                    f"Review on PR #{pr.get('number', 0)}"
                )
            },
            "Type": {
                "select": {"name": "Review"}
            },
            "Repository": {
                "rich_text": self._create_rich_text(repository.get("full_name", ""))
            },
            "Action": {
                "select": {"name": action.title()}
            },
            "Author": {
                "rich_text": self._create_rich_text(review.get("user", {}).get("login", "Unknown"))
            },
            "Review State": {
                "select": {"name": review.get("state", "unknown").title()}
            },
            "Date": {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            "URL": {
                "url": review.get("html_url", "")
            }
        }
        
        # Create page content
        children = [
            self._create_text_block(f"Review {action} on PR #{pr.get('number')}: {pr.get('title', '')}"),
            self._create_text_block(f"Review state: {review.get('state', 'unknown')}"),
        ]
        
        if review.get("body"):
            children.append(self._create_text_block("Review comment:"))
            children.append(self._create_text_block(review.get("body", "")[:1000]))
        
        await self.create_page(properties, children)
        logger.info(f"Created Notion page for review on PR #{pr.get('number')} ({action})")