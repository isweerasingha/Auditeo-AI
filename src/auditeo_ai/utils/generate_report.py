from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from auditeo_ai.models import InsightsCrewOutput, RecommendationCrewOutput


def _wrap_text(value: str, width: int = 100) -> list[str]:
    words = value.split()
    if not words:
        return [""]

    lines: list[str] = []
    current_line: list[str] = []

    for word in words:
        test_line = " ".join([*current_line, word])
        if len(test_line) <= width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def _write_factual_metrics(write_line, metrics: Any) -> None:
    if metrics is None:
        write_line(
            "No factual metrics were found in the flow state.",
            "Helvetica-Bold",
            12,
        )
        return

    write_line("Factual Metrics", "Helvetica-Bold", 14)
    write_line(f"Total word count: {metrics.total_word_count}")
    write_line(f"H1 count: {metrics.heading_counts.h1}")
    write_line(f"H2 count: {metrics.heading_counts.h2}")
    write_line(f"H3 count: {metrics.heading_counts.h3}")
    write_line(f"CTA count: {metrics.cta_count}")
    write_line(f"Internal links: {metrics.link_counts.internal}")
    write_line(f"External links: {metrics.link_counts.external}")
    write_line(f"Total links: {metrics.link_counts.total}")
    write_line(f"Image count: {metrics.image_count}")
    write_line(f"Images missing alt text (%): {metrics.images_missing_alt_text_pct}")
    write_line(f"Meta title: {metrics.meta_title or 'N/A'}")
    write_line(f"Meta description: {metrics.meta_description or 'N/A'}")
    write_line("")


def _write_insights(write_line, insights: InsightsCrewOutput) -> None:
    write_line("Insights & KPIs", "Helvetica-Bold", 14)
    write_line(f"SEO score: {insights.kpis.seo_score}")
    write_line(f"Links score: {insights.kpis.links_score}")
    write_line(f"Usability score: {insights.kpis.usability_score}")
    write_line(f"Social score: {insights.kpis.social_score}")
    write_line("")

    write_line("Structured Report:", "Helvetica-Bold", 12)
    report_preview = (insights.structured_report or "")[:2000]
    for line in _wrap_text(report_preview, width=95):
        write_line(f"  {line}")
    write_line("")


def _write_recommendation_item(write_line, rec: Any) -> None:
    priority = getattr(rec, "priority", None)
    title = getattr(rec, "title", "") or ""
    write_line(f"Priority {priority or 'N/A'}: {title}", "Helvetica-Bold", 12)

    action = getattr(rec, "action", "") or ""
    if action:
        write_line("Action:", "Helvetica-Bold", 11)
        for line in _wrap_text(action, width=95):
            write_line(f"  {line}")

    reasoning = getattr(rec, "reasoning", "") or ""
    if reasoning:
        write_line("Reasoning:", "Helvetica-Bold", 11)
        for line in _wrap_text(reasoning, width=95):
            write_line(f"  {line}")

    expected_impact = getattr(rec, "expected_impact", "") or ""
    if expected_impact:
        write_line("Expected impact:", "Helvetica-Bold", 11)
        for line in _wrap_text(expected_impact, width=95):
            write_line(f"  {line}")

    write_line("")


def _write_recommendations(
    write_line, recommendations: RecommendationCrewOutput
) -> None:
    write_line("Recommendations", "Helvetica-Bold", 14)
    validation_status = getattr(recommendations, "validation_status", None)
    if validation_status:
        write_line(f"Validation status: {validation_status}")
    write_line("")

    recs = getattr(recommendations, "recommendations", []) or []
    if not recs:
        write_line("No recommendations found in the flow state.")
        return

    for rec in recs:
        _write_recommendation_item(write_line, rec)


def _write_flow_state_snapshot(write_line, state: Any) -> None:
    write_line("Flow State Snapshot", "Helvetica-Bold", 14)
    clean_text_preview = (state.page_content_clean or "")[:1200]
    if clean_text_preview:
        write_line("Clean content preview:")
        for line in _wrap_text(clean_text_preview, width=95):
            write_line(f"  {line}")
    else:
        write_line("No clean content available.")


def generate_pdf_report(state: Any, output_dir: str = "reports") -> Path:
    website_url = state.website_url or "unknown-site"
    domain = urlparse(website_url).netloc or website_url.replace("https://", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reports_path = Path(output_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    output_path = reports_path / f"audit_report_{domain}_{timestamp}.pdf"

    report = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    y = height - 50

    def write_line(text: str, font: str = "Helvetica", size: int = 11) -> None:
        nonlocal y
        if y < 50:
            report.showPage()
            y = height - 50
        report.setFont(font, size)
        report.drawString(50, y, text)
        y -= 16

    report.setTitle("Auditeo Audit Report")

    write_line("Auditeo Website Audit Report", "Helvetica-Bold", 18)
    write_line(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    write_line(f"Website: {website_url}")
    write_line("")

    _write_factual_metrics(write_line, getattr(state, "factual_metrics", None))

    insights: InsightsCrewOutput | None = getattr(
        state, "insights_crew_output", None
    )
    if insights is not None:
        _write_insights(write_line, insights)

    recommendations: RecommendationCrewOutput | None = getattr(
        state, "recommendations_crew_output", None
    )
    if recommendations is not None:
        _write_recommendations(write_line, recommendations)

    _write_flow_state_snapshot(write_line, state)

    report.save()
    return output_path
