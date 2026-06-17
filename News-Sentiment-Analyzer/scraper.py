import requests
import xml.etree.ElementTree as ET
import email.utils
import logging
from typing import List, Dict
from config import HEADERS, NEWS_SOURCES

# Configure logger
logger = logging.getLogger(__name__)

class NewsScraper:
    """
    Scrapes news article metadata from standard RSS and Atom feeds.
    """
    def __init__(self):
        self.headers = HEADERS

    def fetch_all_sources(self) -> List[Dict]:
        """
        Iterates over all configured news feeds and aggregates new articles.
        
        Returns:
            List[Dict]: A list of article metadata dictionaries.
        """
        all_articles = []
        for name, url in NEWS_SOURCES.items():
            logger.info(f"Fetching news from: {name} ({url})")
            articles = self.fetch_feed(name, url)
            logger.info(f"Retrieved {len(articles)} articles from {name}.")
            all_articles.extend(articles)
        return all_articles

    def fetch_feed(self, source_name: str, feed_url: str) -> List[Dict]:
        """
        Fetches and parses a single RSS or Atom feed.
        
        Args:
            source_name (str): Readable name of the news source.
            feed_url (str): The feed XML URL.
            
        Returns:
            List[Dict]: A list of parsed articles.
        """
        try:
            response = requests.get(feed_url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Error fetching {source_name}: HTTP status {response.status_code}")
                return []

            return self.parse_xml_feed(response.content, source_name)
        except requests.RequestException as e:
            logger.error(f"Network error contacting {source_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing feed {source_name}: {e}")
            return []

    def parse_xml_feed(self, xml_bytes: bytes, source_name: str) -> List[Dict]:
        """
        Parses XML bytes, handling both RSS 2.0 and Atom formats.
        """
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as e:
            logger.error(f"XML parse error for source {source_name}: {e}")
            return []

        articles = []
        
        # Determine format: Atom feeds generally contain namespace or 'feed' tag at the root
        is_atom = 'feed' in root.tag.lower() or root.find('.//{http://www.w3.org/2005/Atom}entry') is not None
        
        if is_atom:
            # Namespace map for Atom
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            # Handle possible default or prefix namespaces
            entries = root.findall('.//atom:entry', ns) or root.findall('.//entry')
            for entry in entries:
                title_node = entry.find('atom:title', ns) or entry.find('title')
                link_node = entry.find('atom:link', ns) or entry.find('link')
                summary_node = (
                    entry.find('atom:summary', ns) or 
                    entry.find('atom:content', ns) or 
                    entry.find('summary') or 
                    entry.find('content')
                )
                updated_node = (
                    entry.find('atom:updated', ns) or 
                    entry.find('updated') or 
                    entry.find('atom:published', ns) or 
                    entry.find('published')
                )
                
                title = title_node.text.strip() if title_node is not None and title_node.text else ""
                
                # Link resolving: Atom uses attributes
                url = ""
                if link_node is not None:
                    url = link_node.attrib.get('href', link_node.text or '').strip()
                
                summary = summary_node.text.strip() if summary_node is not None and summary_node.text else ""
                published_raw = updated_node.text.strip() if updated_node is not None and updated_node.text else ""
                
                if title and url:
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "url": url,
                        "source": source_name,
                        "published_at": published_raw
                    })
        else:
            # RSS 2.0 parsing
            for item in root.findall('.//item'):
                title_node = item.find('title')
                link_node = item.find('link')
                desc_node = item.find('description')
                pub_date_node = item.find('pubDate')
                
                title = title_node.text.strip() if title_node is not None and title_node.text else ""
                url = link_node.text.strip() if link_node is not None and link_node.text else ""
                
                # Fallback to GUID if link node is missing or empty
                if not url:
                    guid_node = item.find('guid')
                    if guid_node is not None and guid_node.text and guid_node.text.startswith('http'):
                        url = guid_node.text.strip()
                
                summary = desc_node.text.strip() if desc_node is not None and desc_node.text else ""
                published_raw = pub_date_node.text.strip() if pub_date_node is not None and pub_date_node.text else ""
                
                # Standardize RSS RFC 822 timestamps into ISO format
                published_iso = ""
                if published_raw:
                    try:
                        dt = email.utils.parsedate_to_datetime(published_raw)
                        published_iso = dt.isoformat()
                    except Exception:
                        published_iso = published_raw  # Fallback to raw string on error
                        
                if title and url:
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "url": url,
                        "source": source_name,
                        "published_at": published_iso
                    })
                    
        return articles
