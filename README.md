# course-recommender
This program is a course recommender for Students of the University of Maryland, as it is a large Schedule of Classes website, this program takes in keywords, as well as departments to search for(to make it easier to use and faster), it uses web scraping to go search departments entered and searches the courses in those departments for the keywords entered.

To run the program, you need to run it through command line, you would need to enter: python recommender.py keywords -d departments for example: python recommender.py java -d CMSC or: python recommender.py "java" "python" "Computer Science" -d "CMSC" "INST"

The program will then open the browser as it uses selenium to do the web scraping, and it will go through the pages/courses and will print in the console the courses that contain the keywords - the information such as course id, title, credits, description, prerequisites, department, and its sections - it will also print the sections info such as section number, instructor, seats, section times, and location.
