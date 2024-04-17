import unittest
from unittest.mock import Mock
from recommender import Catalog, Course, Database, Section, main


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog(
            url="https://app.testudo.umd.edu/soc/",
            driver_path="./chromedriver.exe",
            search_bar_id="course-id-input",
            search_button_id="search-button"
        )
        self.driver_mock = Mock()
        self.catalog.driver = self.driver_mock

    def test_search(self):
        search_bar_mock = Mock()
        search_button_mock = Mock()
        self.driver_mock.find_element.return_value = search_bar_mock
        self.driver_mock.find_element.return_value = search_button_mock

        self.catalog.search("test")

        search_bar_mock.send_keys.assert_called_once_with("test")
        search_button_mock.click.assert_called_once()

    def tearDown(self):
        del self.catalog
        del self.driver_mock


class TestCourse(unittest.TestCase):
    def test_init(self):
        c = Course("CMSC131", "Object-Oriented Programming I", 4, "Introduction to programming and computer science. Emphasizes understanding and implementation of applications using object-oriented techniques. Develops skills such as program design and testing as well as implementation of programs using a graphical IDE. Programming done in Java.", "Corequisite: MATH140. Credit only granted for: CMSC131, CMSC133, or IMDM127.", "CMSC", [])
        self.assertEqual(c.course_id, "CMSC131")
        self.assertEqual(c.title, "Object-Oriented Programming I")
        self.assertEqual(c.credits, 4)
        self.assertEqual(c.description, "Introduction to programming and computer science. Emphasizes understanding and implementation of applications using object-oriented techniques. Develops skills such as program design and testing as well as implementation of programs using a graphical IDE. Programming done in Java.")
        self.assertEqual(c.prerequisites, "Corequisite: MATH140. Credit only granted for: CMSC131, CMSC133, or IMDM127.")
        self.assertEqual(c.department, "CMSC")
        self.assertEqual(c.sections, [])


class TestSection(unittest.TestCase):
    def test_init(self):
        s = Section("0101", "Nelson Padua-Perez", "Seats (Total: 34, Open: 25, Waitlist: 0 )", "MWF 2:00pm - 2:50pm", "IRB 0324")
        self.assertEqual(s.section_number, "0101")
        self.assertEqual(s.instructor, "Nelson Padua-Perez")
        self.assertEqual(s.seats, "Seats (Total: 34, Open: 25, Waitlist: 0 )")
        self.assertEqual(s.section_time, "MWF 2:00pm - 2:50pm")
        self.assertEqual(s.location, "IRB 0324")


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.db.create_tables()

    def test_create_tables(self):
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.db.cursor.fetchall()
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0][0], "courses")
        self.assertEqual(tables[1][0], "sections")

    def test_add_course(self):
        c = Course("CMSC131", "Object-Oriented Programming I", 4, "Introduction to object-oriented programming and programming in Java", "MATH140 or MATH220 or MATH246 or MATH251 or MATH340 or AMSC460", "Computer Science", [])
        self.db.add_course(c)
        self.db.cursor.execute("SELECT * FROM courses WHERE course_id=?", ("CMSC131"))
        result = self.db.cursor.fetchone()
        self.assertIsNotNone(result)

       
