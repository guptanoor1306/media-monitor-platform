from typing import List, Dict, Any, Optional
from openai import OpenAI
from datetime import datetime
from src.config import settings
from src.models import Content, Summary
from src.database import SessionLocal


class SummarizerService:
    """AI-powered content summarization service."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.summarization_max_tokens
    
    def summarize_content(self, content_ids: List[int], prompt: str, user_id: Optional[int] = None) -> Summary:
        """Summarize multiple content items based on a custom prompt."""
        try:
            # Get content from database
            db = SessionLocal()
            contents = db.query(Content).filter(Content.id.in_(content_ids)).all()
            
            if not contents:
                raise ValueError("No content found for the provided IDs")
            
            # Prepare content for summarization
            content_text = self._prepare_content_for_summarization(contents)
            
            # Generate summary using OpenAI
            summary_text = self._generate_summary(content_text, prompt)
            
            # Create summary record
            summary = Summary(
                content_id=content_ids[0],  # Store reference to first content
                prompt=prompt,
                summary_text=summary_text,
                ai_model=self.model,
                tokens_used=len(summary_text.split())  # Approximate token count
            )
            
            # Save to database
            db.add(summary)
            db.commit()
            db.refresh(summary)
            
            return summary
            
        except Exception as e:
            print(f"Error summarizing content: {e}")
            raise
        finally:
            db.close()
    
    def _prepare_content_for_summarization(self, contents: List[Content]) -> str:
        """Prepare content text for AI summarization."""
        prepared_text = []
        
        for content in contents:
            # Add title
            if content.title:
                prepared_text.append(f"Title: {content.title}")
            
            # Add description
            if content.description:
                prepared_text.append(f"Description: {content.description}")
            
            # Add content text if available
            if content.content_text:
                # Truncate very long content
                text = content.content_text[:2000] if len(content.content_text) > 2000 else content.content_text
                prepared_text.append(f"Content: {text}")
            
            # Add metadata
            if content.author:
                prepared_text.append(f"Author: {content.author}")
            
            if content.tags:
                prepared_text.append(f"Tags: {', '.join(content.tags)}")
            
            if content.engagement_metrics:
                metrics = []
                for key, value in content.engagement_metrics.items():
                    if value is not None:
                        metrics.append(f"{key}: {value}")
                if metrics:
                    prepared_text.append(f"Engagement: {', '.join(metrics)}")
            
            prepared_text.append("---")  # Separator between content items
        
        return "\n".join(prepared_text)
    
    def _generate_summary(self, content_text: str, prompt: str) -> str:
        """Generate summary using OpenAI API."""
        try:
            # Prepare the full prompt
            full_prompt = f"""
{prompt}

Content to analyze:
{content_text}

Please provide a comprehensive summary based on the above prompt and content.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert media analyst and business strategist. Provide insightful, well-structured summaries based on the given content and prompt."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary with OpenAI: {e}")
            # Fallback to a basic summary
            return self._generate_fallback_summary(content_text, prompt)
    
    def _generate_fallback_summary(self, content_text: str, prompt: str) -> str:
        """Generate a basic fallback summary when OpenAI fails."""
        lines = content_text.split('\n')
        titles = [line for line in lines if line.startswith('Title:')]
        descriptions = [line for line in lines if line.startswith('Description:')]
        
        summary_parts = [f"Summary based on prompt: {prompt}"]
        summary_parts.append(f"Analyzed {len(titles)} content items:")
        
        for i, title in enumerate(titles[:5]):  # Limit to first 5
            title_text = title.replace('Title: ', '')
            summary_parts.append(f"{i+1}. {title_text}")
        
        if descriptions:
            summary_parts.append("\nKey themes identified:")
            # Extract common keywords
            all_text = ' '.join(descriptions).lower()
            common_words = ['media', 'business', 'economy', 'creator', 'content', 'platform', 'revenue', 'model']
            themes = [word for word in common_words if word in all_text]
            if themes:
                summary_parts.append(f"- {', '.join(themes)}")
        
        return '\n'.join(summary_parts)
    
    def analyze_business_models(self, content_ids: List[int]) -> Summary:
        """Specialized analysis for media business models."""
        prompt = """
Analyze the following content to identify and explain media business models. Focus on:

1. Traditional media business models (advertising, subscriptions, etc.)
2. Non-traditional media businesses that don't look like media but are highly profitable
3. Distribution strategies and revenue streams
4. Creator economy monetization methods
5. Emerging business models in digital media

Provide specific examples and insights from the content.
"""
        return self.summarize_content(content_ids, prompt)
    
    def analyze_creator_economy(self, content_ids: List[int]) -> Summary:
        """Specialized analysis for creator economy trends."""
        prompt = """
Analyze the following content to understand creator economy trends and business models. Focus on:

1. How creators monetize their content
2. Platform strategies and revenue sharing
3. Emerging creator tools and services
4. Investment trends in creator economy
5. Challenges and opportunities for creators

Provide actionable insights and trend analysis.
"""
        return self.summarize_content(content_ids, prompt)
    
    def analyze_vc_trends(self, content_ids: List[int]) -> Summary:
        """Specialized analysis for VC and investment trends."""
        prompt = """
Analyze the following content to understand VC investment trends in media and creator economy. Focus on:

1. Investment themes and sectors
2. Notable deals and valuations
3. Emerging business models attracting investment
4. Market trends and predictions
5. Strategic insights for entrepreneurs and investors

Provide data-driven analysis and strategic recommendations.
"""
        return self.summarize_content(content_ids, prompt)
    
    def detect_themes(self, content_ids: List[int], theme_keywords: List[str]) -> Dict[str, Any]:
        """Detect specific themes in content and provide analysis."""
        prompt = f"""
Analyze the following content to detect mentions and discussions of these specific themes: {', '.join(theme_keywords)}

For each theme, provide:
1. Frequency of mentions
2. Context and sentiment
3. Key insights and trends
4. Related business implications

Focus on identifying patterns and actionable insights.
"""
        
        summary = self.summarize_content(content_ids, prompt)
        
        # Analyze theme frequency
        theme_analysis = {}
        for keyword in theme_keywords:
            count = summary.summary_text.lower().count(keyword.lower())
            theme_analysis[keyword] = {
                'mention_count': count,
                'significance': 'high' if count > 5 else 'medium' if count > 2 else 'low'
            }
        
        return {
            'summary': summary,
            'theme_analysis': theme_analysis
        }
