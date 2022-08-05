from webbrowser import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from decouple import config
from datetime import date as dt
import logging

from main import login_proradis

USERNAME = config('USERNAME',default='')
PASSWORD = config('PASSWORD',default='')
ENTER = Keys.ENTER


class Driver(webdriver.Chrome):
    
    def __init__(self):
        self.driver = login_proradis()
        self.notfound = []
        self.finalizado = {}

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

    def get_date() -> str:
        today = dt.today()
        date = today.strftime("%d/%m/%Y")
        #date = easygui.enterbox('Coloque a data formatada: [dd/mm/aaaa]','Data', date)
        return date     

    def login_proradis(self):   
        """
        Logs on proradis, using USERNAME
        """
        logging.info('Trying to start the driver.')
        service = Service(executable_path=ChromeDriverManager().install())
        chrome_options = Options()
        #chrome_options.add_argument("--headless")                                   #ENABLE THIS TO HIDE CHROME
        #chrome_options.add_experimental_option("detach",True)                       #ENABLE THIS TO HOLD THE SERVICE AFTER FINISHING THE JOB
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()
        self.driver.get("https://proradis.uncisal.edu.br")
        self.userInput = self.driver.find_element(by=By.NAME,value="username")
        self.userInput.send_keys(USERNAME)
        self.passInput = self.driver.find_element(By.NAME,"password")
        self.passInput.send_keys(PASSWORD + Keys.ENTER)
        log = logging.getLogger(__name__)
        logging.info('The driver is set up and running.')
        return self.driver