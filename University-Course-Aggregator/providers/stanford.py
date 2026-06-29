import xml.etree.ElementTree as ET
import requests
from providers.base import BaseCourseProvider

class StanfordCourseProvider(BaseCourseProvider):
    def get_name(self) -> str:
        return "stanford"

    def fetch_courses(self, search_query: str) -> list:
        # Format the query for Stanford ExploreCourses XML view
        # We search with the query terms
        url = f"{self.STANFORD_BASE_URL}?view=xml&filter-coursestatus-Active=on&q={requests.utils.quote(search_query)}"
        self.logger.info(f"Fetching Stanford courses from: {url}")
        
        courses = []
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch data from Stanford. Status: {response.status_code}")
                return []
            
            # Parse the XML response
            root = ET.fromstring(response.content)
            for course_el in root.findall(".//course"):
                subject = course_el.findtext("subject", "").strip()
                code = course_el.findtext("codeElement", "").strip()
                course_id = f"{subject} {code}".strip()
                
                title = course_el.findtext("title", "").strip()
                description = course_el.findtext("description", "").strip()
                
                # Extract Instructors and Schedule from Sections
                instructors = set()
                schedules = []
                terms = set()
                
                for section in course_el.findall(".//section"):
                    term = section.findtext("term", "").strip()
                    if term:
                        terms.add(term)
                        
                    for inst in section.findall(".//instructor"):
                        name = inst.text
                        if name:
                            instructors.add(name.strip())
                            
                    for sched in section.findall(".//schedule"):
                        days = sched.findtext("days", "").strip()
                        start = sched.findtext("startTime", "").strip()
                        end = sched.findtext("endTime", "").strip()
                        loc = sched.findtext("location", "").strip()
                        
                        sched_str = f"{days} {start}-{end}"
                        if loc:
                            sched_str += f" ({loc})"
                        schedules.append(sched_str.strip())
                
                # De-duplicate schedule strings
                unique_schedules = list(set(schedules))
                schedule_info = "; ".join(unique_schedules)
                if terms:
                    schedule_info = f"Terms: {', '.join(terms)} | Schedule: " + schedule_info
                
                instructor_info = ", ".join(instructors)
                course_url = f"https://explorecourses.stanford.edu/search?q={subject}+{code}"
                
                # Syllabus is often not explicitly structured in Stanford XML, so we point to description or sections
                syllabus_preview = "Refer to description and syllabus at course URL."
                
                courses.append({
                    "course_id": course_id,
                    "title": title,
                    "description": description,
                    "instructor": instructor_info,
                    "schedule": schedule_info,
                    "syllabus": syllabus_preview,
                    "url": course_url
                })
                
        except requests.exceptions.Timeout:
            self.logger.warning("Timeout connecting to Stanford ExploreCourses API. Outbound network may be blocked.")
            # Gracefully handle instead of crashing
        except Exception as e:
            self.logger.error(f"Error fetching/parsing Stanford courses: {str(e)}")
            
        return courses

    # Allow custom base URL override for tests or local proxies
    STANFORD_BASE_URL = "https://explorecourses.stanford.edu/search"
