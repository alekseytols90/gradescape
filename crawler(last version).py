import os
import platform
import re, csv
from time import sleep, time
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
from django.conf import settings

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

path = os.getcwd() + '/mygrades/chromedriver'

counter = 0
delayTime = 5


def seven_days():
    a = datetime.date.today()
    day = a.weekday() % 6
    enddate = day + 1 if a.weekday() == 6 else day + 2
    startdate = enddate + 6
    date = a - datetime.timedelta(days=enddate)
    startdate = a - datetime.timedelta(days=startdate)
    return (datetime.datetime(startdate.year, startdate.month, startdate.day, startdate.weekday()),
            datetime.datetime(date.year, date.month, date.day, startdate.weekday()))
# step3 
def get_epiclive_data():
    print("scrap giet epiclive data")
    request_url = "https://www.epicliveservices.com/attendance/?enrollment__course__course_title" \
                  "=&enrollment__student__last_name=&enrollment__student__first_name" \
                  "=&enrollment__student__regular_teacher_email=Charl&attendance_type=&attendance_date= "

    response = {'data':{}}
    items = ['first_name', 'last_name','present', 'absent']

    response['status_code'] = '100'
    response['message'] = "Records Pulled Successfully"
    response['site'] = "Epic Live Attendance"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]


    driver = webdriver.Chrome(executable_path=path, options=options)
    try:
        wait = WebDriverWait(driver, delayTime)
        login_url = "https://www.epicliveservices.com/admin/"

        driver.get(login_url)
        soup = BeautifulSoup(driver, 'html.parser')
        inputs = soup.find('input')['value']
        param = soup.findAll('input')[-2]['value']
        payload = {'username': 'charlotte.wood',
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
            # response = {'data': {}}
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
                                                   'present': epic_id,
                                                   'absent': attendance}
                                                #    'class_title': class_title,
                                                #    'date': date}

                        count += 1


            else:
                response = {'status_code': '204',
                            'message': 'Record Not Found',
                            'site': 'Epic Live'}
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Epic Live Attendance'}
        pass
    return response

# step1 dream bos minutes
def get_dream_box_data():

    items = ['first_name', 'last_name', 'total_time', 'lesson_completed']
    response = {'data': {}}
    response['status_code'] = '100'
    response['message'] = "Records Pulled Successfully"
    response['site'] = "Dreambox Minutes"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]


    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, delayTime)

    try:

        login_url = "https://play.dreambox.com/dashboard/login/"
        a = str(seven_days()[0]).split()[0]
        b = str(seven_days()[1]).split()[0]

        a = "".join(a.split('-'))
        b = "".join(b.split('-'))
        #https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd2019110td20191109&timeframeId=custom&by=week
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
            
            
            for row in rows:
                rec = row.find_all('span', attrs={'class': 'ng-binding'})
                response['data'][count] = {'first_name': rec[1].text.strip(),
                                        'last_name': rec[2].text.strip(),
                                        'total_time': rec[4].text.strip(),
                                        'lesson_completed': rec[8].text.strip()}
                count += 1


        else:
            response = {'status_code': '204', 'message': 'record not found', 'site': 'Dreambox Minutes'}

        driver.close()
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Dream Box Minutes'}
        pass         
    return response
# step 2 
def get_dream_box_lessons_data():
    items = ['first_name', 'last_name', 'total_time', 'lesson_completed']
    response = {'data': {}}
    response['status_code'] = '100'
    response['message'] = "Records Pulled Successfully"
    response['site'] = "Dreambox Lessons"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    
    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, delayTime)

    try:



        login_url = "https://play.dreambox.com/dashboard/login/"
        a = str(seven_days()[0]).split()[0]
        b = str(seven_days()[1]).split()[0]

        a = "".join(a.split('-'))
        b = "".join(b.split('-'))
        #https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd2019110td20191109&timeframeId=custom&by=week
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
            
            
            for row in rows:
                rec = row.find_all('span', attrs={'class': 'ng-binding'})
                response['data'][count] = {'first_name': rec[1].text.strip(),
                                        'last_name': rec[2].text.strip(),
                                        'total_time': rec[4].text.strip(),
                                        'lesson_completed': rec[8].text.strip()}
                count += 1


        else:
            response = {'status_code': '204', 'message': 'record not found', 'site': 'Dream Box Lessons'}
        driver.close()
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Dream Box Lessons'}
        pass         
    return response

#step 5 Reading Eggs
def get_reading_eggs_data():
    response = {'data': {}}

    items = ['first_name', 'last_name', 'lessons_completed']
    response['status_code'] = '100'
    response['title'] = 'Reading Eggs'
    response['message'] = "pulled Successfully"
    if not response['data']:
        response['status_code'] = '204',
        response['message'] = 'Data Could Not Be Pulled'
    response['site'] = "Reading Eggs"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]

    driver = webdriver.Chrome(executable_path=path, options=options)
    

    wait = WebDriverWait(driver, delayTime)
    counter = 0

    try:
        
        def get_data(link, x_path):
            counter = 0
            try:
                print("get data")
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
                                                'lessons_completed': tds[2].text.strip()}
                    counter = counter + 1
            except Exception:
                
                pass
            return response

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
        response = get_data('https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggs/course-progress/reading', '/html/body/div[1]/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[12]/div[0]/tbody')
        driver.close()
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Reading Eggs'}
    return response

#step 6 Reading Eggspress
def get_reading_eggspress_data():
    # counter = 0
    response = {'data': {}}
    items = ['first_name', 'last_name', 'lessons_completed']
    response['status_code'] = '100'
    response['title'] = 'Reading Eggspress'
    response['message'] = "pulled Successfully"
    if not response['data']:
        response['status_code'] = '204',
        response['message'] = 'Data Could Not Be Pulled'
    response['site'] = "Reading Eggspress"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]

    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, delayTime)

    
    try:


        def get_data(link, x_path):
            # response = {'data': {}}
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
                                            'lessons_completed': tds[2].text.strip()}
                counter = counter + 1
            return response

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

        response = get_data('https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggspress/books-read/by-genre', '/html/body/div[1]/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[3]/div[0]/div[0]/tbody')


        driver.close()
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Reading Eggspress'}
        pass

    return response

#step 7 Math Seeds
def get_math_seeds():
    response = {'data': {}}
    items = ['first_name', 'last_name', 'lessons_completed']
    response['status_code'] = '100'
    response['title'] = 'Math Seeds'
    response['message'] = "pulled Successfully"
    if not response['data']:
        response['status_code'] = '204',
        response['message'] = 'Data Could Not Be Pulled'
    response['site'] = "Math Seeds"
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]

    driver = webdriver.Chrome(executable_path=path, options=options)

    wait = WebDriverWait(driver, delayTime)

    try:

        def get_data(link, x_path):
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
                                            'lessons_completed': tds[2].text.strip()}
                counter = counter + 1
            return response

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
        response = get_data('https://app.readingeggs.com/v1/teacher#/maths/reporting/teacher/4807656/mathseeds/course-progress/lessons', '/html/body/div[1]/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[8]/div[0]/tbody')


        driver.close()
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Math Seeds'}
    return response

def get_learning_wood_data():
    if settings.CRAWLER_USE_FAKE_DATA:
        from gradebook.crawler_sample_data import Compass
        return Compass

    login_url = "https://www.thelearningodyssey.com"
    driver = webdriver.Firefox(executable_path=path, options=options)
    # driver = webdriver.Chrome(executable_path=path, options=options)
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
    sleep(5.0)

    # provide visibility to non-popup window by hiding the other (do not close since it breaks the session)
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]
    driver.switch_to_window(window_after)
    driver.set_window_size(0, 0)
    driver.switch_to_window(window_before)

    session_id = driver.get_cookie('SessionID')['value']
    dashboard_url = 'https://www.thelearningodyssey.com/InstructorAdmin/Dashboard.aspx?SessionID={}'.format(session_id)
    driver.get(dashboard_url)
    driver.get('https://www.thelearningodyssey.com/Assignments/CourseManager.aspx')
    sleep(5.0)
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
            full_title_split = title_text.split('-')[1].replace(' GRADE ', '').replace('Semester ','').split(' ')
            response['data'][count] = {'first_name': name.split(",")[1].split()[0],
                                       'last_name': name.split(",")[0],
                                       "score": int(scores[i * 2].get_attribute('innerHTML').replace("%", '').replace('--', '0').replace('-', '')),
                                       'completion': int(completions[i].get_attribute('innerHTML').replace("%", '').replace('-', '0')),
                                       'title': full_title_split[-1],
                                       'subject': full_title_split[1],
                                       'grade_level': full_title_split[0],
                                       }

            count = count + 1
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['site'] = 'Learning'
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    if not response['data']:
        response['message'] = 'The data could not be pulled'
        response['status_code'] = '204'
    driver.close()
    print(response)
    return response

#step 8 MyON by Minutes
def get_my_on_by_minutes():
    if settings.CRAWLER_USE_FAKE_DATA:
        from gradebook.crawler_sample_data import MyONMinutesRead
        return MyONMinutesRead

    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, delayTime)
    # https://clever.com/oauth/authorize?channel=clever&client_id=4c63c1cf623dce82caac&confirmed=true&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state=11cdc4173b1aecbbfb0adbb9a51fa44c6d42a0e52f53408c64532313295efc31&district_id=520a6793a9dd788a46000fdc
    login_url = "https://clever.com/oauth/authorize?channel=clever&client_id" \
                "=4c63c1cf623dce82caac&confirmed=true" \
                "&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state" \
                "=11cdc4173b1aecbbfb0adbb9a51fa44c6d42a0e52f53408c64532313295efc31&district_id" \
                "=520a6793a9dd788a46000fdc"
                
    driver.get(login_url)
    # driver.implicitly_wait(30)
    elem = driver.find_element_by_xpath('//*[@id="react-server-root"]/div/div[2]/div[1]/a[1]')
    elem.click()
    # driver.implicitly_wait(30)

    try:
        wait.until(
            EC.presence_of_element_located((By.ID, "Email"))
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
                EC.presence_of_element_located((By.ID, "Email"))
            )

    except selenium.common.exceptions.TimeoutException:
        print('enter here')

    elem = driver.find_element_by_xpath('//*[@id="Email"]')
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_xpath('//*[@id="next"]')
    elem.click()

    wait.until(
        EC.visibility_of_element_located((By.NAME, "Passwd"))
    )
    elem = driver.find_element_by_name('Passwd')
    elem.send_keys('Principal1234!')
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='signIn']")))

    elm = driver.find_element_by_xpath("//*[@id='signIn']")
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

    sleep(2)
    select = driver.find_element_by_xpath('/html/body/div[2]/main/div[1]/div/div[1]/select/option[text()=\'Time spent reading\']')
    select.click()
    sleep(2)
    wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="student-table"]/div[6]/div[2]/table/tbody'))
    )

    # beware this doesn't always work if 'Time spent reading' selection above fails 
    elem = driver.find_element(By.XPATH, '//*[@id="student-table"]/div[6]/div[2]/table/tbody')

    # sleep(5)
    tml = elem.get_attribute('innerHTML')
    soup = BeautifulSoup(tml, 'html.parser')
    trs = soup.find_all("tr")
    response = {'data': {}}
    count = 0
    for tr in trs:
        previous = tr.find('div', attrs={'class': 'pc-previous-label'}).text.strip().split(' ')
        current = tr.find('div', attrs={'class': 'pc-current-label'}).text.strip().split(' ')
        prevTime = int(previous[-2]) if len(previous) == 2 else 60 + int(previous[-2])
        curTime = int(current[-2]) if len(current) == 2 else 60 + int(current[-2])
        response['data'][count] = {'first_name': tr.find_all('a')[0].text.strip(),
                                   "last_name": tr.find_all('a')[1].text.strip(),
                                   'total': prevTime + curTime
                                   }
        count += 1
    response['status_code'] = '100'
    response['message'] = "pulled successfully"
    response['site'] = 'MyON by Minutes'
    response['title'] = 'MyON by Minutes'
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    if not response['data']:
        response['status_code'] = '115',
        response['message'] = 'data could not be pulled'
    driver.close()
    return response

#step 9 MyON Books Finished
def get_my_on_books_finished():
    if settings.CRAWLER_USE_FAKE_DATA:
        from gradebook.crawler_sample_data import MyONMinutesRead
        return MyONMinutesRead

    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    # https://clever.com/oauth/authorize?channel=clever&client_id=4c63c1cf623dce82caac&confirmed=true&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state=11cdc4173b1aecbbfb0adbb9a51fa44c6d42a0e52f53408c64532313295efc31&district_id=520a6793a9dd788a46000fdc
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
            EC.presence_of_element_located((By.ID, "Email"))
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
                EC.presence_of_element_located((By.ID, "Email"))
            )

    except selenium.common.exceptions.TimeoutException:
        print('enter here')

    elem = driver.find_element_by_xpath('//*[@id="Email"]')
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_xpath('//*[@id="next"]')
    elem.click()

    wait.until(
        EC.visibility_of_element_located((By.NAME, "Passwd"))
    )
    elem = driver.find_element_by_name('Passwd')
    elem.send_keys('Principal1234!')
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='signIn']")))

    elm = driver.find_element_by_xpath("//*[@id='signIn']")
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

    sleep(3)
    select = driver.find_element_by_xpath('/html/body/div[2]/main/div[1]/div/div[1]/select/option[text()=\'Books finished\']')
    select.click()
    sleep(5)
    wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="student-table"]/div[8]/div[2]/table/tbody'))
    )

    # beware this doesn't always work if 'Time spent reading' selection above fails 
    elem = driver.find_element(By.XPATH, '//*[@id="student-table"]/div[8]/div[2]/table/tbody')

    sleep(5)
    tml = elem.get_attribute('innerHTML')
    soup = BeautifulSoup(tml, 'html.parser')
    trs = soup.find_all("tr")
    response = {'data': {}}
    count = 0
    for tr in trs:
        previous = tr.find('div', attrs={'class': 'pc-previous-label'}).text.strip()
        response['data'][count] = {'first_name': tr.find_all('a')[0].text.strip(),
                                   "last_name": tr.find_all('a')[1].text.strip(),
                                   'previous': previous
                                   }
        count += 1
    response['status_code'] = '100'
    response['message'] = "pulled successfully"
    response['title'] = 'MyON Books Finished'
    response['site'] = 'MyON Books Finished'
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

def get_dreambox_minutes():
    print("get_dreambox_minutes")
    # driver = webdriver.Firefox(executable_path=path, options=options)
    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    login_url = "https://play.dreambox.com/dashboard/login/"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]

    a = "".join(a.split('-'))
    b = "".join(b.split('-'))
    #https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd2019110td20191109&timeframeId=custom&by=week
    request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771" \
                  "&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd" + a + "td" + b + \
                  "&timeframeId=custom&by=week "
    driver.get(login_url)
    driver.implicitly_wait(10)
    elem = driver.find_element_by_name("email_address")
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_name("password")
    elem.send_keys("Principal1234!")

    # Pass capcha
    def write_stat(loops, time):
        with open('stat.csv', 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([loops, time])  	 
	
    def check_exists_by_xpath(xpath):
        try:
            driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
        
    def wait_between(a,b):
        rand=uniform(a, b) 
        sleep(rand)
    
    def dimention(driver): 
        d = int(driver.find_element_by_xpath('//div[@id="rc-imageselect-target"]/table').get_attribute("class")[-1])
        return d if d else 3  # dimention is 3 by default
        
    # ***** main procedure to identify and submit picture solution	
    def solve_images(driver):	
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID ,"rc-imageselect-target"))
            ) 		
        dim = dimention(driver)	
        # ****************** check if there is a clicked tile ******************
        if check_exists_by_xpath('//div[@id="rc-imageselect-target"]/table/tbody/tr/td[@class="rc-imageselect-tileselected"]'):
            rand2 = 0
        else:  
            rand2 = 1 

        # wait before click on tiles 	
        wait_between(0.5, 1.0)		 
        # ****************** click on a tile ****************** 
        tile1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH ,   '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(randint(1, dim), randint(1, dim )))) 
            )   
        tile1.click() 
        if (rand2):
            try:
                driver.find_element_by_xpath('//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(randint(1, dim), randint(1, dim))).click()
            except NoSuchElementException:          		
                print('\n\r No Such Element Exception for finding 2nd tile')
    
        
        #****************** click on submit buttion ****************** 
        driver.find_element_by_id("recaptcha-verify-button").click()

    start = time()	 
    url='...'
    # driver = webdriver.Firefox()
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.get(url)

    mainWin = driver.current_window_handle  

    # move the driver to the first iFrame 
    driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[0])

    # *************  locate CheckBox  **************
    CheckBox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID ,"recaptcha-anchor"))
            ) 

    # *************  click CheckBox  ***************
    wait_between(0.5, 0.7)  
    # making click on captcha CheckBox 
    CheckBox.click() 
    
    #***************** back to main window **************************************
    driver.switch_to_window(mainWin)  

    wait_between(2.0, 2.5) 

    # ************ switch to the second iframe by tag name ******************
    driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[1])  
    i=1
    while i<130:
        print('\n\r{0}-th loop'.format(i))
        # ******** check if checkbox is checked at the 1st frame ***********
        driver.switch_to_window(mainWin)   
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME , 'iframe'))
            )  
        wait_between(1.0, 2.0)
        if check_exists_by_xpath('//span[@aria-checked="true"]'): 
            # import winsound
            # winsound.Beep(400,1500)
            write_stat(i, round(time()-start) - 1 ) # saving results into stat file
            break 
            
        driver.switch_to_window(mainWin)   
        # ********** To the second frame to solve pictures *************
        wait_between(0.3, 1.5) 
        driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[1]) 
        solve_images(driver)
        i=i+1








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
    #step 10 Success Maker
def get_success_maker():
    print("scraping www.thelearningodyssey.com")
    # driver = webdriver.Firefox(executable_path=path, options=options)
    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, 30)
    login_url = "https://epicyouth0140.smhost.net/lms/sm.view?headless=1&action=home"
    # a = str(seven_days()[0]).split()[0]
    # b = str(seven_days()[1]).split()[0]

    # a = "".join(a.split('-'))
    # b = "".join(b.split('-'))
    #https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd2019110td20191109&timeframeId=custom&by=week
    # request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771" \
    #               "&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd" + a + "td" + b + \
    #               "&timeframeId=custom&by=week "
    driver.get(login_url)
    main_page = driver.current_window_handle 
    driver.implicitly_wait(10)
    elem = driver.find_element_by_id("user")
    elem.send_keys("charlotte.wood")
    elem = driver.find_element_by_id("login")
    elem.send_keys("Pa55word")
    elem = driver.find_element_by_class_name("loginBtn")
    elem.click()

    sleep(10)

    # provide visibility to non-popup window by hiding the other (do not close since it breaks the session)
    # window_before = driver.window_handles[0]
    # window_after = driver.window_handles[1]
    # driver.switch_to_window(window_after)
    # driver.set_window_size(0, 0)
    # driver.switch_to_window(window_before)

    # session_id = driver.get_cookie('SessionID')['value']
    # dashboard_url = 'https://www.thelearningodyssey.com/InstructorAdmin/Dashboard.aspx?SessionID={}'.format(session_id)
    # driver.get(dashboard_url)
    # driver.get('https://www.thelearningodyssey.com/Assignments/CourseManager.aspx')
    sleep(5.0)
    # wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[2]/div/div/div/div/table/tbody/tr[2]/td/div")))
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div/div/div[5]/div/div[1]/div/div/div/div[1]/div/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/div")))

    sleep(2)



    # elem = driver.find_element_by_xpath('/html/body/div[6]/div[2]/div/div/div/div/table/tbody/tr[2]/td/div]').click()
    driver.find_elements_by_xpath('/html/body/div[3]/div[2]/div/div/div/div[5]/div/div[1]/div/div/div/div[1]/div/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/div').click()
    
    # elem1 = elem.find_element_by_xpath("//table[@id = isc_8Atable]/tbody/tr[2]/td/div").click()

    driver.find_element_by_xpath("//input[@id=isc_AG]").click()

    sleep(5)

    curdate = seven_days()

    startDate = curdate[0].strftime('%m/%d/%Y')
    endDate = curdate[0].strftime('%m/%d/%Y')

    driver.find_element_by_xpath("//input[@id=isc_AP]").send_keys(startDate)
    driver.find_element_by_xpath("//input[@id=isc_Au]").send_keys(endDate)

    driver.find_element_by_xpath("//div[@id = 'isc_96']/table/tbody/tr/td").click()

    sleep(10)

    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]
    driver.switch_to_window(window_after)    

    doc = driver.find_elements_by_xpath('//div[@id = "Document"]/div/div/table/tbody/tr/td/table/tbody')
    response = {'data':{}}
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table_body = soup.find('tbody')
    trs = table_body.find_all('tr')
    for tr in range(9, len(trs)):
        tds = trs[tr].find_all('td')
        full_name = tds[1].find_element('div').text.strip().split(' ')
        time_spent_str = tds[6].find_element('div').text.strip().split(":")
        time_spent = int(time_spent_str[0]) * 60 + int(time_spent_str[1])
        response['data'][counter] = {'first_name': full_name[0],
                                        'last_name': full_name[1],
                                        'time_spent': time_spent}
                                    #  'attendance': int(tds[3].text.strip().replace('-', '0')),
                                    #  'average_score': int(tds[4].text.strip().replace('-', '0').replace('%', ''))}
        counter = counter + 1



    # elem.click()
    # wait.until(EC.presence_of_element_located((By.ID, "Tr1")))
    # like = [item.get_attribute('onclick').split("(")[1].split(')')[0] for item in
    #         driver.find_elements_by_class_name('gbIcon')]

    # response = {'data': {}}
    # count = 0
    # for x in range(0, len(like)):
    #     url = "https://www.thelearningodyssey.com/Assignments/Gradebook.aspx?courseid=" + like[x]
    #     driver.get(url)
    #     wait.until(
    #         EC.presence_of_element_located((By.ID, "dialog"))
    #     )
    #     # kk = driver.find_element_by_id('titleSubstitution')
    #     # if driver.find_element_by_id('titleSubstitution') == null:
    #     #     continue
    #     dialog = driver.find_element_by_id('dialog')
    #     completions = dialog.find_elements_by_class_name('done')
    #     if len(completions) <= 1:
    #         continue
    #     scores = driver.find_elements_by_class_name('score')
    #     names = driver.find_elements_by_class_name('studentName')
    #     title_text = driver.find_element_by_id('titleSubstitution').text
    #     for i in range(1, len(completions)):
    #         name = names[i - 1].get_attribute('innerHTML')
    #         full_title_split = title_text.split('-')[1].replace(' GRADE ', '').replace('Semester ','').split(' ')
    #         response['data'][count] = {'first_name': name.split(",")[1].split()[0],
    #                                    'last_name': name.split(",")[0],
    #                                    'course_name':title_text,
    #                                    "course_grade": int(scores[i * 2].get_attribute('innerHTML').replace("%", '').replace('--', '0').replace('-', '')),
    #                                 #    'completion': int(completions[i].get_attribute('innerHTML').replace("%", '').replace('-', '0')),
    #                                 #    'title': full_title_split[-1],
    #                                 #    'subject': full_title_split[1],
    #                                 #    'grade_level': full_title_split[0],
    #                                    }

    #         count = count + 1
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['title'] = 'Success Maker'
    response['site'] = 'Success Maker'
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]
    if not response['data']:
        response['message'] = 'The data could not be pulled'
        response['status_code'] = '204'
    driver.quit()
    # print(response)
    return response

#step 4 Compass
def get_compass():
    response = {'data': {}}
    items = ['first_name', 'last_name', 'course_name','course_grade']
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['site'] = 'Compass'
    current_date = seven_days()
    response['date_start'] = current_date[0]
    response['date_end'] = current_date[1]

    print("scraping www.thelearningodyssey.com")
    driver = webdriver.Firefox(executable_path=path, options=options)
    # driver = webdriver.Chrome(executable_path=path, options=options)
    
    try:
        

        wait = WebDriverWait(driver, delayTime)
        login_url = "https://www.thelearningodyssey.com/"
        driver.get(login_url)
        main_page = driver.current_window_handle 
        driver.implicitly_wait(10)
        elem = driver.find_element_by_id("UserNameEntry")
        elem.send_keys("charlotte.wood")
        elem = driver.find_element_by_id("UserPasswordEntry")
        elem.send_keys("Pa55word")
        elem = driver.find_element_by_name("SchoolNameEntry")
        elem.clear()
        elem.send_keys("EPIC")
        elem = driver.find_element_by_id("cmdLoginButton")
        elem.click()

        sleep(3)

        # provide visibility to non-popup window by hiding the other (do not close since it breaks the session)
        window_before = driver.window_handles[0]
        window_after = driver.window_handles[1]
        print("windows pass")
        print(len(driver.window_handles))
        driver.switch_to_window(window_after)
        driver.set_window_size(0, 0)
        driver.switch_to_window(window_before)

        session_id = driver.get_cookie('SessionID')['value']
        dashboard_url = 'https://www.thelearningodyssey.com/InstructorAdmin/Dashboard.aspx?SessionID={}'.format(session_id)
        driver.get(dashboard_url)
        driver.get('https://www.thelearningodyssey.com/Assignments/CourseManager.aspx')
        sleep(5.0)
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
            dialog = driver.find_element_by_id('dialog')
            completions = dialog.find_elements_by_class_name('done')
            if len(completions) <= 1:
                continue
            scores = driver.find_elements_by_class_name('score')
            names = driver.find_elements_by_class_name('studentName')
            title_text = driver.find_element_by_id('titleSubstitution').text
            for i in range(1, len(completions)):
                name = names[i - 1].get_attribute('innerHTML')
                full_title_split = title_text.split('-')[1].replace(' GRADE ', '').replace('Semester ','').split(' ')
                response['data'][count] = {'first_name': name.split(",")[1].split()[0],
                                        'last_name': name.split(",")[0],
                                        'course_name':title_text,
                                        "course_grade": int(scores[i * 2].get_attribute('innerHTML').replace("%", '').replace('--', '0').replace('-', '')),
                                        }

                count = count + 1
        if not response['data']:
            response['message'] = 'The data could not be pulled'
            response['status_code'] = '204'
        driver.quit()
    except Exception:
        response = {'status_code': '204', 'message': 'record not found', 'site': 'Compass'}
        pass
    return response
    
    
def get_homework_help():
    path = ''

    if(platform.system() == 'Darwin'):
        path = path_mac
    elif (platform.system() == 'Linux'):
        path = path_linux
    print("scraping www.thelearningodyssey.com")
    # driver = webdriver.Firefox(executable_path=path, options=options)
    driver = webdriver.Chrome(executable_path=path, options=options)
    wait = WebDriverWait(driver, delayTime)
    login_url = "http://homeworkhelp.epiccharterschools.org/"
    # a = str(seven_days()[0]).split()[0]
    # b = str(seven_days()[1]).split()[0]

    # a = "".join(a.split('-'))
    # b = "".join(b.split('-'))
    #https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd2019110td20191109&timeframeId=custom&by=week
    # request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771" \
    #               "&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd" + a + "td" + b + \
    #               "&timeframeId=custom&by=week "
    driver.get(login_url)
    main_page = driver.current_window_handle 
    # driver.implicitly_wait(10)
    elem = driver.find_element_by_id("USER_NAME")
    elem.send_keys("charlotte.wood")
    elem = driver.find_element_by_id("Password")
    elem.send_keys("Pa55word")
    elem = driver.find_element_by_name("SchoolNameEntry")
    elem.clear()
    elem.send_keys("EPIC")
    elem = driver.find_element_by_id("log")
    elem.click()

    # sleep(10)

    # provide visibility to non-popup window by hiding the other (do not close since it breaks the session)
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]
    print("windows pass")
    print(len(driver.window_handles))
    driver.switch_to_window(window_after)
    driver.set_window_size(0, 0)
    driver.switch_to_window(window_before)

    session_id = driver.get_cookie('SessionID')['value']
    dashboard_url = 'https://www.thelearningodyssey.com/InstructorAdmin/Dashboard.aspx?SessionID={}'.format(session_id)
    driver.get(dashboard_url)
    driver.get('https://www.thelearningodyssey.com/Assignments/CourseManager.aspx')
    # sleep(5.0)
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
        # kk = driver.find_element_by_id('titleSubstitution')
        # if driver.find_element_by_id('titleSubstitution') == null:
        #     continue
        dialog = driver.find_element_by_id('dialog')
        completions = dialog.find_elements_by_class_name('done')
        if len(completions) <= 1:
            continue
        scores = driver.find_elements_by_class_name('score')
        names = driver.find_elements_by_class_name('studentName')
        title_text = driver.find_element_by_id('titleSubstitution').text
        for i in range(1, len(completions)):
            name = names[i - 1].get_attribute('innerHTML')
            full_title_split = title_text.split('-')[1].replace(' GRADE ', '').replace('Semester ','').split(' ')
            response['data'][count] = {'first_name': name.split(",")[1].split()[0],
                                       'last_name': name.split(",")[0],
                                       'course_name':title_text,
                                       "course_grade": int(scores[i * 2].get_attribute('innerHTML').replace("%", '').replace('--', '0').replace('-', '')),
                                    #    'completion': int(completions[i].get_attribute('innerHTML').replace("%", '').replace('-', '0')),
                                    #    'title': full_title_split[-1],
                                    #    'subject': full_title_split[1],
                                    #    'grade_level': full_title_split[0],
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
    driver.quit()
    # print(response)
    return response

if __name__ == "__main__":
    print(seven_days())
    pass
