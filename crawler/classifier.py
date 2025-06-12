# File: classifier.py
# This file categorizes a given webpage as either "finance", "medical", "education", or "unknown"

# Classifies a given bot page
def classify_bot(html: str, url: str) -> str:
    text = html.lower()

    # Define domain keywords
    domains = {
        "finance":   ["finance", "bank", "investment", "revenue", "profit", "stock", "trading"],
        "medical":   ["medical", "health", "patient", "clinic", "doctor", "hospital", "hipaa"],
        "education": ["education", "school", "student", "course", "curriculum", "campus", "university"]
    }

    # Count occurrences of each keyword in text
    counts = {
        domain: sum(text.count(keyword) for keyword in keywords)
        for domain, keywords in domains.items()
    }

    # Pick the domain with the highest count
    best_domain, best_count = max(counts.items(), key=lambda item: item[1])
    if best_count > 0:
        return best_domain

    # Fallback: classify based on URL substrings
    lower_url = url.lower()
    if "finance" in lower_url:
        return "finance"
    if "med" in lower_url or "health" in lower_url:
        return "medical"
    if "edu" in lower_url or "school" in lower_url:
        return "education"

    return "unknown"