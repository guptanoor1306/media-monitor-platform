from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models import Content, Summary
from src.database import SessionLocal

class SummarizerService:
    """Minimal summarizer service for deployment."""
    
    def __init__(self):
        # Don't initialize OpenAI client at startup
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.use_legacy_api = False  # Track which API style to use
    
    def _init_client(self):
        """Initialize OpenAI client only when needed."""
        if self.client is None:
            try:
                from openai import OpenAI
                from src.config import settings
                
                # Check if API key is available
                if not settings.openai_api_key:
                    print("❌ OpenAI API key not found in environment variables")
                    print("💡 Set OPENAI_API_KEY in your Render environment variables")
                    return False
                
                if not settings.openai_api_key.startswith('sk-'):
                    print(f"❌ Invalid OpenAI API key format: {settings.openai_api_key[:10]}...")
                    print("💡 OpenAI API keys should start with 'sk-'")
                    return False
                
                print(f"✅ Initializing OpenAI client with key: {settings.openai_api_key[:10]}...")
                
                # Initialize with minimal parameters to avoid version conflicts
                try:
                    self.client = OpenAI(api_key=settings.openai_api_key)
                    self.use_legacy_api = False
                except TypeError as te:
                    # Handle version-specific initialization issues
                    print(f"⚠️  Trying alternative initialization due to: {te}")
                    import openai
                    openai.api_key = settings.openai_api_key
                    self.client = openai
                    self.use_legacy_api = True  # Flag that we're using legacy API
                    print(f"✅ OpenAI client initialized with legacy method")
                    return True
                
                # Test the client with a simple request (only for new style)
                if not self.use_legacy_api:
                    test_response = self.client.models.list()
                    print(f"✅ OpenAI client successfully initialized and tested")
                else:
                    print(f"✅ OpenAI legacy client initialized (skipping test)")
                return True
                
            except Exception as e:
                print(f"❌ OpenAI client initialization failed: {e}")
                print(f"🔧 Error type: {type(e).__name__}")
                return False
        return True
    
    def summarize_content(self, content_ids: List[int], prompt: str, user_id: Optional[int] = None) -> Summary:
        """Summarize content with fallback."""
        try:
            db = SessionLocal()
            contents = db.query(Content).filter(Content.id.in_(content_ids)).all()
            
            if not contents:
                raise ValueError("No content found for the provided IDs")
            
            # Try to use OpenAI, fallback to simple summary
            if self._init_client():
                summary_text = self._generate_ai_summary(contents, prompt)
            else:
                summary_text = self._generate_fallback_summary(contents, prompt)
            
            # Create summary record
            summary = Summary(
                content_id=content_ids[0],
                prompt=prompt,
                summary_text=summary_text,
                ai_model=self.model,
                tokens_used=len(summary_text.split())
            )
            
            db.add(summary)
            db.commit()
            db.refresh(summary)
            return summary
            
        except Exception as e:
            print(f"Error summarizing content: {e}")
            # Return minimal summary on error and save to database
            try:
                summary = Summary(
                    content_id=content_ids[0] if content_ids else 1,  # Use valid content_id
                    prompt=prompt,
                    summary_text=f"📋 **Summary Generation Error**\n\n**Error:** {str(e)}\n\n**Prompt:** {prompt}\n\n💡 *This usually means the content IDs don't exist. Try selecting different articles.*",
                    ai_model="error-fallback",
                    tokens_used=0
                )
                db.add(summary)
                db.commit()
                db.refresh(summary)
                return summary
            except Exception as db_error:
                print(f"Database error in fallback: {db_error}")
                # If even the error summary fails, raise the original error
                raise e
        finally:
            db.close()
    
    def _generate_ai_summary(self, contents: List[Content], prompt: str) -> str:
        """Generate summary using OpenAI."""
        try:
            content_text = "\n".join([f"{c.title}: {c.description}" for c in contents])
            
            # Use the appropriate API style based on initialization
            if self.use_legacy_api:
                # Use legacy OpenAI API style (for v1.3.8)
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": f"{prompt}\n\nContent:\n{content_text}"}
                    ],
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
            else:
                # Use new OpenAI client style
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": f"{prompt}\n\nContent:\n{content_text}"}
                    ],
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"🔧 OpenAI API call failed: {e}")
            return self._generate_fallback_summary(contents, prompt)
    
    def _generate_fallback_summary(self, contents: List[Content], prompt: str) -> str:
        """Generate enhanced fallback summary with descriptions."""
        summary_parts = [
            f"📊 **Analysis Summary** (OpenAI unavailable - using fallback)",
            f"**Prompt:** {prompt}",
            f"**Articles Analyzed:** {len(contents)}",
            "",
            "**Key Articles:**"
        ]
        
        for i, content in enumerate(contents):
            title = content.title or "Untitled"
            desc = content.description or "No description available"
            # Truncate long descriptions
            desc = desc[:200] + "..." if len(desc) > 200 else desc
            summary_parts.append(f"{i+1}. **{title}**")
            summary_parts.append(f"   {desc}")
            if content.author:
                summary_parts.append(f"   *By: {content.author}*")
            summary_parts.append("")
        
        summary_parts.append("💡 *For full AI analysis, configure OpenAI API key in environment variables.*")
        return "\n".join(summary_parts)
