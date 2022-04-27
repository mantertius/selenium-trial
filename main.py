from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from decouple import config
#pip install selenium 
#pip install python-decouple
#pip install webdriver-manager

USERNAME = config('USERNAME',default='')
PASSWORD = config('PASSWORD',default='')
_ent = Keys.ENTER

def login_proradis() -> webdriver.Chrome:
    """
    Logs on proradis, using USERNAME
    """
    service = Service(executable_path=ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_experimental_option("detach",True)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://proradis.uncisal.edu.br")
    userInput = driver.find_element(by=By.NAME,value="username")
    userInput.send_keys(USERNAME)
    passInput = driver.find_element(By.NAME,"password")
    passInput.send_keys(PASSWORD + Keys.ENTER)
    return driver

def get_Biradis(driver:webdriver.Chrome) -> webdriver.Chrome:
    """
    Downloads BIRADS list at set range.
    """
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
    
def get_Biopsy(driver:webdriver.Chrome) -> webdriver.Chrome:
    """
    Download core biopsy of today.
    """
    searchType = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.NAME,'busca-por'))
    id = searchType.get_attribute('id')
    fullId = '//*[@id="'+id+'_chzn"]'#/div/div/input'
    searchType = driver.find_element(By.XPATH,fullId)
    print(fullId)
    xPathSelecter = '/html/body/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[1]/div[1]/a'
    selector = driver.find_element(By.XPATH,xPathSelecter).click()
    #breakpoint() #//*[@id="selMDC_chzn"]/div/div/input
    searchType.send_keys('exame')
    examName = driver.find_element(By.XPATH,'//*[@id="selQ6A_chzn"]/div/div/input')
    examName.send_keys('PUNCAO'+_ent)

    checkAll = driver.find_element(By.XPATH,'//*[@id="check_all"]').click()
    getTags = driver.find_element(By.XPATH,'//*[@id="report-table-content"]/div[6]/div/div[2]/button[3]').click()

    return driver

def send_Electro(driver:webdriver.Chrome) -> webdriver.Chrome:
    ecgRadial = driver.find_element(By.XPATH,'//*[@id="mod-ECG"]').click()
    dateRangeFinder = driver.find_element(By.XPATH,'//*[@id="entre"]').click()
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]')
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]')
    dateInit.send_keys('27/04/2022')#input('Coloque a data de inicio formatada dd/mm/aaaa:'))
    dateEnd.send_keys('27/04/2022')#input('Coloque a data de fim formatada dd/mm/aaaa:') + _ent)
    submitBtn = driver.find_element(By.XPATH,'//*[@id="full_search"]').send_keys(_ent)
    driver.implicitly_wait(20)
    WebDriverWait(driver,3,5,(StaleElementReferenceException)).until(lambda d:driver.find_element(By.XPATH,'//*[@id="vApp"]/div[5]/div').is_displayed())
    driver.find_element(By.XPATH,'//*[@title="Documentação"]').click()
    #at this point, we enter the Documentação 
    #TODO find a way to enter the laudo using XPATH or something else.
    enterLaudo  = driver.find_element(By.CSS_SELECTOR,"a[aria-label^='Laudo']").click()
    
    neglectResponsible = driver.find_element(By.XPATH,'//*[@id="simplemodal-overlay"]').click()
    patName = driver.find_element(By.XPATH,'//*[@id="pat_name"]').get_attribute('text')
    addAnnex = driver.find_element(By.XPATH,'//*[@id="left-panel"]/div[4]/div[8]/div[1]/button/i')
    dropzone = driver.find_element(By.XPATH,'//*[@id="dropzone-master"]')
    # breakpoint()



driver = login_proradis()
#driver = get_Biopsy(driver)
driver = send_Electro(driver)