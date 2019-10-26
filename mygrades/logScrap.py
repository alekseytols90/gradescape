import os
import requests
import time
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
path = os.getcwd() + '/mygrades/geckodriver'
driver = webdriver.Firefox(executable_path=path, options=options)

# start chrome browser
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_driver_path = os.path.join(os.getcwd(), "mygrades/chromedriver")
print(chrome_driver_path)
time.sleep(10)
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver_path)
chrome_wait = WebDriverWait(driver, 3)

wait = WebDriverWait(driver, 10)
def seven_days():
    a = datetime.date.today()
    day = a.weekday() % 6
    enddate = day + 1 if a.weekday() == 6 else day + 2
    startdate = enddate + 6
    # endate
    date = a - datetime.timedelta(days=enddate)

    startdate = a - datetime.timedelta(days=startdate)

    return (datetime.datetime(startdate.year, startdate.month, startdate.day),
            datetime.datetime(date.year, date.month, date.day))


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
        out = "Surname,LastName,Presence,Date\n"
        count = 0
        response = {'data': {}}
        if len(a) > 0:

            for attend in a:
                rec = attend.strip().split('\n')
                surname = rec[0]
                lastname = rec[1].strip('-').strip()
                presence = rec[2].split('-')[0].strip()
                date = rec[3].split('-')[1]
                date = date.split()
                date = date[0][:3] + " " + date[1] + " " + date[2]
                rec[4].strip('held on').strip()
                dt = datetime.datetime.strptime(date, '%b %d, %Y')
                if (dt >= seven_days()[0] and dt <= seven_days()[1]):
                    out += "{},{},{},\"{}\"\n".format(surname, lastname, presence, date)
                    response['data'][count] = {'first_name': lastname,
                                               'last_name': surname,
                                               'presence': presence,
                                               'date': date}

                    count += 1
            response['status_code'] = '100'
            response['message'] = "Records pulled successfully"
            response['site'] = "clives"

        else:
            response = {'status_code': '115',
                        'message': 'record not found',
                        'site': 'clives'}
        return response


def get_dream_box_data():
    login_url = "https://play.dreambox.com/dashboard/login/"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]

    a = "".join(a.split('-'))
    b = "".join(b.split('-'))
    request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771" \
                  "&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd" + a + "td" + b + \
                  "&timeframeId=custom&by=week "
    driver.get(login_url)
    driver.implicitly_wait(30)
    elem = driver.find_element_by_name("email_address")
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_name("password")
    elem.send_keys("Teacher1")
    elem = driver.find_element_by_name("dashboard")
    elem.click()
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "dbl-icon"))
    )
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
            fname = rec[1].text.strip()
            lname = rec[2].text.strip()
            t_time = rec[4].text.strip()
            lesson_com = rec[8].text.strip()
            response['data'][count] = {'first_name': fname, 'last_name': lname, 'total_time': t_time,
                                       'lesson_completed': lesson_com}
            count += 1
        response['status_code'] = '100'
        response['message'] = "Records pulled successfully"
        response['site'] = "dreambox"

    else:
        response = {'status_code': '115', 'message': 'record not found', 'site': 'dreambox'}
    return response


def get_readingeggs_data():
    login_url = "https://sso.readingeggs.com/login"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]
    request_url1 = "https://app.readingeggs.com/v1/teacher#/reading/" \
                   "reporting/teacher/4807656/reading-eggs/assessment" \
                   "-scores?dateRange=custom-range%3A" + a + "%3A" + b
    request_url2 = "https://app.readingeggs.com/v1/teacher#/reading/" \
                   "reporting/teacher/4807656/reading-eggspress/quiz" \
                   "-scores?dateRange=custom-range%3A" + a + "%3A" + b
    driver.get(login_url)
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
    driver.get(request_url2)
    wait.until(
        EC.presence_of_element_located((By.ID, "ember73"))
    )
    elem = driver.find_elements_by_xpath("//div[@class='flex-container']/table[1]")
    count = 0
    response = {'data': {'rec_1': {}, 'rec_2': {}}}
    if len(elem) > 0:

        elem = driver.find_element_by_xpath("//div[@class='flex-container']/table[1]")
        bo = elem.get_attribute('innerHTML')

        soup = BeautifulSoup(bo, 'html.parser')
        tbody = soup.find('tbody')
        trs = tbody.find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            fname = tds[0].text.strip()
            lname = tds[1].text.strip()
            quiz = tds[2].text.strip()
            att = tds[3].text.strip()
            avg_sc = tds[4].text.strip()
            response['data']['rec_1'][count] = {'fist_name': fname,
                                                'last_name': lname,
                                                'quiz': quiz, 'attendance': att,
                                                'average_score': avg_sc}
        response['status_code'] = '100'
        response['message'] = "Records 1 pulled successfully"
        response['site'] = "readingEggs"
    else:
        response = {'status_code': '115', 'message': 'record 1 not found', 'site': 'readingEggs'}

    driver.get(request_url1)
    wait.until(
        EC.presence_of_element_located((By.ID, "ember73"))
    )

    elem = driver.find_elements_by_xpath("//div[@class='assessment-scores-table']/table[1]")
    if len(elem) > 0:
        elem = driver.find_element_by_xpath("//div[@class='assessment-scores-table']/table[1]")
        bo = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(bo, 'html.parser')
        tbody = soup.find('tbody')
        trs = tbody.find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            fname = tds[0].text.strip()
            lname = tds[1].text.strip()
            quiz = tds[2].text.strip()
            att = tds[3].text.strip()
            avg_sc = tds[4].text.strip()
            response['data']['rec_2'][count] = {'fist_name': fname,
                                                'last_name': lname,
                                                'quiz': quiz, 'attendance': att,
                                                'average_score': avg_sc}
        response['status_code'] = '100'
        response['message'] += "Records 2 pulled successfully"
        response['table_type'] = "readingEggs"

    else:

        print("record not found for the last seven days")
        response = {'status_code': response['status_code'] + '/115',
                    'message': response['message'] + '/record not found'}
    return response


def get_learning_wood_data():
    login_url = "https://www.thelearningodyssey.com"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]
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

    driver.implicitly_wait(30)
    han = driver.window_handles
    driver.switch_to.window(han[1])
    driver.implicitly_wait(30)
    try:
        wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "frame"))
        )
    except selenium.common.exceptions.TimeoutException:
        print('timed out')
        get_learning_wood_data()


    ele = driver.find_element_by_name('CLOMain')
    popup_url = ele.get_attribute('src')
    try:
        driver.implicitly_wait(30)
        driver.get(popup_url)
        driver.implicitly_wait(30)
        elem = driver.find_element_by_xpath('/html/body/form/div[3]/div[3]/div[2]/div[1]/a[3]')
        elem.click()
        wait.until(
            EC.presence_of_element_located((By.ID, "btnCP"))
        )
    except selenium.common.exceptions.UnexpectedAlertPresentException:
        print('UnexpectedAlertPresentException Occurred')
        driver.get("https://www.thelearningodyssey.com/Assignments/as_AssignmentHome.aspx")
    wait.until(
        EC.presence_of_element_located((By.ID, "btnCP"))
    )

    elem = driver.find_element_by_xpath('/html/body/form/div[3]/div[4]/div/div/div/table/tbody/tr/td[1]/a[2]')
    elem.click()

    wait.until(
        EC.presence_of_element_located((By.ID, "CourseManagerTree1t5"))
    )
    elem = driver.find_element_by_id('CourseManagerTree1t5')
    elem.click()

    wait.until(
        EC.presence_of_element_located((By.ID, "Tr1"))
    )

    like = [item.get_attribute('onclick').split("(")[1].split(')')[0] for item in
            driver.find_elements_by_class_name('gbIcon')]

    for x in range(0, len(like)):
        url = "https://www.thelearningodyssey.com/Assignments/Gradebook.aspx?courseid=" + like[x]
        driver.get(url)
        wait.until(
            EC.presence_of_element_located((By.ID, "dialog"))
        )
        elems = driver.find_elements_by_id("Tr1")

        if len(elems) > 0:
            response = {'data': {}}
            count = 0
            completions = driver.find_elements_by_class_name('done')
            scores = driver.find_elements_by_class_name('score')
            names = driver.find_elements_by_class_name('studentName')
            for i in range(1, len(completions)):
                comp = completions[i].get_attribute('innerHTML').replace("%", '')
                name = names[i - 1].get_attribute('innerHTML')
                score = scores[i * 2].get_attribute('innerHTML')
                name_split = name.split(",")
                fname = name_split[0]
                lname = name_split[1].split()[0]
                response['data'][count] = {'first_name': fname,
                                           'last_name': lname,
                                           "score": score, 'completion': comp}
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['site'] = 'learningWood'
    if response['data']:
        return response
    else:
        response = {'status_code': '115', 'message': 'The data could not be pulled', 'site': 'learningWood'}
        return response


def get_clever_data():
    login_url = "https://clever.com/oauth/authorize?channel=clever&client_id" \
                "=4c63c1cf623dce82caac&confirmed=true" \
                "&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state" \
                "=11cdc4173b1aecbbfb0adbb9a51fa44c6d42a0e52f53408c64532313295efc31&district_id" \
                "=520a6793a9dd788a46000fdc "
    driver.get(login_url)
    driver.implicitly_wait(30)
    elem = driver.find_element_by_xpath('//*[@id="react-server-root"]/div/div[2]/div[1]/a[1]')
    elem.click()
    wait.until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    elem = driver.find_element_by_xpath('//*[@id="identifierId"]')
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span')
    elem.click()

    wait.until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )
    elem = driver.find_element_by_name('password')
    elem.send_keys('Principal!')
    wait.until(
        EC.visibility_of_element_located((By.XPATH, "//span[text()='Next']"))
    )
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))

    elm = driver.find_element_by_xpath("//span[text()='Next']")
    elm.click()

    wait.until(
        EC.presence_of_element_located((By.ID, "__MAIN_APP__"))
    )
    elem = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div/a')
    elem.click()
    driver.implicitly_wait(15)
    driver.switch_to.window(driver.window_handles[1])
    driver.implicitly_wait(15)
    wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div[2]/div/div[8]/div[2]/table/tbody"))
    )
    elem = driver.find_element_by_xpath('/html/body/div[2]/main/div[2]/div[2]/div/div[8]/div[2]/table/tbody')
    tml = elem.get_attribute('innerHTML')

    soup = BeautifulSoup(tml, 'html.parser')

    trs = soup.find_all("tr")
    response = {'data': {}}
    count = 0
    for tr in trs:
        fname = tr.find_all('a')[0].text.strip()
        lname = tr.find_all('a')[1].text.strip()
        previous = tr.find('div', attrs={'class': 'pc-previous-label'}).text.strip()
        response['data'][count] = {'first_name': fname, "last_name": lname, 'previous': previous}
        response['status_code'] = '100'
        response['message'] = "pulled successfully"
        response['site'] = 'clever'
    if response['data']:
        return response
    else:
        return {'status_code': '115', 'message': 'data could not be pulled', 'site': 'clever'}


if __name__ == "__main__":
    path = os.getcwd() + '/geckodriver'
    print(path)
    driver = webdriver.Firefox(executable_path=path, options=options)
    # get_epiclive_data()
    # get_readingeggs_data()
    # get_dream_box_data()
    # get_clever_data()
    # get_learning_wood_data()
