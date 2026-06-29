import requests
from providers.base import BaseCourseProvider

class CourseraCourseProvider(BaseCourseProvider):
    def get_name(self) -> str:
        return "coursera"

    def fetch_courses(self, search_query: str) -> list:
        # Coursera's public API allows searching using parameters: q=search and query=SEARCH_QUERY
        # We also request extra fields: description, partnerIds, workload, promoPhoto
        url = f"{self.COURSERA_BASE_URL}?q=search&query={requests.utils.quote(search_query)}&fields=description,workload"
        self.logger.info(f"Fetching Coursera courses from: {url}")
        
        courses = []
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch data from Coursera. Status: {response.status_code}")
                return []
            
            data = response.json()
            elements = data.get("elements", [])
            
            for elem in elements:
                slug = elem.get("slug", "")
                course_id = elem.get("id", slug)
                title = elem.get("name", "").strip()
                description = elem.get("description", "").strip()
                workload = elem.get("workload", "Self-paced").strip()
                
                course_url = f"https://www.coursera.org/learn/{slug}" if slug else "https://www.coursera.org"
                
                # Setup details
                schedule_info = f"Online / {workload}"
                instructor_info = "Coursera University Partner"
                syllabus_preview = "Syllabus available on Coursera page."
                
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
            self.logger.warning("Timeout connecting to Coursera API. Outbound network may be blocked.")
        except Exception as e:
            self.logger.error(f"Error fetching/parsing Coursera courses: {str(e)}")
            
        return courses

    COURSERA_BASE_URL = "https://api.coursera.org/api/courses.v1"
