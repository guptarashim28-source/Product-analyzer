import streamlit as st
import requests
import json
from typing import Dict, Any

st.set_page_config(
    page_title="🛒 Blinkit Product Analyzer",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 3rem;
    }
    .product-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #4ECDC4;
    }
    .gap-analysis {
        background-color: #fff;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin: 2rem 0;
        color: #2c3e50;
    }
    .gap-analysis h4 {
        color: #e74c3c;
    }
    .gap-analysis p {
        color: #34495e;
    }
    .news-card {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .news-card h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .news-card p {
        color: #34495e;
    }
    .news-card a {
        color: #3498db;
        text-decoration: none;
        font-weight: 500;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .insights-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
    }
    .insights-box h3, .insights-box h4 {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🛒 Blinkit Product Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">AI-Powered Market Intelligence with Gemini & NewsAPI</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shopping-cart.png", width=100)
    st.title("⚙️ Configuration")
    
    category = st.text_input("📦 Product Category", value="snacks", placeholder="e.g., protein bar, cookies")
    pincode = st.text_input("📍 Pincode", value="380015", placeholder="e.g., 110001")
    max_products = st.slider("🔢 Max Products to Analyze", min_value=3, max_value=10, value=3)
    
    st.warning("⏱️ **Estimated Time:** ~2 minutes for scraping + 30 seconds per product for AI analysis")
    
    st.divider()
    
    # API endpoint selection
    api_mode = st.radio("🌐 API Mode", ["Local (localhost:8000)", "Custom URL"])
    
    if api_mode == "Custom URL":
        api_url = st.text_input("API URL", value="https://your-app.onrender.com")
    else:
        api_url = "http://localhost:8000"
    
    st.divider()
    
    analyze_button = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🔑 Features")
    st.markdown("- ✅ Live Blinkit Scraping")
    st.markdown("- 🤖 Gemini AI Analysis")
    st.markdown("- 📰 Market News & Trends")
    st.markdown("- 📊 Gap Analysis")
    st.markdown("- 💡 Product Recommendations")

# Main content
if analyze_button:
    if not category:
        st.error("❌ Please enter a product category!")
    else:
        with st.spinner(f"🔍 Analyzing {category} products in pincode {pincode}... This may take 3-5 minutes. Please wait..."):
            try:
                # Make API request with longer timeout
                response = requests.post(
                    f"{api_url}/analyze",
                    json={
                        "category": category,
                        "max_products": max_products,
                        "pincode": pincode
                    },
                    timeout=600  # 10 minutes timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    report = data.get("report", {})
                    
                    # Success metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{data.get('total_products', 0)}</h3>
                            <p>Products Scraped</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{len(report.get('products', []))}</h3>
                            <p>Analyzed by AI</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{len(report.get('news_insights', []))}</h3>
                            <p>News Articles</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        gaps = report.get('gap_analysis', {}).get('market_gaps', [])
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{len(gaps)}</h3>
                            <p>Market Gaps</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Summary
                    st.success(f"✅ {report.get('summary', 'Analysis complete!')}")
                    
                    # Tabs for different sections
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 Product Analysis", "💡 Gap Analysis", "📰 News", "📈 Market Trends"])
                    
                    # Tab 1: Product Analysis
                    with tab1:
                        st.header("🔍 AI-Analyzed Products")
                        products = report.get('products', [])
                        
                        if products:
                            for i, product in enumerate(products, 1):
                                # Handle both dict and potential string formats
                                if isinstance(product, str):
                                    st.warning(f"Product {i}: {product}")
                                    continue
                                    
                                product_name = product.get('name', product.get('title', 'Unknown Product'))
                                
                                with st.expander(f"🏆 #{i} - {product_name}", expanded=(i==1)):
                                    col1, col2 = st.columns([2, 1])
                                    
                                    with col1:
                                        st.markdown(f"**Brand:** {product.get('brand', 'N/A')}")
                                        st.markdown(f"**Price:** ₹{product.get('price', 0)} ({product.get('weight', product.get('description', 'N/A'))})")
                                        price_per_100g = product.get('price_per_100g')
                                        if price_per_100g:
                                            st.markdown(f"**Price per 100g:** ₹{price_per_100g}")
                                    
                                    with col2:
                                        st.metric("Rating", "⭐ 4.0")
                                    
                                    analysis = product.get('analysis', {})
                                    
                                    # Handle case where analysis might be a string
                                    if isinstance(analysis, str):
                                        st.info(analysis)
                                    elif analysis:
                                        st.markdown("### 📝 Description")
                                        st.write(analysis.get('description', 'No description available'))
                                        
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.markdown("### ✅ Pros")
                                            pros = analysis.get('pros', [])
                                            if isinstance(pros, list):
                                                for pro in pros:
                                                    st.markdown(f"- {pro}")
                                            else:
                                                st.write(pros)
                                        
                                        with col2:
                                            st.markdown("### ❌ Cons")
                                            cons = analysis.get('cons', [])
                                            if isinstance(cons, list):
                                                for con in cons:
                                                    st.markdown(f"- {con}")
                                            else:
                                                st.write(cons)
                                        
                                        nutrition = analysis.get('nutrition_analysis', {})
                                        if nutrition:
                                            st.markdown("### 🥗 Nutrition Analysis")
                                            if isinstance(nutrition, dict):
                                                st.info(nutrition.get('summary', 'No nutrition data'))
                                            else:
                                                st.info(str(nutrition))
                                    else:
                                        st.info("No detailed analysis available for this product.")
                        else:
                            st.warning("No products analyzed yet.")
                    
                    # Tab 2: Gap Analysis
                    with tab2:
                        gap_analysis = report.get('gap_analysis', {})
                        
                        if gap_analysis and isinstance(gap_analysis, dict):
                            st.header("💡 Market Opportunity Analysis")
                            
                            # Market Overview
                            st.markdown("### 🌍 Market Overview")
                            st.info(gap_analysis.get('market_overview', 'No overview available'))
                            
                            # Strengths & Weaknesses
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### 💪 Common Strengths")
                                strengths = gap_analysis.get('common_strengths', [])
                                if isinstance(strengths, list):
                                    for strength in strengths:
                                        st.success(f"✓ {strength}")
                                else:
                                    st.write(strengths)
                            
                            with col2:
                                st.markdown("### ⚠️ Common Weaknesses")
                                weaknesses = gap_analysis.get('common_weaknesses', [])
                                if isinstance(weaknesses, list):
                                    for weakness in weaknesses:
                                        st.warning(f"✗ {weakness}")
                                else:
                                    st.write(weaknesses)
                            
                            # Market Gaps
                            st.markdown("### 🎯 Identified Market Gaps")
                            gaps = gap_analysis.get('market_gaps', [])
                            if isinstance(gaps, list):
                                for gap in gaps:
                                    if isinstance(gap, dict):
                                        with st.container():
                                            st.markdown(f"""
                                            <div class="gap-analysis">
                                                <h4>🔍 {gap.get('gap', 'Unknown Gap')}</h4>
                                                <p><strong>Opportunity:</strong> {gap.get('opportunity', 'N/A')}</p>
                                                <p><strong>Priority:</strong> <span style="color: {'red' if gap.get('priority')=='High' else 'orange'};">{gap.get('priority', 'N/A')}</span></p>
                                            </div>
                                            """, unsafe_allow_html=True)
                            
                            # Recommended Product
                            recommended = gap_analysis.get('recommended_product', {})
                            if recommended and isinstance(recommended, dict):
                                st.markdown("### 🚀 Recommended Product Launch")
                                st.markdown(f"#### {recommended.get('product_concept', 'Product Concept')}")
                                
                                st.markdown("**Key Features:**")
                                features = recommended.get('key_features', [])
                                if isinstance(features, list):
                                    for feature in features:
                                        st.markdown(f"- {feature}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Target Price:** {recommended.get('target_price_range', 'N/A')}")
                                    st.markdown(f"**USP:** {recommended.get('usp', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Target Audience:** {recommended.get('target_audience', 'N/A')}")
                        else:
                            st.info("No gap analysis available.")
                    
                    # Tab 3: News
                    with tab3:
                        st.header("📰 Latest Industry News")
                        
                        # AI-Powered News Insights
                        ai_insights = report.get('ai_news_analysis', {})
                        if ai_insights and isinstance(ai_insights, dict) and ai_insights.get('key_trends'):
                            st.markdown("""
                            <div class="insights-box">
                                <h3>🤖 AI-Powered Market Insights</h3>
                                <p>Gemini AI analyzed recent news to extract actionable insights for your product launch</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### 📈 Key Market Trends")
                                for trend in ai_insights.get('key_trends', []):
                                    st.success(f"• {trend}")
                                
                                st.markdown("### 👥 Consumer Behaviors")
                                for behavior in ai_insights.get('consumer_behaviors', []):
                                    st.info(f"• {behavior}")
                                
                                st.markdown("### 💡 Market Opportunities")
                                for opp in ai_insights.get('market_opportunities', []):
                                    st.warning(f"• {opp}")
                            
                            with col2:
                                st.markdown("### 🎯 Launch Recommendations")
                                for rec in ai_insights.get('launch_recommendations', []):
                                    st.success(f"✓ {rec}")
                                
                                st.markdown("### 🏆 Competitive Insights")
                                for insight in ai_insights.get('competitive_insights', []):
                                    st.info(f"• {insight}")
                            
                            # Positioning and Timing
                            st.markdown("### 🚀 Strategic Recommendations")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Positioning Strategy:**")
                                st.write(ai_insights.get('positioning_strategy', 'N/A'))
                            with col2:
                                st.markdown("**Timing Insights:**")
                                st.write(ai_insights.get('timing_insights', 'N/A'))
                            
                            st.markdown("---")
                        
                        # News Articles
                        st.markdown("### 📰 Source News Articles")
                        news = report.get('news_insights', [])
                        
                        if news:
                            for article in news:
                                st.markdown(f"""
                                <div class="news-card">
                                    <h4>{article.get('title', 'No title')}</h4>
                                    <p>{article.get('description', 'No description')}</p>
                                    <p><small>📅 {article.get('published_at', 'N/A')} | 📰 {article.get('source', 'Unknown')}</small></p>
                                    <a href="{article.get('url', '#')}" target="_blank">Read more →</a>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No news articles found.")
                    
                    # Tab 4: Market Trends
                    with tab4:
                        st.header("📈 Market Trends & Industry Insights")
                        trends = report.get('market_trends', [])
                        news = report.get('news_insights', [])
                        
                        if trends and isinstance(trends, list) and len(trends) > 0:
                            st.markdown("### 📊 Long-term Market Trends (30-day analysis)")
                            for article in trends:
                                if isinstance(article, dict):
                                    st.markdown(f"""
                                    <div class="news-card">
                                        <h4>{article.get('title', 'No title')}</h4>
                                        <p>{article.get('description', 'No description')}</p>
                                        <p><small>📅 {article.get('published_at', 'N/A')} | 📰 {article.get('source', 'Unknown')}</small></p>
                                        <a href="{article.get('url', '#')}" target="_blank">Read more →</a>
                                    </div>
                                    """, unsafe_allow_html=True)
                        elif news and isinstance(news, list) and len(news) > 0:
                            st.info("📊 No specific 30-day trend data available. Showing recent 7-day news as trends:")
                            for article in news[:5]:  # Show first 5 news as trends
                                if isinstance(article, dict):
                                    st.markdown(f"""
                                    <div class="news-card">
                                        <h4>{article.get('title', 'No title')}</h4>
                                        <p>{article.get('description', 'No description')}</p>
                                        <p><small>📅 {article.get('published_at', 'N/A')} | 📰 {article.get('source', 'Unknown')}</small></p>
                                        <a href="{article.get('url', '#')}" target="_blank">Read more →</a>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.warning("📊 No market trends data available.")
                            st.markdown("""
                            **Why no trends?**
                            - NewsAPI free tier has limited historical data access
                            - The category might be too specific for trend analysis
                            - Market trends require broader industry keywords
                            
                            💡 **Alternative:** Check the **"News" tab** for recent industry articles that can indicate current trends.
                            
                            **What you can do:**
                            - Try broader categories (e.g., "snacks" instead of "protein snacks")
                            - Upgrade to NewsAPI paid tier for better historical data
                            - Check industry reports and analyst publications separately
                            """)
                    
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out after 10 minutes. This usually means:")
                st.markdown("""
                - The scraping is taking too long (website slow/blocking)
                - Try with fewer products (3 instead of 5+)
                - Check if the backend is still running
                - Refresh and try again
                """)
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 Cannot connect to API at {api_url}. Make sure the backend is running!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

else:
    # Welcome screen
    st.markdown("## 👋 Welcome!")
    st.markdown("""
    This app provides comprehensive market intelligence by combining:
    
    - 🔍 **Live Product Scraping** from Blinkit
    - 🤖 **AI Analysis** using Google Gemini for nutrition, ingredients, pros/cons
    - 📰 **News Intelligence** with trending articles and market insights
    - 📊 **Gap Analysis** to identify market opportunities
    - 💡 **Product Recommendations** based on competitor weaknesses
    
    ### 🚀 Get Started:
    1. Enter a product category in the sidebar (e.g., "snacks", "protein bar")
    2. Select your pincode and number of products to analyze
    3. Click **"Start Analysis"** button
    4. Wait for the AI to work its magic! ✨
    
    ### ⚙️ Setup:
    Make sure your backend API is running:
    ```bash
    cd amazon_blinkit_scrapping
    uvicorn backend:app --reload --port 8000
    ```
    """)
    
    st.info("💡 **Tip:** Start with 5 products for faster results. Each product takes ~6 seconds to analyze due to API rate limits.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Made with ❤️ using Streamlit, FastAPI, Gemini AI & NewsAPI<br>
    🛒 Blinkit Product Analyzer v1.0
</div>
""", unsafe_allow_html=True)
