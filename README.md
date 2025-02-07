
# Recomendador de Streamers 🎮📺

Este proyecto tiene como objetivo crear un sistema de recomendación de streamers para viewers basado en contenido similar al que consumen. Utilizando datos obtenidos mediante scraping de Twitch y otras plataformas de streaming, se almacena la información de cada streamer, los juegos que transmiten, y otros parámetros relevantes para generar recomendaciones personalizadas.

## Tecnologías utilizadas ⚙️

- **Python**: Lenguaje de programación principal para todo el desarrollo del proyecto.
- **SeleniumBase**: Utilizado para realizar scraping de datos de manera eficiente.
- **MongoDB**: Base de datos NoSQL para almacenar la información de los streamers y juegos, debido a su flexibilidad y escalabilidad.
- **Streamlit**: Herramienta de visualización interactiva para presentar las recomendaciones y datos de los streamers.
- **Modelos de clasificación**: Utilizados para analizar patrones en el contenido consumido por los viewers y generar recomendaciones.

## Funcionalidades 🚀

- **Recomendación de streamers**: Basado en el contenido que los viewers consumen, el sistema sugiere streamers similares.
- **Comparación de streamers**: Permite comparar distintos streamers según diversas métricas.
- **Historial de streamers**: Muestra el historial de transmisiones de un streamer con detalles sobre los juegos que ha jugado.
- **Interactividad con Streamlit**: A través de una interfaz de usuario interactiva, los viewers pueden explorar las recomendaciones, comparar streamers y obtener información adicional con solo hacer clic.

## Estructura de la base de datos 📊

La base de datos está organizada en colecciones separadas por tipo de datos:

- **Streamers**: Información básica sobre cada streamer, como nombre, número de seguidores, juegos transmitidos, etc.
- **Juegos**: Detalles sobre los juegos que se transmiten en las sesiones de los streamers.
- **Historial**: Un registro completo de las transmisiones de cada streamer.

## Uso 💻

1. Clona este repositorio en tu máquina local:

   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   ```

2. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el scraper para extraer los datos (modifica el script según tus necesidades):

   ```bash
   python scraper.py
   ```

4. Corre la aplicación de Streamlit para acceder a la interfaz de usuario:

   ```bash
   streamlit run app.py
   ```

## Contribuciones ✨

Si deseas contribuir a este proyecto, por favor crea un fork del repositorio y envía un pull request con tus mejoras. Asegúrate de seguir las mejores prácticas y de escribir pruebas para cualquier nueva funcionalidad que agregues.

<!-- ## Licencia 📜

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles. -->

## Contacto 📧

Si tienes alguna duda, no dudes en contactarme.
