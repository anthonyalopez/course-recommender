import argparse
import sys
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

class Catalog:
    """ CLass to represent a university catalog website """
    def __init__(self, url, driver_path, search_bar_id, search_button_id):
        self.url = url
        self.driver_path = driver_path
        self.search_bar_id = search_bar_id
        self.search_button_id = search_button_id

        # Create a new instance of the Chrome driver
        self.driver = webdriver.Chrome(executable_path=self.driver_path)

        # Navigate to the catalog page
        self.driver.get(self.url)
        time.sleep(1)
        
    def search(self, search_term):
        # Find the search bar and enter the search term
        search_bar = self.driver.find_element(By.ID, self.search_bar_id)
        search_bar.clear()
        search_bar.send_keys(search_term)

        # Find the search button and click it
        search_button = self.driver.find_element(By.ID, self.search_button_id)
        search_button.click()
        time.sleep(1)

        # Wait for the search results to load
        EC.presence_of_element_located((By.ID, "course-search-results"))
    
    def __del__(self):
        # Close the browser window
        self.driver.quit()

class Course:
    """
    A class representing a course.

    Attributes:
    - course_id(int): identifier for the course.
    - title(str): title of the course.
    - credits(int): credits of each course.
    - description(str): brief description of the course.
    - prerequisites(list): string list of prerequisites required for course.
    - department(str): department course is a part of.
    - sections(list): string list of the section a course is a part of.
    """
    def __init__(self, course_id, title, credits, description, prerequisites, department, sections):
        self.course_id = course_id
        self.title = title
        self.credits = credits
        self.description = description
        self.prerequisites = prerequisites
        self.department = department
        self.sections = sections


class Section:
    """
    A class representing a section of a course.

    Attributes:
    - section_number(int): unique section number.
    - instructor(str): instructor teaching course section.
    - seats(int): number of seats in the section.
    - section_time(str): time the section is.
    - location(str): location of the section.
    """
    def __init__(self, section_number, instructor, seats, section_time, location):
        self.section_number = section_number
        self.instructor = instructor
        self.seats = seats
        self.section_time = section_time
        self.location = location

class Database:
    #Represents a SQLite database for storing course and section information

    def __init__(self, db_path):
        #Initializes the Database class with the path to the SQLite database file

        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        #Creates the necessary tables in the database
        self.cursor.execute('''DROP TABLE IF EXISTS courses''')
        self.cursor.execute('''CREATE TABLE courses
            (course_id TEXT PRIMARY KEY,
            title TEXT,
            credits INTEGER,
            description TEXT,
            prerequisites TEXT,
            department TEXT)''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sections (
            section_number INTEGER PRIMARY KEY,
            course_id TEXT,
            instructor TEXT,
            seats TEXT,
            section_time TEXT,
            location TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )''')

        self.conn.commit()

    def add_course(self, course):
        #Adds a course to the courses table in the database
        try:
            self.cursor.execute('''INSERT INTO courses (course_id, title, credits, description, prerequisites, department) VALUES (?, ?, ?, ?, ?, ?)''', (course.course_id, course.title, course.credits, course.description, course.prerequisites, course.department))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Course {course.course_id} already exists in database")

    def add_section(self, section_number, course_id, instructor, seats, section_time, location):
        #Adds a section to the sections table in the database
        try:
            self.cursor.execute('''INSERT INTO sections VALUES (?, ?, ?, ?, ?, ?)''', (section_number, course_id, instructor, seats, section_time, location))
            self.conn.commit()
            print(f"Added section {section_number} of course {course_id}")
        except sqlite3.IntegrityError:
            print(f"Section{section_number} of course already exists in database")
          

def main(keywords, department_list):
    catalog = Catalog(
        url="https://app.testudo.umd.edu/soc/",
        driver_path="./chromedriver.exe",
        search_bar_id="course-id-input",
        search_button_id="search-button"
    )
    db = Database("courses.db")
    db.create_tables()

    # Get all the courses and their descriptions for the given departments
    courses_data = []
    for department_name in department_list:
        # Search for the department
        catalog.search(department_name)
        time.sleep(1)

        # Get all the courses
        courses = catalog.driver.find_elements(By.XPATH, ".//div[@class='course']")

        # Parse each course for course data
        for course in courses:
            try:
                show_sections_button = course.find_element(By.XPATH, ".//a[@class='toggle-sections-link']")
                if show_sections_button.is_displayed():
                    show_sections_button.click()
                time.sleep(1)
            except NoSuchElementException:
                continue

            # Get the course sections
            sections = []
            section_divs = course.find_elements(By.XPATH, ".//div[@class='sections-container']//div[@class='section delivery-f2f']")
            for section_div in section_divs:
                try:
                    section_number = section_div.find_element(By.XPATH, ".//span[@class='section-id']").text
                except NoSuchElementException:
                    section_number = "No Section Number"
                try:
                    instructor = section_div.find_element(By.XPATH, ".//span[@class='section-instructors']").text
                except NoSuchElementException:
                    instructor = "No Instructor"
                try:
                    seats = section_div.find_element(By.XPATH, ".//span[@class='seats-info']").text
                except NoSuchElementException:
                    seats = "No Seats"
                try:
                    section_time = section_div.find_element(By.XPATH, ".//div[@class='section-day-time-group push_two five columns']").text
                except NoSuchElementException:
                    section_time = "No Time"
                try:
                    location = section_div.find_element(By.XPATH, ".//span[@class='class-building']").text
                except NoSuchElementException:
                    location = "No Location"

                # Create a Section object
                s = Section(section_number, instructor, seats, section_time, location)
                sections.append(s)

            # Get the course data
            try:
                theCourse = course.find_element(By.XPATH, ".//div[@class='course-id']").text
            except NoSuchElementException:
                theCourse = "No Course ID"
            try:
                credits = course.find_element(By.XPATH, ".//span[@class='course-min-credits']").text
            except NoSuchElementException:
                credits = "No Credits"
            try:
                title = course.find_element(By.XPATH, ".//span[@class='course-title']").text
            except NoSuchElementException:
                title = "No Title"
            try:
                description = course.find_element(By.XPATH, './/div[contains(@class, "approved-course-text")][not(contains(text(), "Restriction:"))][not(contains(text(), "Cross-listed with:"))][not(contains(text(), "Credit only granted for:"))]').text
            except NoSuchElementException:
                description = "No Description"
            try:
                prerequisites = course.find_element(By.XPATH, ".//div[@class='twelve columns']//div[@class='approved-course-text']").text
            except NoSuchElementException:
                prerequisites = "No Prerequisites"

            # Get the department from the department_list
            department = department_name

            # Create a Course object
            c = Course(theCourse, title, credits, description, prerequisites, department, sections)

            # Check if any of the keywords are in the title or description
            for keyword in keywords:
                if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                    courses_data.append(c)
                    db.add_course(c)
                    for section in sections:
                        db.add_section(section.section_number, theCourse, section.instructor, section.seats, section.section_time, section.location)
                    break

            # Print the courses and sections in the database
            db.cursor.execute("SELECT * FROM courses")
            courses = db.cursor.fetchall()
            for course in courses:
                print(f"Course ID: {course[0]}, Title: {course[1]}, Credits: {course[2]}, Department: {course[5]}, Description: {course[3]}")
                
                db.cursor.execute("SELECT * FROM sections WHERE course_id=?", (course[0],))
                sections = db.cursor.fetchall()
                for section in sections:
                    print(f"\tSection Number: {section[0]}, Instructor: {section[2]}, Seats: {section[3]}, Section Time: {section[4]}, Location: {section[5]} \n")

def parse_args(args_list):
    """Takes a list of strings from the command prompt and passes them through as arguments
    
    Args:
        args_list (list) : the list of strings from the command prompt
    Returns:
        args (ArgumentParser)
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('keywords', metavar='keyword', type=str, nargs='+', help='keywords to search for')
    parser.add_argument('-d', "--departments", metavar='D', type=str, nargs='+', help='list of department names to search for')
    
    args = parser.parse_args(args_list)
    
    return args

if __name__ == "__main__":
    arguments = parse_args(sys.argv[1:])
    main(arguments.keywords, arguments.departments)