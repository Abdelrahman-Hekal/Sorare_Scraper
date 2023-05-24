from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import time
import csv
import os
from datetime import datetime
import pandas as pd
import unidecode
import warnings
from pathlib import Path
import shutil
from datetime import datetime
import random
warnings.filterwarnings('ignore')


def initialize_bot():

    class Spoofer(object):

        def __init__(self):
            self.userAgent = self.get()

        def get(self):
            ua = ('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36'.format(random.randint(90, 105)))

            return ua

    class DriverOptions(object):

        def __init__(self):

            self.options = uc.ChromeOptions()
            #self.options.add_argument('--log-level=3')
            #self.options.add_argument('--start-maximized')
            #self.options.add_argument('--disable-dev-shm-usage')
            #self.options.add_argument("--incognito")
            #self.options.add_argument('--disable-popup-blocking')
            #self.options.add_argument("--headless")
            self.helperSpoofer = Spoofer()
            #self.seleniumwire_options = {}
           
            # random user agent
            #self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36'.format(random.randint(90, 105)))
            self.options.page_load_strategy = 'eager'
           
            # Create empty profile for non Windows OS
            if os.name != 'nt':
                if os.path.isdir('./profile11'):
                    shutil.rmtree('./profile11')
                os.mkdir('./profile11')
                Path('./profile11/First Run').touch()
                self.options.add_argument('--user-data-dir=./profile11/')
   
    class WebDriver(DriverOptions):

        def __init__(self):
            DriverOptions.__init__(self)
            self.driver_instance = self.get_driver()

        def get_driver(self):

            #webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
            # uc Chrome driver
            #driver = uc.Chrome(options=self.options, seleniumwire_options=self.seleniumwire_options)
            driver = uc.Chrome(options=self.options)
            driver.set_page_load_timeout(60)
            driver.command_executor.set_timeout(60)

            return driver

    driver= WebDriver()
    driverinstance = driver.driver_instance
    driverinstance.maximize_window()
    return driverinstance

def login_sorare(driver, name, pwd):

    URL1 = "https://sorare.com/?action=signin"
    # navigating to the website link
    driver.get(URL1)
    time.sleep(4)
    iframe = wait(driver, 30).until(EC.presence_of_element_located((By.ID, "wallet")))
    driver.switch_to.frame(iframe)
    time.sleep(4)
    # signing in 
    username = wait(driver, 30).until(EC.presence_of_element_located((By.ID, "Email")))
    password = wait(driver, 30).until(EC.presence_of_element_located((By.ID, "Password")))
    username.send_keys(name)
    time.sleep(2)
    password.send_keys(pwd)
    time.sleep(2)
    button = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
    driver.execute_script("arguments[0].click();", button)
    time.sleep(5)


def login_soraredata(driver):

    URL1 = "https://www.soraredata.com/login"
    # navigating to the website link
    driver.get(URL1)
    time.sleep(3)
    buttons = wait(driver, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'button')))
    for button in buttons:
        if 'Login with your Sorare account' in button.text:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
            break

    # signing in 
    buttons = wait(driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))
    for button in buttons:
        if button.text == 'Authorise':
            driver.execute_script("arguments[0].click();", button)
            break

    time.sleep(5)


def get_players(driver):

    URL = 'https://www.soraredata.com/rankings'
    driver.get(URL)
    time.sleep(3)
    
    # applying number of games filter to 0
    node = wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='rc-slider-handle']")))
    ActionChains(driver).drag_and_drop_by_offset(node,-175,0).perform()

    buttons = wait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))
    for button in buttons:
        if button.text == 'Filter':
            driver.execute_script("arguments[0].click();", button)
            break
    time.sleep(10)

    print('scrolling for the full players list ...')
    # scrolling down to the bottom of the site to view the full list
    for _ in range(95):
        htmlelement= wait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        htmlelement.send_keys(Keys.END)
        time.sleep(1)

    print('Done scrolling for the full players list!')
    print('Collecting the players web pages ...')
    # getting the full player's list
    players = []
    divs = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class = 'bg-white flex flex-row rounded-xl p-2 md:space-x-2 space-x-4 hover:shadow-custom overflow-y-auto md:overflow-y-hidden no-scroll-bar w-full']")))
    time.sleep(5)
    links = []

    for elem in divs:
        a = wait(elem, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        name = wait(a, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'p')))[0].text
        name = unidecode.unidecode(name)
        players.append(name)
        link = a.get_attribute('href')
        links.append(link)

    return players, links

def scrape_soraredata(driver, player, link):
    
    data = {}
    driver.get(link)
    time.sleep(3)
    wait60 = wait(driver, 5)
    info_div = wait60.until(EC.presence_of_element_located((By.XPATH,"//div[@class = 'text-center xl:text-left text-white space-y-1 z-20']")))

    name = wait(info_div, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME,"p")))[0].text
    name = unidecode.unidecode(name)
    
    try:
        info = wait(info_div, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME,"p")))[-1].text
        club = info.split('(')[0].strip()
        club = unidecode.unidecode(club)
        if len(club) == 0:
            club = "NA"
    except:
        club = 'NA'    
        
    try:
        info = wait(info_div, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME,"p")))[-1].text
        league = info[info.find('(') + 1: info.find(')')]
        league = unidecode.unidecode(league)
        if len(league) == 0:
            league = "NA"       
    except:
        league = 'NA'   
  
    try:
        pos1 = wait60.until(EC.presence_of_element_located((By.XPATH,"//div[@class='flex flex-row space-x-2 bg-white text-sm self-center justify-center font-semibold p-2 rounded w-28 max-w-28 text-center']"))).text
        if len(pos1) == 0 or pos1 == 'none':
            pos1 = "NA"       
    except:
        status = 'NA'

    try:
        pos2_div = wait60.until(EC.presence_of_element_located((By.XPATH,"//div[@class='w-7/12 py-2 space-y-2 self-center overflow-hidden text-ellipsis']")))
        pos2 = wait(pos2_div, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME,"p")))[1].text
        if len(pos2) == 0 or pos2 == 'none':
            pos2 = "NA"       
    except:
        pos2 = 'NA'    

    try:
        p = wait(info_div, 30).until(EC.presence_of_element_located((By.XPATH,"//span[@class='font-semibold']"))).text
        date = p.split('(')[0].replace('Born on', "").strip()
        digits = date.split(' ')
        digits[1] = digits[1][:-2]
        date = ' '.join(digits)
        date_obj = datetime.strptime(date, '%b %d %Y')
        date = str(date_obj.month) + '/' + str(date_obj.day) + '/' + str(date_obj.year)
        if len(date) == 0:
            date = "NA"       
    except:
        date = 'NA'
    
    try:
        status = wait60.until(EC.presence_of_element_located((By.XPATH,"//div[@class='bg-white text-sm self-center font-semibold p-2 rounded w-24 text-center']"))).text
        if len(status) == 0:
            status = "NA"       
    except:
        status = 'NA'
    
    data[name] = [status]
    data[name].append(link)

    tags = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='flex flex-col space-y-1 mx-auto items-center']")))
    for tag in tags:
        score = wait(tag, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))[0].text
        data[name].append(score)

    if len(tags) < 3:
        n = 3 - len(tags)
        for i in range(n):
            data[name].append('NA')

    # scraping editions data
    values_divs = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='flex flex-col space-y-1 py-1 mx-4 xl:mx-4 w-6/12']")))
    for elem in values_divs:
        values = wait(elem, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
        data[name].append(values.copy()[0].text.replace('Ξ', '').strip())
        data[name].append(values.copy()[1].text.replace('Ξ', '').strip())
        data[name].append(values.copy()[3].text.replace('Ξ', '').strip())
        data[name].append(values.copy()[4].text.replace('Ξ', '').strip())

    for _ in range(10):
        try:
            # clicking on "SO5 scores" tab
            nav = wait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'nav')))
            buttons = wait(nav, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'button')))
            for button in buttons:
                if button.text == 'SO5 Scores':
                    driver.execute_script("arguments[0].click();", button)
                    break
            time.sleep(2)
            # clicking on "All" button
            buttons = wait(driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'button')))
            for button in buttons:
                if button.text == 'All':
                    driver.execute_script("arguments[0].click();", button)
                    break
            time.sleep(4)

            table = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table[@class='z-0 min-h-48 overflow-hidden border-collapse rounded-t-lg rounded-b-lg table-fixed w-full bg-white whitespace-no-wrap mx-auto']")))
            scores = wait(table, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))[1:]

            time.sleep(1)
            if len(scores) == 0:
                driver.refresh()
                time.sleep(5)
                continue
            for row in scores:
                # All-around scores
                #score = wait(row, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'td')))[-2].text
                # Total scores
                score = wait(row, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'td')))[-1].text
                data[name].append(score)
            break
        except:
            continue

    return data, club, league, pos1, pos2, date, name
        
def scrape_sorare(driver, player, club, league, pos1, pos2, date):
    
    data = {}
    pos1 = unidecode.unidecode(pos1)    
    pos2 = unidecode.unidecode(pos2)    
    league = unidecode.unidecode(league)
    club = unidecode.unidecode(club)
    data[player] = [player, date, pos1, pos2, club, league]

    return data

def initialize_output():

    # removing the previous output file
    path = os.getcwd()
    files = os.listdir(path)
    for file in files:
        if 'Scraped_Data' in file:
            os.remove(file)

    header = ['Player Name', 'Date of Birth', 'Position', 'Position Two', 'Players Club', 'League','Playing Status','Link To Player Profile on SorareData', 'L5', 'L15', 'L40', 'Limited 3 Day Avg', 'Limited 7 Day Avg', 'Limited 1 Month Avg', 'Limited Best Offer', 'Rare 3 Day Avg', 'Rare 7 Day Avg', 'Rare 1 Month Avg', 'Rare Best Offer']

    for i in range(175):
        header.append(str(i+1))

    filename = 'Scraped_Data_{}.csv'.format(datetime.now().strftime("%d_%m_%Y_%H_%M"))

    if path.find('/') != -1:
        output = path + "/" + filename
    else:
        output = path + "\\" + filename

    with open(output, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

    return output

def resume_output():

    # removing the previous output file
    found = False
    path = os.getcwd()
    files = os.listdir(path)
    for file in files:
        if 'Scraped_Data' in file:
            found = True
            if path.find('/') != -1:
                output = path + "/" + file
            else:
                output = path + "\\" + file

    if found:
        return output
    else:
        print('No valid output file is found!')
        exit()

def processing_data(sorare, soraredata, output, player):
    
    row = []
    for value in sorare[player]:
        row.append(value)    
    for value in soraredata[player]:
        row.append(value)

    with open(output, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)
        
        
def skip_output(player, output):
    
    row = [player]
    for i in range(26):
        row.append('Skipped')
    with open(output, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')

    
# Website login credentials
name1 = ""
pwd1 = ""

os.system("color")
COLOR = {"HEADER": "\033[95m", "BLUE": "\033[94m", "GREEN": "\033[92m",
            "RED": "\033[91m", "ENDC": "\033[0m", "YELLOW" :'\033[33m'}


if __name__ == '__main__':

    mode = ''
    while True:
        mode = input('Do you wish to start a new scraping session or resume the current one? \n 1: New Session \n 2: Resume Current Session \n')
        try:
            mode = int(mode)
        except:
            print('Invalid input, please try again!')
            continue

        if mode == 1 or mode == 2:
            break
        else:
            print('Invalid input, please try again!')
            continue

    start_time = time.time()
    if mode == 1:
        try:
            output = initialize_output()
        except:
            print('Failure in deleting the previous output file or creating the new one!')
            exit()
    else:
        try:
            output = resume_output()
        except:
            print('Failure in accessing the previous output file!')
            exit()

    driver = initialize_bot()
    clear_screen()
    nfail = 0
    signin = False
    print('Logging in the websites ....')
    players_list = False
    done = False
    nplayers = 0
    nscraped = 0
    iplayer = 0

    df = pd.read_csv(output, on_bad_lines='skip')
    iplayer = df.shape[0]
    skip = False
    while True:
        try:
            if skip:
                skip_output(players[iplayer], output)
                iplayer += 1
                skip = False
                
            if not signin:
                login_sorare(driver, name1, pwd1)
                login_soraredata(driver)
                signin = True
            if not players_list:
                cwd = os.getcwd()
                if cwd.find('/') != -1:
                    list_path = cwd + "/" + 'players_list.csv'
                else:
                    list_path = cwd + "\\" + 'players_list.csv'
                if os.path.isfile(list_path) and mode == 2:
                    df_players = pd.read_csv(list_path)
                    players = df_players.iloc[:, 0].values.tolist()
                    links = df_players.iloc[:, 1].values.tolist()
                    players_list = True
                    nplayers = len(players)
                    print('-'*50)
                    print('Total number of players: {}'.format(nplayers))
                    print('-'*50)
                else:
                    print('Getting the players list ... ')
                    players, links = get_players(driver)
                    players_list = True
                    df_out = pd.DataFrame()
                    df_out['Player Name'] = players
                    df_out['SorareData Links'] = links
                    df_out.to_csv('players_list.csv', encoding='UTF-8', index=False)
                    nplayers = len(players)
                    print('-'*50)
                    print('Total number of players: {}'.format(nplayers))
                    print('-'*50)



            start = iplayer

            for i in range(start, nplayers):
                # skipping players after ten scraping attempts with failure
                soraredata, club, league, pos1, pos2, date, name = scrape_soraredata(driver, players[i], links[i])
                sorare = scrape_sorare(driver, name, club, league, pos1, pos2, date)
                processing_data(sorare, soraredata, output, name)
                nscraped += 1
                nfail = 0
                print('Data is successfully scraped for player {}'.format(iplayer + 1))
                iplayer += 1

            done = True
            break
        except:
            nfail += 1
            print('-'*50)
            print('Failure in Scraping the data! Re-attempt number {} ...'.format(nfail))
            print('-'*50)

            if nfail > 10: 
                nfail = 0
                print('Skipping player {} ...'.format(iplayer + 1))
                skip = True

            # iterating on driver quit till process occurred successfully
            for j in range(100):
                try:
                    driver.quit()
                    break
                except:
                    time.sleep(10)
                    continue

            time.sleep(10)

            # iterating on driver restart till process occurred successfully
            for k in range(100):
                try:
                    driver = initialize_bot()
                    break
                except:
                    print(' Error occurred during restarting the web driver, retrying ... ')
                    time.sleep(10)
                    continue

            signin = False


    if done:
        df_output = pd.read_csv(output)
        df_output[['L5', 'L15', 'L40']] = df_output[['L5', 'L15', 'L40']].astype(str)
        df_output['L40'].replace('nan', 'NA', inplace=True)
        df_output['L15'].replace('nan', 'NA', inplace=True)
        df_output['L5'].replace('nan', 'NA', inplace=True)
        df_output.drop_duplicates(inplace=True)
        df_output.to_csv(output, encoding='UTF-8', index=False)
        print('-'*50)
        print('Data is scraped successfully! Total scraping time is {:.1f} mins'.format((time.time() - start_time)/60))
        print('-'*50)
        print("{} players are scraped of {} players".format(nscraped, nplayers))
        print('-'*50)
