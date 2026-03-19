def generate_url(website_url: str) -> str:
    """
    Generate the URL
    """
    if not website_url.startswith(("http://", "https://")):
        website_url = f"https://{website_url}"

    print(f"Generated URL: {website_url} \n")
    return website_url
