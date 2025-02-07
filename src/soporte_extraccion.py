
# Hay que implementar función para limpiar valores
# Limpiar soporte y organización

import pandas as pd
import numpy as np

import random

from time import sleep

# Importar librerías para automatización de navegadores web con Selenium
# -----------------------------------------------------------------------
from selenium import webdriver  # Selenium es una herramienta para automatizar la interacción con navegadores web.
from webdriver_manager.chrome import ChromeDriverManager  # ChromeDriverManager gestiona la instalación del controlador de Chrome.
from selenium.webdriver.common.keys import Keys  # Keys es útil para simular eventos de teclado en Selenium.
from selenium.webdriver.support.ui import Select  # Select se utiliza para interactuar con elementos <select> en páginas web.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException # Excepciones comunes de selenium que nos podemos encontrar
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from tqdm import tqdm

# Para la extracción de información de las categorias
from selenium.webdriver.common.by import By
from seleniumbase import Driver

# Imports para el Backup
import os
import shutil
from IPython.display import display

# Para almacenamiento en sql
import sys
sys.path.append("../")
from src import soporte_bbdd_postgre as sbp
from . import soporte_bbdd_mongo as sbm

# Funciones para extraer la lista de todas las categorias
def extraer_lista_categorias(silent_mode = False):
    url = "https://twitchtracker.com/games"
    if silent_mode:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome()
    driver.get(url)
    sleep(0.5)
    driver.implicitly_wait(1)
    if not silent_mode:
        driver.maximize_window()
        sleep(0.2)
    try:
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p").click()
        sleep(0.2)
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p").click()
        sleep(0.2)
    except NoSuchElementException:
        pass

    df_categorias = pd.DataFrame()
    terminado = False

    # Creamos un bucle para recorrer las categorías
    for pagina in tqdm(range(2, 77)):
        for categoria in range(3, 23):
            try:
                nombre = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[3]/a").text
            except NoSuchElementException:
                terminado = True
                break
            enlace = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[3]/a").get_attribute("href")
            id_twitch = enlace.split("/")[-1]
            media_viewers = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[4]/div").text
            if media_viewers[-1] == "K":
                media_viewers = float(media_viewers.replace("K", "")) * 1000
            media_viewers = int(media_viewers)
            try:
                seven_days_change = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/span").text.replace("%", "")
                if seven_days_change[-1] == "K":
                    seven_days_change = float(seven_days_change.replace("K", "")) * 1000
                # seven_days_change = int(seven_days_change)
                tipo = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/i").get_attribute("class")
                tipo = tipo.split("-")[-1]
                if tipo == "down":
                    seven_days_change = f"-{seven_days_change}"
            except NoSuchElementException:
                seven_days_change = float(0)
            twitch_share = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[6]").text.replace("%", "")
            dicc = {"ID": id_twitch, "Nombre": nombre, "Media_Viewers": media_viewers, "7-Day_change_%": seven_days_change, "Twitch_share_%": twitch_share, "Enlace": enlace}

            df_categorias = pd.concat([df_categorias, pd.DataFrame(dicc, index=[0])], axis=0)
            # if not silent_mode:
            #     driver.execute_script(f"window.scrollTo(0, {categoria*75})")
            
            # sleep(random.uniform(0.1, 0.5))
        if not terminado:
            sleep(random.uniform(0.2, 1.5))
            driver.get(f"{url}?page={pagina}")
            # print(f"------ Página {pagina} ------")
        else:
            break
    
    print("\nNO SE HAN ENCONTADO MÁS CATEGORIAS\nEXTRACCIÓN COMPLETADA\n")
    driver.quit()
    print("DRIVER CERRADO")
    # df_categorias.sort_values(by=["Nombre"], inplace=True)
    # df_categorias.reset_index(inplace=True, drop=True)
    return df_categorias

def extraer_lista_categorias_ampliado(endpoint: str, silent_mode = False):
    url_base = "https://twitchtracker.com/games"
    url = f"{url_base}/{endpoint}"
    if silent_mode:
        driver = Driver(uc = True, headless = True, browser = "chrome", guest = True)
    else:
        driver = Driver(uc = True, browser = "chrome", guest = True)
    driver.get(url)
    sleep(0.5)
    driver.implicitly_wait(1)
    if not silent_mode:
        driver.maximize_window()
        sleep(0.2)
    try:
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p").click()
        sleep(0.2)
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p").click()
        sleep(0.2)
    except NoSuchElementException:
        pass

    df_categorias = pd.DataFrame()
    terminado = False
    lista_prueba = []

    # Creamos un bucle para recorrer las categorías
    for pagina in tqdm(range(2, 77)):
        for categoria in range(3, 23):
            lista_datos = []
            try:
                nombre = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[3]/a").text
            except NoSuchElementException:
                terminado = True
                break
            sleep(0.2)
            enlace = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[3]/a").get_attribute("href")
            id_twitch = enlace.split("/")[-1]
            lista_datos.append(id_twitch)
            lista_datos.append(nombre)

            if not endpoint.startswith("peak") and not endpoint.startswith("to"):
                # Obtener la media de viewers
                if endpoint == "rating":
                    media_viewers = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[4]/span").text
                    media_viewers = limpiar_valor(media_viewers)
                    # media_viewers = int(media_viewers)
                else:
                    media_viewers = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[4]/div").text
                    media_viewers = limpiar_valor(media_viewers)
                    # media_viewers = int(media_viewers)
                
                lista_datos.append(media_viewers)
                
                # Obtener el cambio en los ultimos 7 días/10 ultimos minutos
                try:
                    if endpoint == "live":
                        ten_minutes_change = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/span").text
                        ten_minutes_change = limpiar_valor(ten_minutes_change)
                        tipo = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/i").get_attribute("class")
                        tipo = tipo.split("-")[-1]
                        if tipo == "down":
                            ten_minutes_change = f"-{ten_minutes_change}"
                        lista_datos.append(ten_minutes_change)
                    elif endpoint == "rating":
                        seven_days_change = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span").text
                        seven_days_change = limpiar_valor(seven_days_change, int)
                        lista_datos.append(seven_days_change)
                    else:
                        seven_days_change = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/span").text
                        seven_days_change = limpiar_valor(seven_days_change)
                        tipo = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/i").get_attribute("class")
                        tipo = tipo.split("-")[-1]
                        if tipo == "down":
                            seven_days_change = f"-{seven_days_change}"
                        lista_datos.append(seven_days_change)
                except NoSuchElementException:
                    seven_days_change = float(0)
                    lista_datos.append(seven_days_change)
                
                # Obtener la última opción
                twitch_share = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[6]").text.replace("%", "")
                #dicc = {"ID": id_twitch, "Nombre": nombre, "Media_Viewers": media_viewers, "7-Day_change_%": seven_days_change, "Twitch_share_%": twitch_share, "Enlace": enlace}
                twitch_share = limpiar_valor(twitch_share)
                lista_datos.append(twitch_share)
            elif endpoint.startswith("to"):
                # Obtener primera columna
                media_viewers = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[4]/span").text
                media_viewers = limpiar_valor(media_viewers)
                lista_datos.append(media_viewers)

                # Obtener segunda columna
                try:
                    segunda = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span").text
                    segunda = limpiar_valor(segunda)
                    # tipo = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[5]/span/i").get_attribute("class")
                    # tipo = tipo.split("-")[-1]
                    # if tipo == "down":
                    #     seven_days_change = f"-{seven_days_change}"
                    lista_datos.append(segunda)
                except NoSuchElementException:
                    segunda = float(0)
                    lista_datos.append(segunda)
                
                # Obtener tercera columna
                tercera = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[6]").text
                tercera = limpiar_valor(tercera)
                lista_datos.append(tercera)

                # Obtener la cuarta columna
                cuarta = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[7]/span").text
                # cuarta = limpiar_valor(cuarta)
                lista_datos.append(cuarta)
            else:
                # Obtener la media de viewers
                max_element = driver.find_element(By.XPATH, f"//*[@id='content-wrapper']/div[2]/div[{categoria}]/div[4]/div").text
                max_element = limpiar_valor(max_element)
                lista_datos.append(max_element)

            lista_datos.append(enlace)
            # Obtener los encabezados
            header_divs = driver.find_elements('.ranked-item-header div')
            headers = [header.text.title().strip().replace("\n", "_") for header in header_divs]
            encabezados = ["ID", "Nombre"] + headers + ["Enlace"]
            
            #df_temp = pd.DataFrame(data=lista_datos, columns=encabezados)
            #df_categorias = pd.concat([df_categorias, df_temp], axis=0, ignore_index=True)

            #dicc = {"ID": id_twitch, "Nombre": nombre, "Media_Viewers": media_viewers, "7-Day_change_%": seven_days_change, "Twitch_share_%": twitch_share, "Enlace": enlace}
            lista_prueba.append(tuple(lista_datos))
            if not silent_mode:
                driver.execute_script(f"window.scrollTo(0, {categoria*75})")
            # print(f"Categoria: {categoria}")
            n_aleatorio = f"0.{random.randint(1, 3)}"
            sleep(float(n_aleatorio))
        # terminado = True
        if not terminado:
            sleep(1)
            driver.get(f"{url}?page={pagina}")
            # print(f"------ Página {pagina} ------")
        else:
            
            # print(lista_prueba)
            # print(lista_datos)
            df_categorias = pd.DataFrame(lista_prueba, columns=encabezados)
            break
    
    print("\nNO SE HAN ENCONTADO MÁS CATEGORIAS\nEXTRACCIÓN COMPLETADA\n")
    driver.quit()
    print("DRIVER CERRADO")
    # df_categorias.sort_values(by=["Nombre"], inplace=True)
    # df_categorias.reset_index(inplace=True, drop=True)
    #df_categorias = cambiar_tipos_columnas(df_categorias, df_categorias.columns.to_list())
    print("\nPROCESO TERMINADO")
    return df_categorias

def cambiar_tipos_columnas(df_categorias: pd.DataFrame, lista_columnas: list):
    # Cambiar tipos de las columnas
    # df_categorias["ID"] = df_categorias["ID"].astype(int)
    # df_categorias["Media_Viewers"] = df_categorias["Media_Viewers"].astype(int)
    # df_categorias["7-Day_change_%"] = df_categorias["7-Day_change_%"].astype(float)
    # df_categorias["Twitch_share_%"] = df_categorias["Twitch_share_%"].astype(float)

    for columna in lista_columnas:
        columna = str(columna)
        if columna == "ID" or columna.startswith("Avg") or columna.startswith("Max") or columna.startswith("Live") or columna.startswith("Hours"):
            df_categorias[columna] = df_categorias[columna].astype(int)
        elif columna.startswith("7") or columna.startswith("10") or columna.startswith("Twitch"):
            df_categorias[columna] = df_categorias[columna].astype(float)
    return df_categorias

def obtener_identificadores(df_categorias: pd.DataFrame):
    # Divido dataframes
    df_identificadores = df_categorias[["ID", "Nombre", "Enlace"]]
    return df_identificadores


# Funciones para extraer la información de las categorias recogidas anteriormente
def extraer_info_categoria_a_categoria(df_categorias: pd.DataFrame, silent_mode = False, dividir = False):
    url = "https://twitchtracker.com/games"

    df_total = pd.DataFrame()

    # Creo el bucle para iterar por cada categoria
    for row in tqdm(df_categorias["Nombre"].tolist()):
        categoria = str(row)
        twitch_id = df_categorias.loc[df_categorias["Nombre"] == categoria, "ID"].values[0]

        # Creo el driver
        if silent_mode:
            driver = Driver(uc = True, headless = True, browser = "chrome", guest = True)
        else:
            driver = Driver(uc = True, browser = "chrome", guest = True)
        driver.get(f"{url}/{twitch_id}")
        driver.implicitly_wait(1)
        if not silent_mode:
            driver.maximize_window()
        
        try:
            driver.find_element("xpath", "/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p").click()
            sleep(0.2)
            driver.find_element("xpath", "/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p").click()
            sleep(0.4)
        except NoSuchElementException:
            pass
        
        # Obtengo la tabla que contiene los encabezados
        tabla_encabezados = driver.find_element(By.XPATH, "//*[@id='DataTables_Table_0_wrapper']/div[2]/div/div/div[1]/div/table")

        # Extraer encabezados desde el atributo 'aria-label'
        encabezados_elementos = tabla_encabezados.find_elements(By.TAG_NAME, "th")
        encabezados = [th.get_attribute("aria-label").split(":")[0] for th in encabezados_elementos]
        encabezados[2] = f"ViewersGain"
        encabezados[3] = f"PercentageGainViewers"
        encabezados[-3] = f"PercentageGainStreams"
        encabezados[-2] = f"StreamsGain"

        # Obtengo la tabla que contiene los datos
        tabla_datos = driver.find_element(By.ID, "DataTables_Table_0")

        # Extraigo todas las filas para iterar posteriormente
        filas = tabla_datos.find_elements(By.TAG_NAME, "tr")

        # Extraigo los datos de cada fila
        datos = []
        for fila in filas[1:]:
            celdas = fila.find_elements(By.TAG_NAME, "td")
            datos.append([celda.text.strip() for celda in celdas])

        # Crea el DataFrame
        df_datos_categoria = pd.DataFrame(datos, columns=encabezados)

        # Limpieza de las columnas
        df_datos_categoria["AvgViewers"] = df_datos_categoria["AvgViewers"].str.replace(",", "").astype(int)
        df_datos_categoria["AvgStreams"] = df_datos_categoria["AvgStreams"].str.replace(",", "").astype(int)
        df_datos_categoria["ViewersGain"] = df_datos_categoria["ViewersGain"].str.replace(",", "").replace("-", "0").astype(int)
        df_datos_categoria["StreamsGain"] = df_datos_categoria["StreamsGain"].str.replace(",", "").replace("-", "0").astype(int)
        
        # Aplicar la función a la columna "HoursWatched"
        df_datos_categoria["HoursWatched"] = df_datos_categoria["HoursWatched"].apply(convertir_a_numero)
        df_datos_categoria["HoursWatched"] = df_datos_categoria["HoursWatched"].astype(int)
        df_datos_categoria["PercentageGainStreams"] = df_datos_categoria["PercentageGainStreams"].apply(limpiar_valor)
        df_datos_categoria["PercentageGainViewers"] = df_datos_categoria["PercentageGainViewers"].apply(limpiar_valor)
        df_datos_categoria["PercentageGainStreams"] = df_datos_categoria["PercentageGainStreams"].astype(float)
        df_datos_categoria["PercentageGainViewers"] = df_datos_categoria["PercentageGainViewers"].astype(float)

        # Separar el mes y el año
        df_nuevo = df_datos_categoria["Month"].str.split(" ", expand=True)
        df_nuevo.rename(columns={0: "Month", 1: "Year"}, inplace=True)
        df_nuevo = df_nuevo.reindex(columns=["Year", "Month"])
        df_concatenado = pd.concat([df_nuevo, df_datos_categoria.drop(columns="Month")], axis=1)

        # Almacenamiento de estos datos en csv
        if dividir:
            # Separar por datos de viewers y por datos de streams
            df_datos_viewers = df_concatenado[["Year", "Month", "AvgViewers", "ViewersGain", "PercentageGainViewers", "PeakViewers", "HoursWatched"]]
            df_datos_streams = df_concatenado[["Year", "Month", "AvgStreams", "StreamsGain", "PercentageGainStreams", "HoursWatched"]]
            df_datos_viewers.to_csv(f"../datos/output/categorias/viewers/{categoria.replace(":", "").replace(" ", "_").lower()}_viewers.csv")
            df_datos_streams.to_csv(f"../datos/output/categorias/streams/{categoria.replace(":", "").replace(" ", "_").lower()}_streams.csv")
        else:
            df_concatenado.to_csv(f"../datos/output/categorias/all/{categoria.replace(":", "").replace(" ", "_").replace("/", "_").lower()}.csv")

        # Concatenación del data frame que va a contener todo
        df_concatenado.insert(0, "Categoria", categoria)
        df_total = pd.concat([df_total, df_concatenado], axis=0)

        # Espera aleatoria
        n_aleatorio = f"0.{random.randint(1, 5)}"
        sleep(float(n_aleatorio))

        # Cierro el driver
        driver.close()

        # Esperamos a abrir la nueva ventana para no saturar la web
        # sleep(random.randint(1, 2))
        sleep(random.uniform(0.2, 1.5))
        # if row == "World of Warcraft":
        #     break

    # Apago el driver
    driver.quit()

    return df_total

def convertir_a_numero(valor, tipo = float):
    if "M" in valor:
        return float(valor.replace("M", "")) * 1000000
    elif "K" in valor:
        return float(valor.replace("K", "")) * 1000
    else:
        return tipo(valor)
    
def limpiar_valor(valor, tipo = float):
    # Eliminar símbolos %, + y espacios en blanco
    valor = valor.replace("%", "").replace("+", "").replace("hours", "")
    valor = valor.replace(",", "").strip()
    # Reemplazar guiones solitarios por 0
    if valor == "-" or valor == "--":
        return 0
    
    # Convertir directamente a float si es un número normal
    else:
        valor = convertir_a_numero(valor, tipo)
        return valor
    
def consolidar_backup(carpeta_csv, archivo_backup, eliminar_carpeta=False, modificar_nombres=False):
    """
    Consolida todos los archivos CSV en la carpeta dada, agregando una columna de categoría
    en la primera posición, y guarda el resultado en un archivo pickle.

    Args:
        carpeta_csv (str): Ruta a la carpeta que contiene los CSV.
        archivo_backup (str): Ruta del archivo de backup (formato .pkl).
        eliminar_carpeta (bool): Si es True, elimina la carpeta después de consolidar.
    """
    try:
        # Lista de DataFrames
        dataframes = []

        # Procesar cada archivo CSV
        for archivo in os.listdir(carpeta_csv):
            if archivo.endswith(".csv"):
                ruta_archivo = os.path.join(carpeta_csv, archivo)
                # Leer el archivo
                df = pd.read_csv(ruta_archivo, index_col=0)
                # Extraer categoría del nombre del archivo (sin extensión)
                categoria = os.path.splitext(archivo)[0]
                # Modificar nombre categoria
                if modificar_nombres:
                    categoria = str(categoria).replace("_", " ").capitalize()
                # Agregar columna de categoría en la primera posición
                df.insert(0, "categoria", categoria)
                # Agregar al listado
                dataframes.append(df)

        # Concatenar todos los DataFrames
        if dataframes:
            df_consolidado = pd.concat(dataframes, ignore_index=True)
            display(df_consolidado)
            # Guardar en archivo pickle
            df_consolidado.to_pickle(f"{archivo_backup}.pkl")
            df_consolidado.to_csv(f"{archivo_backup}.csv")
            print(f"Backup consolidado guardado en: {archivo_backup}.pkl")

        # Eliminar carpeta si se especifica
        if eliminar_carpeta:
            shutil.rmtree(carpeta_csv)
            print(f"Carpeta '{carpeta_csv}' eliminada después del backup.")

    except Exception as e:
        print(f"Error durante la consolidación: {e}")


# STREAMERS

# Función principal
def extraer_lista_streamers(silent_mode=True):
    
    url = "https://twitchtracker.com/channels/ranking/spanish"
    rango = 51

    # Configuración del navegador
    chrome_options = Options()
    if silent_mode:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    driver.implicitly_wait(1)
    sleep(0.5)

    if not silent_mode:
        driver.maximize_window()

    # Cerrar pop-ups, si existen
    try:
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p").click()
        sleep(0.2)
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p").click()
        sleep(0.2)
    except NoSuchElementException:
        pass

    # Obtener encabezados dinámicamente
    encabezados_html = driver.find_elements(By.CSS_SELECTOR, "#channels thead tr th")
    headers = ["Nombre"] + [header.text.capitalize().strip().replace("\n", "_").replace(" ", "_") for header in encabezados_html[3:]] + ["Enlace"]
    # sleep(0.2)

    while headers.__contains__(""):
        headers.remove("")

    # Preparar para extraer datos
    datos = []

    for pagina in tqdm(range(1, rango)):  # Iterar sobre las 50 páginas
        for row in range(1, 54):  # Cada página tiene 50 streamers
            try:
                fila = driver.find_element(By.XPATH, f"//*[@id='channels']/tbody/tr[{row}]")
                
                # Extraer los datos
                streamer = fila.find_element(By.XPATH, "td[3]/a").text.capitalize()
                enlace = fila.find_element(By.XPATH, "td[3]/a").get_attribute("href")
                avg_viewers = limpiar_valor(fila.find_element(By.XPATH, "td[4]").text)
                time_streamed = limpiar_valor(fila.find_element(By.XPATH, "td[5]").text, tipo=float)
                peak_viewers = limpiar_valor(fila.find_element(By.XPATH, "td[6]").text)
                hours_watched = limpiar_valor(fila.find_element(By.XPATH, "td[7]").text)
                rank = limpiar_valor(fila.find_element(By.XPATH, "td[8]").text, tipo=int)
                followers_gained = limpiar_valor(fila.find_element(By.XPATH, "td[9]").text)
                total_followers = limpiar_valor(fila.find_element(By.XPATH, "td[10]").text)
                total_views = limpiar_valor(fila.find_element(By.XPATH, "td[11]").text)

                datos.append([streamer, avg_viewers, time_streamed, peak_viewers, hours_watched,
                                rank, followers_gained, total_followers, total_views, enlace])
                # # Crear DataFrame
                # df = pd.DataFrame(datos, columns=headers)
            except NoSuchElementException:
                # print(f"No se encontró información para la fila {row} en la página {pagina}.")
                pass
        # sleep(random.uniform(0.1, 0.5))
        # Ir a la siguiente página
        if pagina <= 50:
            # print(f"------ Página {pagina} ------")
            next_page_url = f"{url}?page={pagina+1}"
            driver.get(next_page_url)
            sleep(random.uniform(0.2, 1.5))  # Pausa aleatoria para evitar bloqueos
        else:
            break
        
    driver.quit()

    # Crear DataFrame
    df = pd.DataFrame(datos, columns=headers)

    # Guardar en un archivo CSV
    # ruta_almacenamiento = "../datos/raw/streamers/streamers_ranking"
    # df.to_csv(f"{ruta_almacenamiento}.csv", index=False)
    # df.to_pickle(f"{ruta_almacenamiento}.pkl")
    # print(f"Datos guardados en '{ruta_almacenamiento}.csv'.")
    return df


# Funciones para extraer la información de los streamers recogidos anteriormente
def extraer_info_stremaer_a_streamer(df_streamers: pd.DataFrame, concatenar = False, silent_mode = False, dividir = False):

    df_total = pd.DataFrame()
    # client, db = sbm.conectar_mongo(local=False)

    df_streamers.reset_index(inplace=True)
    # df_streamers = df_streamers[["index", "Nombre"]]

    # Creo el bucle para iterar por cada categoria
    for streamer in tqdm(df_streamers["Nombre"].tolist()):
        
        try:
            streamer = str(streamer)
            # streamers = df_streamers.loc[df_streamers["Nombre"] == categoria, "ID"].values[0]
            url = f"https://twitchtracker.com/{streamer.lower()}/statistics"
            url_categorias = f"https://twitchtracker.com/{streamer.lower()}/games"
            

            # Creo el driver
            if silent_mode:
                driver = Driver(uc = True, headless = True, browser = "chrome", guest = True)
            else:
                driver = Driver(uc = True, browser = "chrome", guest = True)
            driver.get(url)
            driver.implicitly_wait(1)
            sleep(0.2)
            if not silent_mode:
                driver.maximize_window()
            
            try:
                driver.find_element("xpath", "/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p").click()
                sleep(0.2)
                driver.find_element("xpath", "/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p").click()
                sleep(0.2)
            except NoSuchElementException:
                pass

            try:
                driver.find_element("xpath", "//*[@id='more-table']/button").click()
                sleep(0.2)
            except:
                pass
            
            # Obtengo la tabla que contiene los encabezados
            tabla_encabezados = driver.find_element(By.XPATH, "//*[@id='DataTables_Table_0_wrapper']/div[2]/div/div/div[1]/div/table")

            # Extraer encabezados desde el atributo 'aria-label'
            encabezados_elementos = tabla_encabezados.find_elements(By.TAG_NAME, "th")
            encabezados = [th.get_attribute("aria-label").split(":")[0] for th in encabezados_elementos]
            #encabezados = [encabezado.title().strip().replace("\n", "_").replace(" ", "_") for encabezado in encabezados]
            encabezados[2] = f"ViewersGain"
            encabezados[3] = f"PercentageGainViewers"
            encabezados[-3] = f"PercentageGainFollowers"
            encabezados[-2] = f"FollowesGain"

            # Obtengo la tabla que contiene los datos
            tabla_datos = driver.find_element(By.ID, "DataTables_Table_0")

            # Extraigo todas las filas para iterar posteriormente
            filas = tabla_datos.find_elements(By.TAG_NAME, "tr")

            # Extraigo los datos de cada fila
            datos = []
            for fila in filas[1:]:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                datos.append([celda.text.strip() for celda in celdas])

            # Crea el DataFrame
            df_datos_streamer = pd.DataFrame(datos, columns=encabezados)
            df_datos_streamer.rename(columns={"Gain": "HoursGain", f"%_Gain": "PercentageGainHours"}, inplace=True)

            # Limpieza de las columnas
            df_datos_streamer["AvgViewers"] = df_datos_streamer["AvgViewers"].str.replace(",", "").astype(int)
            #df_datos_streamer["AvgStreams"] = df_datos_streamer["AvgStreams"].str.replace(",", "").astype(int)
            df_datos_streamer["ViewersGain"] = df_datos_streamer["ViewersGain"].str.replace(",", "").replace("-", "0").astype(int)
            #df_datos_streamer["StreamsGain"] = df_datos_streamer["StreamsGain"].str.replace(",", "").replace("-", "0").astype(int)
            
            # Aplicar la función a la columna "HoursWatched"
            df_datos_streamer["HoursStreamed"] = df_datos_streamer["HoursStreamed"].apply(convertir_a_numero)
            df_datos_streamer["PeakViewers"] = df_datos_streamer["PeakViewers"].apply(limpiar_valor)
            #df_datos_streamer["PercentageGainStreams"] = df_datos_streamer["PercentageGainStreams"].apply(limpiar_valor)
            df_datos_streamer["PercentageGainViewers"] = df_datos_streamer["PercentageGainViewers"].apply(limpiar_valor)
            #df_datos_streamer["PercentageGainStreams"] = df_datos_streamer["PercentageGainStreams"].astype(float)
            df_datos_streamer["PercentageGainViewers"] = df_datos_streamer["PercentageGainViewers"].astype(float)

            # Separar el mes y el año
            df_nuevo = df_datos_streamer["Month"].str.split(" ", expand=True)
            df_nuevo.rename(columns={0: "Month", 1: "Year"}, inplace=True)
            df_nuevo = df_nuevo.reindex(columns=["Year", "Month"])
            df_concatenado = pd.concat([df_nuevo, df_datos_streamer.drop(columns="Month")], axis=1)

            driver.get(url_categorias)
            driver.wait_for_element_visible("body", timeout=10)

            # Cerrar pop-ups, si existen
            try:
                driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p", timeout=10)
                driver.click("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p")
                driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p", timeout=10)
                driver.click("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p")
            except:
                pass

            # Esperar a que la tabla cargue
            driver.wait_for_element_visible("table#games", timeout=10)

            # Extraer los nombres de los juegos
            game_elements = driver.find_elements(By.CSS_SELECTOR, "table#games tbody tr td a")
            game_elements = game_elements[:30]
            game_names = [game.text for game in game_elements if game.text.strip()]

            hours_elements = driver.find_elements(By.CSS_SELECTOR, "table#games tbody tr td.sorting_1 span")
            hours_elements = hours_elements[:30]
            hours_streameadas = [hour.text for hour in hours_elements if hour.text.strip()]
            # df_concatenado["Categorias"] = game_names
            df_categorias = pd.DataFrame({"nombre": [streamer] * len(game_names), "categoria": game_names, "horas_streameadas": hours_streameadas})
            # df_concatenado["id"] = df_concatenado.index  # Si no tienes un ID único, agrégalo
            # df_categorias["id_streamer"] = df_concatenado["id"].iloc[0]  # Relacionarlo con el primer ID del streamer
            df_concatenado.insert(0, "Nombre", streamer)

            # index_a = str(df_streamers.index[df_streamers["Nombre"] == streamer].to_list())
            # df_concatenado.insert(0, "id_streamer", [int(index_a.replace("[", "").replace("]", ""))] * len(df_concatenado))
            # display(df_concatenado)
            
            # df_categorias.insert(0, "id_streamer", [int(index_a.replace("[", "").replace("]", ""))] * len(df_categorias))
            # display(df_categorias)
            # Almacenamiento de estos datos en csv
            if dividir:
                # Separar por datos de viewers y por datos de streams
                df_datos_viewers = df_concatenado[["Year", "Month", "AvgViewers", "ViewersGain", "PercentageGainViewers", "PeakViewers", "HoursWatched"]]
                df_datos_streams = df_concatenado[["Year", "Month", "AvgStreams", "StreamsGain", "PercentageGainStreams", "HoursWatched"]]
                df_datos_viewers.to_csv(f"../datos/output/streamers/viewers/{streamer.replace(" ", "_").lower()}_viewers.csv")
                df_datos_streams.to_csv(f"../datos/output/streamers/streams/{streamer.replace(" ", "_").lower()}_streams.csv")
            else:
                df_concatenado.to_csv(f"../datos/output/streamers/all/{streamer.replace(" ", "_").lower()}.csv")
                df_categorias.to_csv(f"../datos/output/streamers/cats_streams/cat_streams_{streamer.replace(" ", "_").lower()}.csv")
                # sbm.insertar_en_coleccion(db, "historico_streamers", df_concatenado, True, "id_streamer")
                # sbm.insertar_en_coleccion(db, "categorias_streameadas", df_categorias, True, None)

            # Concatenación del data frame que va a contener todo
            if concatenar:
                df_concatenado.insert(0, "Nombre", streamer)
                df_total = pd.concat([df_total, df_concatenado], axis=0)

            # Espera aleatoria
            # n_aleatorio = f"0.{random.randint(1, 5)}"
            # sleep(float(n_aleatorio))

            # Cierro el driver
            driver.quit()

            # Esperamos a abrir la nueva ventana para no saturar la web
            # sleep(random.randint(1, 2))
            # sleep(random.uniform(0.2, 1.5))
            # if row == "World of Warcraft":
            #     break
        except:
            pass

        

    # # Apago el driver
    if 'driver' in locals():
        driver.quit()
    
    # client.close()

    if concatenar:
        return df_total
    

def asignar_ids_streamers(df: pd.DataFrame):
    """
    Asigna IDs a los streamers en el DataFrame según la columna 'Nombre'.
    
    Parámetros:
        df (pd.DataFrame): DataFrame con la columna 'Nombre' de los streamers.
        file_path (str): Ruta del archivo CSV que contiene los IDs y nombres de los streamers.

    Retorna:
        pd.DataFrame: DataFrame con una nueva columna 'Streamer_ID' asignando el ID a cada streamer.
                      Si la columna 'Nombre' no está presente, muestra un error.
    """
    # Cargar el archivo de IDs y nombres
    df_ids = pd.read_csv("../datos/raw/streamers/ids_streamers.csv")
    
    # Crear el diccionario de mapeo {Nombre: Streamer_ID}
    streamers_id_dict = df_ids.set_index("Nombre")["Streamer_ID"].to_dict()

    df.columns = df.columns.str.lower()
    
    if "nombre" not in df.columns:
        print("Error: El DataFrame no contiene la columna 'Nombre'. No se pueden asignar IDs.")
        return None  # Retorna el DataFrame sin cambios
    
    # Asignar IDs usando el diccionario generado
    df["id_streamer"] = df["nombre"].map(streamers_id_dict)

    # Mover la columna 'Streamer_ID' al inicio
    column_order = ["id_streamer"] + [col for col in df.columns if col != "id_streamer"]
    df = df[column_order]

    return df