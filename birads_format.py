import glob
import pandas as pd
import xlrd
import os
import sys

PATH = r"C:\Biradis"

def birads():

    file_list = glob.glob( PATH +"\*.xls")
    print(file_list)

    excel_list = []
    excl_merged = pd.DataFrame()

    for file in file_list:
        workbook = xlrd.open_workbook(file, ignore_workbook_corruption = True)
        excel_list.append(pd.read_excel(workbook))

    for excl_file in excel_list:
        excl_merged = excl_merged.append(excl_file, ignore_index=True)

    biradsFile = PATH + '\\birads.xlsx'
    excl_merged.to_excel(biradsFile, index=False)

    df = pd.read_excel(biradsFile)
    df = df[['etiqueta','nome','codigo_paciente','cpf','cel','solicitante','entrega']]
    new_ticker = 'BIRADS ' + sys.argv[:-1]
    print(new_ticker)
    df = df.fillna({"etiqueta": new_ticker})
    df.rename(columns={'etiqueta': 'Etiqueta','nome':'Nome','codigo_paciente':'ID','cpf':'CPF','cel':'Cel','solicitante':'Solicitante','entrega':'Data de Nascimento'}, inplace=True)
    df.to_excel(PATH+'\\done\\'+sys.argv[1]+new_ticker+'.xlsx', index=False)
    for file in file_list:
        os.remove(file)

    os.remove(biradsFile)

birads()
