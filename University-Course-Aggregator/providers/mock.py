from providers.base import BaseCourseProvider

class MockCourseProvider(BaseCourseProvider):
    def get_name(self) -> str:
        return "mock"

    def fetch_courses(self, search_query: str) -> list:
        self.logger.info(f"Generating mock university courses for query: '{search_query}'")
        
        # A list of predefined high-quality realistic course catalogs
        mock_catalog = [
            {
                "course_id": "CS 101",
                "title": "Introduction to Computer Science & Programming",
                "description": "Fundamental concepts of programming, algorithms, and computational thinking using Python.",
                "instructor": "Dr. Alan Turing, Prof. Grace Hopper",
                "schedule": "Mon/Wed 10:00 AM - 11:30 AM (Science Hall 201)",
                "syllabus": "Week 1: Variables & Control Flow; Week 2: Functions & Scope; Week 3: Data Structures; Week 4: Recursion; Week 5: Search & Sort Algorithms; Week 6: Final Project.",
                "url": "https://university.edu/courses/cs101"
            },
            {
                "course_id": "CS 106A",
                "title": "Programming Methodology",
                "description": "Introduction to software engineering principles, object-oriented programming, and interface design.",
                "instructor": "Prof. Mehran Sahami",
                "schedule": "Tue/Thu 1:30 PM - 3:00 PM (Hewlett Teaching Center)",
                "syllabus": "1. Karel the Robot (Control Flow); 2. Java Basics & OOP; 3. Graphics & Event Handling; 4. Memory & Decomposition; 5. Text processing.",
                "url": "https://university.edu/courses/cs106a"
            },
            {
                "course_id": "CS 224N",
                "title": "Natural Language Processing with Deep Learning",
                "description": "Deep learning models for processing natural language, covering word vectors, recurrent networks, transformers, and large language models.",
                "instructor": "Prof. Christopher Manning",
                "schedule": "Mon/Wed 3:15 PM - 4:45 PM (NVIDIA Auditorium)",
                "syllabus": "Lecture 1: Word Vectors; Lecture 2: Neural Nets; Lecture 3: RNNs and LSTMs; Lecture 4: Transformers & Attention; Lecture 5: Pretraining & Prompting.",
                "url": "https://university.edu/courses/cs224n"
            },
            {
                "course_id": "MATH 51",
                "title": "Linear Algebra, Multivariable Calculus, and Modern Applications",
                "description": "Unified treatment of multivariable calculus and linear algebra, with application to machine learning and optimization.",
                "instructor": "Dr. Maria Mirzakhani",
                "schedule": "Mon/Tue/Thu/Fri 11:00 AM - 12:00 PM (Math Corner 380)",
                "syllabus": "Unit 1: Vectors, Matrices, and Systems of Equations; Unit 2: Linear Subspaces and Eigenvalues; Unit 3: Derivatives and Gradients; Unit 4: Optimization.",
                "url": "https://university.edu/courses/math51"
            },
            {
                "course_id": "CHEM 31",
                "title": "Chemical Principles and Chemical Structure",
                "description": "Atomic structures, chemical bonding, gas properties, and molecular interactions.",
                "instructor": "Dr. Linus Pauling",
                "schedule": "Wed/Fri 9:00 AM - 10:30 AM (Chemical Science Lab)",
                "syllabus": "1. Quantum Mechanics of Atoms; 2. Chemical Bonds & Molecular Geometry; 3. Intermolecular Forces; 4. Gas Laws & Phase diagrams.",
                "url": "https://university.edu/courses/chem31"
            },
            {
                "course_id": "PHYS 41",
                "title": "Mechanics and Special Relativity",
                "description": "Newtonian mechanics, conservation laws, rotational dynamics, gravitation, and an introduction to special relativity.",
                "instructor": "Prof. Richard Feynman",
                "schedule": "Mon/Wed/Fri 2:00 PM - 3:00 PM (Physics Lecture Hall A)",
                "syllabus": "Week 1-3: Kinematics & Newton's Laws; Week 4-6: Energy and Momentum Conservation; Week 7-8: Rotational Mechanics; Week 9-10: Lorentz Transformations.",
                "url": "https://university.edu/courses/phys41"
            },
            {
                "course_id": "BIO 150",
                "title": "Evolution and Genetics",
                "description": "Introduction to modern genetics, evolutionary processes, gene regulations, and heredity mechanisms.",
                "instructor": "Dr. Charles Darwin",
                "schedule": "Tue/Thu 10:30 AM - 12:00 PM (Biology Lab Auditorium)",
                "syllabus": "1. Mendelian Genetics; 2. DNA Replication & Transcription; 3. Mechanisms of Evolution; 4. Speciation and Phylogeny; 5. Population Genetics.",
                "url": "https://university.edu/courses/bio150"
            }
        ]
        
        # Filter mock catalog based on search query match
        query = search_query.lower().strip()
        if not query:
            return mock_catalog
            
        filtered_courses = []
        for course in mock_catalog:
            # Check for matches in title, course_id, description, or syllabus
            if (query in course["course_id"].lower() or 
                query in course["title"].lower() or 
                query in course["description"].lower() or 
                query in course["syllabus"].lower()):
                filtered_courses.append(course)
                
        return filtered_courses
