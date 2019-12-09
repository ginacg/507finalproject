from bs4 import BeautifulSoup
import requests
import json
import plotly.graph_objects as go
import sys
import sqlite3

CACHE_FNAME = "final_cache.json"

conn = sqlite3.connect("final.sqlite")
cur = conn.cursor()
conn.commit()

try:
    cache_file = open(CACHE_FNAME, "r")
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def check_cache():
    if len(CACHE_DICTION.keys()) != 0:
        name_data = CACHE_DICTION
        return name_data
    else:
        scrape_info()

def scrape_info():
    name_dict = {}
    baseurl = "http://www.behindthename.com/top/lists/united-states/"
    years = list(range(1880, 2019))

    for year in years:
        year_m_dict = {}
        year_f_dict = {}
        year_url = baseurl + str(year)
        year_text = requests.get(year_url).text
        year_soup = BeautifulSoup(year_text, "html.parser")

        table_rows = year_soup.find_all("tr")

        for row in table_rows:
            table_cells = row.find_all("td")
            if len(table_cells) == 4:
                rank = table_cells[0].text.strip()
                name = table_cells[1].text.strip()
                percent = table_cells[2].text.strip()

                if len(year_m_dict) < 1000:
                    year_m_dict[name] = {"Gender":"M", "Rank":rank, "Percent of Births":percent}
                else:
                    year_f_dict[name] = {"Gender":"F", "Rank":rank, "Percent of Births":percent}

        name_dict[str(year) + " (M)"] = year_m_dict
        name_dict[str(year) + " (F)"] = year_f_dict

    CACHE_DICTION = name_dict
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME, "w")
    fw.write(dumped_json_cache)
    fw.close()

    create_database()

    return(name_dict)

def create_database(name_data):
    for year in name_data:
        try:
            statement = "CREATE TABLE '" + year + "' ('Id' INTEGER PRIMARY KEY AUTOINCREMENT, 'Name' TEXT, 'Gender' TEXT, 'Rank' INTEGER, 'Percent' FLOAT)"
            conn.commit()
            cur.execute(statement)
        except:
            pass

        year_dict = name_data[year]

        for name in year_dict:
            name_dict = year_dict[name]
            ranked_name = name
            gender = name_dict["Gender"]
            rank = name_dict["Rank"]
            percent = name_dict["Percent of Births"][:-1]

            insertion = (None, ranked_name, gender, rank, percent)
            insert_statement = "INSERT INTO '" + year + "'"
            insert_statement += "VALUES (?, ?, ?, ?, ?)"
            conn.commit()
            cur.execute(insert_statement, insertion)

def display_table(name_data, year="2018", gender="F", num=100):

    gender = gender.upper()

    if gender == "F":
        title = "Top " + str(num) + " girl names of " + year
    else:
        title = "Top " + str(num) + " boy names of " + year


    num = int(num)
    headers = dict(values=["Rank", "Gender", "Name", "Percent of Births"])
    rank_column = list(range(1, num+1))
    gender_column = []
    for item in range(1, num+1):
        gender_column += gender

    for ranking_dict in name_data:
        year_gender = ranking_dict.split()
        if gender == "F":
            if year_gender[0] == year and "F" in year_gender[1]:
                name_list = name_data[ranking_dict]
        else:
            if year_gender[0] == year and "M" in year_gender[1]:
                name_list = name_data[ranking_dict]

    name_column = []
    percent_column = []
    data_count = 1
    for name in name_list:
        if data_count <= num:
            name_column += [name]
            percent_column += [name_list[name]["Percent of Births"]]
            data_count +=1

    fig = go.Figure(data=[go.Table(header=headers, cells=dict(values=[rank_column, gender_column, name_column, percent_column]))])
    fig.update_layout(title=title)

    fig.show()

    return fig

def display_one_change(name_data, name, gender):
    gender = gender.upper()
    year_column = []
    rank_column = []

    for dict in name_data:
        if gender in dict:
            gender_dict = name_data[dict]
            year_gender = dict.split()
            year = year_gender[0]

            for a_name in gender_dict:
                if a_name == name:
                    year_column += [year]
                    rank = gender_dict[name]["Rank"]
                    rank = int(rank[:-1])
                    rank_column += [rank]

    title = "Popularity of " + name + " from 1880 - 2018"

    fig = go.Figure(data=go.Scatter(x=year_column, y=rank_column))
    fig.update_xaxes(range=[1880,2018])
    fig.update_yaxes(range=[1000,1])
    fig.update_layout(title=title)

    fig.show()

    return fig

def compare_change(name_data, name1, name2, gender):
    gender = gender.upper()
    year_column1 = []
    year_column2 = []
    rank_column1 = []
    rank_column2 = []

    for dict in name_data:
        if gender in dict:
            gender_dict = name_data[dict]
            year_gender = dict.split()
            year = year_gender[0]

            for a_name in gender_dict:
                if a_name == name1:
                    year_column1 += [year]
                    rank = gender_dict[name1]["Rank"]
                    rank = int(rank[:-1])
                    rank_column1 += [rank]
                if a_name == name2:
                    year_column2 += [year]
                    rank = gender_dict[name2]["Rank"]
                    rank = int(rank[:-1])
                    rank_column2 += [rank]

    title = "Popularity of " + name1 + " and " + name2 + " from 1880 - 2018"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=year_column1, y=rank_column1, name=name1))
    fig.add_trace(go.Scatter(x=year_column2, y=rank_column2, name=name2))
    fig.update_xaxes(range=[1880,2018])
    fig.update_yaxes(range=[1000,1])
    fig.update_layout(title=title)

    fig.show()

    return fig

def show_distribution(name_data, year, gender):
    gender = gender.upper()
    top_10 = 0.00
    top_100 = 0.00
    top_500 = 0.00
    top_1000 = 0.00
    below_top_1000 = 0.00

    for dict in name_data:
        year_gender = dict.split()
        if gender == "F":
            if year_gender[0] == year and "F" in year_gender[1]:
                name_list = name_data[dict]
        else:
            if year_gender[0] == year and "M" in year_gender[1]:
                name_list = name_data[dict]

    for name in name_list:
        rank = name_list[name]["Rank"]
        rank = int(rank[:-1])
        percent = name_list[name]["Percent of Births"]
        percent = float(percent[:-1])
        if rank <= 10:
            top_10 += percent
        elif rank > 10 and rank <= 100:
            top_100 += percent
        elif rank > 100 and rank <= 500:
            top_500 += percent
        else:
            top_1000 += percent

    below_top_1000 = 100.00 - top_10 - top_100 - top_500 - top_1000

    labels = ["Top 10", "Ranked 11 - 100", "Ranked 101 - 500", "Ranked 501 - 1000", "Outside Top 1000"]
    values = [top_10, top_100, top_500, top_1000, below_top_1000]

    if gender == "F":
        title = "Distribution of popular girl names for " + year
    else:
        title = "Distribution of popular boy names for " + year

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title=title)
    fig.show()

    return fig

def help_text():

    text = "Available commands:\n\n"
    text += "table\n"
    text += "\t\t Displays the top names for a given year and gender.\n"
    text += "\t\t Format: table, year, M/F, number to display (up to 1000) \n\n"
    text += "change\n"
    text += "\t\t Displays the change in popularity over time for one or two names.\n"
    text += "\t\t Format: change, name, M/F OR change, name1, name2, M/F\n\n"
    text += "dist"
    text += "\t\t Displays the distrubtion of popular names (e.g., which percentage of babies were given one of the ten most popular names) for a given year and gender.\n"
    text += "\t\t Format: dist, year, M/F\n\n"
    text += "help\n"
    text += "\t\t Displays this text."
    text += "\n\n Stuck? Check the formatting of your command. All components must be separated with a comma. Only years from 1880 to 2018 have data."

    print(text)

def process_command(command):
    name_data = check_cache()

    if "table" in command:
        try:
            split_command = command.split(",")
            year = split_command[1].strip()
            gender = split_command[2].strip()
            num = split_command[3].strip()
            display_table(name_data, year=year, gender=gender, num=num)
        except:
            help_text()

    elif "change" in command:
        try:
            split_command = command.split(",")
            if len(split_command) == 3:
                name = split_command[1].strip()
                gender = split_command[2].strip()
                display_one_change(name_data, name=name, gender=gender)
            else:
                name1 = split_command[1].strip()
                name2 = split_command[2].strip()
                gender = split_command[3].strip()
                compare_change(name_data, name1=name1, name2=name2, gender=gender)
        except:
            help_text()

    elif "dist" in command:
        try:
            split_command = command.split(",")
            year = split_command[1].strip()
            gender = split_command[2].strip()
            show_distribution(name_data, year, gender)
        except:
            help_text()

    elif "exit" in command:
        exit()

    else:
        help_text()

    command = input("Please enter a command! Type help for more information.")
    process_command(command)

if __name__=="__main__":
    name_data = check_cache()
    help_text()
    command = input("Please enter a command! Type help for more information.")
    process_command(command)


conn.close()
