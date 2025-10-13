import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from io import BytesIO
import json

# ===========================
# PAGE CONFIGURATION
# ===========================
st.set_page_config(
    page_title="VizBot Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================
# CUSTOM CSS STYLING
# ===========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Main header styling - Elegant gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        pointer-events: none;
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        opacity: 0.8;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Card styling - Modern and clean */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    /* Success/Error message styling - Soft and elegant */
    .success-message {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        color: #065f46;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #a7f3d0;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    
    .success-message h3 {
        color: #047857;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fef2f2 0%, #fef7f7 100%);
        color: #991b1b;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #fecaca;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);
    }
    
    /* Tab styling - Modern and sleek */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 8px;
        border-radius: 16px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        padding: 0 24px;
        background: transparent;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #64748b;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transform: translateY(-1px);
    }
    
    /* Sidebar styling - Clean and modern */
    .sidebar-content {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #667eea;
        background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Chart container styling */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        overflow: hidden;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
        border: 1px solid #bfdbfe;
        border-radius: 12px;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        border: 1px solid #a7f3d0;
        border-radius: 12px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fffbeb 0%, #fefce8 100%);
        border: 1px solid #fde68a;
        border-radius: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fef7f7 100%);
        border: 1px solid #fecaca;
        border-radius: 12px;
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Smooth animations */
    * {
        transition: all 0.3s ease;
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    
    /* Enhanced hover effects */
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# CONSTANTS
# ===========================
API_URL = "http://localhost:8000"

# ===========================
# HELPER FUNCTIONS
# ===========================
def display_chart_from_backend(chart_data):
    try:
        if "error" in chart_data:
            st.error(f"❌ {chart_data['error']}")
            return False
        
        if "plotly_chart" not in chart_data:
            st.warning("⚠️ No chart data available")
            return False
        
        chart_obj = chart_data["plotly_chart"]
        
        try:
            fig_json = json.dumps(chart_obj)
            fig = pio.from_json(fig_json)
            st.plotly_chart(fig, use_container_width=True)
            return True
        except Exception as e1:
            st.warning(f"Method 1 failed: {str(e1)}")
        
        try:
            fig = go.Figure(chart_obj)
            st.plotly_chart(fig, use_container_width=True)
            return True
        except Exception as e2:
            st.warning(f"Method 2 failed: {str(e2)}")
        
        try:
            if isinstance(chart_obj, dict) and 'data' in chart_obj and 'layout' in chart_obj:
                fig = go.Figure(data=chart_obj['data'], layout=chart_obj['layout'])
                st.plotly_chart(fig, use_container_width=True)
                return True
        except Exception as e3:
            st.warning(f"Method 3 failed: {str(e3)}")
        
        st.error("❌ All chart reconstruction methods failed")
        st.error(f"Chart data type: {type(chart_obj)}")
        if isinstance(chart_obj, dict):
            st.error(f"Chart data keys: {list(chart_obj.keys())}")
        
        return False
        
    except Exception as e:
        st.error(f"❌ Unexpected error displaying chart: {str(e)}")
        st.error(f"Chart data structure: {type(chart_data)}")
        return False

def create_metric_card(title, value, delta=None):
    if delta:
        st.metric(title, value, delta)
    else:
        st.metric(title, value)

def display_data_quality_report(missing_data):
    if missing_data:
        st.markdown("### 🔍 Data Quality Issues")
        df = pd.DataFrame(missing_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("✅ No missing values detected - Data quality is excellent!")

def display_statistics_table(stats_data, title):
    if stats_data:
        st.markdown(f"### 📈 {title}")
        df = pd.DataFrame(stats_data).T
        st.dataframe(df.round(2), use_container_width=True)
    else:
        st.info(f"No {title.lower()} available")

# ===========================
# MAIN APPLICATION
# ===========================

st.markdown("""
<div class="main-header">
    <h1>📊 VizBot Analytics</h1>
    <h2>AI-Powered Exploratory Data Analysis</h2>
    <p>Transform your data into actionable insights with our intelligent analytics platform. Upload your datasets and discover patterns, trends, and correlations through beautiful, interactive visualizations.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #667eea; font-family: 'Inter', sans-serif; font-weight: 600; margin-bottom: 0.5rem;">🎯 Analysis Options</h2>
        <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Choose your data source</p>
    </div>
    """, unsafe_allow_html=True)
    
    analysis_type = st.radio(
        "Select Analysis Type:",
        ["📁 CSV File Analysis", "🗄️ Database Analysis"],
        help="Choose between uploading a CSV file or connecting to a database"
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 1rem; border-radius: 12px; margin: 1rem 0; border: 1px solid #bae6fd;">
        <h4 style="color: #0369a1; margin-bottom: 0.5rem; font-family: 'Inter', sans-serif;">✨ Key Features</h4>
        <ul style="color: #0c4a6e; font-size: 0.85rem; margin: 0; padding-left: 1rem;">
            <li>Automated data profiling</li>
            <li>Statistical analysis</li>
            <li>Interactive visualizations</li>
            <li>AI-generated insights</li>
            <li>Outlier detection</li>
            <li>Correlation analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📚 How to Use"):
        st.markdown("""
        <div style="font-family: 'Inter', sans-serif;">
        
        **📁 CSV Analysis:**
        1. 📤 Upload your CSV file
        2. 🔍 Click 'Analyze Data'
        3. 📊 Explore the generated insights
        4. 💡 Review AI recommendations
        
        **🗄️ Database Analysis:**
        1. 🔧 Select database type
        2. 🔗 Enter connection details
        3. ✅ Test connection first
        4. 🚀 Run comprehensive analysis
        
        **💡 Tips:**
        - Ensure your CSV has headers
        - Clean data yields better insights
        - Large files may take longer to process
        
        </div>
        """, unsafe_allow_html=True)

if analysis_type == "📁 CSV File Analysis":
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 class="section-header">📁 Upload Your Data</h2>
        <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">Drag and drop your CSV file or click to browse</p>
    </div>
    """, unsafe_allow_html=True)
    
    upload_container = st.container()
    with upload_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type=['csv'],
                help="Upload a CSV file to begin analysis. Maximum file size: 200MB",
                label_visibility="collapsed"
            )
    
    if uploaded_file is not None:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); 
                        padding: 1.5rem; border-radius: 16px; text-align: center; 
                        border: 1px solid #a7f3d0; margin: 1rem 0;">
                <h4 style="color: #047857; margin-bottom: 0.5rem; font-family: 'Inter', sans-serif;">
                    ✅ File Successfully Loaded
                </h4>
                <p style="color: #065f46; margin: 0.5rem 0;"><strong>📄 Name:</strong> {uploaded_file.name}</p>
                <p style="color: #065f46; margin: 0;"><strong>📊 Size:</strong> {len(uploaded_file.getvalue())/1024/1024:.2f} MB</p>
            </div>
            """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        
        st.markdown("---")
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #1e293b; font-family: 'Inter', sans-serif; margin-bottom: 0.5rem;">Ready to Discover Insights?</h3>
            <p style="color: #64748b; margin-bottom: 2rem;">Our AI will analyze your data and generate comprehensive insights in minutes</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            analyze_button = st.button(
                "🚀 Start AI Analysis", 
                type="primary", 
                use_container_width=True,
                help="Launch comprehensive AI-powered analysis of your dataset"
            )
        
        if analyze_button:
            with st.spinner("🤖 AI Agent is analyzing your data... This may take a few moments."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    response = requests.post(f"{API_URL}/api/analyze", files=files, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("""
                        <div class="success-message">
                            <h3>✅ Analysis Completed Successfully!</h3>
                            <p>Your data has been analyzed and insights have been generated.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        st.markdown("## 🤖 AI-Generated Insights")
                        with st.container():
                            st.markdown(result["narrative_summary"])
                        
                        st.markdown("---")
                        
                        tab1, tab2, tab3 = st.tabs([
                            "📊 Dataset Summary", 
                            "📈 Univariate Analysis", 
                            "🔗 Bivariate Analysis"
                        ])
                        
                        with tab1:
                            st.markdown("## 📊 Dataset Overview")
                            
                            basic_stats = result["analysis_results"]["basic_stats"]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                create_metric_card("Total Rows", f"{basic_stats['shape']['rows']:,}")
                            with col2:
                                create_metric_card("Total Columns", basic_stats["shape"]["columns"])
                            with col3:
                                create_metric_card("Duplicates", basic_stats["duplicates"])
                            with col4:
                                create_metric_card("Memory Usage", f"{basic_stats['memory_usage']:.2f} MB")
                            
                            st.markdown("---")
                            
                            missing_data = []
                            for col, count in basic_stats["missing_values"].items():
                                if count > 0:
                                    missing_data.append({
                                        "Column": col,
                                        "Missing Values": count,
                                        "Percentage": f"{basic_stats['missing_percentage'][col]:.2f}%"
                                    })
                            
                            display_data_quality_report(missing_data)
                            
                            st.markdown("---")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                display_statistics_table(basic_stats["numerical_stats"], "Numerical Statistics")
                            
                            with col2:
                                if basic_stats["categorical_stats"]:
                                    st.markdown("### 📋 Categorical Statistics")
                                    for col, stats in basic_stats["categorical_stats"].items():
                                        with st.expander(f"📋 {col}"):
                                            st.write(f"**Unique Values:** {stats['unique_values']}")
                                            st.write(f"**Most Common:** {stats['mode']}")
                                            if stats['top_values']:
                                                st.bar_chart(stats['top_values'])
                            
                            st.markdown("---")
                            outliers = result["analysis_results"]["outliers"]
                            if outliers:
                                st.markdown("### 🎯 Outlier Detection")
                                outlier_data = []
                                for col, info in outliers.items():
                                    outlier_data.append({
                                        "Column": col,
                                        "Outlier Count": info["count"],
                                        "Percentage": f"{info['percentage']:.2f}%",
                                        "Lower Bound": f"{info['lower_bound']:.2f}",
                                        "Upper Bound": f"{info['upper_bound']:.2f}"
                                    })
                                st.dataframe(pd.DataFrame(outlier_data), use_container_width=True)
                            else:
                                st.info("✅ No outliers detected in numerical columns")
                        
                        with tab2:
                            st.markdown("## 📈 Univariate Analysis")
                            st.markdown("*Individual variable distributions and patterns*")
                            
                            univariate = result["analysis_results"]["visualizations"]["univariate"]
                            
                            if univariate:
                                for viz in univariate:
                                    st.markdown(f"### {viz['type'].title()}: {viz['column']}")
                                    
                                    success = display_chart_from_backend(viz)
                                    
                                    if not success:
                                        st.info(f"Unable to display {viz['type']} for {viz['column']}")
                                    
                                    st.markdown("---")
                            else:
                                st.info("📊 No univariate visualizations available for this dataset")
                        
                        with tab3:
                            st.markdown("## 🔗 Bivariate Analysis")
                            st.markdown("*Relationships and correlations between variables*")
                            
                            correlations = result["analysis_results"]["correlations"]
                            
                            bivariate = result["analysis_results"]["visualizations"]["bivariate"]
                            heatmap_found = False
                            
                            for viz in bivariate:
                                if viz["type"] == "correlation_heatmap":
                                    st.markdown("### 🔥 Correlation Heatmap")
                                    success = display_chart_from_backend(viz)
                                    if success:
                                        heatmap_found = True
                                    break
                            
                            if not heatmap_found and "correlation_matrix" in correlations:
                                st.markdown("### 🔥 Correlation Heatmap")
                                corr_df = pd.DataFrame(correlations["correlation_matrix"])
                                
                                fig = px.imshow(
                                    corr_df,
                                    text_auto=True,
                                    aspect="auto",
                                    color_continuous_scale='RdBu_r',
                                    title="Correlation Matrix"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            if correlations.get("strong_correlations"):
                                st.markdown("### ⚡ Strong Correlations Detected")
                                strong_corr_df = pd.DataFrame(correlations["strong_correlations"])
                                st.dataframe(strong_corr_df, use_container_width=True)
                            
                            scatter_plots = [viz for viz in bivariate if viz["type"] == "scatter"]
                            
                            if scatter_plots:
                                st.markdown("### 📊 Scatter Plots")
                                for viz in scatter_plots:
                                    col1_name = viz.get("column", "X")
                                    col2_name = viz.get("second_column", "Y")
                                    
                                    st.markdown(f"#### {col1_name} vs {col2_name}")
                                    
                                    success = display_chart_from_backend(viz)
                                    
                                    if not success:
                                        st.info(f"Unable to display scatter plot for {col1_name} vs {col2_name}")
                            else:
                                st.info("📊 Not enough numerical columns for bivariate analysis")
                    
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            <h3>❌ Analysis Failed</h3>
                            <p>{response.json().get('detail', 'Unknown error occurred')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timeout. The analysis is taking too long. Please try with a smaller dataset.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Cannot connect to the API. Please make sure the backend server is running.")
                except Exception as e:
                    st.error(f"💥 An unexpected error occurred: {str(e)}")
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; 
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
                    border-radius: 20px; margin: 3rem 0; 
                    border: 1px solid rgba(102, 126, 234, 0.1);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #1e293b; font-family: 'Inter', sans-serif; font-weight: 600; margin-bottom: 1rem;">
                Ready to Unlock Your Data's Potential?
            </h3>
            <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 1.5rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                Upload your CSV file and let our AI-powered analytics platform transform your raw data into actionable insights
            </p>
            <div style="background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); 
                        padding: 1.5rem; border-radius: 12px; margin: 2rem auto; 
                        max-width: 400px; border: 1px solid #a7f3d0;">
                <h4 style="color: #047857; margin-bottom: 0.5rem;">📋 What You'll Get:</h4>
                <ul style="color: #065f46; text-align: left; margin: 0; padding-left: 1.5rem;">
                    <li>Comprehensive data profiling</li>
                    <li>Statistical analysis & insights</li>
                    <li>Interactive visualizations</li>
                    <li>AI-generated recommendations</li>
                    <li>Outlier & pattern detection</li>
                </ul>
            </div>
            <p style="color: #9ca3af; font-size: 0.9rem; margin-top: 2rem;">
                📁 Supported: CSV files up to 200MB | 🔒 Your data is processed securely
            </p>
        </div>
        """, unsafe_allow_html=True)

else:  
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 class="section-header">🗄️ Database Connection</h2>
        <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">Connect to your database and unlock powerful insights from your live data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                padding: 1.5rem; border-radius: 16px; margin: 1.5rem 0; 
                border: 1px solid #bae6fd; text-align: center;">
        <h4 style="color: #0369a1; margin-bottom: 1rem; font-family: 'Inter', sans-serif;">
            🎯 Select Your Database Type
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        db_type = st.selectbox(
            "Database Type:",
            ["PostgreSQL", "MongoDB"],
            help="Select your database type for connection",
            label_visibility="collapsed"
        )
    
    if db_type == "PostgreSQL":
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #1e293b; font-family: 'Inter', sans-serif; margin-bottom: 0.5rem;">🐘 PostgreSQL Connection</h3>
            <p style="color: #64748b; margin-bottom: 2rem;">Enter your PostgreSQL database credentials</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("postgresql_form"):
            st.markdown("""
            <div style="background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); 
                        padding: 1.5rem; border-radius: 16px; margin: 1rem 0; 
                        border: 1px solid rgba(102, 126, 234, 0.1);">
                <h4 style="color: #374151; margin-bottom: 1rem; font-family: 'Inter', sans-serif;">
                    🔧 Connection Details
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                pg_host = st.text_input("🌐 Host", value="localhost", help="Database server hostname or IP address")
                pg_database = st.text_input("🗄️ Database Name", help="Name of the PostgreSQL database")
                pg_username = st.text_input("👤 Username", help="Database username")
            
            with col2:
                pg_port = st.number_input("🔌 Port", value=5432, min_value=1, max_value=65535, help="Database port (default: 5432)")
                pg_password = st.text_input("🔐 Password", type="password", help="Database password")
                st.markdown("<br>", unsafe_allow_html=True)  
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                test_conn = st.form_submit_button("🔗 Test Connection", use_container_width=True, help="Verify database connection")
            
            with col2:
                st.markdown("") 
            
            with col3:
                analyze_db = st.form_submit_button("🚀 Analyze Database", type="primary", use_container_width=True, help="Start comprehensive database analysis")
        
        if test_conn:
            with st.spinner("Testing PostgreSQL connection..."):
                try:
                    payload = {
                        "db_type": "postgresql",
                        "postgresql_config": {
                            "host": pg_host,
                            "port": int(pg_port),
                            "database": pg_database,
                            "username": pg_username,
                            "password": pg_password
                        }
                    }
                    response = requests.post(f"{API_URL}/api/database/test-connection", json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        st.success("✅ PostgreSQL connection successful!")
                    else:
                        st.error(f"❌ Connection failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        
        if analyze_db:
            with st.spinner("🤖 AI Agent is analyzing your PostgreSQL database..."):
                try:
                    payload = {
                        "db_type": "postgresql",
                        "postgresql_config": {
                            "host": pg_host,
                            "port": int(pg_port),
                            "database": pg_database,
                            "username": pg_username,
                            "password": pg_password
                        }
                    }
                    response = requests.post(f"{API_URL}/api/database/analyze", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Database analysis completed!")
                        st.markdown("---")
                        
                        st.markdown("## 🤖 AI-Generated Database Analysis")
                        with st.container():
                            st.markdown(result["narrative_summary"])
                        
                        st.markdown("---")
                        
                        tab1, tab2, tab3 = st.tabs([
                            "🗄️ Database Overview", 
                            "📈 Table Analysis", 
                            "📊 Visualizations"
                        ])
                        
                        with tab1:
                            st.markdown("## 🗄️ Database Structure")
                            
                            database_info = result.get("database_info", {})
                            
                            if "tables" in database_info:
                                col1, col2 = st.columns(2)
                                with col1:
                                    create_metric_card("Total Tables", database_info.get("total_tables", 0))
                                with col2:
                                    total_columns = sum(table.get("column_count", 0) for table in database_info.get("tables", []))
                                    create_metric_card("Total Columns", total_columns)
                                
                                st.markdown("---")
                                st.markdown("### 📋 Tables Overview")
                                
                                tables_data = []
                                for table in database_info.get("tables", []):
                                    tables_data.append({
                                        "Table Name": table.get("name", ""),
                                        "Columns": table.get("column_count", 0),
                                        "Column Details": ", ".join([col.get("name", "") for col in table.get("columns", [])[:5]]) + ("..." if len(table.get("columns", [])) > 5 else "")
                                    })
                                
                                if tables_data:
                                    st.dataframe(pd.DataFrame(tables_data), use_container_width=True)
                            
                            elif "collections" in database_info:
                                col1, col2 = st.columns(2)
                                with col1:
                                    create_metric_card("Total Collections", database_info.get("total_collections", 0))
                                with col2:
                                    total_docs = sum(collection.get("document_count", 0) for collection in database_info.get("collections", []))
                                    create_metric_card("Total Documents", f"{total_docs:,}")
                                
                                st.markdown("---")
                                st.markdown("### 📋 Collections Overview")
                                
                                collections_data = []
                                for collection in database_info.get("collections", []):
                                    collections_data.append({
                                        "Collection Name": collection.get("name", ""),
                                        "Document Count": f"{collection.get('document_count', 0):,}",
                                        "Fields": collection.get("field_count", 0),
                                        "Field Details": ", ".join([field.get("name", "") for field in collection.get("fields", [])[:5]]) + ("..." if len(collection.get("fields", [])) > 5 else "")
                                    })
                                
                                if collections_data:
                                    st.dataframe(pd.DataFrame(collections_data), use_container_width=True)
                        
                        with tab2:
                            st.markdown("## 📈 Table/Collection Analysis")
                            st.markdown("*Statistical analysis of individual tables and collections*")
                            
                            analysis_results = result.get("analysis_results", {})
                            table_analyses = analysis_results.get("table_analyses", [])
                            
                            if table_analyses:
                                for analysis in table_analyses:
                                    table_name = analysis.get("table_name") or analysis.get("collection_name", "Unknown")
                                    stats = analysis.get("stats", {})
                                    
                                    st.markdown(f"### 📊 {table_name}")
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        create_metric_card("Rows", f"{stats.get('shape', {}).get('rows', 0):,}")
                                    with col2:
                                        create_metric_card("Columns", stats.get('shape', {}).get('columns', 0))
                                    with col3:
                                        create_metric_card("Duplicates", stats.get('duplicates', 0))
                                    with col4:
                                        create_metric_card("Memory Usage", f"{stats.get('memory_usage', 0):.2f} MB")
                                    
                                    missing_data = []
                                    for col, count in stats.get("missing_values", {}).items():
                                        if count > 0:
                                            missing_data.append({
                                                "Column": col,
                                                "Missing Values": count,
                                                "Percentage": f"{stats.get('missing_percentage', {}).get(col, 0):.2f}%"
                                            })
                                    
                                    display_data_quality_report(missing_data)
                                    
                                    # Display statistics
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        display_statistics_table(stats.get("numerical_stats", {}), "Numerical Statistics")
                                    
                                    with col2:
                                        if stats.get("categorical_stats"):
                                            st.markdown("### 📋 Categorical Statistics")
                                            for col, cat_stats in stats.get("categorical_stats", {}).items():
                                                with st.expander(f"📋 {col}"):
                                                    st.write(f"**Unique Values:** {cat_stats.get('unique_values', 0)}")
                                                    st.write(f"**Most Common:** {cat_stats.get('mode', 'N/A')}")
                                                    if cat_stats.get('top_values'):
                                                        st.bar_chart(cat_stats['top_values'])
                                    
                                    st.markdown("---")
                            else:
                                st.info("📊 No table analysis data available")
                        
                        with tab3:
                            st.markdown("## 📊 Database Visualizations")
                            st.markdown("*Charts and graphs from your database tables*")
                            
                            visualizations = result.get("visualizations", {})
                            
                            if visualizations:
                                for table_name, viz_data in visualizations.items():
                                    st.markdown(f"### 📊 {table_name}")
                                    
                                    univariate = viz_data.get("univariate", [])
                                    if univariate:
                                        st.markdown("#### 📈 Individual Column Analysis")
                                        for viz in univariate:
                                            st.markdown(f"**{viz.get('type', '').title()}: {viz.get('column', '')}**")
                                            
                                            viz_data_obj = viz.get("data", {})
                                            success = display_chart_from_backend(viz_data_obj)
                                            
                                            if not success:
                                                st.info(f"Unable to display {viz.get('type', '')} for {viz.get('column', '')}")
                                    
                                    bivariate = viz_data.get("bivariate", [])
                                    if bivariate:
                                        st.markdown("#### 🔗 Relationship Analysis")
                                        for viz in bivariate:
                                            if viz.get("type") == "scatter":
                                                st.markdown(f"**Scatter Plot: {viz.get('data', {}).get('column', 'X')} vs {viz.get('data', {}).get('second_column', 'Y')}**")
                                            else:
                                                st.markdown(f"**{viz.get('type', '').title()}**")
                                            
                                            viz_data_obj = viz.get("data", {})
                                            success = display_chart_from_backend(viz_data_obj)
                                            
                                            if not success:
                                                st.info(f"Unable to display {viz.get('type', '')} visualization")
                                    
                                    st.markdown("---")
                            else:
                                st.info("📊 No visualizations available for this database")
                        
                    else:
                        st.error(f"❌ Analysis failed: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"💥 An error occurred: {str(e)}")
    
    else:  
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #1e293b; font-family: 'Inter', sans-serif; margin-bottom: 0.5rem;">🍃 MongoDB Connection</h3>
            <p style="color: #64748b; margin-bottom: 2rem;">Enter your MongoDB database credentials</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("mongodb_form"):
            st.markdown("""
            <div style="background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); 
                        padding: 1.5rem; border-radius: 16px; margin: 1rem 0; 
                        border: 1px solid rgba(102, 126, 234, 0.1);">
                <h4 style="color: #374151; margin-bottom: 1rem; font-family: 'Inter', sans-serif;">
                    🔧 Connection Details
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                mongo_host = st.text_input("🌐 Host", value="localhost", help="MongoDB server hostname or IP address")
                mongo_database = st.text_input("🗄️ Database Name", help="Name of the MongoDB database")
                mongo_username = st.text_input("👤 Username (optional)", help="Database username (leave empty if no auth)")
            
            with col2:
                mongo_port = st.number_input("🔌 Port", value=27017, min_value=1, max_value=65535, help="MongoDB port (default: 27017)")
                mongo_password = st.text_input("🔐 Password (optional)", type="password", help="Database password (leave empty if no auth)")
                mongo_auth_source = st.text_input("🔑 Auth Source", value="admin", help="Authentication database (default: admin)")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                test_conn_mongo = st.form_submit_button("🔗 Test Connection", use_container_width=True, help="Verify database connection")
            
            with col2:
                st.markdown("") 
            
            with col3:
                analyze_db_mongo = st.form_submit_button("🚀 Analyze Database", type="primary", use_container_width=True, help="Start comprehensive database analysis")
        
        if test_conn_mongo:
            with st.spinner("Testing MongoDB connection..."):
                try:
                    payload = {
                        "db_type": "mongodb",
                        "mongodb_config": {
                            "host": mongo_host,
                            "port": int(mongo_port),
                            "database": mongo_database,
                            "username": mongo_username if mongo_username else None,
                            "password": mongo_password if mongo_password else None,
                            "auth_source": mongo_auth_source
                        }
                    }
                    response = requests.post(f"{API_URL}/api/database/test-connection", json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        st.success("✅ MongoDB connection successful!")
                    else:
                        st.error(f"❌ Connection failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        
        if analyze_db_mongo:
            with st.spinner("🤖 AI Agent is analyzing your MongoDB database..."):
                try:
                    payload = {
                        "db_type": "mongodb",
                        "mongodb_config": {
                            "host": mongo_host,
                            "port": int(mongo_port),
                            "database": mongo_database,
                            "username": mongo_username if mongo_username else None,
                            "password": mongo_password if mongo_password else None,
                            "auth_source": mongo_auth_source
                        }
                    }
                    response = requests.post(f"{API_URL}/api/database/analyze", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ MongoDB database analysis completed!")
                        st.markdown("---")
                        
                        st.markdown("## 🤖 AI-Generated Database Analysis")
                        with st.container():
                            st.markdown(result["narrative_summary"])
                        
                        st.markdown("---")
                        
                        tab1, tab2, tab3 = st.tabs([
                            "🗄️ Database Overview", 
                            "📈 Collection Analysis", 
                            "📊 Visualizations"
                        ])
                        
                        with tab1:
                            st.markdown("## 🗄️ Database Structure")
                            
                            database_info = result.get("database_info", {})
                            
                            if "collections" in database_info:
                                col1, col2 = st.columns(2)
                                with col1:
                                    create_metric_card("Total Collections", database_info.get("total_collections", 0))
                                with col2:
                                    total_docs = sum(collection.get("document_count", 0) for collection in database_info.get("collections", []))
                                    create_metric_card("Total Documents", f"{total_docs:,}")
                                
                                st.markdown("---")
                                st.markdown("### 📋 Collections Overview")
                                
                                collections_data = []
                                for collection in database_info.get("collections", []):
                                    collections_data.append({
                                        "Collection Name": collection.get("name", ""),
                                        "Document Count": f"{collection.get('document_count', 0):,}",
                                        "Fields": collection.get("field_count", 0),
                                        "Field Details": ", ".join([field.get("name", "") for field in collection.get("fields", [])[:5]]) + ("..." if len(collection.get("fields", [])) > 5 else "")
                                    })
                                
                                if collections_data:
                                    st.dataframe(pd.DataFrame(collections_data), use_container_width=True)
                        
                        with tab2:
                            st.markdown("## 📈 Collection Analysis")
                            st.markdown("*Statistical analysis of individual collections*")
                            
                            analysis_results = result.get("analysis_results", {})
                            table_analyses = analysis_results.get("table_analyses", [])
                            
                            if table_analyses:
                                for analysis in table_analyses:
                                    collection_name = analysis.get("collection_name", "Unknown")
                                    stats = analysis.get("stats", {})
                                    
                                    st.markdown(f"### 📊 {collection_name}")
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        create_metric_card("Documents", f"{stats.get('shape', {}).get('rows', 0):,}")
                                    with col2:
                                        create_metric_card("Fields", stats.get('shape', {}).get('columns', 0))
                                    with col3:
                                        create_metric_card("Duplicates", stats.get('duplicates', 0))
                                    with col4:
                                        create_metric_card("Memory Usage", f"{stats.get('memory_usage', 0):.2f} MB")
                                    
                                    missing_data = []
                                    for col, count in stats.get("missing_values", {}).items():
                                        if count > 0:
                                            missing_data.append({
                                                "Field": col,
                                                "Missing Values": count,
                                                "Percentage": f"{stats.get('missing_percentage', {}).get(col, 0):.2f}%"
                                            })
                                    
                                    display_data_quality_report(missing_data)
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        display_statistics_table(stats.get("numerical_stats", {}), "Numerical Statistics")
                                    
                                    with col2:
                                        if stats.get("categorical_stats"):
                                            st.markdown("### 📋 Categorical Statistics")
                                            for col, cat_stats in stats.get("categorical_stats", {}).items():
                                                with st.expander(f"📋 {col}"):
                                                    st.write(f"**Unique Values:** {cat_stats.get('unique_values', 0)}")
                                                    st.write(f"**Most Common:** {cat_stats.get('mode', 'N/A')}")
                                                    if cat_stats.get('top_values'):
                                                        st.bar_chart(cat_stats['top_values'])
                                    
                                    st.markdown("---")
                            else:
                                st.info("📊 No collection analysis data available")
                        
                        with tab3:
                            st.markdown("## 📊 Database Visualizations")
                            st.markdown("*Charts and graphs from your database collections*")
                            
                            visualizations = result.get("visualizations", {})
                            
                            if visualizations:
                                for collection_name, viz_data in visualizations.items():
                                    st.markdown(f"### 📊 {collection_name}")
                                    
                                    univariate = viz_data.get("univariate", [])
                                    if univariate:
                                        st.markdown("#### 📈 Individual Field Analysis")
                                        for viz in univariate:
                                            st.markdown(f"**{viz.get('type', '').title()}: {viz.get('column', '')}**")
                                            
                                            viz_data_obj = viz.get("data", {})
                                            success = display_chart_from_backend(viz_data_obj)
                                            
                                            if not success:
                                                st.info(f"Unable to display {viz.get('type', '')} for {viz.get('column', '')}")
                                    
                                    bivariate = viz_data.get("bivariate", [])
                                    if bivariate:
                                        st.markdown("#### 🔗 Relationship Analysis")
                                        for viz in bivariate:
                                            if viz.get("type") == "scatter":
                                                st.markdown(f"**Scatter Plot: {viz.get('data', {}).get('column', 'X')} vs {viz.get('data', {}).get('second_column', 'Y')}**")
                                            else:
                                                st.markdown(f"**{viz.get('type', '').title()}**")
                                            
                                            viz_data_obj = viz.get("data", {})
                                            success = display_chart_from_backend(viz_data_obj)
                                            
                                            if not success:
                                                st.info(f"Unable to display {viz.get('type', '')} visualization")
                                    
                                    st.markdown("---")
                            else:
                                st.info("📊 No visualizations available for this database")
                        
                    else:
                        st.error(f"❌ Analysis failed: {response.json().get('detail', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"💥 An error occurred: {str(e)}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>Built with ❤️ using <strong>Streamlit</strong>, <strong>FastAPI</strong>, and <strong>LangGraph</strong></p>
    <p>Powered by <strong>Groq Llama 3.1</strong> for AI-driven insights</p>
</div>
""", unsafe_allow_html=True)
