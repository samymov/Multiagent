"""
Observability module for LangFuse integration.
Provides a simple context manager for setting up and flushing traces.
"""

import os
import logging
from contextlib import contextmanager

# Use root logger for Lambda compatibility
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@contextmanager
def observe():
    """
    Context manager for observability with LangFuse.

    Sets up LangFuse observability if environment variables are configured,
    and ensures traces are flushed on exit.

    Usage:
        from observability import observe

        with observe():
            # Your code that uses OpenAI Agents SDK
            result = await agent.run(...)
    """
    logger.info("🔍 Observability: Checking configuration...")
    
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if langfuse_secret_key and langfuse_public_key:
        logger.info(f"✅ LangFuse configured: {langfuse_host}")
        try:
            from langfuse import Langfuse
            
            langfuse = Langfuse(
                secret_key=langfuse_secret_key,
                public_key=langfuse_public_key,
                host=langfuse_host
            )
            
            logger.info("✅ LangFuse client initialized")
            
            try:
                yield
            finally:
                # Flush traces before exiting
                langfuse.flush()
                logger.info("✅ LangFuse traces flushed")
        
        except ImportError:
            logger.warning("⚠️ LangFuse not installed, skipping observability")
            yield
        except Exception as e:
            logger.error(f"❌ LangFuse error: {e}")
            yield
    else:
        logger.info("ℹ️ LangFuse not configured, skipping observability")
        yield

