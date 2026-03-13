import pandas as pd
import numpy as np

def format_int(x):
    # Utility function to format ints when printing integers
    return '{:,}'.format(x)

def groupby_sum(df, old_column, new_column):
    """
    Utility function to group a table by Número fondo and Fecha 
    while summing up the given 'old column', then renames old_column to new_column 

    df: pd.Dataframe
    old_column: str
    new_column: str
    """
    df = df[['Número fondo', 'Fecha', old_column]]
    df = df.groupby(['Número fondo', 'Fecha'])
    df = df.sum()
    return df.rename(columns={old_column: new_column})

def import_fondos_hasta():
    print('Reading fondos_hasta1500.csv file')
    # List of columns to keep when reading the csv file
    keep_columns = ['Número fondo', 'Fecha', 'ISIN', 'Valor de realización (VR)']
    # Read the 'fondos_hasta1500.csv' file
    fondos_hasta = pd.read_csv('fondos_hasta1500.csv', delimiter=';', thousands='.', decimal=',', usecols=keep_columns)
    # Remove rows containing NaN value (empty cells)
    fondos_hasta = fondos_hasta.dropna()
    # Drop duplicates rows of ('Fecha', 'Número fondo', 'ISIN') and keep the last duplicate only
    fondos_hasta = fondos_hasta.drop_duplicates(subset=['Fecha', 'Número fondo', 'ISIN'], keep="last")
    # Convert the Fecha column type to datetime using the date format from the file 
    fondos_hasta['Fecha'] = pd.to_datetime(fondos_hasta['Fecha'], format='%d/%m/%y')
    # Sort the rows by 'Número fondo', 'Fecha', and 'ISIN'
    fondos_hasta = fondos_hasta.sort_values(['Número fondo', 'Fecha', 'ISIN'])
    print('Done reading fondos_hasta1500.csv')
    return fondos_hasta

def import_lista_isins_no_rv():
    # Import the 'ISIN' and 'Titulos No Rvble' columns from the 'LISTA ISINs NO RV' csv file
    lista_no_rv = pd.read_csv('LISTA ISINs NO RV.csv', delimiter=';', usecols=['ISIN', 'Titulos No Rvble'])
    # Drop rows that do not contain an 'ISIN' (empty cells)
    lista_no_rv = lista_no_rv[lista_no_rv['ISIN'].notna()]
    # Sort the rows by 'ISIN' (increasing order)
    lista_no_rv = lista_no_rv.sort_values('ISIN')
    return lista_no_rv

def compute_sumatorio_vr(fondos_hasta):
    # Sum all 'Valor de realización (VR)' per Número fondo and Fecha
    sum_vr = groupby_sum(fondos_hasta, 'Valor de realización (VR)', 'Sumatorio VR')
    # Join the resulting dataframe with fondos_hasta to add the 'Sumatorio VR' column
    return pd.merge(fondos_hasta, sum_vr, how='left', on=['Número fondo', 'Fecha'])


def compute_valor_de_realizacion_en_rv(fondos_hasta, lista_isins_no_rv):
    # Join file with the Lista ISINs No RV list based on the ISINs
    fondos_hasta = pd.merge(fondos_hasta, lista_isins_no_rv, how='left', left_on='ISIN', right_on='ISIN')
    # Map the 'Titulos No Rvble' column to identify the RV rows i.e. where 'Titulos No Rvble' is different than * or 1
    fondos_hasta['Titulos No Rvble'] = fondos_hasta['Titulos No Rvble'].map(lambda x: 0 if x == '*' or x == '1' else 1)
    # 'en RV' = 'VR' * 'Titulos No Rvble'
    fondos_hasta['Valor de realización en RV'] = fondos_hasta['Valor de realización (VR)'] * fondos_hasta['Titulos No Rvble']
    return fondos_hasta

def compute_cartera_de_rvble(fondos_hasta):
    # Sum all 'Valor de realización en RV' per Número fondo and Fecha
    sum_cartera = groupby_sum(fondos_hasta, 'Valor de realización en RV', 'Cartera de Rvble')
    # Join sum_cartera with fondos_hasta on 'Fecha' and 'Número fondo', to add the 'Cartera de Rvble' column
    return pd.merge(fondos_hasta, sum_cartera, how='left', on=['Fecha', 'Número fondo']).fillna(0)

def import_lista_fietf():
    # Conversion function for the 'Todos ETF o FI Rvble' column resulting in either the values 2, 1000 or 0
    converters = {'Todos ETF o FI Rvble': lambda x: int(x) if x == '2' or x == '1000' else 0}
    # Read the 'LISTA FI-ETF.csv' file, keeping only the 'ISIN' and 'Todos ETF o FI Rvble' colums
    lista_fietf = pd.read_csv('LISTA FI-ETF.csv', delimiter=';', usecols=['ISIN', 'Todos ETF o FI Rvble'], converters=converters)
    # Remove rows that contain NaN values (empty cells)
    lista_fietf = lista_fietf.dropna()
    # Sort the table by 'ISIN' (ascending order)
    lista_fietf = lista_fietf.sort_values('ISIN')
    return lista_fietf

def compute_cartera_rvble_sin_fietf_no_ibex(fondos_hasta):
    # 'Cartera Rvble sin FI-ETF no IBEX35' = 'Cartera de Rvble' - ('Valor de realización en RV'   WHEN   'Todos ETF o FI Rvble' == 2   OTHERWISE  0)
    fondos_hasta['Cartera Rvble sin FI-ETF no IBEX35'] = fondos_hasta['Cartera de Rvble'] - (fondos_hasta['Todos ETF o FI Rvble'] == 2).astype(int) * fondos_hasta['Valor de realización en RV']
    return fondos_hasta

def compute_cartera_rvble_sin_fi_o_etf(fondos_hasta):
    # Similar to compute_cartera_rvble_sin_fietf_no_ibex but with Todos ETF o FI Rvble == 1000
    # 'Cartera Rvble sin FI o ETFs' = 'Cartera Rvble sin FI-ETF no IBEX35' - ('Valor de realización en RV'   WHEN   'Todos ETF o FI Rvble' == 1000  OTHERWISE  0)
    fondos_hasta['Cartera Rvble sin FI o ETFs'] = fondos_hasta['Cartera Rvble sin FI-ETF no IBEX35'] - (fondos_hasta['Todos ETF o FI Rvble'] == 1000).astype(int) * fondos_hasta['Valor de realización en RV']
    return fondos_hasta

def compute_peso_en_cartera(fondos_hasta):
    # 'Peso en Cartera' = 'Titulos No Rvble' * VR * 100 / 'Cartera Rvble sin FI o ETFs'
    # + Round the result with 4 decimal digits
    fondos_hasta['Peso en Cartera Rvble sin FI o ETFs VR=0 pone 0%'] = round(fondos_hasta['Titulos No Rvble'] * fondos_hasta['Valor de realización (VR)'] * 100 / fondos_hasta['Cartera Rvble sin FI o ETFs'], 4)
    return fondos_hasta

def compute_coef_ajuste(fondos_hasta):
    # 'Coef Ajuste' = 'Cartera Rvble sin FI o ETFs' / 'Cartera Rvble sin FI-ETF no IBEX35'
    fondos_hasta['Coef. Ajuste ASFI o ETF Ibex35'] = fondos_hasta['Cartera Rvble sin FI o ETFs'] / fondos_hasta['Cartera Rvble sin FI-ETF no IBEX35']
    return fondos_hasta

def import_ibex():
    # Read the 'Ibex.csv' file and keep only the 'ISIN 1', 'Fecha' and 'Peso' columns
    ibex = pd.read_csv('Ibex.csv', delimiter=';', decimal=',', usecols=['ISIN 1', 'Fecha', 'Peso'])
    # Remove rows that contain NaN values (empty cells)
    ibex = ibex.dropna()
    # Convert the Fecha column type to datetime using the date format from the file 
    ibex['Fecha'] = pd.to_datetime(ibex['Fecha'], format='%d/%m/%y')
    # Sort the rows by 'Fecha', and 'ISIN'
    ibex = ibex.sort_values(['Fecha', 'ISIN 1'])
    return ibex

def merge_fondos_ibex(fondos_hasta, ibex):
    # Join fondos_hasta with ibex based on 'Fecha' and 'ISIN'
    fondos_hasta = pd.merge(fondos_hasta, ibex, how='left', left_on=['Fecha', 'ISIN'], right_on=['Fecha', 'ISIN 1']).fillna(0)
    # Drop the unused column 'ISIN 1' which is a repetition of the 'ISIN' column
    fondos_hasta = fondos_hasta.drop(columns=['ISIN 1'])
    return fondos_hasta

def compute_peso_titulo_ibex(fondos_hasta):
    # 'Peso titulo en Ibex35' = 'Peso'  WHEN  ('Titulos No Rvble' != 0 or 'Todos ETF o FI Rvble' == 0)  OTHERWISE  0
    fondos_hasta['Peso titulo en Ibex35'] = np.logical_or(fondos_hasta['Titulos No Rvble'] != 0, fondos_hasta['Todos ETF o FI Rvble'] == 0) * fondos_hasta['Peso']
    return fondos_hasta

def compute_wi_windexi(fondos_hasta):
    # 'wi-windexi' = 'Coef. Ajuste ASFI o ETF Ibex35' * ABS('Peso en Cartera Rvble sin FI o ETFs VR=0 pone 0%' - 'Peso titulo en Ibex35')
    fondos_hasta['wi-windexi'] = fondos_hasta['Coef. Ajuste ASFI o ETF Ibex35'] * np.abs(fondos_hasta['Peso en Cartera Rvble sin FI o ETFs VR=0 pone 0%'] - fondos_hasta['Peso titulo en Ibex35'])
    return fondos_hasta

def print_summary(df, cols):
    for col in cols:
        print(f'{col}: {format_int(df[col].sum())}')
    
def sum_wi_windexi(fondos_hasta):
    # Sum all 'wi-windexi' per Número fondo and Fecha
    AS = groupby_sum(fondos_hasta, 'wi-windexi', 'Σ wi-windexi')
    # Round the result with 4 decimal digits
    AS['Σ wi-windexi'] = round(AS['Σ wi-windexi'] / 100, 4)
    # Convert the GroupBy Dataframe to a single Dataframe
    AS = AS.reset_index()
    return AS

def compute_active_share_titulos_fondo(AS):
    # 'Active Share titulos fondo vs indice' = 'Σ wi-windexi' / 2
    # + Round the result with 4 decimal digits
    AS['Active Share titulos fondo vs indice'] = round(AS['Σ wi-windexi'] / 2, 4)
    return AS

def compute_percentage_ibex(fondos_hasta, AS):
    # Sum all 'Peso titulo en Ibex35' per Número fondo and Fecha
    ibex_no_incluido = groupby_sum(fondos_hasta, 'Peso titulo en Ibex35', '% Ibex no incluido por el fondo')
    # '% Ibex no incluido por el fondo' = 1 - sum('Peso titulo en Ibex35') / 100
    # + Round the result with 4 decimal digits
    ibex_no_incluido['% Ibex no incluido por el fondo'] = round(1 - ibex_no_incluido['% Ibex no incluido por el fondo'] / 100, 4)
    # Join ibex_no_incluido with AS on 'Número fondo' and 'Fecha', to add the '% Ibex no incluido por el fondo' column
    AS = pd.merge(AS, ibex_no_incluido, how='left', on=['Número fondo', 'Fecha'])
    return AS

def compute_wi_windex_2(AS):
    # 'Σ wi-windexi 2' = '% Ibex no incluido por el fondo' / 2
    # + Round the result with 4 decimal digits
    AS['Σ wi-windexi 2'] = round(AS['% Ibex no incluido por el fondo'] / 2, 4)
    return AS

def add_coef_ajuste(fondos_hasta, AS):
    # Take subset of fondos_hasta
    temp = fondos_hasta[['Fecha', 'Número fondo', 'Coef. Ajuste ASFI o ETF Ibex35']]
    # Remove columns based on 'Fecha' and 'Número fondo', keep first row for each tuple
    no_duplicates = temp.drop_duplicates(subset=['Fecha', 'Número fondo'], keep="first")
    # Join no_duplicates with AS on 'Número fondo' and 'Fecha', to add the 'Coef. Ajuste ASFI o ETF Ibex35' column
    AS = pd.merge(AS, no_duplicates, how='left', on=['Fecha', 'Número fondo'])
    return AS

def compute_fondo_fecha(AS):
    # Fondo-Fecha = 'Número fondo'-'Fecha'(Month)'Fecha'(Year)
    AS['Fondo-Fecha'] = AS['Número fondo'].astype(int).astype(str) + '-' + AS['Fecha'].dt.month.astype(str) + AS['Fecha'].dt.year.astype(str)
    return AS

def compute_active_share_titulos_ibex(AS):
    # 'Active Share titulos ibex no incluidos en fondo' = 'Σ wi-windexi 2' * 'Coef. Ajuste ASFI o ETF Ibex35'
    # + Round the result with 4 decimal digits
    AS['Active Share titulos ibex no incluidos en fondo'] = round(AS['Σ wi-windexi 2'] * AS['Coef. Ajuste ASFI o ETF Ibex35'], 4)
    return AS

def compute_as_def(AS):
    # 'AS def' = 'Active Share titulos ibex no incluidos en fondo' + 'Active Share titulos fondo vs indice'
    # + Round the result with 4 decimal digits
    AS['AS def'] = round(AS['Active Share titulos ibex no incluidos en fondo'] + AS['Active Share titulos fondo vs indice'], 4)
    return AS

def reorder_columns(AS):
    return AS.iloc[:, [7,0,1,2,3,4,5,6,8,9]]

if __name__ == '__main__':
    # Import 'fondos_hasta1500.csv' file
    fondos_hasta = import_fondos_hasta()
    # Adds 'Sumatorio VR' column
    fondos_hasta = compute_sumatorio_vr(fondos_hasta)
    # Import 'LISTA ISINs NO RV.csv' file 
    lista_isins_no_rv = import_lista_isins_no_rv()
    # Adds 'Titulos No Rvble' and 'Valor de realización en RV' columns
    fondos_hasta = compute_valor_de_realizacion_en_rv(fondos_hasta, lista_isins_no_rv)
    # Adds 'Cartera de Rvble' column
    fondos_hasta = compute_cartera_de_rvble(fondos_hasta)
    # Import 'LISTA FI-ETF.csv' file
    lista_fietf = import_lista_fietf()
    # Join lista_fietf with fondos_hasta based on 'ISIN'
    fondos_hasta = pd.merge(fondos_hasta, lista_fietf, how='left', on='ISIN').fillna(0)
    # Adds 'Cartera Rvble sin FI-ETF no IBEX35' column
    fondos_hasta = compute_cartera_rvble_sin_fietf_no_ibex(fondos_hasta)
    # Adds 'Cartera Rvble sin FI o ETFs' column
    fondos_hasta = compute_cartera_rvble_sin_fi_o_etf(fondos_hasta)
    # Adds 'Peso en Cartera Rvble sin FI o ETFs VR=0 pone 0%'
    fondos_hasta = compute_peso_en_cartera(fondos_hasta)
    # Adds 'Coef. Ajuste ASFI o ETF Ibex35' column
    fondos_hasta = compute_coef_ajuste(fondos_hasta)
    # Import 'Ibex.csv'
    ibex = import_ibex()
    # Join fondos_hasta with ibex based on 'Fecha' and 'ISIN'
    fondos_hasta = merge_fondos_ibex(fondos_hasta, ibex)
    # Adds 'Peso titulo en Ibex35' column
    fondos_hasta = compute_peso_titulo_ibex(fondos_hasta)
    # Adds 'wi-windexi' column
    fondos_hasta = compute_wi_windexi(fondos_hasta)
    # Prints the sums of some columns to check the script did ok
    print_summary(fondos_hasta, cols=[
        'Valor de realización (VR)', 'Valor de realización en RV', 
        'Cartera Rvble sin FI-ETF no IBEX35', 'Cartera Rvble sin FI o ETFs',
        'Peso titulo en Ibex35', 'wi-windexi'
    ])

    """  Second table called AS in excel """
    # AS starts with 'Número fondo', 'Fecha' and 'Σ wi-windexi', this function computes 'Σ wi-windexi' which we use as 'AS' directly
    AS = sum_wi_windexi(fondos_hasta)
    # Adds 'Active Share titulos fondo vs indice' column
    AS = compute_active_share_titulos_fondo(AS)
    # Adds '% Ibex no incluido por el fondo' column
    AS = compute_percentage_ibex(fondos_hasta, AS)
    # Adds 'Σ wi-windexi 2' column
    AS = compute_wi_windex_2(AS)
    # Adds 'Coef. Ajuste ASFI o ETF Ibex35' column
    AS = add_coef_ajuste(fondos_hasta, AS)
    # Adds 'Fondo-Fecha' column
    AS = compute_fondo_fecha(AS)
    # Adds 'Active Share titulos ibex no incluidos en fondo' column
    AS = compute_active_share_titulos_ibex(AS)
    # Adds 'AS def' column
    AS = compute_as_def(AS)
    # Reorders columns to make 'Fondo-Fecha' the first column
    AS = reorder_columns(AS)
    # Prints the sums of some columns to check the script did ok
    print_summary(AS, cols=[
        'Active Share titulos ibex no incluidos en fondo',
        'AS def'
    ])

    # Save both table to their respective files
    fondos_hasta.to_csv('fondos_hasta.csv', index=False, sep=';', decimal=',')
    AS.to_csv('AS.csv', index=False, sep=';', decimal=',')