import pandas as pd
import numpy as np
xls = pd.read_excel('CEDIM 2022.xls')

print(xls)
breakpoint()

df = xls
contagem = df['codigo_unificado'].value_counts()
for index in contagem.index:
    _name = df.loc[df['codigo_unificado'] == index].iloc[0].descricao_procedimento

df.loc[df['codigo_unificado'] == index, 'descricao_procedimento'] = _name

exams_count = df['descricao_procedimento'].value_counts()
exams_count.to_csv()