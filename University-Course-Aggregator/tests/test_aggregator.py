import unittest
import os
import tempfile
import json
import csv
from database import CourseDatabase
from providers.mock import MockCourseProvider
from providers.coursera import CourseraCourseProvider
from providers.stanford import StanfordCourseProvider
from providers.mit_ocw import MITOCWCourseProvider
import config

class TestCourseAggregator(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing to avoid overwriting production data
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db = CourseDatabase(self.db_path)

    def tearDown(self):
        # Close connection and clean up temp db file
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_database_initialization(self):
        """Verifies database initializes correctly and starts empty."""
        self.assertEqual(self.db.count_courses(), 0)
        self.assertEqual(len(self.db.get_courses()), 0)

    def test_database_upsert_and_retrieval(self):
        """Tests inserting a course and updating (upserting) it in the database."""
        # Insert a course
        self.db.upsert_course(
            provider="mock",
            course_id="CS 101",
            title="Intro to CS",
            description="Learn Programming",
            instructor="Grace Hopper",
            schedule="MWF 10:00 AM",
            syllabus="Week 1: Python Basics",
            url="http://example.com/cs101"
        )
        
        self.assertEqual(self.db.count_courses(), 1)
        courses = self.db.get_courses(provider="mock")
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]["title"], "Intro to CS")
        self.assertEqual(courses[0]["instructor"], "Grace Hopper")

        # Update the same course
        self.db.upsert_course(
            provider="mock",
            course_id="CS 101",
            title="Intro to CS - Advanced",
            description="Learn advanced python",
            instructor="Grace Hopper",
            schedule="MWF 10:00 AM",
            syllabus="Week 1: Advanced structures",
            url="http://example.com/cs101"
        )

        self.assertEqual(self.db.count_courses(), 1)  # Unique constraint ensures no duplicate row
        courses_updated = self.db.get_courses(provider="mock")
        self.assertEqual(courses_updated[0]["title"], "Intro to CS - Advanced")
        self.assertEqual(courses_updated[0]["description"], "Learn advanced python")

    def test_database_search_filtering(self):
        """Tests that searching the DB matches key words in different fields."""
        # Insert two courses
        self.db.upsert_course(
            provider="mock",
            course_id="CS 101",
            title="Intro to Programming",
            description="Uses Python language",
            instructor="Alice",
            schedule="Mon 9 AM",
            syllabus="Intro basics",
            url=""
        )
        self.db.upsert_course(
            provider="mock",
            course_id="MATH 101",
            title="Calculus I",
            description="Limits and derivatives",
            instructor="Bob",
            schedule="Tue 9 AM",
            syllabus="Math concepts",
            url=""
        )

        # Search for Python
        res_py = self.db.get_courses(search_query="Python")
        self.assertEqual(len(res_py), 1)
        self.assertEqual(res_py[0]["course_id"], "CS 101")

        # Search for Math
        res_math = self.db.get_courses(search_query="Math")
        self.assertEqual(len(res_math), 1)
        self.assertEqual(res_math[0]["course_id"], "MATH 101")

        # Search for non-existent term
        res_none = self.db.get_courses(search_query="Chemistry")
        self.assertEqual(len(res_none), 0)

    def test_mock_provider(self):
        """Validates that the Mock Provider generates expected courses and filters correctly."""
        provider = MockCourseProvider()
        self.assertEqual(provider.get_name(), "mock")

        # Fetch all
        all_courses = provider.fetch_courses("")
        self.assertGreater(len(all_courses), 0)

        # Filtered fetch
        cs_courses = provider.fetch_courses("CS")
        self.assertGreater(len(cs_courses), 0)
        for course in cs_courses:
            match = ("cs" in course["course_id"].lower() or 
                     "cs" in course["title"].lower() or 
                     "cs" in course["description"].lower() or 
                     "cs" in course["syllabus"].lower())
            self.assertTrue(match)

    def test_real_providers_offline_graceful_failures(self):
        """Tests that real providers handle timeouts or connection issues gracefully without crashes."""
        # Set super low timeout to simulate instant timeout or verify connection failures don't crash
        coursera = CourseraCourseProvider(timeout=0.001)
        courses_coursera = coursera.fetch_courses("deep learning")
        self.assertEqual(courses_coursera, [])

        stanford = StanfordCourseProvider(timeout=0.001)
        courses_stanford = stanford.fetch_courses("CS106")
        self.assertEqual(courses_stanford, [])

        mit_ocw = MITOCWCourseProvider(timeout=0.001)
        courses_mit = mit_ocw.fetch_courses("math")
        self.assertEqual(courses_mit, [])

    def test_config_loader(self):
        """Validates that configuration variables are loaded and have correct types."""
        self.assertIsNotNone(config.DB_NAME)
        self.assertIsInstance(config.REQUEST_TIMEOUT, int)
        self.assertIsInstance(config.MAX_RETRIES, int)
        self.assertIsNotNone(config.DEFAULT_QUERY)

if __name__ == "__main__":
    unittest.main()
