import disposable_email_domains as ded

from urllib.parse import urlparse


def get_domain(url):
    """
    Extracts the domain from a given URL.
    """
    if not url:
        return ""
    return urlparse(url).netloc


def is_email_blacklisted(email):
    if "@" not in email:
        raise ValueError("Invalid email address %s" % email)

    black_list_domains = set(ded.blocklist)
    domain = email.split("@")[-1].lower()
    return domain in black_list_domains
