
import glob
import pandas as pd
import sys

PATH = r"C:\Biradis"

def merge_xlsx(path):
    file_list = glob.glob( path +"\*.xlsx")
    print(file_list)

    excel_list = []
    
    for file in file_list:
        excel_list.append(pd.read_excel(file))

    excel_merged = pd.concat(excel_list, ignore_index=True)

    biradsFile = path + '\\birads.xlsx'
    excel_merged.to_excel(biradsFile, index=False)

if __name__ == '__main__':
    
    merge_xlsx(PATH + '\\done\\' + sys.argv[1])
