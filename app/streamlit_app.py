"""
Streamlit web interface for Stock Analyzer.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import StockAnalyzer
from data.database import DatabaseManager
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #00c853;
        font-weight: bold;
    }
    .negative {
        color: #ff1744;
        font-weight: bold;
    }
    .neutral {
        color: #757575;
    }
</style>
""", unsafe_allow_html=True)


def create_price_chart(data: pd.DataFrame, ticker: str):
    """Create interactive price chart with indicators."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{ticker} Price & Moving Averages', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Add moving averages if enough data
    if len(data) >= 50:
        sma_50 = data['Close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(x=data.index, y=sma_50, name='SMA 50',
                      line=dict(color='orange', width=1)),
            row=1, col=1
        )
    
    if len(data) >= 200:
        sma_200 = data['Close'].rolling(window=200).mean()
        fig.add_trace(
            go.Scatter(x=data.index, y=sma_200, name='SMA 200',
                      line=dict(color='red', width=1)),
            row=1, col=1
        )
    
    # Volume bar chart
    colors = ['red' if data['Close'][i] < data['Open'][i] else 'green' 
              for i in range(len(data))]
    fig.add_trace(
        go.Bar(x=data.index, y=data['Volume'], name='Volume',
               marker_color=colors, showlegend=False),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    return fig


def display_signals(signals: list, title: str):
    """Display analysis signals in a formatted way."""
    st.subheader(title)
    
    for signal, score, sentiment in signals:
        if sentiment == "Info":
            st.info(f"ℹ️ {signal}")
        elif sentiment in ["Positif", "Haussier"]:
            st.success(f"✅ {signal} (Score: +{score:.1f})")
        elif sentiment in ["Négatif", "Baissier"]:
            st.error(f"❌ {signal} (Score: {score:.1f})")
        else:
            st.info(f"➖ {signal}")


def display_fundamentals(fundamentals: dict):
    """Display fundamental metrics in organized sections."""
    st.subheader("📊 Données Fondamentales")
    
    # Company Info
    with st.expander("🏢 Informations de l'Entreprise", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Secteur", fundamentals.get('Sector', 'N/A'))
        with col2:
            st.metric("Industrie", fundamentals.get('Industry', 'N/A'))
        with col3:
            st.metric("Pays", fundamentals.get('Country', 'N/A'))
    
    # Valuation Metrics
    with st.expander("💰 Valorisation"):
        col1, col2, col3, col4 = st.columns(4)
        
        pe = fundamentals.get('PE_Ratio', 'N/A')
        with col1:
            st.metric("P/E Ratio", f"{pe:.2f}" if isinstance(pe, (int, float)) else "N/A")
        
        peg = fundamentals.get('PEG_Ratio', 'N/A')
        with col2:
            st.metric("PEG Ratio", f"{peg:.2f}" if isinstance(peg, (int, float)) else "N/A")
        
        pb = fundamentals.get('Price_to_Book', 'N/A')
        with col3:
            st.metric("Price/Book", f"{pb:.2f}" if isinstance(pb, (int, float)) else "N/A")
        
        ps = fundamentals.get('Price_to_Sales', 'N/A')
        with col4:
            st.metric("Price/Sales", f"{ps:.2f}" if isinstance(ps, (int, float)) else "N/A")
    
    # Profitability Metrics
    with st.expander("📈 Rentabilité"):
        col1, col2, col3 = st.columns(3)
        
        roe = fundamentals.get('ROE', 'N/A')
        with col1:
            if isinstance(roe, (int, float)):
                st.metric("ROE", f"{roe*100:.1f}%")
            else:
                st.metric("ROE", "N/A")
        
        margin = fundamentals.get('Profit_Margin', 'N/A')
        with col2:
            if isinstance(margin, (int, float)):
                st.metric("Profit Margin", f"{margin*100:.1f}%")
            else:
                st.metric("Profit Margin", "N/A")
        
        roa = fundamentals.get('ROA', 'N/A')
        with col3:
            if isinstance(roa, (int, float)):
                st.metric("ROA", f"{roa*100:.1f}%")
            else:
                st.metric("ROA", "N/A")
    
    # Growth Metrics
    with st.expander("🚀 Croissance"):
        col1, col2 = st.columns(2)
        
        rev_growth = fundamentals.get('Revenue_Growth', 'N/A')
        with col1:
            if isinstance(rev_growth, (int, float)):
                st.metric("Revenue Growth", f"{rev_growth*100:.1f}%")
            else:
                st.metric("Revenue Growth", "N/A")
        
        earn_growth = fundamentals.get('Earnings_Growth', 'N/A')
        with col2:
            if isinstance(earn_growth, (int, float)):
                st.metric("Earnings Growth", f"{earn_growth*100:.1f}%")
            else:
                st.metric("Earnings Growth", "N/A")
    
    # Debt Metrics
    with st.expander("💳 Endettement & Liquidité"):
        col1, col2, col3 = st.columns(3)
        
        dte = fundamentals.get('Debt_to_Equity', 'N/A')
        with col1:
            st.metric("Debt/Equity", f"{dte:.0f}%" if isinstance(dte, (int, float)) else "N/A")
        
        current = fundamentals.get('Current_Ratio', 'N/A')
        with col2:
            st.metric("Current Ratio", f"{current:.2f}" if isinstance(current, (int, float)) else "N/A")
        
        quick = fundamentals.get('Quick_Ratio', 'N/A')
        with col3:
            st.metric("Quick Ratio", f"{quick:.2f}" if isinstance(quick, (int, float)) else "N/A")


def main():
    """Main application logic."""
    # Initialize database manager
    db = DatabaseManager()
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Ticker input
    ticker = st.sidebar.text_input(
        "Symbole de l'action",
        value="AAPL",
        help="Entrez le symbole boursier (ex: AAPL, MSFT, MC.PA)"
    ).upper()
    
    # Period selection
    period = st.sidebar.selectbox(
        "Période d'analyse",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        help="Période pour les données historiques"
    )
    
    # Analyze button
    analyze_button = st.sidebar.button("🔍 Analyser", type="primary", use_container_width=True)
    
    # Cache controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ Cache")
    
    cache_stats = db.get_cache_stats()
    st.sidebar.metric("Prix en cache", cache_stats['stock_prices'])
    st.sidebar.metric("Fondamentaux en cache", cache_stats['fundamentals'])
    st.sidebar.metric("Analyses sauvegardées", cache_stats['analysis_results'])
    
    if st.sidebar.button("🗑️ Vider le cache", use_container_width=True):
        db.clear_all_cache()
        st.sidebar.success("Cache vidé!")
        st.rerun()
    
    # Main content
    st.title(f"📈 {PAGE_TITLE}")
    st.markdown("### Analyse technique et fondamentale d'actions boursières")
    
    # Analysis
    if analyze_button and ticker:
        with st.spinner(f"Analyse de {ticker} en cours..."):
            try:
                # Create analyzer
                analyzer = StockAnalyzer(ticker, db)
                
                # Fetch data
                if not analyzer.fetch_all_data(period):
                    st.error(f"❌ Impossible de récupérer les données pour {ticker}")
                    return
                
                # Perform analysis
                results = analyzer.analyze()
                
                if not results['success']:
                    st.error(f"❌ {results.get('error', 'Erreur inconnue')}")
                    return
                
                # Display results
                st.success(f"✅ Analyse terminée pour {ticker}")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    price = results.get('current_price', 0)
                    st.metric("Prix Actuel", f"${price:.2f}" if price else "N/A")
                
                with col2:
                    fund_score = results.get('fundamental_score', 0)
                    st.metric("Score Fondamental", f"{fund_score:+.1f}")
                
                with col3:
                    tech_score = results.get('technical_score')
                    if tech_score is not None:
                        st.metric("Score Technique", f"{tech_score:+.1f}")
                    else:
                        st.metric("Score Technique", "N/A")
                
                with col4:
                    final_score = results.get('final_score', 0)
                    st.metric("Score Final", f"{final_score:+.1f}")
                
                # Recommendation
                rec = results.get('recommendation', 'N/A')
                horizon = results.get('time_horizon', 'N/A')
                
                if "ACHAT" in rec:
                    st.success(f"### 🎯 Recommandation: {rec}")
                elif "VENTE" in rec:
                    st.error(f"### 🎯 Recommandation: {rec}")
                else:
                    st.warning(f"### 🎯 Recommandation: {rec}")
                
                st.info(f"**Horizon d'investissement:** {horizon}")
                
                # Price chart
                st.markdown("---")
                st.subheader("📊 Graphique des Prix")
                if analyzer.historical_data is not None:
                    fig = create_price_chart(analyzer.historical_data, ticker)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Signals
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if results.get('fundamental_signals'):
                        display_signals(results['fundamental_signals'], "📋 Analyse Fondamentale")
                
                with col2:
                    if results.get('technical_signals'):
                        display_signals(results['technical_signals'], "📉 Analyse Technique")
                
                # Fundamentals
                st.markdown("---")
                if analyzer.fundamentals:
                    display_fundamentals(analyzer.fundamentals)
                
                # Historical analyses
                st.markdown("---")
                st.subheader("📜 Historique des Analyses")
                history = analyzer.get_analysis_history(5)
                
                if history:
                    history_df = pd.DataFrame([
                        {
                            'Date': h['timestamp'],
                            'Recommandation': h['recommendation'],
                            'Score': f"{h['score']:+.1f}"
                        }
                        for h in history
                    ])
                    st.dataframe(history_df, use_container_width=True)
                else:
                    st.info("Aucun historique disponible")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                st.exception(e)
    
    elif not ticker:
        st.info("👈 Entrez un symbole d'action dans la barre latérale pour commencer")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>⚠️ <strong>Avertissement:</strong> Cette analyse est fournie à titre informatif uniquement.<br>
        Elle ne constitue pas un conseil financier ou d'investissement.<br>
        Consultez toujours un conseiller financier professionnel.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()