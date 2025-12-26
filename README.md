# extractor-mapas

## English

### Demo Version
The final version of this tool is not public.

### About the Tool
This tool was developed to automate the extraction of geospatial information from flat PDFs *generated* and sent by the Dirección de Obras Hidráulicas (DOH). It identifies service areas for Rural Sanitation Services (Servicios Sanitarios Rurales - SSR), tanks, and other system elements.

The tool locates the table of vertices (or points) and performs OCR in the area if necessary. This is because the PDF files are partially digitized. Additionally, it looks for the projection within the files—often hidden from the naked eye (e.g., written in white letters on a white background). Generally, the WGS1984 UTM18S projection is used for the Isla Grande de Chiloé, but due to inconsistencies in the data, each case must be verified individually.

These flat PDFs were generated in QGIS and sent by the DOH.

---

## Español

### Versión de Demostración
La versión final de esta herramienta no es pública.

### Sobre la Herramienta
Esta herramienta fue desarrollada para automatizar la extracción de información geoespacial de archivos PDF planos *generados* y enviados por la Dirección de Obras Hidráulicas (DOH). Identifica las áreas de servicios de Servicios Sanitarios Rurales (SSR), estanques y otros elementos del sistema.

La herramienta localiza la tabla de vértices (o puntos) y realiza un OCR en la zona si es necesario debido a que los archivos PDF están parcialmente digitalizados. Además, busca la proyección en los archivos, la cual muchas veces está oculta a simple vista (por ejemplo, escrita en letras blancas sobre fondo blanco). Generalmente, se utiliza la proyección WGS1984 UTM18S para la Isla Grande de Chiloé, pero debido a las inconsistencias en los datos, cada caso debe ser verificado individualmente.

Estos PDF planos fueron generados en QGIS y enviados por la DOH.