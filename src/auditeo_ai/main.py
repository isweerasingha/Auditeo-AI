import sys

from auditeo_ai.flows.audit_flow import AuditFlow


def main():
    """
    Main function
    """
    print("Starting the audit flow...")

    website_url = input("Enter the website URL: ").strip()
    if not website_url.startswith(("http://", "https://")):
        website_url = f"https://{website_url}"

    print(f"Website URL: {website_url}")

    try:
        flow = AuditFlow()
        inputs = {"website_url": website_url}
        flow.kickoff(inputs=inputs)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
