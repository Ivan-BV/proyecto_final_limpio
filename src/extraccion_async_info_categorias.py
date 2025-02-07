# ----- Versión funcional -----
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
from tqdm import tqdm
from time import sleep
import sys
sys.path.append("../")
from src import soporte_bbdd_mongo as sbm

# Función de limpieza (debes definir convertir_a_numero y limpiar_valor)
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

def extraer_datos_categoria(categoria, twitch_id, max_retries = 5, concatenar = False, dividir = False, silent_mode = True):
    # print(f"\nIniciando extracción de {categoria}")
    url = f"https://twitchtracker.com/games/{twitch_id}"
    retries = 0
    while retries < max_retries:
        try:
            driver = Driver(uc=True, headless=silent_mode, browser="chrome", guest=True, disable_gpu=True)
            driver.get(url)
            driver.wait_for_element_visible("body", timeout=10)  # Asegurar que la página cargue

            if driver.current_url != url:
                # print(f"\nError: El navegador no se redirigió a {url}. Intentando de nuevo...")
                # driver.get(url)
                # driver.wait_for_element_visible("body", timeout=10)
                raise Exception(f"El navegador no se redirigió a {url}. URL actual: {driver.current_url}")

            try:
                driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p", timeout=10)
                driver.click("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p")
                driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p", timeout=10)
                driver.click("/html/body/div[4]/div[2]/div[3]/div[3]/div[2]/button[2]/p")
            except:
                pass

            # Espera hasta que la tabla esté lista
            driver.wait_for_element_visible("//*[@id='DataTables_Table_0_wrapper']/div[2]/div/div/div[1]/div/table", timeout=10)
            tabla_encabezados = driver.find_element(By.XPATH, "//*[@id='DataTables_Table_0_wrapper']/div[2]/div/div/div[1]/div/table")
            encabezados = [th.get_attribute("aria-label").split(":")[0] for th in tabla_encabezados.find_elements(By.TAG_NAME, "th")]
            encabezados[2], encabezados[3] = "ViewersGain", "PercentageGainViewers"
            encabezados[-3], encabezados[-2] = "PercentageGainStreams", "StreamsGain"

            driver.wait_for_element_visible("#DataTables_Table_0", timeout=10)
            tabla_datos = driver.find_element(By.ID, "DataTables_Table_0")
            filas = tabla_datos.find_elements(By.TAG_NAME, "tr")
            datos = [[celda.text.strip() for celda in fila.find_elements(By.TAG_NAME, "td")] for fila in filas[1:]]
            df_datos_categoria = pd.DataFrame(datos, columns=encabezados)

            # Limpieza de datos
            df_datos_categoria["AvgViewers"] = df_datos_categoria["AvgViewers"].str.replace(",", "").astype(int)
            df_datos_categoria["AvgStreams"] = df_datos_categoria["AvgStreams"].str.replace(",", "").astype(int)
            df_datos_categoria["ViewersGain"] = df_datos_categoria["ViewersGain"].str.replace(",", "").replace("-", "0").astype(int)
            df_datos_categoria["StreamsGain"] = df_datos_categoria["StreamsGain"].str.replace(",", "").replace("-", "0").astype(int)
            df_datos_categoria["HoursWatched"] = df_datos_categoria["HoursWatched"].apply(convertir_a_numero)
            df_datos_categoria["PercentageGainStreams"] = df_datos_categoria["PercentageGainStreams"].apply(limpiar_valor)
            df_datos_categoria["PercentageGainViewers"] = df_datos_categoria["PercentageGainViewers"].apply(limpiar_valor)

            # Separar el mes y el año
            df_nuevo = df_datos_categoria["Month"].str.split(" ", expand=True)
            df_nuevo.rename(columns={0: "Month", 1: "Year"}, inplace=True)
            df_nuevo = df_nuevo.reindex(columns=["Year", "Month"])
            df_concatenado = pd.concat([df_nuevo, df_datos_categoria.drop(columns="Month")], axis=1)

            if dividir:
                # Separar por datos de viewers y por datos de streams
                df_datos_viewers = df_concatenado[["Year", "Month", "AvgViewers", "ViewersGain", "PercentageGainViewers", "PeakViewers", "HoursWatched"]]
                df_datos_streams = df_concatenado[["Year", "Month", "AvgStreams", "StreamsGain", "PercentageGainStreams", "HoursWatched"]]

                # Almacenamiento de estos datos en csv
                df_datos_viewers.to_csv(f"../datos/output/categorias/viewers/{categoria.replace(":", "").replace(" ", "_").lower()}_viewers.csv")
                df_datos_streams.to_csv(f"../datos/output/categorias/streams/{categoria.replace(":", "").replace(" ", "_").lower()}_streams.csv")
            else:
                # df_concatenado.insert(0, "nombre", categoria)
                df_concatenado.to_csv(f"../datos/output/categorias/all/{categoria.replace(":", "").replace(" ", "_").lower()}.csv")
            
            if concatenar:
                df_concatenado.insert(0, "Nombre", categoria)
                return df_concatenado
            else:
                df_concatenado.insert(0, "Nombre", categoria)
                client, db = sbm.conectar_mongo(local = True)
                sbm.insertar_en_coleccion(db, "historico_categorias", df_concatenado, silent_mode=True)
                client.close()
            return 
        except Exception as e:
                retries += 1
        finally:
            driver.quit()
            # print(f"\nExtracción de {categoria} finalizada")
    return 

def main():
    # Cargar los datos
    data_pickle = pd.read_pickle("../datos/raw/categorias/identificadores/categories_id.pkl")
    df_categorias = pd.DataFrame(data_pickle).head(10)

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        tareas = {
            executor.submit(extraer_datos_categoria, row["nombre"], row["id"]): row["nombre"]
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

# Ejecutar la función principal
if __name__ == "__main__":
    main()


# ----- Versión más limpia y un poco más eficiente -----

# import pandas as pd
# from seleniumbase import Driver
# from selenium.webdriver.common.by import By
# import concurrent.futures
# from tqdm import tqdm
# import os
# import sys
# from time import sleep

# sys.path.append("../")
# from . import soporte_bbdd_mongo as sbm

# # Funciones de limpieza
# def convertir_a_numero(valor, tipo=float):
#     if not valor:
#         return 0
#     valor = valor.replace(",", "").strip()
#     if "M" in valor:
#         return float(valor.replace("M", "")) * 1_000_000
#     elif "K" in valor:
#         return float(valor.replace("K", "")) * 1_000
#     try:
#         return tipo(valor)
#     except ValueError:
#         return 0

# def limpiar_valor(valor, tipo=float):
#     if not valor or valor in ["-", "--"]:  # Valores vacíos o guiones
#         return 0
#     valor = valor.replace("%", "").replace("+", "").replace("hours", "").replace(",", "").strip()
#     try:
#         return convertir_a_numero(valor, tipo)
#     except ValueError:
#         return 0  # Evitar fallos por valores inesperados

# def extraer_datos_categoria(categoria, twitch_id, max_retries=5, concatenar=False, dividir=False, silent_mode=False):
#     url = f"https://twitchtracker.com/games/{twitch_id}"
#     retries = 0
#     driver = None  # Se inicializa fuera del bucle

#     while retries < max_retries:
#         try:
#             driver = Driver(uc=True, headless=silent_mode, browser="chrome", disable_gpu=True)
#             driver.get(url)  # Volvemos a cargar la URL en cada intento
#             driver.implicit_wait(5)
#             driver.wait_for_element_visible("body", timeout=20)

#             if driver.current_url != url:
#                 raise Exception(f"Redirección incorrecta: {driver.current_url}")

#             # Cerrar pop-ups si aparecen
#             try:
#                 driver.wait_for_element_visible("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p", timeout=5)
#                 driver.click("/html/body/div[4]/div[2]/div[2]/div[3]/div[2]/button[2]/p")
#             except:
#                 pass

#             driver.wait_for_element_visible("#DataTables_Table_0", timeout=10)
#             tabla = driver.find_element(By.ID, "DataTables_Table_0")
#             filas = tabla.find_elements(By.TAG_NAME, "tr")

#             # Extraer encabezados
#             encabezados = [th.get_attribute("aria-label").split(":")[0] for th in tabla.find_elements(By.TAG_NAME, "th")]
#             encabezados[2], encabezados[3] = "ViewersGain", "PercentageGainViewers"
#             encabezados[-3], encabezados[-2] = "PercentageGainStreams", "StreamsGain"

#             # Extraer datos
#             datos = [[celda.text.strip() for celda in fila.find_elements(By.TAG_NAME, "td")] for fila in filas[1:]]
#             df_datos_categoria = pd.DataFrame(datos, columns=encabezados)

#             # Limpieza de datos
#             df_datos_categoria["AvgViewers"] = df_datos_categoria["AvgViewers"].str.replace(",", "").astype(int)
#             df_datos_categoria["AvgStreams"] = df_datos_categoria["AvgStreams"].str.replace(",", "").astype(int)
#             df_datos_categoria["ViewersGain"] = df_datos_categoria["ViewersGain"].str.replace(",", "").replace("-", "0").astype(int)
#             df_datos_categoria["StreamsGain"] = df_datos_categoria["StreamsGain"].str.replace(",", "").replace("-", "0").astype(int)
#             df_datos_categoria["HoursWatched"] = df_datos_categoria["HoursWatched"].apply(convertir_a_numero)
#             df_datos_categoria["PercentageGainStreams"] = df_datos_categoria["PercentageGainStreams"].apply(limpiar_valor)
#             df_datos_categoria["PercentageGainViewers"] = df_datos_categoria["PercentageGainViewers"].apply(limpiar_valor)

#             # Separar mes y año
#             df_fecha = df_datos_categoria["Month"].str.split(" ", expand=True)
#             df_fecha.columns = ["Month", "Year"]
#             df_concatenado = pd.concat([df_fecha, df_datos_categoria.drop(columns="Month")], axis=1)

#             # Guardado en CSV
#             nombre_archivo = categoria.replace(":", "").replace(" ", "_").lower()
#             output_path = "../datos/output/categorias"
            
#             if dividir:
#                 df_datos_viewers = df_concatenado[["Year", "Month", "AvgViewers", "ViewersGain", "PercentageGainViewers", "PeakViewers", "HoursWatched"]]
#                 df_datos_streams = df_concatenado[["Year", "Month", "AvgStreams", "StreamsGain", "PercentageGainStreams", "HoursWatched"]]

#                 df_datos_viewers.to_csv(os.path.join(output_path, "viewers", f"{nombre_archivo}_viewers.csv"))
#                 df_datos_streams.to_csv(os.path.join(output_path, "streams", f"{nombre_archivo}_streams.csv"))
#             else:
#                 df_concatenado.to_csv(os.path.join(output_path, "all", f"{nombre_archivo}.csv"))

#             # Guardado en MongoDB
#             if concatenar:
#                 return df_concatenado
#             else:
#                 df_concatenado.insert(0, "Nombre", categoria)
#                 client, db = sbm.conectar_mongo(local=False)
#                 sbm.insertar_en_coleccion(db, "historico_categorias", df_concatenado, silent_mode=True)
#                 client.close()

#             driver.quit()  # Cerrar después de éxito
#             return 

#         except Exception as e:
#             retries += 1
#             sleep(2**retries)  # Retraso exponencial
#             driver.quit()  # Cerrar el navegador antes de reiniciar

#     driver.quit()  # Cerrar al terminar los reintentos
#     return

# ### FUNCIÓN MAIN
# def main():
#     # Cargar los datos desde el pickle
#     data_pickle = pd.read_pickle("../datos/raw/categorias/identificadores/categories_id.pkl")
#     df_categorias = pd.DataFrame(data_pickle).head(10)

#     with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
#         tareas = {
#             executor.submit(extraer_datos_categoria, row["nombre"], row["id"]): row["nombre"]
#             for _, row in df_categorias.iterrows()
#         }

#         # Mostrar progreso con tqdm
#         for tarea in tqdm(concurrent.futures.as_completed(tareas), total=len(tareas)):
#             try:
#                 categoria = tareas[tarea]
#                 tarea.result(timeout=120)  # Establecer timeout de 2 minutos por tarea
#             except Exception as e:
#                 # print(f"\nError procesando {categoria}: {e}")
#                 pass

#     print("EXTRACCIÓN COMPLETADA 🚀")

# # Ejecutar la función principal solo si el script se ejecuta directamente
# if __name__ == "__main__":
#     main()
