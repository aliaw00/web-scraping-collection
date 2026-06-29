import argparse
import sys
import os
import json
import csv
import logging
from config import DB_NAME, LOG_LEVEL, REQUEST_TIMEOUT, MAX_RETRIES, DEFAULT_QUERY
from database import CourseDatabase

# Import providers
from providers.coursera import CourseraCourseProvider
from providers.stanford import StanfordCourseProvider
from providers.mit_ocw import MITOCWCourseProvider
from providers.mock import MockCourseProvider

def setup_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def export_courses(courses, fmt, output_path):
    if not courses:
        print("No courses to export.")
        return

    try:
        if fmt == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(courses, f, indent=4, ensure_ascii=False)
            print(f"Successfully exported {len(courses)} courses to JSON: {output_path}")
        elif fmt == "csv":
            keys = courses[0].keys()
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(courses)
            print(f"Successfully exported {len(courses)} courses to CSV: {output_path}")
    except Exception as e:
        print(f"Error exporting courses: {e}", file=sys.stderr)

def print_courses_table(courses):
    if not courses:
        print("\nNo courses found matching criteria.")
        return

    print(f"\n--- Found {len(courses)} Courses ---")
    for idx, course in enumerate(courses, 1):
        print(f"\n[{idx}] {course.get('course_id', 'N/A')} - {course.get('title', 'N/A')}")
        print(f"    Provider:   {course.get('provider', 'N/A')}")
        print(f"    Instructor: {course.get('instructor', 'N/A')}")
        print(f"    Schedule:   {course.get('schedule', 'N/A')}")
        print(f"    URL:        {course.get('url', 'N/A')}")
        desc = course.get('description', '')
        if desc:
            desc_preview = desc[:120] + "..." if len(desc) > 120 else desc
            print(f"    Description: {desc_preview}")
        syllabus = course.get('syllabus', '')
        if syllabus:
            syl_preview = syllabus[:100] + "..." if len(syllabus) > 100 else syllabus
            print(f"    Syllabus:   {syl_preview}")
    print("\n-------------------------")

def main():
    setup_logging()
    logger = logging.getLogger("CourseAggregator")

    # Map provider name to class
    available_providers = {
        "coursera": CourseraCourseProvider,
        "stanford": StanfordCourseProvider,
        "mit_ocw": MITOCWCourseProvider,
        "mock": MockCourseProvider
    }

    parser = argparse.ArgumentParser(
        description="University Course Aggregator - Consolidates course syllabi, descriptions and timings."
    )
    parser.add_argument(
        "--query", "-q",
        default=DEFAULT_QUERY,
        help=f"Search term for courses (default: '{DEFAULT_QUERY}')"
    )
    parser.add_argument(
        "--provider", "-p",
        action="append",
        choices=list(available_providers.keys()) + ["all"],
        help="Provider(s) to scrape. Use multiple times to scrape multiple (e.g. -p coursera -p stanford). Default is 'mock'."
    )
    parser.add_argument(
        "--search-db", "-s",
        action="store_true",
        help="Query and display matching courses from local database without performing a live scrap/crawl."
    )
    parser.add_argument(
        "--export", "-e",
        choices=["json", "csv"],
        help="Export results to a file format."
    )
    parser.add_argument(
        "--output", "-o",
        help="File path to save the exported data."
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="Display the list of available providers."
    )

    args = parser.parse_args()

    if args.list_providers:
        print("\nAvailable Course Providers:")
        for p in available_providers.keys():
            print(f" - {p}")
        return

    # Initialize Database
    db = CourseDatabase(DB_NAME)

    # If --search-db is specified, query the database and exit
    if args.search_db:
        logger.info(f"Querying local database for: '{args.query}'")
        courses = db.get_courses(search_query=args.query)
        print_courses_table(courses)
        if args.export and args.output:
            export_courses(courses, args.export, args.output)
        return

    # Determine which providers to run
    providers_to_run = []
    if not args.provider:
        # Default to mock to prevent test sandboxes/networks from failing or hanging
        providers_to_run = ["mock"]
    elif "all" in args.provider:
        providers_to_run = [p for p in available_providers.keys() if p != "mock"]
    else:
        providers_to_run = args.provider

    all_fetched_courses = []

    # Run scrapers/apis
    for p_name in providers_to_run:
        logger.info(f"Running scraper for provider: '{p_name}'")
        provider_class = available_providers[p_name]
        # Instantiate with timeout and retries from config
        provider = provider_class(timeout=REQUEST_TIMEOUT, retries=MAX_RETRIES)
        
        try:
            fetched = provider.fetch_courses(args.query)
            logger.info(f"Fetched {len(fetched)} courses from '{p_name}'")
            
            for course in fetched:
                # Add provider field
                course["provider"] = p_name
                # Upsert into database
                db.upsert_course(
                    provider=p_name,
                    course_id=course["course_id"],
                    title=course["title"],
                    description=course.get("description", ""),
                    instructor=course.get("instructor", ""),
                    schedule=course.get("schedule", ""),
                    syllabus=course.get("syllabus", ""),
                    url=course.get("url", "")
                )
                all_fetched_courses.append(course)
        except Exception as e:
            logger.exception(f"Scraper '{p_name}' failed to run: {e}")

    # Display consolidated list
    print_courses_table(all_fetched_courses)

    # Export if requested
    if args.export and args.output:
        export_courses(all_fetched_courses, args.export, args.output)

if __name__ == "__main__":
    main()
