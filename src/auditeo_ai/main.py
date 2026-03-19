import sys

from auditeo_ai.flows.audit_flow import AuditFlow
from auditeo_ai.utils import generate_pdf_report


def main():
    """
    Main function
    """
    print("Starting the audit flow...")

    website_url = input("Enter the website URL: ")
    print(f"Website URL: {website_url}")

    try:
        flow = AuditFlow()
        inputs = {"website_url": website_url}
        flow.kickoff(inputs=inputs)

        state = flow.state
        report_path = generate_pdf_report(state=state)
        print(f"Audit report generated: {report_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
