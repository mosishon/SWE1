import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseModel


class Token(BaseModel):
    id: Mapped[int] = mapped_column(
        primary_key=True, unique=True, index=True, autoincrement=True
    )
    token: Mapped[str] = mapped_column(unique=True, index=True)
    force_expired: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default_factory=lambda: datetime.datetime.now(tz=None)
    )
