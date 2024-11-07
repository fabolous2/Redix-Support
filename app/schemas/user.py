from datetime import datetime, UTC

from dataclasses import dataclass, field


@dataclass
class User():
    user_id: int 
    topic_id: int
    info_message: int
    created_at: datetime = field(default=datetime.now(UTC))
    status: str = field(default='not banned')
    unban_at: datetime = field(default=None)