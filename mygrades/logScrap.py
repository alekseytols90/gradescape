#import requests
#from requests_html import HTMLSession,AsyncHTMLSession
import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium
from selenium.webdriver.firefox.options import Options

def seven_days():
    a = datetime.date.today()
    day = a.weekday() % 6
    enddate =day+1 if a.weekday() ==6 else day+2
    startdate =enddate+6
    #endate
    date = a - datetime.timedelta(days=enddate)

    startdate = a - datetime.timedelta(days=startdate)
   
    return (datetime.datetime(startdate.year,startdate.month,startdate.day),datetime.datetime(date.year,date.month,date.day))

def clives():
    #<form action="/admin/login/?next=/admin/" method="post" id="login-form"><input type="hidden" name="csrfmiddlewaretoken" value="WdOU8YI8hMO80jgCvp25PwoCpufBIHyyS9LkczjQqOeqddi3THzzDZLxvJsdNTB8">
    
    login_url = "https://www.epicliveservices.com/admin/login/?next=/admin/"
    request_url = "https://www.epicliveservices.com/attendance/?enrollment__course__course_title=&enrollment__student__last_name=&enrollment__student__first_name=&enrollment__student__regular_teacher_email=Charl&attendance_type=&attendance_date="
   
    r = requests.get('https://www.epicliveservices.com/admin/login')
    print(r.cookies)
    content = r.content
    soup = BeautifulSoup(content,'html.parser')
    inputs = soup.find('input')['value']
    param = soup.findAll('input')[-2]['value']
    payload = {'username':'charlottewood','password':"Pa55word!",'csrfmiddlewaretoken':inputs,"next":param}
    print(inputs)
    print(param)
    with requests.Session() as sess:
        post = sess.post("https://www.epicliveservices.com/admin/login/?next=/admin/",data=payload,
        headers={'referer':'https://www.epicliveservices.com/admin/login','X-CSRF-Token':inputs,},cookies=r.cookies)
        #https://www.epicliveservices.com/admin/
        p = sess.get(request_url,headers={'referer':'https://www.epicliveservices.com/admin/','X-CSRF-Token':inputs,},cookies=r.cookies)
        soup = BeautifulSoup(p.content,'html.parser')
        #open('clives.txt',mode="a+").write(p.content.decode())
        divs = soup.find_all('div',attrs={'class':['col-80', 'col-md-100', 'mb-1', 'mx-auto']})
        a = [div.find_all('div',attrs={'class':'card-body'})[0].text for div in divs]
        #output = open("clives.csv",mode="w")
        out = "Surname,LastName,Presence,Date\n"
        count=0
        response={'data':{}}
        if len(a) > 0:
            
            for attend in a:
                rec = attend.strip().split('\n')
                surname = rec[0]
                lastname = rec[1].strip('-').strip()
                presence = rec[2].split('-')[0].strip()
                date = rec[3].split('-')[1]
                date = date.split()
                date = date[0][:3]+" "+date[1]+" "+date[2]
                subject = rec[4].strip('held on').strip()
                dt = datetime.datetime.strptime(date,'%b %d, %Y')
                if (dt>=seven_days()[0] and dt<=seven_days()[1]):
                    out += "{},{},{},\"{}\"\n".format(surname,lastname,presence,date)
                    response['data'][count] ={'first_name':lastname,'last_name':surname,'presence':presence,'date':date}
           
                    count+=1
            response['status_code'] = '100'
            response['message'] = "Records pulled successfully"
            response['site'] = "clives"

        else:
            response = {'status_code':'115','message':'record not found','site':'clives'}
       
        return response
            #output.write(out)
        #else:


def dreambox():
    login_url = "https://play.dreambox.com/dashboard/login/"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]
  
    a= "".join(a.split('-'))
    b= "".join(b.split('-'))
    #request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=7d&by=day"
    request_url = "https://insight.dreambox.com/district/19207/classroom/1850338?schoolId=47805&teacherId=12317771&breadcrumbs=d,sc,t,c&pane=overview&order=asc&sort=first_name&timeframe=fd"+a+"td"+b+"&timeframeId=custom&by=week"
    print(request_url)
        #post = sess.post(login_url,data=payload,
        #headers={'referer':'https://play.dreambox.com/dashboard/login/',"User-Agent":'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'})
        #print(post.text)
        #r = sess.get(request_url)
        #print(r)
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    #driver = webdriver.Firefox()
    driver.get(login_url)
    elem = driver.find_element_by_name("email_address")
   
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_name("password")
    elem.send_keys("Teacher1")
    elem = driver.find_element_by_name("dashboard")
    elem.click()
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dbl-icon"))
    )
    driver.get(request_url)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Click Here"))
    )
    elem = driver.find_elements_by_xpath("//div[@class='ng-scope']/section/table[1]")
    
    if len(elem) > 0:
        elem = driver.find_element_by_xpath("//div[@class='ng-scope']/section/table[1]") 
        bo = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(bo,'html.parser')
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        count=0
        response={'data':{}}
        for row in rows:
            rec = row.find_all('span',attrs={'class':'ng-binding'})
            fname = rec[1].text.strip()
            lname = rec[2].text.strip()
            t_time = rec[4].text.strip()
            lesson_com = rec[8].text.strip()
            response['data'][count] ={'first_name':fname,'last_name':lname,'total_time':t_time,'lesson_completed':lesson_com}
            count+=1
        response['status_code'] = '100'
        response['message'] = "Records pulled successfully"
        response['site'] = "dreambox"

    else:
        response = {'status_code':'115','message':'record not found','site':'dreambox'}
    return response

def readingEggs():    

    login_url = "https://sso.readingeggs.com/login"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]
    request_url1 = "https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggs/assessment-scores?dateRange=custom-range%3A"+a+"%3A"+b
    request_url2="https://app.readingeggs.com/v1/teacher#/reading/reporting/teacher/4807656/reading-eggspress/quiz-scores?dateRange=custom-range%3A"+a+"%3A"+b
    print(request_url1)
    print(request_url2)
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    #driver = webdriver.Firefox()
    
    driver.get(login_url)
    elem = driver.find_element_by_name("username")
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_name("password")
    elem.send_keys("Principal1")
    elem = driver.find_element_by_name("commit")
    elem.click()
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "sidebar"))
    )
    #request one
    driver.get(request_url2)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "ember73"))
    )
    elem = driver.find_elements_by_xpath("//div[@class='flex-container']/table[1]")
    count = 0
    response ={}
    response['data']={'rec_1':{},'rec_2':{}}
    if len(elem) > 0:
        
        elem = driver.find_element_by_xpath("//div[@class='flex-container']/table[1]")
        bo = elem.get_attribute('innerHTML')
        

        soup = BeautifulSoup(bo,'html.parser')
        tbody = soup.find('tbody')
        trs =tbody.find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            fname =tds[0].text.strip()
            lname = tds[1].text.strip()
            quiz = tds[2].text.strip()
            att = tds[3].text.strip()
            avg_sc = tds[4].text.strip()
            print(fname,lname,quiz,att,avg_sc)
            response['data']['rec_1'][count] = {'fist_name':fname,'last_name':lname,'quiz':quiz,'attendance':att,'average_score':avg_sc}
        response['status_code'] = '100'
        response['message'] = "Records 1 pulled successfully"
        response['site'] = "readingEggs"

        
    else:
        print("records not found")
        response = {'status_code':'115','message':'record 1 not found','site':'readingEggs'}
    
    #request tow
    driver.get(request_url1)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "ember73"))
    )
   
    elem = driver.find_elements_by_xpath("//div[@class='assessment-scores-table']/table[1]")
    if len(elem) > 0:
        elem = driver.find_element_by_xpath("//div[@class='assessment-scores-table']/table[1]")
        bo = elem.get_attribute('innerHTML')
        soup = BeautifulSoup(bo,'html.parser')
        tbody = soup.find('tbody')
        trs =tbody.find_all('tr')

        for tr in trs:
            tds = tr.find_all('td')
            fname =tds[0].text.strip()
            lname = tds[1].text.strip()
            quiz = tds[2].text.strip()
            att = tds[3].text.strip()
            avg_sc = tds[4].text.strip()
            print(fname,lname,quiz,att,avg_sc)
            response['data']['rec_2'][count] = {'fist_name':fname,'last_name':lname,'quiz':quiz,'attendance':att,'average_score':avg_sc}
        response['status_code'] = '100'
        response['message'] += "Records 2 pulled successfully"
        response['table_type'] = "readingEggs"

    else:
       
        print("record not found for the last seven days")
        response = {'status_code': response['status_code']+'/115','message':response['message']+'/record not found'}   
    return response
def learningWood():
    #UserNameEntry
    #UserPasswordEntry
    #SchoolNameEntry
    #cmdLoginButton
    payload={
        'username':'charlotte.wood',
        'password':'Pa55word',
        'school':'EPIC'
    }
    login_url = "https://www.thelearningodyssey.com"
    a = str(seven_days()[0]).split()[0]
    b = str(seven_days()[1]).split()[0]
    options = Options()
    options.headless = True
    driver = webdriver.Firefox()
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
    han3 = driver.current_window_handle
    print(han)
    driver.switch_to.window(han[1])
    driver.implicitly_wait(30)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "frame"))
    )
    ele = driver.find_element_by_name('CLOMain')
    popup_url = ele.get_attribute('src')
    try:
        driver.implicitly_wait(30)
        driver.get(popup_url)
        driver.implicitly_wait(30)
        #print(driver.page_source)
        elem = driver.find_element_by_xpath('/html/body/form/div[3]/div[3]/div[2]/div[1]/a[3]')
        elem.click()
        element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "btnCP"))
        )
    except selenium.common.exceptions.UnexpectedAlertPresentException:
        driver.get("https://www.thelearningodyssey.com/Assignments/as_AssignmentHome.aspx")
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "btnCP"))
        )
    
    elem = driver.find_element_by_xpath('/html/body/form/div[3]/div[4]/div/div/div/table/tbody/tr/td[1]/a[2]')
    elem.click()
    
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "CourseManagerTree1t5"))
    )
    elem = driver.find_element_by_id('CourseManagerTree1t5')
    elem.click()
    
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "Tr1"))
    )

    like = [item.get_attribute('onclick').split("(")[1].split(')')[0] for item in driver.find_elements_by_class_name('gbIcon')]

    for x in range(0,len(like)):
        url = "https://www.thelearningodyssey.com/Assignments/Gradebook.aspx?courseid="+like[x]
        driver.get(url)
        element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "dialog"))
        )
        elems = driver.find_elements_by_id("Tr1")
        
        if len(elems) > 0:
            response={'data':{}}
            count = 0
            completions = driver.find_elements_by_class_name('done')
            scores = driver.find_elements_by_class_name('score')
            names = driver.find_elements_by_class_name('studentName')
            for i in range(1,len(completions)):
                comp = completions[i].get_attribute('innerHTML').replace("%",'')
                name = names[i-1].get_attribute('innerHTML')
                score = scores[i*2].get_attribute('innerHTML')
                name_split = name.split(",")
                fname = name_split[0]
                lname = name_split[1].split()[0]
                print(fname,lname,score,comp)
                response['data'][count] = {'first_name':fname,'last_name':lname,"score":score,'completion':comp}
    response['status_code'] = '100'
    response['message'] = 'pulled successfully'
    response['site'] = 'learningWood'
        # else:
        #     print("class %s has no record yet"%(like[x]))
        #     response={'status_code':'115','message':"class has no record yet",'site':'learningWood'}
    if response['data']:

        return response
    else:
        return {'status_code':'115','message': 'The data could not be pulled','site':'learningWood'}


   
def clever():
    login_url = "https://clever.com/oauth/authorize?channel=clever&client_id=4c63c1cf623dce82caac&confirmed=true&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state=11cdc4173b1aecbbfb0adbb9a51fa44c6d42a0e52f53408c64532313295efc31&district_id=520a6793a9dd788a46000fdc"
    #username
    #password
    #charlotte.wood@epiccharterschools.org
    #Principal!
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(login_url)
    #PageContent--content
    elem = driver.find_element_by_xpath('//*[@id="react-server-root"]/div/div[2]/div[1]/a[1]')
    elem.click()
    #
    # element = WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located((By.ID, "view_container"))
    # )
    # elem = driver.find_element_by_xpath('//*[@id="view_container"]/div/div/div[2]/div/div/div/form/span/section/div/div/div/div/ul/li[3]/div/div/div[2]')
    # elem.click()
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    elem = driver.find_element_by_xpath('//*[@id="identifierId"]')
    elem.send_keys("charlotte.wood@epiccharterschools.org")
    elem = driver.find_element_by_xpath('//*[@id="identifierNext"]/span/span')
    elem.click()

    #//*[@id="password"]/div[1]/div/div[1]/input
    element = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )
    elem = driver.find_element_by_name('password')
    
    #driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input')
    elem.send_keys('Principal!')
    element = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.XPATH, "//span[text()='Next']"))
    )
    element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH,"//span[text()='Next']")))
    
    elm = driver.find_element_by_xpath("//span[text()='Next']") 
    elm.click()
    
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "__MAIN_APP__"))
    )
    elem = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/div/a')
    elem.click()
    driver.implicitly_wait(15)
    driver.switch_to.window(driver.window_handles[1])
    element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div[2]/div/div[8]/div[2]/table/tbody"))
        )
    elem = driver.find_element_by_xpath('/html/body/div[2]/main/div[2]/div[2]/div/div[8]/div[2]/table/tbody') 
    tml = elem.get_attribute('innerHTML')
    
    soup = BeautifulSoup(tml,'html.parser')

    trs = soup.find_all("tr")
    response ={'data':{}}
    count=0
    for tr in trs:
        fname =tr.find_all('a')[0].text.strip()
        lname = tr.find_all('a')[1].text.strip()
        previous = tr.find('div',attrs={'class':'pc-previous-label'}).text.strip()
        #print(fname,lname,previous)
        response['data'][count] = {'first_name':fname,"last_name":lname,'previous':previous}
        response['status_code'] = '100'
        response['message'] = "pulled successfully"
        response['site'] = 'clever'
    if response['data']:
        return response
    else:
        return {'status_code':'115','message':'data could not be pulled','site':'clever'}




    #//*[@id="__MAIN_APP__"]/div/div[1]/div/h1






if __name__ == "__main__":
    #driver = webdriver.Firefox(executable_path="[Firefox driver path]")
    #readingEggs()
    #clives()
    #dreambox()
    learningWood()
    #clever()
    #print(str(seven_days()[0]))