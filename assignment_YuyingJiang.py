import requests
import sys
from bs4 import BeautifulSoup
from datetime import timedelta, date, tzinfo, datetime

class SimpleUTC(tzinfo):
    """
    used to transform date format
    """
    def tzname(self,**kwargs):
        return "UTC"
    def utcoffset(self, dt):
        return timedelta(0)

class SpaceFlight2019:

    def __init__(self, URL, start_dt, end_dt):
        self.count_dict = {}
        self.URL = URL
        self.start_dt = start_dt
        self.end_dt = end_dt

    def count_from_table(self):
        """
        read html, count the number of distinct lanuches each date and store in 'self.count_dict.'
        """
        page = requests.get(self.URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find("table", class_="wikitable")
        rows = table.find_all("tr")
        date_to_be_updated = None
        status_flag = False
        # status_flag is used to check whether there is at least one satified payload.
        # date_to_be_updated is used to record the date of current payload being read, and if the launch is added,
        # date_to_be_updated will be changed into None for avoiding counting each lanuch multiple times.
        for tr in rows:
            column = 0
            tds = tr.find_all("td")
            for td in tds:
                if td.find(class_="nowrap") and column == 0:
                    date_to_be_updated = str(tr.find(class_="nowrap").contents[0])
                    status_flag = False
                if td.text.find("Operational") == 0 or td.text.find("Successful") == 0 or td.text.find("En Route") == 0:
                    status_flag = True

                column += 1
            if status_flag and date_to_be_updated:
                if date_to_be_updated in self.count_dict:
                    self.count_dict[date_to_be_updated] += 1
                else:
                    self.count_dict[date_to_be_updated] = 1
                date_to_be_updated = None

    def write_file(self):
        """
        write the all dates in 2019 and corresponding number of lanuches from 'self.count_dict' into csv file.

        """

        month_list = ["January", "February", "March", "April", "May", "June", "July", "August",
                      "September", "October", "November", "December"]
        # used to find month letter by month number
        date_list = []
        # store all dates in 2019
        for n in range(int((self.end_dt - self.start_dt).days)+1):
            date_list.append(self.start_dt + timedelta(n))
        with open("SpaceFlight.csv", "w") as f:
            f.write("date, value" + "\n")
            for dt in date_list:
                year = dt.year
                month_letter = month_list[dt.month - 1]
                month = dt.month
                day = dt.day
                date_time_str = str(year) + "-" + str(month) + "-" + str(day)
                date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d')
                date_time_obj = date_time_obj.replace(microsecond=0, tzinfo=SimpleUTC()).isoformat()
                # if the date in self.count_dict, then get the number of launches,
                # otherwise, the number of launches is zero.
                if (str(day) + " " + str(month_letter)) in self.count_dict:
                    number_of_launches = self.count_dict[str(day) + " " + str(month_letter)]
                    f.write(str(date_time_obj) + ", " + str(number_of_launches) + "\n")
                else:
                    f.write((str(date_time_obj) + ", " + "0" + "\n"))



if __name__ == "__main__":
    if len(sys.argv) == 1:
        year = 2019
    else:
        year = sys.argv[1]
    URL = 'https://en.wikipedia.org/wiki/{}_in_spaceflight'.format(year)
    start_dt = date(int(year), 1, 1)
    end_dt = date(int(year), 12, 31)
    SpaceFlight2019_tool = SpaceFlight2019(URL, start_dt, end_dt)
    SpaceFlight2019_tool.count_from_table()
    SpaceFlight2019_tool.write_file()