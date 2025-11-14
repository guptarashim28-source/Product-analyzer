"""
STP (Segmentation, Targeting, Positioning) Analysis Helper
Analyzes market segments, recommends target segments, and creates positioning statements
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def analyze_stp(products, category, gap_analysis=None, news_insights=None, google_trends=None):
    """
    Perform comprehensive STP analysis using Gemini AI
    
    Args:
        products: List of scraped product data
        category: Product category
        gap_analysis: Gap analysis results
        news_insights: News insights from AI analysis
        google_trends: Google Trends data
    
    Returns:
        dict: STP analysis with segments, target recommendation, and positioning
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare context for analysis
        product_summary = "\n".join([
            f"- {p.get('name', 'Unknown')}: ₹{p.get('price', 'N/A')}, {p.get('description', 'No description')}"
            for p in products[:10]  # Limit to first 10 products
        ])
        
        gaps = ""
        if gap_analysis:
            gaps = f"""
Market Gaps Identified:
{chr(10).join([f"- {gap}" for gap in gap_analysis.get('gaps', [])])}

Market Opportunities:
{chr(10).join([f"- {opp}" for opp in gap_analysis.get('opportunities', [])])}
"""
        
        news_context = ""
        if news_insights:
            news_context = f"""
Key Market Trends:
{chr(10).join([f"- {trend}" for trend in news_insights.get('key_trends', [])])}

Consumer Behaviors:
{chr(10).join([f"- {behavior}" for behavior in news_insights.get('consumer_behaviors', [])])}
"""
        
        trends_context = ""
        if google_trends and not google_trends.get('error'):
            trends_context = f"""
Google Trends Insights:
- Trend Direction: {google_trends.get('trend_direction', 'unknown').upper()}
- Average Interest: {google_trends.get('average_interest', 0)}/100
- Peak Interest: {google_trends.get('peak_interest', 0)}/100
- Rising Queries: {', '.join(google_trends.get('related_queries', {}).get('rising', [])[:5])}
"""
        
        prompt = f"""
You are a strategic marketing consultant. Perform a comprehensive STP (Segmentation, Targeting, Positioning) analysis for the {category} category in India.

**Current Market Context:**

Products in Market:
{product_summary}

{gaps}
{news_context}
{trends_context}

**Your Task:**

1. **SEGMENTATION**: Identify 3-4 key market segments in this category. For each segment, provide:
   - Segment Name
   - Demographics (age, income, location type)
   - Psychographics (lifestyle, values, attitudes)
   - Behavioral Traits (purchase patterns, usage frequency)
   - Size & Growth Potential
   - Current Market Coverage (well-served or underserved)

2. **TARGETING**: Recommend THE BEST target segment for a NEW ENTRANT. Provide:
   - Which segment to target and why
   - Specific reasons (attractiveness, accessibility, profitability)
   - Entry barriers and how to overcome them
   - Expected market share potential in first year

3. **POSITIONING**: Create a compelling positioning statement for the new product targeting this segment:
   - Target Customer Description
   - Category/Frame of Reference
   - Point of Difference (unique benefit)
   - Reason to Believe (why it's credible)
   - Full Positioning Statement in format: "For [target customer] who [need/opportunity], [product name] is a [category] that [unique benefit] because [reason to believe]."

**Format your response as JSON:**
{{
    "segmentation": [
        {{
            "segment_name": "string",
            "demographics": "string",
            "psychographics": "string",
            "behavioral_traits": "string",
            "size_and_growth": "string",
            "market_coverage": "string"
        }}
    ],
    "targeting": {{
        "recommended_segment": "string",
        "rationale": ["reason 1", "reason 2", "reason 3"],
        "entry_barriers": ["barrier 1", "barrier 2"],
        "how_to_overcome": ["strategy 1", "strategy 2"],
        "expected_market_share": "string"
    }},
    "positioning": {{
        "target_customer": "string",
        "category": "string",
        "point_of_difference": "string",
        "reason_to_believe": "string",
        "positioning_statement": "string",
        "key_messages": ["message 1", "message 2", "message 3"]
    }}
}}

Be specific, data-driven, and actionable. Focus on realistic opportunities for a new entrant in the Indian market.
"""
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        # Clean and parse JSON response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        import json
        stp_analysis = json.loads(result_text)
        
        return stp_analysis
        
    except Exception as e:
        print(f"Error in STP analysis: {str(e)}")
        return {
            "error": str(e),
            "segmentation": [],
            "targeting": {},
            "positioning": {}
        }
