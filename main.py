from binascii import a2b_qp
from datetime import date as dt
import shutil
from sqlite3 import Time

from time import sleep
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, InvalidArgumentException, ElementClickInterceptedException, TimeoutException
from decouple import config
from typing import Tuple
from rich import print
import re
import os
import easygui
#pip install selenium 
#pip install python-decouple
#pip install webdriver-manager

USERNAME = config('USERNAME',default='')
PASSWORD = config('PASSWORD',default='')
ENTER = Keys.ENTER

#this string will add an inputable element and will handle the input
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
    print(f'Consegui fazer o upload de {path}')
    return True

def login_proradis() -> webdriver.Chrome:
    """
    Logs on proradis, using USERNAME
    """
    service = Service(executable_path=ChromeDriverManager().install())
    chrome_options = Options()
    #chrome_options.add_argument("--headless")                                   #ENABLE THIS TO HIDE CHROME
    #chrome_options.add_experimental_option("detach",True)                       #ENABLE THIS TO HOLD THE SERVICE AFTER FINISHING THE JOB
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
    fullId = '//*[@id="'+id+'_chzn"]'
    searchType = driver.find_element(By.XPATH,fullId)
    print(fullId)
    xPathSelecter = '/html/body/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[1]/div[1]/a'
    selector = driver.find_element(By.XPATH,xPathSelecter).click()

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

def enter_Laudo_ecg(driver:webdriver.Chrome) -> Tuple[webdriver.Chrome,list]:
    driver.maximize_window()
    ecgRadial = driver.find_element(By.XPATH,'//*[@id="mod-ECG"]').click()
    dateRangeFinder = driver.find_element(By.XPATH,'//*[@id="entre"]').click()
    
    date = get_date()    
    
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]').send_keys(date)
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]').send_keys(date)
    
    date = date.strip().split('/')
    
    submitBtn = driver.find_element(By.XPATH,'//*[@id="full_search"]').click()
    sleep(5)
    driver.implicitly_wait(10)
    WebDriverWait(driver,35,300,(StaleElementReferenceException)).until(lambda d:driver.find_element(By.XPATH,'//*[@id="vApp"]/div[5]/div').is_displayed())
    
    originalWindow = driver.current_window_handle
    weirdClass  = driver.find_element(By.CSS_SELECTOR,".report-line.odd")
    driver.execute_script("arguments[0].click();",weirdClass)

    #at this point, we enter the Laudo 
    for window_handle in driver.window_handles:
        if window_handle != originalWindow:
            driver.switch_to.window(window_handle)
            print("Window Changed!")
            break;
    return send_Electro(driver,date) 

def enter_Laudo_ecg_API(driver:webdriver.Chrome, date:str) -> Tuple[webdriver.Chrome,list]:
    notfound = []
    finalizado_name = []
    finalizado_path = {}
    driver.maximize_window()
    ecgRadial = driver.find_element(By.XPATH,'//*[@id="mod-ECG"]').click()
    dateRangeFinder = driver.find_element(By.XPATH,'//*[@id="entre"]').click()
    print(date)
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]').send_keys(date)
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]').send_keys(date)
    date = date.strip().split('/')
    driver.implicitly_wait(10)
    exits_calendar(driver)
    #breakpoint()
    submitBtn = driver.find_element(By.XPATH,'//*[@id="full_search"]').click()
    sleep(5)
    WebDriverWait(driver,35,300,(StaleElementReferenceException)).until(lambda d:driver.find_element(By.XPATH,'//*[@id="vApp"]/div[5]/div').is_displayed())
    
    originalWindow = driver.current_window_handle
    weirdClass  = driver.find_element(By.CSS_SELECTOR,".report-line.odd")
    driver.execute_script("arguments[0].click();",weirdClass)

    #at this point, we enter the Laudo 
    for window_handle in driver.window_handles:
        if window_handle != originalWindow:
            driver.switch_to.window(window_handle)
            print("Window Changed!")
            break;
    return send_Electro(driver,date)

def exits_calendar(driver):
    driver.find_element(By.XPATH,'//*[@id="filtros"]/div[1]/div[4]/label[1]').click() #to exit the calendar, you must click somewhere other than the calendar. this does it.
    driver.find_element(By.XPATH,'//*[@id="filtros"]/div[1]/div[4]/label[1]').click()

def dateSetter(driver):
    date = input('Coloque a data formatada [dd/mm/aaaa]:')

    if date == 'hoje':
        today = dt.today()
        date = today.strftime("%d/%m/%Y")    
    
    dateInit = driver.find_element(By.XPATH,'//*[@id="data_inicio"]').send_keys(date)
    dateEnd = driver.find_element(By.XPATH,'//*[@id="data_fim"]').send_keys(date)
    return date   

def get_date() -> str:
    today = dt.today()
    date = today.strftime("%d/%m/%Y")
    date = easygui.enterbox('Coloque a data formatada: [dd/mm/aaaa]','Data', date)
    return date      

def send_Electro(driver:webdriver.Chrome, date) -> None:
    [day, month, year] = date
    driver.refresh()
    WebDriverWait(driver,2,2).until(lambda d: driver.find_element(By.XPATH,'//*[@id="cancel_report"]').is_displayed()) #tempo de espera pra cancelar atribuição do responsável
    #neglect_responsible(driver)                                    #ENABLE THIS TO NEGLECT RESPONSIBLE
    patName = get_patName(driver)
    dropzone = addAnnex(driver) #ADICIONA ANEXO
    initPath = r'\\172.19.0.2\\exames-eletro' #r'\\172.19.0.2\exames-eletro\2022\04 - Abril\27'
    
    path = initPath+f'\\{year}\\{get_Month_Full_Path(month)}\\{day}\\'
    patNameJPG = patName+'.jpg'
    fullPath = path + patNameJPG
    try:
        breakpoint()
        upload = drag_and_drop_file(dropzone, fullPath) #faz o upload do ANEXO
        waitForGreenTick = WebDriverWait(driver,5,2).until(lambda d: driver.find_element(By.XPATH,'/html/body/div[7]/div/div/form/div[2]/div[3]').is_displayed())
        leaveDropzone(driver)
        driver.refresh()
        #neglect_responsible(driver)
        addImage(driver, fullPath)
        leaveDropzone(driver)
        print(f'Paciente {patName} finalizado. Indo para o próximo paciente.')
        donePath = path + '\\FINALIZADO\\'
        doneFullPath = donePath + patNameJPG
        driver.implicitly_wait(2)
        finalizado_path[fullPath] = doneFullPath
        nextArrow(driver)
        send_Electro(driver,date)
        
    except InvalidArgumentException:
        print(f'Paciente {patName} não encontrado no armazenamento')
        notfound.append(patName)
        leaveDropzone(driver)
        nextArrow(driver)
        send_Electro(driver,date)        
    except TimeoutException as err:
        #print(traceback.print_exception(err))
        #pass
        print(f'Tempo de espera atingiu o limite. Tentando fazer o upload do mesmo paciente mais uma vez.')
        send_Electro(driver,date)
    finally:

        return None

def addImage(driver, fullPath):
    """Tries to add img. Returns dropzone"""
    try:
        addImage = driver.find_element(By.XPATH,'/html/body/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/button[21]').click() 
        dropzone2 = driver.find_element(By.ID,'dropzone-master')
        upload2 = drag_and_drop_file(dropzone2, fullPath)
        print(f'Dropzone da imagem encontrado.')
    except TimeoutException:
        print('Não consegui encontrar o botão verde da IMAGEM')
    finally:
        return dropzone2

def addAnnex(driver):
    """Opens the first dropzone. Returns dropzone"""
    try:
        addAnnex = driver.find_element(By.XPATH,'//*[@id="left-panel"]/div[4]/div[8]/div[1]/button').click()
        WebDriverWait(driver,10,2).until(lambda d: driver.find_element(By.ID,'dropzone-master').is_displayed())
        dropzone = driver.find_element(By.ID,'dropzone-master')
        #print(f'Dropzone do anexo encontrada.')
    except TimeoutException:
        print('Não consegui encontrar o botão verde do ANEXO')
    finally:
        return dropzone

def get_patName(driver):
    innerHTML = driver.find_element(By.ID,"left-panel").get_attribute('innerHTML')
    result = re.search(re.escape('PACS: ')+"(.*)"+re.escape('</small></span> <br><span><small>'), innerHTML)
    patName = result[0].split('</small>')[0].split('PACS: ')[1].strip()
    patName = patName.replace("^"," ").strip()
    return patName

def neglect_responsible(driver):
    try:
        WebDriverWait(driver,2,5).until(lambda d: driver.find_element(By.XPATH,'//*[@id="simplemodal-overlay"]').is_displayed())
        neglectResponsible = driver.find_element(By.XPATH,'//*[@id="simplemodal-overlay"]').click()
    except TimeoutException:
        print("Responsável não encontrado!")

def leaveDropzone(driver):
    leaveDropzone = driver.find_element(By.XPATH,'//*[@id="simplemodal-container"]/a').click()

def nextArrow(driver):
    driver.find_element(By.XPATH,'//*[@id="next"]').is_enabled()
    nextArrow = driver.find_element(By.XPATH,'//*[@id="next"]').click()

def moveDone(done:dict):
    try:
        fullpath = list(done.values())[0]
        donePath = re.search('.+(?:FINALIZADO)', fullpath)
        if not os.path.exists(donePath[0]):
            os.mkdir(donePath[0])
        for source,destination in done.items():
            shutil.move(source,destination)
        print(f'{len(done)} pacientes movido para a pasta de finalizados.')
    except IndexError:
        print('Nenhum paciente foi finalizado')

def pipeline(date) -> Tuple[list,list]:
    "Runs the pipeline. Returns the patients that were not found and the ones that are done."
    notfound = []
    finalizado_name = []
    finalizado_path = {}
    driver = login_proradis()
    driver.maximize_window()
    driver = enter_Laudo_ecg_API(driver,date)
    moveDone(finalizado_path)
    return notfound,finalizado_name


if __name__ == '__main__':
    
    notfound = []
    finalizado_name = []
    finalizado_path = {}
    try:
        driver = login_proradis()
        driver.maximize_window()
        driver = enter_Laudo_ecg(driver)
        print('Não encontrados:')
        print(notfound)
        moveDone(finalizado_path)
    except KeyboardInterrupt:
        print(notfound)
        moveDone(finalizado_path)
        print('Programa finalizado com Crtl + C.')
    except ElementClickInterceptedException:
        #breakpoint()
        #print(notfound)
        #moveDone(finalizado)
        pass
    finally:
        print(notfound)
        moveDone(finalizado_path)
        print(f'Lista de pacientes finalizada.{len(finalizado_path)} finalizados. {len(notfound)} não encontrados.')
