import os
import time
import requests
import selenium
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
path = os.getcwd() + '/mygrades/geckodriver'


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
            response['message'] = "Records pulled successfully"
            response['site'] = "Epic Live"

        else:
            response = {'status_code': '115',
                        'message': 'record not found',
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
        response['message'] = "Records pulled successfully"
        response['site'] = "Dream Box"

    else:
        response = {'status_code': '115', 'message': 'record not found', 'site': 'Dream Box'}
    driver.close()
    return response


def get_reading_eggs_data():
    driver = webdriver.Firefox(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
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
    count = 0
    response = {'data': {}}
    elem = driver.find_elements_by_xpath("//div[@class='flex-container']/table[1]")
    if len(elem) > 0:
        elem = driver.find_element_by_xpath("//div[@class='flex-container']/table[1]")
        bo = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(bo, 'html.parser')
        tbody = soup.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            response['data'][count] = {'first_name': tds[0].text.strip(),
                                       'last_name': tds[1].text.strip(),
                                       'quiz_score': tds[2].text.strip(),
                                       'attendance': tds[3].text.strip(),
                                       'average_score': tds[4].text.strip()}
            count += 1
        response['status_code'] = '100'
        response['message'] = " Records 1 pulled successfully"
        response['site'] = "Reading Eggs"
    else:
        response['status_code'] = '115'
        response['message'] = " Records 1 not pulled successfully"
        response['site'] = "Reading Eggs"

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
            response['data'][count] = {'fist_name': tds[0].text.strip(),
                                       'last_name': tds[1].text.strip(),
                                       'quiz': tds[2].text.strip(),
                                       'attendance': tds[3].text.strip(),
                                       'average_score': tds[4].text.strip()}
            count += 1
        response['status_code'] = '100'
        response['message'] += " Records 2 pulled successfully"
        response['table_type'] = "Reading Eggs"
    else:
        response['message'] += " Records 2 not pulled successfully"
        response['site'] = "Reading Eggs"
    driver.close()
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

    for x in range(0, len(like)):
        url = "https://www.thelearningodyssey.com/Assignments/Gradebook.aspx?courseid=" + like[x]
        driver.get(url)
        wait.until(
            EC.presence_of_element_located((By.ID, "dialog"))
        )
        elems = driver.find_elements_by_id("Tr1")

        if len(elems) > 0:
            response = {'data': {}}
            counter = 0
            completions = driver.find_elements_by_class_name('done')
            scores = driver.find_elements_by_class_name('score')
            names = driver.find_elements_by_class_name('studentName')
            for i in range(1, len(completions)):
                comp = completions[i].get_attribute('innerHTML').replace("%", '')
                name = names[i - 1].get_attribute('innerHTML')
                score = scores[i * 2].get_attribute('innerHTML')
                name_split = name.split(",")
                first_name = name_split[0]
                last_name = name_split[1].split()[0]
                print(first_name, last_name, score, comp)
                print('counter => ', counter)
                response['data'][counter] = {'first_name': first_name,
                                             'last_name': last_name,
                                             "score": score,
                                             'completion': comp
                                             }
                counter += 1
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['site'] = 'Learning Wood'
    if not response['data']:
        response['message'] = 'The data could not be pulled'
        response['status_code'] = '115'
    driver.close()
    return response


def get_clever_data():
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
    driver.get(
        'https://clever.com/oauth/authorize?channel=clever-portal&client_id=e9883f835c1c58894763&confirmed=true'
        '&district_id=520a6793a9dd788a46000fdc&redirect_uri=https%3A%2F%2Fwww.myon.com%2Fapi%2Foauth%2Fsso.html'
        '%3Ainstantlogin&response_type=code')

    wait.until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div[1]/div/div[1]/select')))
    select = driver.find_element_by_xpath(
        '/html/body/div[2]/main/div[1]/div/div[1]/select/option[text()=\'Time spent reading\']')
    select.click()
    driver.implicitly_wait(30)
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        "div.fixed-header-table-ctl:nth-child(8) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(2)"))
    )
    elem = driver.find_element(By.CSS_SELECTOR,
                               'div.fixed-header-table-ctl:nth-child(8) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(2)')
    tml = elem.get_attribute('innerHTML')
    soup = BeautifulSoup(tml, 'html.parser')
    trs = soup.find_all("tr")
    response = {'data': {}}
    count = 0
    for tr in trs:
        response['data'][count] = {'first_name': tr.find_all('a')[0].text.strip(),
                                   "last_name": tr.find_all('a')[1].text.strip(),
                                   'previous': tr.find('div', attrs={'class': 'pc-previous-label'}).text.strip(),
                                   'current': tr.find('div', attrs={'class': 'pc-current-label'}).text.strip()}
        count += 1
    response['status_code'] = '100'
    response['message'] = "pulled successfully"
    response['site'] = 'Clever'
    if not response['data']:
        response['status_code'] = '115',
        response['message'] = 'data could not be pulled'
    driver.close()
    return response


if __name__ == "__main__":
    # get_epiclive_data()
    # get_readingeggs_data()
    # get_dream_box_data()
    get_clever_data()
    # get_learning_wood_data()
