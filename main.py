from email.policy import default
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from decouple import config
USERNAME = config('USERNAME',default='')
PASSWORD = config('PASSWORD',default='')
_ent = Keys.ENTER
def test_driver_manager_chrome():
    service = Service(executable_path=ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_experimental_option("detach",True)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://proradis.uncisal.edu.br")
    userInput = driver.find_element(by=By.NAME,value="username")
    userInput.send_keys(USERNAME)
    passInput = driver.find_element(By.NAME,"password")
    passInput.send_keys(PASSWORD + Keys.ENTER)
    statusFind  = WebDriverWait(driver,timeout=3).until(lambda d: d.find_element(By.XPATH,'//*[@id="report_status_chzn"]')) 
    statusFind.click()
    statusFind = driver.find_element(By.XPATH,'//*[@id="report_status_chzn"]/div/div/input')
    print(statusFind.accessible_name)
    statusFind.send_keys("laudados" + Keys.ENTER)
    fluxoFinder = driver.find_element(By.XPATH,'//*[@id="filtros"]/div[4]/div/span[2]/span[1]/span')
    fluxoFinder.send_keys("birads 0" + _ent)
    driver.implicitly_wait(.3)
    fluxoFinder.send_keys("birads 3" + _ent)
    fluxoFinder.send_keys("birads 4" + _ent)
    fluxoFinder.send_keys("birads 5" + _ent)
    fluxoFinder.send_keys("birads 6" + _ent)
    dateRangeFinder = driver.find_element(By.XPATH,'//*[@id="entre"]').click()
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]')
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]')
    dateInit.send_keys(input('Coloque a data de inicio formatada dd/mm/aaaa:'))
    dateEnd.send_keys(input('Coloque a data de fim formatada dd/mm/aaaa:') + _ent)
    submitBtn = driver.find_element(By.XPATH,'//*[@id="full_search"]').send_keys(_ent)

    checkAll = driver.find_element(By.XPATH,'//*[@id="check_all"]').click()
    getTags = driver.find_element(By.XPATH,'//*[@id="report-table-content"]/div[6]/div/div[2]/button[3]').click()
    
    #os proximos passos
test_driver_manager_chrome()