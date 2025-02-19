from flask import jsonify, request
from groq import Groq
from datetime import datetime
import json
from config import *
from simple_analytics import DashboardAnalytics
from advanced_analytics import AdvancedAnalytics
from text_analytics import TextAnalytics
from openai import OpenAI


class MarketingChatbot:
    def __init__(self):
        self.analytics = DashboardAnalytics()
        self.advanced_analytics = AdvancedAnalytics()
        self.text_analytics = TextAnalytics()
        self.groq_client = Groq(api_key=CHAT_GROQ_API_KEY)
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.script_prompts = {
            "script_creation": """Create a fully detailed, professional-quality script that includes every dialogue, 
            scene description, and essential elements needed for a complete video production. Ensure the script is 
            structured properly, covering all necessary aspects such as character dialogues, transitions, and cues. 
            Additionally, provide precise recommendations for background lighting and music, specifying the ideal 
            ambiance, intensity, and tone to match the script's mood. The final script should be text-only, 
            allowing me to read it directly for my video without any modifications.""",
            
            "script_enhance": """Review my script and enhance it by refining the dialogues, improving the flow, 
            and ensuring it is engaging and impactful. Maintain the original intent while making the language more 
            compelling, natural, and well-structured. Additionally, ensure proper formatting, smooth transitions, 
            and a professional tone suitable for video production. The final output should be a fully polished, 
            ready-to-use script that I can directly use for my video."""
        }

    def get_context_data(self, category):
        """Gather relevant context data for the category"""
        try:
            # Get base metrics
            engagement_data = self.analytics.get_engagement_metrics(category)
            trend_data = self.analytics.get_search_trends(category)
            channel_data = self.analytics.get_channel_performance(category)
            max_views = max(channel['total_views'] for channel in channel_data.values())
            max_likes = max(channel['total_likes'] for channel in channel_data.values())
            max_comments = max(channel['total_comments'] for channel in channel_data.values())

            # Calculate normalized scores for each channel
            scored_channels = {}
            print("15")
            for channel, metrics in channel_data.items():
                # Normalize values between 0 and 1
                normalized_views = metrics['total_views'] / max_views
                normalized_likes = metrics['total_likes'] / max_likes
                normalized_comments = metrics['total_comments'] / max_comments
                
                # Calculate weighted score (50% views, 30% likes, 20% comments)
                score = (normalized_views * 0.3) + (normalized_likes * 0.3) + (normalized_comments * 0.4)
                
                # Add score to metrics
                channel_data = metrics.copy()
                channel_data['composite_score'] = round(score * 100, 2)  # Convert to percentage
                scored_channels[channel] = channel_data

            # Sort channels by composite score
            sorted_channels = dict(
                sorted(
                    scored_channels.items(),
                    key=lambda x: (x[1]['composite_score'], x[1]['total_views']),  # Use views as tiebreaker
                    reverse=True
                )
            )
            print("20")

            # Get top 5 channels
            top_5_channels = dict(list(sorted_channels.items())[:5])
            print("\nTop 5 Channels:")
            for channel, metrics in top_5_channels.items():
                print(f"\nChannel: {channel}")
                print(f"Views: {metrics['total_views']:,}")
                print(f"Likes: {metrics['total_likes']:,}")
                print(f"Comments: {metrics['total_comments']:,}")
                print(f"Score: {metrics['composite_score']}%")
            # Format data for context
            
            # Format data for context
            context = {
                "category_metrics": {
                    "total_videos": len(engagement_data),
                    "top_channels": list(channel_data.keys())[:5],
                    "trending_topics": list(trend_data.get('top_keywords', {}).keys())[:5],
                    "recent_campaigns": [
                        video['title'] for video in engagement_data[:5]
                    ]
                },
                "market_trends": trend_data.get('news_topics', {}),
                "performance_data": channel_data
            }
            
            return context
        except Exception as e:
            return {"error": f"Error gathering context: {str(e)}"}

    def generate_response(self, category, user_question, mode=None, script_content=None):
        """Generate chatbot response using Groq's Mistral model with script modes"""
        try:
            # Get context data
            context = self.get_context_data(category)
            
            # Create dynamic system prompt based on question type and mode
            system_prompt = self._create_system_prompt(user_question, mode)
            
            # Create detailed prompt with context and script mode
            prompt = self._create_chat_prompt(category, user_question, context, mode, script_content)
            
            # Get response from Groq
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.5,
                max_tokens=2048
            )
            
            return {
                "response": response.choices[0].message.content,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": category,
                    "mode": mode,
                    "context_used": bool(context)
                }
            }
        except Exception as e:
            return {"error": f"Error generating response: {str(e)}"}

    def _create_system_prompt(self, question,mode=None):
        """Create appropriate system prompt based on question type and mode"""
        if mode in ["script_creation", "script_enhance"]:
            return """You are an expert scriptwriter and content creator with deep experience in 
                    video production, dialogue writing, and scene direction. Provide detailed, 
                    professional-quality scripts with clear instructions for production elements."""
        
        # Original keyword-based prompt selection for other cases
        marketing_keywords = ['campaign', 'marketing', 'advertisement', 'promote', 'strategy']
        script_keywords = ['script', 'copy', 'write', 'content', 'message']
        analysis_keywords = ['compare', 'analyze', 'trend', 'performance', 'metrics']
        content_creation_keywords = ['youtube', 'instagram', 'tiktok', 'reel', 'shorts', 'content creation', 
                                   'video', 'editing', 'thumbnails', 'views', 'engagement']
        
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in marketing_keywords):
            return """You are an expert marketing strategist with deep knowledge of digital marketing, 
                    brand building, and campaign optimization. Provide specific, actionable advice 
                    based on current market data and trends."""
                    
        elif any(keyword in question_lower for keyword in script_keywords):
            return """You are a professional copywriter specializing in marketing content and 
                    advertising scripts. Create engaging, persuasive content that aligns with 
                    brand voice and marketing objectives."""
                    
        elif any(keyword in question_lower for keyword in analysis_keywords):
            return """You are a data-driven marketing analyst expert in interpreting market trends, 
                    consumer behavior, and campaign performance. Provide analytical insights and 
                    data-based recommendations."""
                    
        elif any(keyword in question_lower for keyword in content_creation_keywords):
            return """You are an expert content strategist specializing in video creation, social media growth, 
                    and audience engagement. Provide detailed recommendations on:
                    - Video and audio quality improvements
                    - Background music and lighting setup
                    - Engaging scriptwriting techniques
                    - Editing styles to enhance watch time
                    - Thumbnail and title optimization for better click-through rates
                    - Platform-specific growth strategies (YouTube, Instagram Reels, TikTok, etc.)
                    - Increasing viewer engagement and retention"""
                    
        else:
            return """You are a knowledgeable marketing assistant with expertise in various aspects 
                    of digital marketing, content creation, and market analysis. Provide helpful, 
                    accurate information based on the given context."""


    def _create_chat_prompt(self, category, question, context, mode=None, script_content=None):
        """Create detailed prompt with context for the chat model, incorporating script modes"""
        base_prompt = f"""
        Context for {category} category:
        
        User Question: {question}
        
        Context used: {json.dumps(context, indent=4)}
        """
        
        if mode == "script_creation":
            return base_prompt + "\n" + self.script_prompts["script_creation"]
        elif mode == "script_enhance":
            if script_content:
                return base_prompt + f"\nOriginal Script:\n{script_content}\n\n" + self.script_prompts["script_enhance"]
            else:
                return base_prompt + "\nError: Script content is required for enhancement mode."
        else:
            # Return original marketing-focused prompt
            return base_prompt + """
            Please provide a detailed response that:
            1. Directly addresses the user's question
            2. Incorporates relevant market data and trends
            3. Provides specific, actionable recommendations when applicable
            4. Maintains accuracy and relevance to the {category} category
            5. Includes examples or specifics when helpful
            
            If the question is related to content creation, include:
            - Video and audio quality improvements
            - Background music and lighting setup
            - Engaging scriptwriting techniques
            - Editing styles to enhance watch time
            - Thumbnail and title optimization for better click-through rates
            - Platform-specific growth strategies (YouTube, Instagram Reels, TikTok, etc.)
            - Increasing viewer engagement and retention
            
            Response should be clear, concise, and directly useful for marketing or content creation purposes.
            """
