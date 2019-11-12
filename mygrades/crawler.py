import os
import re
import time
import requests
import selenium
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = False
path = os.getcwd() + '/mygrades/geckodriver'

counter = 0


def seven_days():
    a = datetime.date.today()
    day = a.weekday() % 6
    enddate = day + 1 if a.weekday() == 6 else day + 2
    startdate = enddate + 6
    date = a - datetime.timedelta(days=enddate)
    startdate = a - datetime.timedelta(days=startdate)
    return (datetime.datetime(startdate.year, startdate.month, startdate.day, startdate.weekday()),
            datetime.datetime(date.year, date.month, date.day, startdate.weekday()))


def get_epiclive_data():
    request_url = "https://www.epicliveservices.com/attendance/?enrollment__course__course_title" \
                  "=&enrollment__student__last_name=&enrollment__student__first_name" \
                  "=&enrollment__student__regular_teacher_email=Charl&attendance_type=&attendance_date= "

    r = requests.get("https://www.epicliveservices.com/admin/login")
    content = r.content
    soup = BeautifulSoup(content, 'html.parser')
    inputs = soup.find('input')['value']
    param = soup.findAll('input')[-2]['value']
    payload = {'username': 'charlottewood',
               'password': "Pa55word!",
               'csrfmiddlewaretoken': inputs, "next": param}
    with requests.Session() as sess:
        sess.post('https://www.epicliveservices.com/admin/login/?next=/admin/', data=payload,
                  headers={'referer': 'https://www.epicliveservices.com/admin/login',
                           'X-CSRF-Token': inputs, },
                  cookies=r.cookies)
        p = sess.get(request_url,
                     headers={'referer': 'https://www.epicliveservices.com/admin/',
                              'X-CSRF-Token': inputs, },
                     cookies=r.cookies)
        soup = BeautifulSoup(p.content, 'html.parser')
        divs = soup.find_all('div', attrs={'class': ['col-80', 'col-md-100', 'mb-1', 'mx-auto']})
        a = [div.find_all('div', attrs={'class': 'card-body'})[0].text for div in divs]
        out = "FirstName,LastName, EpicID,Attendance,ClassTitle,Date\n"
        count = 0
        response = {'data': {}}
        if len(a) > 0:

            for attend in a:
                rec = attend.strip().split('\n')
                first_name = rec[0]
                last_name = rec[1].strip('-').strip()
                epic_id = rec[2].split('-')[0].strip()
                attendance = rec[3].split('-')[0].strip()
                class_title = rec[4].strip().replace(' held on',
                                                     '').replace('(can NOT say CAS anywhere on it)',
                                                                 '').replace('CX REQUIRED', '')
                date = rec[3].split('-')[1]
                date = date.split()
                date = date[0][:3] + " " + date[1] + " " + date[2]
                rec[4].strip('held on').strip()
                dt = datetime.datetime.strptime(date, '%b %d, %Y')
                if seven_days()[0] <= dt <= seven_days()[1]:
                    out += "{},{},{},{},{},\"{}\"\n".format(first_name, last_name, epic_id,
                                                            attendance, class_title, date)
                    response['data'][count] = {'first_name': first_name,
                                               'last_name': last_name,
                                               'epic_id': epic_id,
                                               'attendance': attendance,
                                               'class_title': class_title,
                                               'date': date}

                    count += 1
            response['status_code'] = '100'
            response['message'] = "Records Pulled Successfully"
            response['site'] = "Epic Live Attendance"
            current_date = seven_days()
            response['date_start'] = current_date[0]
            response['date_end'] = current_date[1]

        else:
            response = {'status_code': '204',
                        'message': 'Record Not Found',
                        'site': 'Epic Live'}

        return response


def get_dream_box_data():
    driver = webdriver.Firefox(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    login_url = "https://play.dreambox.com/dashboard/login/"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]

    a = "".join(a.split('-'))
    b = "".join(b.split('-'))
    request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771" \
                  "&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd" + a + "td" + b + \
                  "&timeframeId=custom&by=week "
    driver.get(login_url)
    driver.implicitly_wait(10)
    elem = driver.find_element_by_name("email_address")
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_name("password")
    elem.send_keys("Teacher1")
    elem = driver.find_element_by_name("dashboard")
    elem.click()
    try:
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "dbl-icon"))
        )
    except selenium.common.exceptions.TimeoutException:
        pass
    driver.get(request_url)
    wait.until(
        EC.presence_of_element_located((By.LINK_TEXT, "Click Here"))
    )
    elem = driver.find_elements_by_xpath("//div[@class='ng-scope']/section/table[1]")

    if len(elem) > 0:
        elem = driver.find_element_by_xpath("//div[@class='ng-scope']/section/table[1]")
        bo = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(bo, 'html.parser')
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        count = 0
        response = {'data': {}}
        for row in rows:
            rec = row.find_all('span', attrs={'class': 'ng-binding'})
            response['data'][count] = {'first_name': rec[1].text.strip(),
                                       'last_name': rec[2].text.strip(),
                                       'total_time': rec[4].text.strip(),
                                       'lesson_completed': rec[8].text.strip()}
            count += 1
        response['status_code'] = '100'
        response['message'] = "Records Pulled Successfully"
        response['site'] = "Dreambox"
        current_date = seven_days()
        response['date_start'] = current_date[0]
        response['date_end'] = current_date[1]

    else:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Dream Box'}
    driver.close()
    return response


def get_reading_eggs_data():
    driver = webdriver.Firefox(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    counter = 0
    response = {'data': {}}

    def get_data(link, x_path):
        response = {'data': {}}
        counter = 0
        driver.get(link)
        try:
            wait.until(
            EC.presence_of_element_located((By.XPATH, x_path))
            )
        except TimeoutException:
            pass
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_body = soup.find('tbody')
        trs = table_body.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            response['data'][counter] = {'first_name': tds[0].text.strip(),
                                         'last_name': tds[1].text.strip(),
                                         'quiz_score': int(tds[2].text.strip().replace('-', '0')),
                                         'attendance': int(tds[3].text.strip().replace('-', '0')),
                                         'average_score': int(tds[4].text.strip().replace('-', '0').replace('%', ''))}
            counter = counter + 1
        return response

    def get_difference(egg_1, egg_2):
        global counter
        for i, j in zip(egg_2['data'].values(), egg_1['data'].values()):
            d3 = {}
            for k, v in i.items():
                d3[k] = abs(v - j.get(k, 0)) if isinstance(v, int) else j.get(k, 0)
                response['data'][counter] = d3
            counter += 1

    driver.get("https://sso.readingeggs.com/login")
    driver.implicitly_wait(10)
    elem = driver.find_element_by_name("username")
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_name("password")
    elem.send_keys("Principal1")
    elem = driver.find_element_by_name("commit")
    elem.click()
    wait.until(
        EC.presence_of_element_located((By.ID, "sidebar"))
    )

    egg_last_7_days = get_data("https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggs" \
                               "/assessment-scores?dateRange=named-period%3Alast-7-days",
                               '/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div/div/div/div[3]/div[2]/div/div/div/table/tbody')
    egg_this_year = get_data("https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggs" \
                             "/assessment-scores?dateRange=named-period%3Athis-year",
                             '/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div/div/div/div[3]/div[4]/div/div/div/table/tbody')
    egg_press_last_7_days = get_data("https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading" \
                                     "-eggspress/quiz-scores?dateRange=named-period%3Alast-7-days",
                                     '/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div/div/div/div[3]/div['
                                     '4]/div/div/table/tbody')
    egg_press_this_year = get_data(
        "https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggspress" \
        "/quiz-scores?dateRange=named-period%3Athis-year",
        '/html/body/div[2]/div[2]/div[2]/div[2]/div/div/div/div/div/div[3]/div['
        '4]/div/div/table/tbody')

    get_difference(egg_this_year, egg_last_7_days)
    get_difference(egg_press_this_year, egg_press_last_7_days)

    response['status_code'] = '100'
    response['message'] = " Records  Pulled Successfully"
    if not response['data']:
        response['status_code'] = '204',
        response['message'] = 'Data Could Not Be Pulled'
    response['site'] = "Reading Eggs"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    driver.close()
    print(response)
    return response


def get_learning_wood_data():
    login_url = "https://www.thelearningodyssey.com"
    driver = webdriver.Firefox(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    x = 'https://www.thelearningodyssey.com/InstructorAdmin/Dashboard.aspx?SessionID=75475339FFBE4B049F30C89AF326247F'
    driver.get(login_url)
    elem = driver.find_element_by_id("UserNameEntry")
    elem.send_keys("charlotte.wood")
    elem = driver.find_element_by_id("UserPasswordEntry")
    elem.send_keys("Pa55word")
    elem = driver.find_element_by_id("SchoolNameEntry")
    elem.clear()
    elem.send_keys("EPIC")
    elem = driver.find_element_by_id("cmdLoginButton")
    elem.click()
    time.sleep(5.0)
    session_id = driver.get_cookie('SessionID')['value']
    dashboard_url = 'https://www.thelearningodyssey.com/InstructorAdmin/Dashboard.aspx?SessionID={}'.format(session_id)
    driver.get(dashboard_url)
    driver.get('https://www.thelearningodyssey.com/Assignments/CourseManager.aspx')
    time.sleep(5.0)
    elem = driver.find_element_by_xpath('//*[@id="CourseManagerTree1t5"]')
    elem.click()
    wait.until(EC.presence_of_element_located((By.ID, "Tr1")))
    like = [item.get_attribute('onclick').split("(")[1].split(')')[0] for item in
            driver.find_elements_by_class_name('gbIcon')]

    response = {'data': {}}
    count = 0
    for x in range(0, len(like)):
        url = "https://www.thelearningodyssey.com/Assignments/Gradebook.aspx?courseid=" + like[x]
        driver.get(url)
        wait.until(
            EC.presence_of_element_located((By.ID, "dialog"))
        )
        completions = driver.find_elements_by_class_name('done')
        scores = driver.find_elements_by_class_name('score')
        names = driver.find_elements_by_class_name('studentName')
        title_text = driver.find_element_by_id('titleSubstitution').text
        for i in range(1, len(completions)):
            name = names[i - 1].get_attribute('innerHTML')
            response['data'][count] = {'first_name': name.split(",")[1].split()[0],
                                       'last_name': name.split(",")[0],
                                       "score": int(scores[i * 2].get_attribute('innerHTML').replace("%", '').replace('--', '0').replace('-', '')),
                                       'completion': int(completions[i].get_attribute('innerHTML').replace("%", '').replace('-', '0')),
                                       'title': title_text.split('-')[1].replace(' GRADE ', '').replace('Semester ',
                                                                                                        '').split(' ')[
                                           -1]
                                       }

            count = count + 1
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['site'] = 'Compass'
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    if not response['data']:
        response['message'] = 'The data could not be pulled'
        response['status_code'] = '204'
    driver.close()
    print(response)
    return response


def get_my_on_data():
    driver = webdriver.Firefox(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    login_url = "https://clever.com/oauth/authorize?channel=clever&client_id" \
                "=4c63c1cf623dce82caac&confirmed=true" \
                "&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state" \
                "=11cdc4173b1aecbbfb0adbb9a51fa44c6d42a0e52f53408c64532313295efc31&district_id" \
                "=520a6793a9dd788a46000fdc"
    driver.get(login_url)
    driver.implicitly_wait(30)
    elem = driver.find_element_by_xpath('//*[@id="react-server-root"]/div/div[2]/div[1]/a[1]')
    elem.click()
    driver.implicitly_wait(30)

    try:
        wait.until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )

        # force google to english regardless of server location
        # check for url has hl=en if not, replace hl=[a-z]{,2} to hl=en in url, refresh page and wait until again (just once)
        if 'hl=en' not in driver.current_url:
            if "hl=" in driver.current_url: # replace if exists
                new_url = re.sub(r'hl=[a-z]+', 'hl=en', driver.current_url) 
            else:
                new_url = driver.current_url + "&hl=en"

            driver.get(new_url)
            wait.until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )

    except selenium.common.exceptions.TimeoutException:
        print('enter here')

    elem = driver.find_element_by_xpath('//*[@id="identifierId"]')
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span')
    elem.click()

    wait.until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )
    elem = driver.find_element_by_name('password')
    elem.send_keys('Principal1234!')
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))

    elm = driver.find_element_by_xpath("//span[text()='Next']")
    elm.click()

    wait.until(
        EC.presence_of_element_located((By.ID, "__MAIN_APP__"))
    )
    driver.get(
        'https://clever.com/oauth/authorize?channel=clever-portal&client_id=e9883f835c1c58894763&confirmed=true'
        '&district_id=520a6793a9dd788a46000fdc&redirect_uri=https%3A%2F%2Fwww.myon.com%2Fapi%2Foauth%2Fsso.html'
        '%3Ainstantlogin&response_type=code')

    wait.until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div[1]/div/div[1]/select')))
    select = driver.find_element_by_xpath(
        '/html/body/div[2]/main/div[1]/div/div[1]/select/option[text()=\'Time spent reading\']')
    select.click()
    time.sleep(5)
    wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="student-table"]/div[6]/div[2]/table/tbody'))
    )
    # this doesn't always work since div 6 might be on 8, that might be some crawler protection
    #elem = driver.find_element(By.XPATH,
    #                           '//*[@id="student-table"]/div[6]/div[2]/table/tbody')

    elem = driver.find_element(By.XPATH, '//*[@id="student-table"]/div[not(contains(@style,"display: none;"))]/div[2]/table/tbody')

    time.sleep(5)
    tml = elem.get_attribute('innerHTML')
    soup = BeautifulSoup(tml, 'html.parser')
    trs = soup.find_all("tr")
    response = {'data': {}}
    count = 0
    for tr in trs:
        previous = tr.find('div', attrs={'class': 'pc-previous-label'}).text.strip().split(' ')
        current = tr.find('div', attrs={'class': 'pc-current-label'}).text.strip().split(' ')
        response['data'][count] = {'first_name': tr.find_all('a')[0].text.strip(),
                                   "last_name": tr.find_all('a')[1].text.strip(),
                                   'previous': int(previous[-2]) if len(previous) == 2 else 60 + int(previous[-2]),
                                   'current': int(current[-2]) if len(current) == 2 else 60 + int(current[-2])
                                   }
        count += 1
    response['status_code'] = '100'
    response['message'] = "pulled successfully"
    response['site'] = 'MyON'
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    if not response['data']:
        response['status_code'] = '115',
        response['message'] = 'data could not be pulled'
    driver.close()
    print(response)
    return response


def get_all_data():
    a = get_epiclive_data()
    b = get_dream_box_data()
    c = get_reading_eggs_data()
    # d = get_my_on_data()
    d = {}
    e = get_learning_wood_data()
    response = {'data': (a, b, c, d, e), 'site': "all"}
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    return response


if __name__ == "__main__":
    print(seven_days())
    pass
