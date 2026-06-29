from abc import ABC, abstractmethod
import logging

class BaseCourseProvider(ABC):
    def __init__(self, timeout=10, retries=3):
        self.timeout = timeout
        self.retries = retries
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_name(self) -> str:
        """Returns the unique name identifier of this course provider."""
        pass

    @abstractmethod
    def fetch_courses(self, search_query: str) -> list:
        """Fetches courses matching search_query.
        
        Returns:
            list of dict: Each dict containing:
                - course_id (str): Unique code for course
                - title (str): Course title
                - description (str, optional): Description
                - instructor (str, optional): Course instructor(s)
                - schedule (str, optional): Timing/Schedule details
                - syllabus (str, optional): Syllabi details
                - url (str, optional): Link to course homepage
        """
        pass
