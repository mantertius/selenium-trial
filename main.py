from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from decouple import config
import re
import os
#pip install selenium 
#pip install python-decouple
#pip install webdriver-manager

USERNAME = config('USERNAME',default='')
PASSWORD = config('PASSWORD',default='')
ENTER = Keys.ENTER

#this string will add an inputable element and will handle 
JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""

def drag_and_drop_file(drop_target, path):
    '''INPUT INJECTION'''
    driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)



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
    fluxoFinder.send_keys("birads 0" + ENTER)
    driver.implicitly_wait(.3)
    fluxoFinder.send_keys("birads 3" + ENTER)
    fluxoFinder.send_keys("birads 4" + ENTER)
    fluxoFinder.send_keys("birads 5" + ENTER)
    fluxoFinder.send_keys("birads 6" + ENTER)
    dateRangeFinder = driver.find_element(By.XPATH,'//*[@id="entre"]').click()
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]')
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]')
    dateInit.send_keys(input('Coloque a data de inicio formatada dd/mm/aaaa:'))
    dateEnd.send_keys(input('Coloque a data de fim formatada dd/mm/aaaa:') + ENTER)
    submitBtn = driver.find_element(By.XPATH,'//*[@id="full_search"]').send_keys(ENTER)

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
    examName.send_keys('PUNCAO'+ ENTER)

    checkAll = driver.find_element(By.XPATH,'//*[@id="check_all"]').click()
    getTags = driver.find_element(By.XPATH,'//*[@id="report-table-content"]/div[6]/div/div[2]/button[3]').click()

    return driver

def get_Month_Full_Path(month:int) -> str:
    monthsPath = {'01':'01 - Janeiro', 
              '02':'02 - Fevereiro',
              '03':'03 - Março',
              '04':'04 - Abril',
              '05':'05 - Maio',
              '06':'06 - Junho',
              '07':'07 - Julho',
              '08':'08 - Agosto',
              '09':'09 - Setembro',
              '10':'10 - Outubro',
              '11':'11 - Novembro',
              '12':'12 - Dezembro'}
    return monthsPath[month]
        

def send_Electro(driver:webdriver.Chrome) -> webdriver.Chrome:
    ecgRadial = driver.find_element(By.XPATH,'//*[@id="mod-ECG"]').click()
    dateRangeFinder = driver.find_element(By.XPATH,'//*[@id="entre"]').click()
    
    date = input('Coloque a data formatada [dd/mm/aaaa]:')
   
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]').send_keys(date)
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]').send_keys(date + ENTER)
    date = date.strip().split('/')
    day = date[0]
    month = date[1]
    year = date[2]

    breakpoint()

    submitBtn = driver.find_element(By.XPATH,'//*[@id="full_search"]').send_keys(ENTER)
    driver.implicitly_wait(20)
    WebDriverWait(driver,3,5,(StaleElementReferenceException)).until(lambda d:driver.find_element(By.XPATH,'//*[@id="vApp"]/div[5]/div').is_displayed())
    
    originalWindow = driver.current_window_handle
    weirdClass  = driver.find_element(By.CSS_SELECTOR,".report-line.odd")
    driver.execute_script("arguments[0].click();",weirdClass)

    #at this point, we enter the Laudo 
    for window_handle in driver.window_handles:
        if window_handle != originalWindow:
            driver.switch_to.window(window_handle)
            print("Window Changed!")
            break

    WebDriverWait(driver,5,5).until(lambda d: driver.find_element(By.XPATH,'//*[@id="report-editor"]').is_displayed())
    neglectResponsible = driver.find_element(By.XPATH,'//*[@id="simplemodal-overlay"]').click()
    innerHTML = driver.find_element(By.ID,"left-panel").get_attribute('innerHTML')
    result = re.search(re.escape('PACS: ')+"(.*)"+re.escape('</small></span> <br><span><small>'), innerHTML)
    patName = result[0].split('</small>')[0].split('PACS: ')[1].strip()
    
    addAnnex = driver.find_element(By.XPATH,'//*[@id="left-panel"]/div[4]/div[8]/div[1]/button').click()
    WebDriverWait(driver,3,2).until(lambda d: driver.find_element(By.ID,'dropzone-master').is_displayed())
    dropzone = driver.find_element(By.ID,'dropzone-master') #send_keys(os.path.abspath(r"C:\Users\manoel.terceiro\Pictures\e3j.jpg"))
    #breakpoint()
    initPath = r'\\172.19.0.2\\exames-eletro' #r'\\172.19.0.2\exames-eletro\2022\04 - Abril\27'
    
    path = initPath+f'\\{year}\\{get_Month_Full_Path(month)}'
    drag_and_drop_file(dropzone, initPath+patName)
    


driver = login_proradis()
#driver = get_Biopsy(driver)
driver = send_Electro(driver)