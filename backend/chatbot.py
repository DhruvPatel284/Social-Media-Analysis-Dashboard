from flask import jsonify, request
from groq import Groq
from datetime import datetime
import json
from config import *
from simple_analytics import DashboardAnalytics
from advanced_analytics import AdvancedAnalytics
from text_analytics import TextAnalytics

class MarketingChatbot:
    def __init__(self):
        self.analytics = DashboardAnalytics()
        self.advanced_analytics = AdvancedAnalytics()
        self.text_analytics = TextAnalytics()
        self.groq_client = Groq(api_key=GROQ_API_KEY)

    def get_context_data(self, category):
        """Gather relevant context data for the category"""
        try:
            # Get base metrics
            engagement_data = self.analytics.get_engagement_metrics(category)
            trend_data = self.analytics.get_search_trends(category)
            channel_data = self.analytics.get_channel_performance(category)
            
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

    def generate_response(self, category, user_question):
        """Generate chatbot response using Groq's Mistral model"""
        try:
            # Get context data
            context = self.get_context_data(category)
            
            # Create dynamic system prompt based on question type
            system_prompt = self._create_system_prompt(user_question)
            
            # Create detailed prompt with context
            prompt = self._create_chat_prompt(category, user_question, context)
            
            # Get response from Groq
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=2048
            )
            
            return {
                "response": response.choices[0].message.content,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": category,
                    "context_used": bool(context)
                }
            }
        except Exception as e:
            return {"error": f"Error generating response: {str(e)}"}

    def _create_system_prompt(self, question):
        """Create appropriate system prompt based on question type"""
        # Keywords for different types of questions
        marketing_keywords = ['campaign', 'marketing', 'advertisement', 'promote', 'strategy']
        script_keywords = ['script', 'copy', 'write', 'content', 'message']
        analysis_keywords = ['compare', 'analyze', 'trend', 'performance', 'metrics']
        
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
                     
        else:
            return """You are a knowledgeable marketing assistant with expertise in various aspects 
                     of digital marketing, content creation, and market analysis. Provide helpful, 
                     accurate information based on the given context."""

    def _create_chat_prompt(self, category, question, context):
        """Create detailed prompt with context for the chat model"""
        return f"""
        Context for {category} category:
        
        User Question: {question}
        
        Please provide a detailed response that:
        1. Directly addresses the user's question
        2. Incorporates relevant market data and trends
        3. Provides specific, actionable recommendations when applicable
        4. Maintains accuracy and relevance to the {category} category
        5. Includes examples or specifics when helpful
        
        Response should be clear, concise, and directly useful for marketing purposes.
        """