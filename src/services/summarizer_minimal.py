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
                self.client = OpenAI(api_key=settings.openai_api_key)
                
                # Test the client with a simple request
                test_response = self.client.models.list()
                print(f"✅ OpenAI client successfully initialized and tested")
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
            # Return minimal summary on error
            summary = Summary(
                content_id=content_ids[0] if content_ids else 0,
                prompt=prompt,
                summary_text=f"Summary generation failed: {str(e)}",
                ai_model="fallback",
                tokens_used=0
            )
            return summary
        finally:
            db.close()
    
    def _generate_ai_summary(self, contents: List[Content], prompt: str) -> str:
        """Generate summary using OpenAI."""
        try:
            content_text = "\n".join([f"{c.title}: {c.description}" for c in contents])
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\nContent:\n{content_text}"}
                ],
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
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
