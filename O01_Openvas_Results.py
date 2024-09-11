##########################################################
## Programa para extraer los Resultados de OpenVas
## H.Ghirardelli
## 2024-Sep-09
##########################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from datetime import datetime
import pandas as pd
import math
import io
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Cargar las variables del archivo .env
load_dotenv()

# Obtener las variables de entorno
var_username = os.getenv("USERNAME")
var_password = os.getenv("PASSWORD")


##################################################
############### FUNCIONES  ########################

def ahora():
    # Obtener la fecha y hora actual
    fecha_y_hora_actual = datetime.now()

    # Imprimir la fecha y hora actual en un formato personalizado
    print("Fecha y hora actual:", fecha_y_hora_actual.strftime("%Y-%m-%d %H:%M:%S"))
    return()

def transforma_en_arreglo(dato):
    arreglo=[]
    for elemento in dato:
        arreglo.append(elemento.text)
    return(arreglo)


def procesar_html(driver):
    # Obtener el contenido HTML
    html_content = driver.page_source

    # Convertir el contenido HTML a un objeto StringIO
    html_content_io = io.StringIO(html_content)

    # Leer el contenido HTML en un DataFrame
    df = pd.read_html(html_content_io)

    # Convertir el DataFrame a un diccionario
    df_dict = df[0].to_dict(orient='records')

    # Crear un nuevo diccionario con las segundas claves
    new_dict = []

    for entry in df_dict:
        # Nos quedamos solo con la segunda llave
        new_entry = {key[1]: value for key, value in entry.items()}
        new_dict.append(new_entry)

    # Reemplazar 'Severity\xa0▼' por 'Severity' manteniendo la posición
    for entry in new_dict:
        # Crear un nuevo diccionario para mantener el orden
        new_ordered_entry = {}
        for key, value in entry.items():
            # Reemplazar 'Severity\xa0▼' por 'Severity'
            if key == 'Severity\xa0▼':
                new_ordered_entry['Severity'] = value
            else:
                new_ordered_entry[key] = value
        entry.clear()  # Limpiamos el diccionario original
        entry.update(new_ordered_entry)  # Actualizamos con el nuevo diccionario ordenado

    # Eliminar el último registro de la lista new_dict
    if new_dict:
        new_dict.pop()

    # Devolver la lista de diccionarios procesados
    return new_dict


############## FUNCIONAES (FIN) ####################

current_directory = os.getcwd()
var_Cliente = "CLIENTE"


##############################################
########## BROWSER ###########################
## Opcion 1 para Maximizar
options = webdriver.ChromeOptions()

# Establecer la ruta de descarga para los archivos PDF al directorio actual
options.add_experimental_option("prefs", {
    "download.default_directory": current_directory,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True})

# Esto funciona: driver = webdriver.Chrome(options=options)
driver = webdriver.Chrome(options=options)

driver.maximize_window()
driver.implicitly_wait(5)
##################### BROWSER (FIN) #########################################


##############################################################################
###################### Proceso de Login ######################################

## La URL de OpenVAS y el acceso 
url_base="http://127.0.0.1:8888/"
driver.get(url_base)

Mi_Email = driver.find_element(By.XPATH,'//input[@name="username"]')
Mi_Email.send_keys(var_username)
time.sleep(1)

Mi_Password = driver.find_element(By.XPATH,'//input[@name="password"]')
Mi_Password.send_keys(var_password)
time.sleep(1)

Mi_Login = driver.find_element(By.XPATH,'//button[@data-testid="login-button"]')
Mi_Login.click()
time.sleep(5)
################ Proceso de Login (FIN) #####################################


url_reports= url_base + "results"
driver.get(url_reports)

time.sleep(45)

#####################################
## Rescatar el Numero de paginas
#### Objeto HTML ####################

Lista_Nro_Registros = []

Html_Nro_Registros = driver.find_element(By.XPATH,'//span[@class="sc-fxNNzt eaXFEc"]')
print(type(Html_Nro_Registros.text))
Lista_Nro_Registros = Html_Nro_Registros.text.split()
#print(Mi_Numero_Paginas.text)
print(Lista_Nro_Registros[-1])
var_Nro_Registros = int(Lista_Nro_Registros[-1])
var_Reg_por_Pagina = int(Lista_Nro_Registros[2])
print(var_Reg_por_Pagina)

var_Nro_Click=math.ceil(var_Nro_Registros/var_Reg_por_Pagina)

print(var_Nro_Click)

#### Objeto HTML (FIN) ##############
#####################################

##### INICIO ##############################
#### Ciclo for para recorrer los resultados
###########################################

Lista_Acumula_Resultados = []

for i in range(var_Nro_Click):
    if i<1:
        new_dict=procesar_html(driver)
        Lista_Acumula_Resultados.append(new_dict)
    else:
        Html_Avance_Pagina = driver.find_element(By.XPATH,'//div/span[@title="Next"]')
        Html_Avance_Pagina.click()
        time.sleep(20)
        new_dict=procesar_html(driver)
        Lista_Acumula_Resultados.append(new_dict)
    

# Aplanar la lista de listas (si los resultados están anidados)
resultados_planos = [item for sublist in Lista_Acumula_Resultados for item in sublist]


# Convertir los diccionarios combinados en un único DataFrame
df_final = pd.DataFrame(resultados_planos)

print(df_final.columns)


# Guardar el DataFrame en un archivo CSV separado por ';'
df_final.to_csv(f'{var_Cliente}_resultado.txt', sep=';', index=False)
# Guardar el DataFrame en un archivo Excel
df_final.to_excel(f'{var_Cliente}_resultado.xlsx', index=False)

driver.close()