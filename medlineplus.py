import requests
import xml.etree.ElementTree as ET

# MedlinePlus Health Topics search
BASE = "https://wsearch.nlm.nih.gov/ws/query"

def summary(topic: str):
    params = {"db": "healthTopics", "term": topic}
    r = requests.get(BASE, params=params, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    # Grab first list/listitem/document
    doc = root.find("./list/listitem/document")
    if doc is None:
        return {"topic": topic, "summary": None, "references": []}
    title = (doc.findtext("content[@name='title']") or "").strip()
    url = (doc.findtext("content[@name='url']") or "").strip()
    # The 'fullsummary' can be long; use 'alt' or 'snippet' if available
    snippet = (doc.findtext("content[@name='snippet']") or "").strip()
    fullsummary = (doc.findtext("content[@name='fullsummary']") or "").strip()
    text = snippet or fullsummary or None
    refs = [{"id": None, "title": title or "MedlinePlus", "url": url or None, "source": "MedlinePlus"}]
    return {"topic": topic, "summary": text, "references": refs}
