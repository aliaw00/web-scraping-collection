import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from providers.base import BaseCourseProvider

class MITOCWCourseProvider(BaseCourseProvider):
    def get_name(self) -> str:
        return "mit_ocw"

    def fetch_courses(self, search_query: str) -> list:
        # MIT OCW has an RSS feed for new courses: https://ocw.mit.edu/rss/new/index.xml
        # We can parse this RSS XML feed or fallback to the static listing page
        url = self.MIT_OCW_FEED_URL
        self.logger.info(f"Fetching MIT OCW courses from RSS feed: {url}")
        
        courses = []
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                # Parse RSS XML
                root = ET.fromstring(response.content)
                # Find all <item> tags
                items = root.findall(".//item")
                for item in items:
                    title = item.findtext("title", "").strip()
                    description = item.findtext("description", "").strip()
                    link = item.findtext("link", "").strip()
                    
                    # Skip if search query does not match title/description
                    if search_query.lower() not in title.lower() and search_query.lower() not in description.lower():
                        continue
                        
                    # Extract course code (often in brackets or prefix)
                    # MIT courses often look like: "18.01 Single Variable Calculus"
                    course_id = "MIT-OCW-" + title.split(" ")[0] if title else "MIT-OCW-UNKNOWN"
                    
                    courses.append({
                        "course_id": course_id,
                        "title": title,
                        "description": description,
                        "instructor": "MIT Faculty",
                        "schedule": "Self-paced (Open Courseware)",
                        "syllabus": "Refer to course site for lecture notes and syllabus details.",
                        "url": link
                    })
            else:
                self.logger.error(f"Failed to fetch MIT OCW feed. Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.logger.warning("Timeout connecting to MIT OCW RSS feed. Outbound network may be blocked.")
        except Exception as e:
            self.logger.error(f"Error fetching/parsing MIT OCW courses: {str(e)}")
            
        # Fallback scraper: scrape the audio-video courses list page if feed yields nothing and query matches
        if not courses:
            courses = self._scrape_av_courses_page(search_query)
            
        return courses

    def _scrape_av_courses_page(self, search_query: str) -> list:
        url = "https://ocw.mit.edu/courses/audio-video-courses/"
        self.logger.info(f"Attempting fallback scrape of static audio-video course listings: {url}")
        
        courses = []
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for course links under lists or table rows
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.text.strip()
                
                # Filter for relative course paths (e.g. /courses/18-01-single-variable-calculus-fall-2006)
                if href.startswith('/courses/') and not href.endswith('/audio-video-courses/') and len(href.split('/')) > 2:
                    if search_query.lower() in text.lower() or search_query.lower() in href.lower():
                        # Synthesize details
                        slug = href.split('/')[-2] if href.endswith('/') else href.split('/')[-1]
                        course_id = f"MIT-OCW-{slug.upper()}"
                        
                        courses.append({
                            "course_id": course_id,
                            "title": text or slug.replace('-', ' ').title(),
                            "description": f"MIT OpenCourseWare static class listing for {text}.",
                            "instructor": "MIT Faculty",
                            "schedule": "Self-paced / Offline Materials",
                            "syllabus": "Download syllabus and readings from MIT OCW website.",
                            "url": f"https://ocw.mit.edu{href}"
                        })
        except requests.exceptions.Timeout:
            self.logger.warning("Timeout during MIT OCW fallback scrape.")
        except Exception as e:
            self.logger.error(f"Error during MIT OCW fallback scrape: {str(e)}")
            
        return courses

    MIT_OCW_FEED_URL = "https://ocw.mit.edu/rss/new/index.xml"
