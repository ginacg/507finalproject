import unittest
import json
import sqlite3
import finalproject as proj

conn = sqlite3.connect("final.sqlite")
cur = conn.cursor()
conn.commit()

class TestProject(unittest.TestCase):

    def testScraping(self):
        name_data = proj.check_cache()
        test_name = name_data["1980 (F)"]["Jennifer"]

        self.assertEqual(type(name_data), type({}))
        self.assertEqual(len(name_data.keys()), 278)
        self.assertIn("1910 (F)", name_data.keys())
        self.assertIn("2005 (M)", name_data.keys())
        self.assertIn("Percent of Births", test_name.keys())

    def testDatabase(self):

        test_statement1 = "SELECT COUNT('1995 (M)'.Name) FROM '1995 (M)'"
        db_result1 = cur.execute(test_statement1)
        db_result1 = db_result1.fetchall()
        for row in db_result1:
            test_result1 = str(row[0])
        self.assertEqual(test_result1, "1000")

        test_statement2 = "SELECT Name FROM '1970 (F)' WHERE Rank = 2"
        db_result2 = cur.execute(test_statement2)
        db_result2 = db_result2.fetchall()
        for row in db_result2:
            test_result2 = row[0]
        self.assertEqual(test_result2, "Lisa")

        test_statement3 = "SELECT Name FROM '1942 (F)' WHERE Name LIKE 'Mary%'"
        db_result3 = cur.execute(test_statement3)
        db_result3 = db_result3.fetchall()
        row_count3 = 0
        for row in db_result3:
            row_count3 +=1
        self.assertEqual(row_count3, 10)

        test_statement4 = "SELECT Name FROM '2018 (M)' WHERE Percent >= 1"
        db_result4 = cur.execute(test_statement4)
        db_result4 = db_result4.fetchall()
        row_count4 = 0
        for row in db_result4:
            row_count4 += 1
        self.assertEqual(row_count4, 1)

        test_statement5 = "SELECT Name FROM '1880 (M)' WHERE Percent >= 1"
        db_result5 = cur.execute(test_statement5)
        db_result5 = db_result5.fetchall()
        row_count5 = 0
        for row in db_result5:
            row_count5 += 1
        self.assertEqual(row_count5, 16)

    def testProcess(self):

        name_data = proj.check_cache()

        table_test = proj.display_table(name_data, year="2006", gender="F", num=10)
        self.assertEqual(str(type(table_test)), "<class 'plotly.graph_objs._figure.Figure'>")

        display_one_test1 = proj.display_one_change(name_data, "Rose", "F")
        self.assertEqual(str(type(display_one_test1)), "<class 'plotly.graph_objs._figure.Figure'>")

        display_one_test2 = proj.display_one_change(name_data, "Elzada", "F")
        self.assertEqual(str(type(display_one_test2)), "<class 'plotly.graph_objs._figure.Figure'>")

        compare_test = proj.compare_change(name_data, "Walter", "Jaden", "M")
        self.assertEqual(str(type(compare_test)), "<class 'plotly.graph_objs._figure.Figure'>")

        pie_test = proj.show_distribution(name_data, "1960", "M")
        self.assertEqual(str(type(compare_test)), "<class 'plotly.graph_objs._figure.Figure'>")

unittest.main()

conn.close()


#3 test cases
#15 assertions
