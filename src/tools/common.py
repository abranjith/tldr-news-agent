from urllib.parse import urlparse
import validators

def get_filtered_results(results, domain_filter_list):
    """Filters search results by a list of domains."""
    if not domain_filter_list:
        return results
    filtered_results = []
    for result in results:
        url = result.get("url") or result.get("link", "") or result.get("href", "")
        if not validators.url(url):
            continue
        domain = urlparse(url).netloc
        if any(domain.endswith(d) for d in domain_filter_list):
            filtered_results.append(result)
    return filtered_results