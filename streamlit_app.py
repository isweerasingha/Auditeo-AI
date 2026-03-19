# ruff: noqa: E501

from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Auditeo AI - Website Audit",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants
API_URL = "http://localhost:8000/api/audit"


st.markdown(
    """
<style>
    .metric-box {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 14px;
        color: #aaa;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #4da6ff;
    }
    .priority-1 { border-left: 5px solid #ff4b4b; padding: 15px; background-color: rgba(255, 75, 75, 0.1); border-radius: 0 8px 8px 0; } /* Critical */
    .priority-2 { border-left: 5px solid #ff9f36; padding: 15px; background-color: rgba(255, 159, 54, 0.1); border-radius: 0 8px 8px 0; } /* High */
    .priority-3 { border-left: 5px solid #faca2b; padding: 15px; background-color: rgba(250, 202, 43, 0.1); border-radius: 0 8px 8px 0; } /* Medium */
    .priority-4 { border-left: 5px solid #17b877; padding: 15px; background-color: rgba(23, 184, 119, 0.1); border-radius: 0 8px 8px 0; } /* Low */
    .priority-5 { border-left: 5px solid #00c0f2; padding: 15px; background-color: rgba(0, 192, 242, 0.1); border-radius: 0 8px 8px 0; } /* Info */

    .stButton>button {
        width: 100%;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🔍 Auditeo AI - Website Audit")
st.markdown("Enter a website URL to run a comprehensive AI-powered audit.")

# Input section
with st.form("audit_form"):
    url_input = st.text_input("Website URL", placeholder="https://example.com")
    submit_button = st.form_submit_button("Run Audit", type="primary")

if submit_button:
    if not url_input:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner(
            "Running audit... This may take a few minutes as the AI agents analyze the site."
        ):
            try:
                response = requests.post(API_URL, json={"website_url": url_input})
                response.raise_for_status()

                result = response.json()

                if result.get("success"):
                    data = result.get("data", {})

                    st.success("Audit completed successfully!")

                    # --- Execution Context ---
                    execution_context = result.get("execution_context", {})
                    if execution_context:
                        st.header("⏱️ Execution Details")

                        start_time_str = execution_context.get("start_time")
                        end_time_str = execution_context.get("end_time")

                        exec_time = "N/A"
                        if start_time_str and end_time_str:
                            try:
                                # Parse ISO format, replacing Z with +00:00 for python fromisoformat
                                start_dt = datetime.fromisoformat(
                                    start_time_str.replace("Z", "+00:00")
                                )
                                end_dt = datetime.fromisoformat(
                                    end_time_str.replace("Z", "+00:00")
                                )
                                duration = (end_dt - start_dt).total_seconds()
                                exec_time = f"{duration:.2f}s"
                            except Exception:
                                pass

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                "Execution ID", execution_context.get("id", "N/A")
                            )
                        with col2:
                            st.metric(
                                "Status",
                                str(execution_context.get("status", "N/A")).title(),
                            )
                        with col3:
                            st.metric(
                                "Total Tokens",
                                f"{execution_context.get('total_token_usage', 0):,}",
                            )
                        with col4:
                            st.metric("Execution Time", exec_time)

                        st.divider()

                    # --- Metrics in Boxes ---
                    st.header("📊 Factual Metrics")
                    metrics = data.get("factual_metrics", {})
                    if metrics:
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">Word Count</div><div class="metric-value">{metrics.get("total_word_count", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">Images</div><div class="metric-value">{metrics.get("image_count", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )

                        with col2:
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">CTAs</div><div class="metric-value">{metrics.get("cta_count", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">Missing Alt Text</div><div class="metric-value">{metrics.get("images_missing_alt_text_pct", 0)}%</div></div>',
                                unsafe_allow_html=True,
                            )

                        with col3:
                            headings = metrics.get("heading_counts", {})
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">H1 Tags</div><div class="metric-value">{headings.get("h1", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">H2 Tags</div><div class="metric-value">{headings.get("h2", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )

                        with col4:
                            links = metrics.get("link_counts", {})
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">Internal Links</div><div class="metric-value">{links.get("internal", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="metric-box"><div class="metric-title">External Links</div><div class="metric-value">{links.get("external", 0)}</div></div>',
                                unsafe_allow_html=True,
                            )

                    st.divider()

                    # --- KPIs in Bar Chart ---
                    st.header("📈 Key Performance Indicators (KPIs)")
                    kpis = data.get("kpis", {})
                    if kpis:
                        kpi_data = {
                            "KPI": [
                                "SEO Score",
                                "Links Score",
                                "Usability Score",
                                "Social Score",
                            ],
                            "Score": [
                                kpis.get("seo_score", 0),
                                kpis.get("links_score", 0),
                                kpis.get("usability_score", 0),
                                kpis.get("social_score", 0),
                            ],
                        }
                        df_kpis = pd.DataFrame(kpi_data)

                        fig = px.bar(
                            df_kpis,
                            x="KPI",
                            y="Score",
                            color="KPI",
                            range_y=[0, 100],
                            text="Score",
                            color_discrete_sequence=[
                                "#4da6ff",
                                "#ff9f36",
                                "#17b877",
                                "#faca2b",
                            ],
                        )
                        fig.update_traces(textposition="outside", textfont_size=16)
                        fig.update_layout(
                            showlegend=False,
                            xaxis_title="",
                            yaxis_title="Score (out of 100)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(size=14),
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.divider()

                    # --- Recommendations ---
                    st.header("💡 Top Recommendations")
                    recommendations = data.get("recommendations", [])
                    if recommendations:
                        for rec in sorted(
                            recommendations, key=lambda x: x.get("priority", 5)
                        ):
                            priority = rec.get("priority", 5)

                            st.markdown(
                                f"""
                            <div class="priority-{priority}">
                                <h3 style="margin-top: 0;">Priority {priority}: {rec.get('title', 'Recommendation')}</h3>
                                <p><strong>Action:</strong> {rec.get('action', '')}</p>
                                <p><strong>Reasoning:</strong> {rec.get('reasoning', '')}</p>
                                <p><strong>Expected Impact:</strong> {rec.get('expected_impact', '')}</p>
                            </div>
                            <br>
                            """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No recommendations generated.")

                    st.divider()

                    # --- Report View MD ---
                    st.header("📄 Detailed Insights Report")
                    report = data.get("insights_report", "")
                    if report:
                        with st.expander("View Full Report", expanded=True):
                            st.markdown(report)
                    else:
                        st.info("No detailed report available.")

                else:
                    st.error(f"Audit failed: {result.get('message', 'Unknown error')}")

            except requests.exceptions.RequestException as e:
                st.error(
                    f"Failed to connect to the API. Make sure the backend is running. Error: {e}"
                )
