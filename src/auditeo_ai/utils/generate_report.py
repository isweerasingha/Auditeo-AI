from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


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

    metrics = state.factual_metrics
    if metrics is None:
        write_line(
            "No factual metrics were found in the flow state.",
            "Helvetica-Bold",
            12,
        )
    else:
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
        write_line(
            f"Images missing alt text (%): {metrics.images_missing_alt_text_pct}"
        )
        write_line(f"Meta title: {metrics.meta_title or 'N/A'}")
        write_line(f"Meta description: {metrics.meta_description or 'N/A'}")
        write_line("")

    write_line("Flow State Snapshot", "Helvetica-Bold", 14)
    clean_text_preview = (state.page_content_clean or "")[:1200]
    if clean_text_preview:
        write_line("Clean content preview:")
        for line in _wrap_text(clean_text_preview, width=95):
            write_line(f"  {line}")
    else:
        write_line("No clean content available.")

    report.save()
    return output_path
