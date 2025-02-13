from flask import Blueprint, jsonify, request
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import json
import logging
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analytics_routes = Blueprint('analytics_routes', __name__)

class PromptHandler:
    def __init__(self):
        self.mistral_client = httpx.AsyncClient(
            base_url="https://api.groq.com/v1",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
        )
        self.openai_client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
        )

    def _generate_market_analysis_prompt(self, category: str, query: str, data: Dict[str, Any]) -> str:
        return f"""Analyze the market insights for {category} focusing on {query}.
        
        Context:
        - Total Videos Analyzed: {data['total_videos']}
        - Average Engagement Rate: {data['avg_engagement']}%
        - Top Performing Content: {data['top_content']}
        - Current Trends: {data['trends']}
        
        Please provide:
        1. Market positioning analysis
        2. Target audience insights
        3. Competitor landscape
        4. Market opportunities
        5. Key success factors
        
        Base your analysis on the provided data and current market context.
        Be specific and provide actionable insights."""

    def _generate_content_strategy_prompt(self, category: str, query: str, data: Dict[str, Any]) -> str:
        return f"""Develop a content strategy analysis for {category} with focus on {query}.
        
        Available Data:
        - Engagement Patterns: {data['engagement_patterns']}
        - Best Performing Times: {data['peak_times']}
        - Content Types: {data['content_types']}
        - Audience Response: {data['audience_metrics']}
        
        Provide insights on:
        1. Best performing content types and why
        2. Optimal posting schedule
        3. Content themes that resonate
        4. Engagement triggers
        5. Format recommendations
        
        Support all insights with data-driven evidence."""

    def _generate_campaign_insights_prompt(self, category: str, query: str, data: Dict[str, Any]) -> str:
        return f"""Analyze campaign performance for {category} considering {query}.
        
        Campaign Data:
        - Performance Metrics: {data['performance_metrics']}
        - ROI Data: {data['roi_data']}
        - Conversion Patterns: {data['conversion_patterns']}
        - Seasonal Trends: {data['seasonal_data']}
        
        Provide:
        1. Success factors in top campaigns
        2. ROI optimization opportunities
        3. Conversion drivers
        4. Seasonal strategy recommendations
        5. Campaign structure insights
        
        Focus on actionable insights backed by data."""

    async def get_mistral_analysis(self, 
                                 category: str, 
                                 query: str, 
                                 analysis_type: str, 
                                 data: Dict[str, Any]) -> Dict[str, Any]:
        """Get analysis from Mistral model via Groq API"""
        prompt_functions = {
            'market': self._generate_market_analysis_prompt,
            'content': self._generate_content_strategy_prompt,
            'campaign': self._generate_campaign_insights_prompt
        }
        
        prompt = prompt_functions[analysis_type](category, query, data)
        
        try:
            response = await self.mistral_client.post("/chat/completions", json={
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2048
            })
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'analysis': result['choices'][0]['message']['content'],
                    'model': 'mistral',
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Mistral API error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling Mistral API: {str(e)}")
            return None

    async def get_gpt4_analysis(self, 
                              category: str, 
                              query: str, 
                              analysis_type: str, 
                              data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get analysis from GPT-4 for complex queries"""
        # Similar prompt structure but with more strategic focus
        prompt_functions = {
            'market': self._generate_market_analysis_prompt,
            'content': self._generate_content_strategy_prompt,
            'campaign': self._generate_campaign_insights_prompt
        }
        
        prompt = prompt_functions[analysis_type](category, query, data)
        
        try:
            response = await self.openai_client.post("/chat/completions", json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2048
            })
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'analysis': result['choices'][0]['message']['content'],
                    'model': 'gpt-4o',
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"GPT-4o API error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling GPT-4o API: {str(e)}")
            return None

prompt_handler = PromptHandler()

@analytics_routes.route('/api/analytics/<category>/market', methods=['POST'])
async def market_analysis(category):
    """Get market analysis insights"""
    try:
        data = request.json
        query = data.get('query', '')
        use_gpt4 = data.get('use_gpt4', False)
        
        # Get analysis based on model preference
        if use_gpt4:
            analysis = await prompt_handler.get_gpt4_analysis(
                category, query, 'market', data)
        else:
            analysis = await prompt_handler.get_mistral_analysis(
                category, query, 'market', data)
            
        if analysis:
            return jsonify(analysis)
        else:
            return jsonify({'error': 'Failed to generate analysis'}), 500
    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_routes.route('/api/analytics/<category>/content', methods=['POST'])
async def content_strategy(category):
    """Get content strategy insights"""
    try:
        data = request.json
        query = data.get('query', '')
        use_gpt4 = data.get('use_gpt4', False)
        
        if use_gpt4:
            analysis = await prompt_handler.get_gpt4_analysis(
                category, query, 'content', data)
        else:
            analysis = await prompt_handler.get_mistral_analysis(
                category, query, 'content', data)
            
        if analysis:
            return jsonify(analysis)
        else:
            return jsonify({'error': 'Failed to generate analysis'}), 500
    except Exception as e:
        logger.error(f"Error in content strategy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_routes.route('/api/analytics/<category>/campaign', methods=['POST'])
async def campaign_insights(category):
    """Get campaign performance insights"""
    try:
        data = request.json
        query = data.get('query', '')
        use_gpt4 = data.get('use_gpt4', False)
        
        if use_gpt4:
            analysis = await prompt_handler.get_gpt4_analysis(
                category, query, 'campaign', data)
        else:
            analysis = await prompt_handler.get_mistral_analysis(
                category, query, 'campaign', data)
            
        if analysis:
            return jsonify(analysis)
        else:
            return jsonify({'error': 'Failed to generate analysis'}), 500
    except Exception as e:
        logger.error(f"Error in campaign insights: {str(e)}")
        return jsonify({'error': str(e)}), 500