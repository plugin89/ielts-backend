from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from supabase import create_client, Client
from src.core.config import settings

#engine = create_async_engine(settings.DATABASE_URL, echo=True)
#SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
