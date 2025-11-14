import streamlit as st
import sys
from pathlib import Path

# Add the amazon_blinkit_scrapping directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "amazon_blinkit_scrapping"))

from scraper_logic import scrape_blinkit, analyze_products_with_gemini_and_news

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
    }
    .news-card {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🛒 Blinkit Product Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem;">AI-Powered Product & Market Analysis</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Analysis Settings")
    category = st.text_input("🏷️ Product Category", value="snacks", placeholder="e.g., snacks, beverages, dairy")
    pincode = st.text_input("📍 Pincode", value="110001", placeholder="Enter delivery pincode")
    max_products = st.slider("📦 Max Products to Analyze", min_value=5, max_value=50, value=10, step=5)
    
    analyze_button = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🔑 Features")
    st.markdown("- ✅ Live Blinkit Scraping")
    st.markdown("- 🤖 Gemini AI Analysis")
    st.markdown("- 📰 Market News & Trends")
    st.markdown("- 📊 Gap Analysis")

# Main content
if analyze_button:
    if not category:
        st.error("❌ Please enter a product category!")
    else:
        with st.spinner(f"🔍 Analyzing {max_products} {category} products for pincode {pincode}... This may take 2-3 minutes. Please wait..."):
            try:
                # Step 1: Scrape products
                st.info("📥 Scraping products from Blinkit...")
                products = scrape_blinkit(category, pincode, int(max_products))
                
                if not products:
                    st.error("❌ No products found. Please try a different category or pincode.")
                    st.stop()
                
                # Step 2: Analyze with AI
                st.info(f"🤖 Analyzing {len(products)} products with Gemini AI...")
                report = analyze_products_with_gemini_and_news(products, category)
                
                # Display results
                st.success(f"✅ Analysis complete! Found {len(products)} products.")
                
                # Create tabs
                tab1, tab2, tab3 = st.tabs(["📦 Products Overview", "🎯 Gap Analysis", "📰 News & Trends"])
                
                # Tab 1: Products Overview
                with tab1:
                    st.markdown("### 🏆 Top Products Analysis")
                    
                    analyzed_products = report.get('products', [])
                    if analyzed_products:
                        for i, product in enumerate(analyzed_products, 1):
                            with st.expander(f"**{i}. {product.get('name', 'Unknown')}** - ₹{product.get('price', 'N/A')}"):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown(f"**Brand:** {product.get('brand', 'N/A')}")
                                    st.markdown(f"**Price:** ₹{product.get('price', 'N/A')}")
                                    if product.get('rating'):
                                        st.markdown(f"**Rating:** ⭐ {product['rating']}")
                                    
                                    analysis = product.get('ai_analysis', {})
                                    if analysis:
                                        st.markdown("**💡 AI Insights:**")
                                        st.markdown(f"- **Appeal:** {analysis.get('consumer_appeal', 'N/A')}")
                                        st.markdown(f"- **Market Trend:** {analysis.get('market_trend', 'N/A')}")
                                        st.markdown(f"- **Target Audience:** {analysis.get('target_audience', 'N/A')}")
                                
                                with col2:
                                    if product.get('image_url'):
                                        st.image(product['image_url'], width=150)
                    else:
                        st.warning("No detailed product analysis available.")
                
                # Tab 2: Gap Analysis
                with tab2:
                    st.markdown("### 🎯 Market Gap Analysis")
                    
                    gap_analysis = report.get('gap_analysis', {})
                    if gap_analysis and isinstance(gap_analysis, dict):
                        st.markdown('<div class="gap-analysis">', unsafe_allow_html=True)
                        
                        if gap_analysis.get('missing_segments'):
                            st.markdown("#### 🔍 Missing Market Segments")
                            for segment in gap_analysis['missing_segments']:
                                st.markdown(f"- {segment}")
                        
                        if gap_analysis.get('product_opportunities'):
                            st.markdown("#### 💡 Product Opportunities")
                            for opp in gap_analysis['product_opportunities']:
                                st.markdown(f"- {opp}")
                        
                        if gap_analysis.get('price_gaps'):
                            st.markdown("#### 💰 Price Gap Opportunities")
                            for gap in gap_analysis['price_gaps']:
                                st.markdown(f"- {gap}")
                        
                        if gap_analysis.get('recommendations'):
                            st.markdown("#### 🎯 Strategic Recommendations")
                            for rec in gap_analysis['recommendations']:
                                st.markdown(f"- {rec}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("Gap analysis not available.")
                
                # Tab 3: News & Trends
                with tab3:
                    st.markdown("### 📰 Market News & Trends")
                    
                    news_insights = report.get('news_insights', {})
                    if news_insights and isinstance(news_insights, dict):
                        if news_insights.get('summary'):
                            st.markdown("#### 📊 Market Summary")
                            st.info(news_insights['summary'])
                        
                        if news_insights.get('key_trends'):
                            st.markdown("#### 📈 Key Trends")
                            for trend in news_insights['key_trends']:
                                st.markdown(f"- {trend}")
                        
                        if news_insights.get('opportunities'):
                            st.markdown("#### 💡 Market Opportunities")
                            for opp in news_insights['opportunities']:
                                st.markdown(f"- {opp}")
                    
                    # Display news articles
                    news_articles = report.get('news', [])
                    if news_articles:
                        st.markdown("#### 📰 Recent News Articles")
                        for article in news_articles[:5]:
                            with st.container():
                                st.markdown(f"**{article.get('title', 'No title')}**")
                                st.markdown(f"*Source: {article.get('source', {}).get('name', 'Unknown')}*")
                                if article.get('description'):
                                    st.markdown(article['description'])
                                if article.get('url'):
                                    st.markdown(f"[Read more]({article['url']})")
                                st.markdown("---")
                    else:
                        st.info("No recent news articles found.")
                        
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)

else:
    # Welcome screen
    st.markdown("""
    ### 👋 Welcome to Blinkit Product Analyzer!
    
    This tool helps you:
    - 📊 Analyze market trends for any product category
    - 🎯 Identify gaps and opportunities
    - 💡 Get AI-powered insights
    - 📰 Stay updated with latest market news
    
    **Getting Started:**
    1. Enter a product category (e.g., "snacks", "beverages")
    2. Enter your delivery pincode
    3. Click "Start Analysis"
    4. Wait 2-3 minutes for results
    
    **Note:** Make sure your API keys are configured in the `.env` file.
    """)
