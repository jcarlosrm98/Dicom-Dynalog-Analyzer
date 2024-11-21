# Dicom & Dynalog Files Analyzer

En este repositorio encontrarás un script de Python que permite al usuario poder leer y analizar los archivos Dicom y Dynalog para los tratamientos en radioterapia.
Para ello, creé un primer script que permite leer los ficheros, analizarlos utilizando diferentes métricas, grafica los resultados obtenidos y también hay un script de Django para crear una interfaz web para mostrar los resultados obtenidos. Para el análisis de los archivos Dicom, además de etiquetas de interés, como los datos de estructuras, también calcula la dosis máxima para cada estructura del archivo y lo grafica. Para los archivos dynalog, además de leerlos, también grafica su fluencia real, su fluencia planificada y su error. También incluye un proyecto de Django para tener una interfaz web sencilla, así como un script donde se adjuntan un entorno de pruebas hecho con pytest.

## Status

Personal Project, Beta Status, 2024.

## Technology Stack

- “Pandas”: para poder consultar los archivos.
- “Pydicom”: para poder manejar archivos DICOM.
- “Matplotlib”: para poder graficar los datos.
- “Seaborn”: para poder graficar los datos.
- “Django”: para crear una interfaz web donde poder reflejar los gráficos.
- “Pytest”: para crear tests que apoyasen a la tarea realizada.
- “Pytest-mock”: Plugin para Pytest que permite usar “mocker” (para capturar la llamada de los gráficos).


## How to use it

Para utilizar el script, primero es necesario generar un entorno donde todas las dependencias necesarias estén instaladas. Después es necesario ir a la terminal (o correr los archivos localmente) para que funcionen. Si se desea leer otros archivos Dicom y Dynalog, es necesario cambiar la ruta relativa de los archivos dentro del script. Es necesario correr con python el archivo **analyzer.py**. Si desea visualizar la interfaz web, es necesario que ponga el siguiente comando desde la terminal: **python manage.py runserver**. Para que se ejecuten los tests, es necesario que se ponga el siguiente comando desde la terminal: **pytest tests.py**.

## Resources

Para obtener los archivos Dicom y Dynalog, decidí utilizar archivos de prueba, totalmente público, para no comprometer la privacidad de nadie. Estos archivos se pueden encontrar en:
..* [Dicom files](https://github.com/dicompyler/dicompyler-core/tree/master/tests/testdata/example_data)
..* [Dynalog files](https://physik.gesundheitsverbund.at/dmlc/dmlc_ml.htm)
