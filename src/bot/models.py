from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class ChessBoard(Base):
    __tablename__ = "chess_board"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fen: Mapped[str] = mapped_column(String, nullable=False)
    white: Mapped[str] = mapped_column(String, nullable=True)
    black: Mapped[str] = mapped_column(String, nullable=True)


class UserSavedMessage(Base):
    __tablename__ = "user_saved_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    data: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False
    )

    def pretty(self) -> str:
        return f"{self.id} – {self.created_at.isoformat()}: {self.data}"


class Joke(Base):
    __tablename__ = "joke"
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        line = ""
        if self.title:
            line += f"**{self.title}**\n"
        line += self.body
        return line
