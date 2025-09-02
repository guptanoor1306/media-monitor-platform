from typing import List, Dict, Any, Optional
from datetime import datetime
from src.models import Content, Summary
from src.database import SessionLocal

class SummarizerService:
    """Minimal summarizer service for deployment."""
    
    def __init__(self):
        # Don't initialize OpenAI client at startup
        self.client = None
        self.model = "gpt-4o-mini"  # Use cost-effective GPT-4 model
        self.max_tokens = 1500
    
    def _init_client(self):
        """This method is deprecated - using direct initialization now."""
        return True
    
    def summarize_content(self, content_ids: List[int], prompt: str, user_id: Optional[int] = None) -> Summary:
        """Summarize content with fallback."""
        try:
            db = SessionLocal()
            contents = db.query(Content).filter(Content.id.in_(content_ids)).all()
            
            if not contents:
                raise ValueError("No content found for the provided IDs")
            
            # Force OpenAI to work - no more fallbacks until we know why it fails
            print(f"🔍 FORCING OpenAI initialization...")
            
            # Manual API key verification
            from src.config import settings
            print(f"🔑 API Key exists: {bool(settings.openai_api_key)}")
            print(f"🔑 API Key format: {settings.openai_api_key[:15]}..." if settings.openai_api_key else "None")
            print(f"🔑 API Key length: {len(settings.openai_api_key) if settings.openai_api_key else 0}")
            
            # Force initialization with maximum debugging
            try:
                print(f"🔄 Setting up clean environment...")
                import os
                # Set the API key in environment to avoid parameter issues
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key
                
                from openai import OpenAI
                print(f"🔄 Creating OpenAI client with NO parameters...")
                # Initialize with NO parameters to avoid 'proxies' argument error
                self.client = OpenAI()
                print(f"✅ Client created successfully")
                
                # FORCE a test call - no excuses
                print(f"🧪 FORCING test API call...")
                test_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )
                print(f"✅ TEST API CALL SUCCESSFUL!")
                print(f"🔍 Test response: {test_response.choices[0].message.content}")
                
                # Now do the real summary
                print(f"🔄 Generating REAL AI summary...")
                summary_text = self._generate_ai_summary(contents, prompt)
                print(f"✅ AI SUMMARY COMPLETE: {len(summary_text)} chars")
                
            except Exception as force_error:
                print(f"💥 FORCED TEST FAILED: {force_error}")
                print(f"💥 Error type: {type(force_error).__name__}")
                print(f"💥 Full error: {str(force_error)}")
                # Only NOW use fallback
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
            
            # Detailed debugging
            print(f"🔍 DEBUG: Client exists: {self.client is not None}")
            print(f"🔍 DEBUG: Model: {self.model}")
            print(f"🔍 DEBUG: Content length: {len(content_text)}")
            print(f"🔍 DEBUG: Max tokens: {self.max_tokens}")
            
            # Use OpenAI v1.x API (ChatCompletion was removed in v1.0+)
            print(f"🔄 Using OpenAI v1.x API call...")
            print(f"🔄 Making request to model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\nContent:\n{content_text}"}
                ],
                max_tokens=self.max_tokens
            )
            
            print(f"✅ OpenAI API call successful")
            print(f"🔍 Response type: {type(response)}")
            print(f"🔍 Response choices length: {len(response.choices)}")
            
            result = response.choices[0].message.content.strip()
            print(f"🔍 Result length: {len(result)}")
            return result
                
        except Exception as e:
            print(f"🔧 OpenAI API call failed: {e}")
            print(f"🔧 Error type: {type(e).__name__}")
            
            # Log the actual API key status for debugging
            from src.config import settings
            print(f"🔧 API key exists: {bool(settings.openai_api_key)}")
            print(f"🔧 API key format: {settings.openai_api_key[:10] + '...' if settings.openai_api_key else 'None'}")
            
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
