import glob
import pandas as pd
import olefile
import xlrd
path = r"C:\Biradis"

file_list = glob.glob( path +"\*.xls")
print(file_list)

excel_list = []
excl_merged = pd.DataFrame()

for file in file_list:
    workbook = xlrd.open_workbook(file, ignore_workbook_corruption = True)
    excel_list.append(pd.read_excel(workbook))

for excl_file in excel_list:
    excl_merged = excl_merged.append(excl_file, ignore_index=True)

excl_merged.to_excel('biradis.xlsx', index=False)