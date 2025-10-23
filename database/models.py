from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///db.sqlite", echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class PopUp(Base):
    __tablename__ = "popup"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_reminder_sent: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)

    def __repr__(self):
        return f"<PopUp(id={self.id}, name={self.name}, telegram_id={self.telegram_id})>"


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
