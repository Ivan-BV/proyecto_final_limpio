import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
import concurrent.futures
from tqdm import tqdm
from time import sleep
import os
import sys
sys.path.append("../")
from src import soporte_bbdd_mongo as sbm

from IPython.display import display

# Función de limpieza reutilizable
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

# Función para extraer estadísticas mensuales de un streamer
def extraer_estadisticas_streamer(streamer, silent_mode=True, max_retries=5):
    url = f"https://twitchtracker.com/{streamer.lower()}/statistics"
    url_categorias = f"https://twitchtracker.com/{streamer.lower()}/games"
    retries = 0
    while retries < max_retries:
        try:
            driver = Driver(uc=True, headless=silent_mode, browser="chrome", guest=True, disable_gpu=True)
            driver.get(url)
            driver.wait_for_element_visible("body", timeout=10)

            print("pasa de url", flush=True)

            if driver.current_url != url:
                raise Exception(f"El navegador no se redirigió a {url}. URL actual: {driver.current_url}")
            
            print("pasa de fallo url", flush=True)

            # Cerrar pop-ups, si existen
            try:
                driver.find_element("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p", timeout=10).click()
                # driver.click("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p")
                sleep(0.2)
                driver.find_element("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p", timeout=10).click()
                # driver.click("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p")
            except:
                pass

            print("pasa de cookies", flush=True)

            # Asegurarse de que la tabla está visible
            driver.wait_for_element_visible("//*[@id='DataTables_Table_0']", timeout=10)

            # Obtener encabezados de la tabla
            tabla_encabezados = driver.find_element(By.XPATH, "//*[@id='DataTables_Table_0_wrapper']/div[2]/div/div/div[1]/div/table")
            encabezados = [th.text.replace(" ", "_").strip() for th in tabla_encabezados.find_elements(By.TAG_NAME, "th")]

            # Cambiar nombres específicos de los encabezados
            if len(encabezados) >= 5:  # Comprobar que hay suficientes columnas
                encabezados[2], encabezados[3] = "ViewersGain", "PercentageGainViewers"
                encabezados[-3], encabezados[-2] = "PercentageGainStreams", "StreamsGain"
            print(encabezados, flush=True)

            # Obtener los datos de la tabla
            tabla_datos = driver.find_element(By.ID, "DataTables_Table_0")
            filas = tabla_datos.find_elements(By.TAG_NAME, "tr")
            datos = [[celda.text.strip() for celda in fila.find_elements(By.TAG_NAME, "td")] for fila in filas[1:]]

            # Crear DataFrame con encabezados y datos
            df_estadisticas = pd.DataFrame(datos, columns=encabezados)

            # Limpieza y transformación de datos
            df_estadisticas["Avg_Viewers"] = df_estadisticas["Avg_Viewers"].str.replace(",", "").astype(int)
            df_estadisticas["ViewersGain"] = df_estadisticas["ViewersGain"].str.replace(",", "").replace("-", "0").astype(int)
            df_estadisticas["PercentageGainViewers"] = df_estadisticas["PercentageGainViewers"].apply(limpiar_valor)
            df_estadisticas["Peak_Viewers"] = df_estadisticas["Peak_Viewers"].str.replace(",", "").astype(int)
            df_estadisticas["Hours_Streamed"] = df_estadisticas["Hours_Streamed"].apply(limpiar_valor)

            print("fin", flush=True)
            
            driver.get(url_categorias)
            driver.wait_for_element_visible("body", timeout=10)

            print("nueva url", flush=True)

            # Cerrar pop-ups, si existen
            try:
                driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p", timeout=10)
                driver.click("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p")
                driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p", timeout=10)
                driver.click("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p")
            except:
                pass

            print("pasa cookies nueva url", flush=True)

            # Esperar a que la tabla cargue
            driver.wait_for_element_visible("table#games", timeout=10)

            # Extraer los nombres de los juegos
            game_elements = driver.find_elements(By.CSS_SELECTOR, "table#games tbody tr td a")
            game_names = [game.text for game in game_elements if game.text.strip()]
            df_estadisticas["Categorias"] = game_names

            # Guardar los datos como CSV
            df_estadisticas.to_csv(f"../datos/output/streamers/all/{streamer}.csv", index=False)
            print(f"Datos guardados para {streamer}.", flush=True)
            df_estadisticas.insert(0, "Nombre", streamer)
            display(df_estadisticas)
            # client, db = sbm.conectar_mongo(local = True)
            # sbm.insertar_en_coleccion(db, "historico_streamers", df_estadisticas)
            # client.close()
            return 
        except Exception as e:
            retries += 1
            # print(f"Error en {streamer}, reintentando ({retries}/{max_retries})...: {e}")
        finally:
            driver.quit()
            # if 'driver' in locals():
            #     driver.quit()

    print(f"No se pudo obtener datos para {streamer} tras {max_retries} intentos.")
    return

# Función principal para procesar múltiples streamers
def main():
    # Cargar lista de streamers desde un archivo CSV
    data_pickle = pd.read_pickle("../datos/raw/streamers/streamers_ranking.pkl")
    df_categorias = pd.DataFrame(data_pickle).head(10)

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        tareas = {
            executor.submit(extraer_estadisticas_streamer, row["Nombre"]): row["Nombre"]
            for _, row in df_categorias.iterrows()
        }
        # for tarea in tqdm(concurrent.futures.as_completed(tareas), total=len(tareas)):
        for tarea in tqdm(concurrent.futures.as_completed(tareas), total=len(tareas)):
            try:
                categoria = tareas[tarea]
                tarea.result(timeout=120)
            except Exception as e:
                # print(f"Error {tareas[tarea]}")
                # print(f"\nError procesando {tareas[tarea]}: {e}")
                pass
                # print(f"\nError procesando {tareas[tarea]}")

    print("EXTRACCIÓN COMPLETADA")
    # ruta_csv = "../datos/raw/streamers/streamers_ranking.csv"
    # if not os.path.exists(ruta_csv):
    #     print(f"Error: El archivo '{ruta_csv}' no existe. Por favor, crea un archivo con los nombres de los streamers.")
    #     return

    # try:
    #     df_streamers = pd.read_csv(ruta_csv).head(5)
    #     if "Nombre" not in df_streamers.columns:
    #         print("Error: El archivo CSV debe tener una columna llamada 'Nombre'.")
    #         return
    #     streamers = df_streamers["Nombre"].dropna().to_list()
    # except Exception as e:
    #     print(f"Error al leer el archivo CSV: {e}")
    #     return

    # # Procesar cada streamer
    # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    #     resultados = list(tqdm(executor.map(extraer_estadisticas_streamer, streamers), total=len(streamers)))
        

    # print("EXTRACCIÓN COMPLETADA 🚀")

if __name__ == "__main__":
    main()
