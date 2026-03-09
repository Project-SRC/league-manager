from supabase import create_client, Client
from src.config import settings, log


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not settings.SUPABASE_KEY:
        log.warning("SUPABASE_KEY not configured, using empty key")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


supabase: Client = get_supabase_client()
