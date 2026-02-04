"""
Data models for Reddit Scout.

This module contains Pydantic models for representing Reddit posts, configuration,
notification records, and service status.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Post(BaseModel):
    """
    Represents a Reddit post with relevant metadata.

    Attributes:
        post_id: Unique identifier for the post
        subreddit: Name of the subreddit (without r/ prefix)
        title: Post title
        url: Full URL to the post content
        upvotes: Number of upvotes (non-negative)
        num_comments: Number of comments on the post
        upvote_ratio: Ratio of upvotes to total votes (0.0 to 1.0)
        created_utc: ISO 8601 timestamp when the post was created
        permalink: Reddit permalink to the post (relative URL)
    """

    post_id: str = Field(..., description="Unique post identifier")
    subreddit: str = Field(..., description="Subreddit name without r/ prefix")
    title: str = Field(..., description="Post title")
    url: str = Field(..., description="Full URL to post content")
    upvotes: int = Field(..., description="Number of upvotes", ge=0)
    num_comments: int = Field(..., description="Number of comments", ge=0)
    upvote_ratio: float = Field(
        ..., description="Upvote ratio", ge=0.0, le=1.0
    )
    created_utc: str = Field(..., description="ISO 8601 creation timestamp")
    permalink: str = Field(..., description="Reddit permalink")

    @field_validator("upvotes")
    @classmethod
    def validate_upvotes(cls, v: int) -> int:
        """Ensure upvotes is non-negative."""
        if v < 0:
            raise ValueError("upvotes must be non-negative")
        return v

    @field_validator("upvote_ratio")
    @classmethod
    def validate_upvote_ratio(cls, v: float) -> float:
        """Ensure upvote_ratio is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("upvote_ratio must be between 0.0 and 1.0")
        return v

    def to_dict(self) -> dict:
        """
        Serialize the post to a dictionary.

        Returns:
            Dictionary representation of the post
        """
        return self.model_dump()

    def to_json(self) -> str:
        """
        Serialize the post to a JSON string.

        Returns:
            JSON string representation of the post
        """
        return self.model_dump_json()


class RedditConfig(BaseModel):
    """
    Configuration for Reddit API access.

    Attributes:
        client_id: Reddit API client ID
        client_secret: Reddit API client secret
        user_agent: User agent string for API requests
    """

    client_id: str = Field(..., description="Reddit API client ID")
    client_secret: str = Field(..., description="Reddit API client secret")
    user_agent: str = Field(..., description="User agent for API requests")


class MonitoringConfig(BaseModel):
    """
    Configuration for subreddit monitoring.

    Attributes:
        subreddits: List of subreddit names to monitor
        check_interval_minutes: How often to check for new posts (in minutes)
        min_upvotes: Minimum upvotes threshold for notifications
        min_upvote_ratio: Minimum upvote ratio for notifications
    """

    subreddits: list[str] = Field(
        ..., description="List of subreddits to monitor"
    )
    check_interval_minutes: int = Field(
        ..., description="Check interval in minutes", gt=0
    )
    min_upvotes: int = Field(
        ..., description="Minimum upvotes threshold", ge=0
    )
    min_upvote_ratio: float = Field(
        ..., description="Minimum upvote ratio", ge=0.0, le=1.0
    )


class NotificationConfig(BaseModel):
    """
    Configuration for notifications via Arcade.

    Attributes:
        arcade_api_key: API key for Arcade notifications
        enabled: Whether notifications are enabled
    """

    arcade_api_key: str = Field(..., description="Arcade API key")
    enabled: bool = Field(default=True, description="Enable notifications")


class Config(BaseModel):
    """
    Main configuration model for Reddit Scout.

    Attributes:
        reddit: Reddit API configuration
        monitoring: Monitoring configuration
        notification: Notification configuration
    """

    reddit: RedditConfig = Field(..., description="Reddit API configuration")
    monitoring: MonitoringConfig = Field(
        ..., description="Monitoring configuration"
    )
    notification: NotificationConfig = Field(
        ..., description="Notification configuration"
    )

    def to_dict(self) -> dict:
        """
        Serialize the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return self.model_dump()

    def to_json(self) -> str:
        """
        Serialize the configuration to a JSON string.

        Returns:
            JSON string representation of the configuration
        """
        return self.model_dump_json()


class NotificationRecord(BaseModel):
    """
    Record of a notification sent for deduplication.

    Attributes:
        post_id: ID of the post that triggered the notification
        subreddit: Subreddit the post came from
        notified_at: ISO 8601 timestamp when notification was sent
        notification_type: Type of notification (e.g., 'trending', 'high_engagement')
    """

    post_id: str = Field(..., description="Post ID")
    subreddit: str = Field(..., description="Subreddit name")
    notified_at: str = Field(..., description="ISO 8601 notification timestamp")
    notification_type: str = Field(
        default="trending", description="Type of notification"
    )

    def to_dict(self) -> dict:
        """
        Serialize the notification record to a dictionary.

        Returns:
            Dictionary representation of the notification record
        """
        return self.model_dump()

    def to_json(self) -> str:
        """
        Serialize the notification record to a JSON string.

        Returns:
            JSON string representation of the notification record
        """
        return self.model_dump_json()


class ServiceStatus(BaseModel):
    """
    Status information for the Reddit Scout daemon.

    Attributes:
        is_running: Whether the service is currently running
        last_check_at: ISO 8601 timestamp of last successful check
        next_check_at: ISO 8601 timestamp of next scheduled check
        monitored_subreddits: List of currently monitored subreddits
        total_posts_checked: Total number of posts checked since start
        total_notifications_sent: Total number of notifications sent
        errors: List of recent error messages
        started_at: ISO 8601 timestamp when service started
    """

    is_running: bool = Field(
        default=False, description="Service running status"
    )
    last_check_at: Optional[str] = Field(
        default=None, description="Last check timestamp"
    )
    next_check_at: Optional[str] = Field(
        default=None, description="Next check timestamp"
    )
    monitored_subreddits: list[str] = Field(
        default_factory=list, description="Currently monitored subreddits"
    )
    total_posts_checked: int = Field(
        default=0, description="Total posts checked", ge=0
    )
    total_notifications_sent: int = Field(
        default=0, description="Total notifications sent", ge=0
    )
    errors: list[str] = Field(
        default_factory=list, description="Recent error messages"
    )
    started_at: Optional[str] = Field(
        default=None, description="Service start timestamp"
    )

    def to_dict(self) -> dict:
        """
        Serialize the service status to a dictionary.

        Returns:
            Dictionary representation of the service status
        """
        return self.model_dump()

    def to_json(self) -> str:
        """
        Serialize the service status to a JSON string.

        Returns:
            JSON string representation of the service status
        """
        return self.model_dump_json()

    def add_error(self, error: str) -> None:
        """
        Add an error message to the error list.

        Args:
            error: Error message to add
        """
        self.errors.append(error)

    def increment_posts_checked(self, count: int = 1) -> None:
        """
        Increment the total posts checked counter.

        Args:
            count: Number of posts to add to the counter (default: 1)
        """
        self.total_posts_checked += count

    def increment_notifications_sent(self, count: int = 1) -> None:
        """
        Increment the total notifications sent counter.

        Args:
            count: Number of notifications to add to the counter (default: 1)
        """
        self.total_notifications_sent += count
