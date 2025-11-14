import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import time

def initialize_gemini():
    """Initialize Gemini API with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    genai.configure(api_key=api_key)
    # Use gemini-2.5-flash (Gemini 2.5 Flash)
    return genai.GenerativeModel('gemini-2.5-flash')


def analyze_news_insights(news_articles: List[Dict], category: str) -> Dict[str, Any]:
    """
    Analyze news articles to extract actionable insights for product launch
    """
    try:
        model = initialize_gemini()
        
        # Prepare news summary for Gemini
        news_summary = "\n\n".join([
            f"Title: {article.get('title', 'N/A')}\nDescription: {article.get('description', 'N/A')}"
            for article in news_articles[:10]  # Analyze top 10 articles
        ])
        
        prompt = f"""
        Analyze these recent news articles about the {category} industry and extract actionable insights for launching a new product.
        
        NEWS ARTICLES:
        {news_summary}
        
        Based on these articles, provide strategic insights for product development and launch.
        
        Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
        {{
            "key_trends": ["Trend 1", "Trend 2", "Trend 3"],
            "consumer_behaviors": ["Behavior insight 1", "Behavior insight 2", "Behavior insight 3"],
            "market_opportunities": ["Opportunity 1", "Opportunity 2"],
            "competitive_insights": ["Insight 1", "Insight 2"],
            "launch_recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
            "positioning_strategy": "Brief positioning recommendation based on current trends",
            "timing_insights": "When to launch and why based on market trends"
        }}
        """
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up response
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        return json.loads(result_text)
        
    except Exception as e:
        print(f"Error analyzing news insights: {e}")
        return {
            "key_trends": [],
            "consumer_behaviors": [],
            "market_opportunities": [],
            "competitive_insights": [],
            "launch_recommendations": [],
            "positioning_strategy": "Unable to generate insights",
            "timing_insights": "Unable to generate insights"
        }


def analyze_product_description(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a single product's description, nutrition, and ingredients
    Returns detailed analysis including pros, cons, and health insights
    """
    try:
        model = initialize_gemini()
        
        prompt = f"""
        Analyze this product from Blinkit and provide insights:
        
        Product Name: {product.get('name', 'N/A')}
        Brand: {product.get('brand', 'N/A')}
        Weight: {product.get('weight', 'N/A')}
        Price: ₹{product.get('price', 'N/A')}
        Price per 100g: ₹{product.get('price_per_100g', 'N/A')}
        
        Based on the product name and brand, provide a detailed analysis. Be specific and practical.
        
        Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
        {{
            "description": "Brief 2-3 sentence product description",
            "nutrition_analysis": "Analysis of likely nutritional value and health benefits based on product type",
            "ingredient_analysis": "Analysis of typical ingredients in this type of product",
            "pros": ["Specific pro 1", "Specific pro 2", "Specific pro 3"],
            "cons": ["Specific con 1", "Specific con 2", "Specific con 3"],
            "health_score": "7/10 - Brief justification",
            "target_audience": "Specific target customer segment"
        }}
        """
        
        # Retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                text = response.text.strip()
                
                # Clean up response
                text = text.replace('```json', '').replace('```', '').strip()
                
                # Try to find JSON in the response
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    text = text[start:end]
                
                analysis = json.loads(text)
                return analysis
                
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'quota' in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 15  # 15, 30, 45 seconds
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                raise e
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error for {product.get('name', 'Unknown')}: {e}")
        print(f"Response text: {text[:200] if 'text' in locals() else 'N/A'}")
        return {
            "error": f"JSON parsing failed: {str(e)}",
            "description": f"Analysis could not be completed for this product",
            "nutrition_analysis": "Unable to analyze - JSON parsing error",
            "ingredient_analysis": "Unable to analyze - JSON parsing error",
            "pros": ["Product data available"],
            "cons": ["Analysis temporarily unavailable"],
            "health_score": "N/A",
            "target_audience": "General consumers"
        }
    except Exception as e:
        error_msg = str(e)
        print(f"Error analyzing {product.get('name', 'Unknown')}: {error_msg}")
        
        # Check if it's a rate limit error
        if '429' in error_msg or 'quota' in error_msg.lower():
            return {
                "error": "Rate limit exceeded",
                "description": "Please wait a few minutes and try again with fewer products (try 3-5 instead of 10)",
                "nutrition_analysis": "Rate limit reached - API quota exceeded",
                "ingredient_analysis": "Rate limit reached - API quota exceeded",
                "pros": ["Product information available"],
                "cons": ["Too many API requests - please reduce analysis count"],
                "health_score": "N/A",
                "target_audience": "General consumers"
            }
        
        return {
            "error": str(e),
            "description": "Analysis temporarily unavailable",
            "nutrition_analysis": "Error occurred during analysis",
            "ingredient_analysis": "Error occurred during analysis",
            "pros": ["Product information available"],
            "cons": ["Technical error in analysis"],
            "health_score": "N/A",
            "target_audience": "General consumers"
        }


def analyze_top_products(products: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Analyze top N products with Gemini AI
    """
    top_products = products[:top_n]
    analyzed_products = []
    
    print(f"Starting analysis of {len(top_products)} products...")
    print(f"Note: Free tier allows ~15 requests per minute. This may take a few minutes...")
    
    for idx, product in enumerate(top_products, 1):
        print(f"Analyzing product {idx}/{len(top_products)}: {product.get('name', 'Unknown')[:50]}...")
        analysis = analyze_product_description(product)
        analyzed_products.append({
            **product,
            "analysis": analysis
        })
        # Add longer delay to avoid rate limiting (free tier limit)
        if idx < len(top_products):
            print(f"Waiting 6 seconds before next request to avoid rate limits...")
            time.sleep(6)  # 6 second delay = ~10 requests per minute (safe for free tier)
    
    print(f"Completed analysis of {len(analyzed_products)} products")
    return analyzed_products


def generate_gap_analysis(analyzed_products: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """
    Generate comprehensive gap analysis and product launch recommendation
    based on drawbacks of top products
    """
    try:
        model = initialize_gemini()
        
        # Prepare product summaries for analysis
        product_summaries = []
        for i, product in enumerate(analyzed_products[:10], 1):
            analysis = product.get("analysis", {})
            summary = f"""
            Rank {i}: {product.get('brand', 'Unknown')} - {product.get('name', 'N/A')}
            Price: ₹{product.get('price', 'N/A')} ({product.get('weight', 'N/A')})
            Price/100g: ₹{product.get('price_per_100g', 'N/A')}
            Pros: {', '.join(analysis.get('pros', [])[:3]) or 'None listed'}
            Cons: {', '.join(analysis.get('cons', [])[:3]) or 'None listed'}
            Health Score: {analysis.get('health_score', 'N/A')}
            """
            product_summaries.append(summary)
        
        prompt = f"""
        You are a product development expert analyzing the "{query}" category.
        
        Top Products Summary:
        {chr(10).join(product_summaries)}
        
        Based on this analysis, create strategic product launch recommendations.
        
        Return ONLY a valid JSON object (no markdown, no code blocks) with this structure:
        {{
            "market_overview": "2-3 sentence overview of the market",
            "common_strengths": ["Strength 1", "Strength 2", "Strength 3"],
            "common_weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
            "market_gaps": [
                {{"gap": "Gap description", "opportunity": "Why this matters", "priority": "High"}},
                {{"gap": "Gap description", "opportunity": "Why this matters", "priority": "Medium"}}
            ],
            "recommended_product": {{
                "product_concept": "Clear product concept",
                "key_features": ["Feature 1", "Feature 2", "Feature 3"],
                "target_price_range": "₹X - ₹Y",
                "usp": "Unique selling point",
                "target_audience": "Target customers",
                "competitive_advantages": ["Advantage 1", "Advantage 2"]
            }},
            "implementation_strategy": {{
                "ingredients_to_include": ["Ingredient 1", "Ingredient 2"],
                "ingredients_to_avoid": ["Ingredient 1", "Ingredient 2"],
                "packaging_recommendations": "Packaging advice",
                "pricing_strategy": "Pricing approach"
            }},
            "success_metrics": ["Metric 1", "Metric 2", "Metric 3"]
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up response
        text = text.replace('```json', '').replace('```', '').strip()
        
        # Try to find JSON in the response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            text = text[start:end]
        
        gap_analysis = json.loads(text)
        return gap_analysis
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in gap analysis: {e}")
        print(f"Response text: {text[:200] if 'text' in locals() else 'N/A'}")
        return {
            "error": f"JSON parsing failed: {str(e)}",
            "market_overview": f"The {query} market shows diverse offerings with varying price points and features.",
            "common_strengths": ["Brand variety", "Multiple price points", "Wide availability"],
            "common_weaknesses": ["Analysis temporarily unavailable"],
            "market_gaps": [{"gap": "Analysis in progress", "opportunity": "Check back soon", "priority": "Medium"}],
            "recommended_product": {
                "product_concept": "Analysis temporarily unavailable",
                "key_features": ["To be determined"],
                "target_price_range": "To be determined",
                "usp": "Analysis in progress",
                "target_audience": "General consumers",
                "competitive_advantages": ["To be determined"]
            },
            "implementation_strategy": {
                "ingredients_to_include": ["Analysis in progress"],
                "ingredients_to_avoid": ["Analysis in progress"],
                "packaging_recommendations": "Analysis in progress",
                "pricing_strategy": "Analysis in progress"
            },
            "success_metrics": ["Market response", "Customer satisfaction", "Sales growth"]
        }
    except Exception as e:
        print(f"Error in gap analysis: {str(e)}")
        return {
            "error": str(e),
            "market_overview": f"Error analyzing {query} market",
            "common_strengths": ["Data available"],
            "common_weaknesses": ["Technical error occurred"],
            "market_gaps": [],
            "recommended_product": {},
            "implementation_strategy": {},
            "success_metrics": []
        }
