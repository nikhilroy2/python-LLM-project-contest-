"""
LLM-powered market analysis module.
Uses Google Gemini to analyze market questions and make predictions.
"""
from typing import Dict, Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Uses LLMs to analyze markets and make predictions."""
    
    def __init__(self, provider: str = "gemini", gemini_key: Optional[str] = None, 
                 openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
        """
        Initialize LLM analyzer.
        
        Args:
            provider: 'gemini', 'openai', or 'anthropic'
            gemini_key: Google Gemini API key
            openai_key: OpenAI API key (optional)
            anthropic_key: Anthropic API key (optional)
        """
        self.provider = provider
        self.gemini_key = gemini_key
        self.openai_key = openai_key
        self.anthropic_key = anthropic_key
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        try:
            if self.provider == "gemini" and self.gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                
                # Use free-tier compatible models first (these have better quota limits)
                # Priority order: free-tier friendly models first
                free_tier_models = [
                    'gemini-1.5-flash',           # Free tier, fast
                    'gemini-flash-latest',        # Latest flash (usually free tier)
                    'gemini-2.0-flash-lite',      # Lite version (free tier)
                    'gemini-2.0-flash',           # Flash model
                ]
                
                model_initialized = False
                last_error = None
                
                for model_name in free_tier_models:
                    try:
                        self._client = genai.GenerativeModel(model_name)
                        logger.info(f"Initialized Gemini with free-tier model: {model_name}")
                        model_initialized = True
                        break
                    except Exception as e:
                        last_error = e
                        logger.debug(f"Could not use model {model_name}: {e}")
                        continue
                
                if not model_initialized:
                    logger.warning(f"Could not initialize free-tier models. Last error: {last_error}")
                    logger.info("Gemini will work but may have quota limitations")
                    # Try gemini-1.5-flash as last resort (most compatible)
                    try:
                        self._client = genai.GenerativeModel('gemini-1.5-flash')
                        logger.info("Initialized Gemini with gemini-1.5-flash (fallback)")
                        model_initialized = True
                    except Exception as e:
                        logger.error(f"Failed to initialize Gemini: {e}")
                        self._client = None
                
                if model_initialized:
                    logger.info("Google Gemini client initialized successfully")
            elif self.provider == "openai" and self.openai_key:
                import openai
                self._client = openai.OpenAI(api_key=self.openai_key)
                logger.info("OpenAI client initialized")
            elif self.provider == "anthropic" and self.anthropic_key:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.anthropic_key)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("No LLM API key provided, LLM analysis disabled")
                self._client = None
        except ImportError as e:
            logger.warning(f"Failed to import LLM library: {e}")
            self._client = None
        except Exception as e:
            logger.error(f"Error initializing LLM client: {e}")
            self._client = None
    
    def analyze_market(self, market: Dict) -> Tuple[float, float, str]:
        """
        Analyze a market using LLM and return prediction.
        
        Args:
            market: Market dictionary from Manifold API
            
        Returns:
            Tuple of (probability, confidence, reasoning)
            - probability: Predicted probability (0-1)
            - confidence: Confidence in prediction (0-1)
            - reasoning: Explanation of the prediction
        """
        if not self._client:
            return 0.5, 0.0, "LLM analysis not available"
        
        question = market.get("question", "")
        current_prob = market.get("probability", 0.5)
        description = market.get("description", "")
        close_time = market.get("closeTime")
        
        prompt = self._build_analysis_prompt(question, description, current_prob, close_time)
        
        try:
            if self.provider == "gemini":
                response = self._analyze_with_gemini(prompt)
            elif self.provider == "openai":
                response = self._analyze_with_openai(prompt)
            else:
                response = self._analyze_with_anthropic(prompt)
            
            return self._parse_response(response)
        except Exception as e:
            error_msg = str(e)
            # Handle quota/rate limit errors specifically
            if "quota" in error_msg.lower() or "429" in error_msg or "rate limit" in error_msg.lower():
                logger.warning(f"Gemini API quota/rate limit exceeded: {error_msg[:100]}")
                return 0.5, 0.0, "Gemini API quota exceeded - using fallback"
            elif "ResourceExhausted" in str(type(e).__name__):
                logger.warning(f"Gemini API resource exhausted: {error_msg[:100]}")
                return 0.5, 0.0, "Gemini API resource exhausted - using fallback"
            else:
                logger.error(f"Error in LLM analysis: {e}")
                return 0.5, 0.0, f"Analysis error: {str(e)[:100]}"
    
    def _build_analysis_prompt(self, question: str, description: str, 
                              current_prob: float, close_time: Optional[int]) -> str:
        """Build the analysis prompt for the LLM."""
        time_info = ""
        if close_time:
            from datetime import datetime
            close_dt = datetime.fromtimestamp(close_time / 1000)
            time_info = f"The market closes on {close_dt.strftime('%Y-%m-%d %H:%M:%S')}."
        
        prompt = f"""You are an expert at analyzing prediction markets. Analyze the following market and provide your assessment.

Market Question: {question}

Description: {description if description else "No additional description provided."}

Current Market Probability: {current_prob:.1%}
{time_info}

Please provide:
1. Your predicted probability that this event will occur (as a number between 0 and 1)
2. Your confidence in this prediction (as a number between 0 and 1)
3. A brief reasoning for your prediction (2-3 sentences)

Respond in JSON format:
{{
    "probability": 0.65,
    "confidence": 0.75,
    "reasoning": "Your reasoning here"
}}"""
        return prompt
    
    def _analyze_with_gemini(self, prompt: str) -> str:
        """Analyze using Google Gemini API."""
        if not self._client:
            raise Exception("Gemini client not initialized")
        
        full_prompt = f"""You are an expert prediction market analyst. Always respond with valid JSON.

{prompt}"""
        
        try:
            response = self._client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 300,
                }
            )
            return response.text
        except Exception as e:
            # Re-raise to be handled by analyze_market
            raise
    
    def _analyze_with_openai(self, prompt: str) -> str:
        """Analyze using OpenAI API."""
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",  # Using cost-effective model
            messages=[
                {"role": "system", "content": "You are an expert prediction market analyst. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    
    def _analyze_with_anthropic(self, prompt: str) -> str:
        """Analyze using Anthropic API."""
        response = self._client.messages.create(
            model="claude-3-haiku-20240307",  # Using cost-effective model
            max_tokens=300,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_response(self, response: str) -> Tuple[float, float, str]:
        """Parse LLM response and extract prediction."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                prob = float(data.get("probability", 0.5))
                confidence = float(data.get("confidence", 0.5))
                reasoning = data.get("reasoning", "No reasoning provided")
                
                # Clamp values
                prob = max(0.0, min(1.0, prob))
                confidence = max(0.0, min(1.0, confidence))
                
                return prob, confidence, reasoning
            else:
                # Fallback: try to extract numbers
                import re
                prob_match = re.search(r'probability["\']?\s*:\s*([0-9.]+)', response)
                conf_match = re.search(r'confidence["\']?\s*:\s*([0-9.]+)', response)
                
                prob = float(prob_match.group(1)) if prob_match else 0.5
                confidence = float(conf_match.group(1)) if conf_match else 0.5
                reasoning = response[:200]  # First 200 chars as reasoning
                
                return prob, confidence, reasoning
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return 0.5, 0.0, f"Parse error: {str(e)}"

