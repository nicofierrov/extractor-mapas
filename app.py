import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import cv2
import numpy as np
import pandas as pd
import re
from PIL import Image
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Extractor de Vértices Topográficos", layout="wide")

st.title("🗺️ Extractor de Coordenadas UTM desde Mapas (PDF/Img)")
st.markdown("""
Esta aplicación soluciona el problema de los 'PDF híbridos'. 
Convierte el mapa en imagen, detecta texto mediante visión artificial (OCR) y estructura los datos.
""")

# --- BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.header("Configuración")
dpi_input = st.sidebar.slider("Calidad de Escaneo (DPI)", 200, 500, 300, help="Más alto es mejor para letras pequeñas, pero más lento.")
threshold_val = st.sidebar.slider("Filtro de Contraste", 0, 255, 150, help="Ajusta para limpiar el ruido de fondo.")

# --- FUNCIONES DE PROCESAMIENTO ---

def preprocess_image(image_pil):
    """Convierte imagen a CV2, escala de grises y aplica umbralización para resaltar números."""
    image_np = np.array(image_pil)
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    
    # Aplicar umbralización (Binarización) para separar texto del fondo (mapa)
    # Esto deja el texto negro y el fondo blanco puro
    _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)
    
    return thresh

def parse_ocr_text(text):
    """Busca patrones de coordenadas en el texto sucio extraído."""
    data = []
    # Regex explicada:
    # ^\s*(\d+) -> Busca el número de vértice al inicio (ej: 1, 2, 40)
    # \D+ -> Ignora cualquier caracter no numérico (espacios, puntos sucios)
    # (\d{3}[.,]?\d{3}\.?\d*) -> Captura coordenada ESTE (aprox 6 dígitos)
    # \D+ -> Separador
    # (\d{1,2}[.,]?\d{3}[.,]?\d{3}\.?\d*) -> Captura coordenada NORTE (aprox 7 dígitos)
    
    # Nota: Esta regex es flexible para tolerar errores comunes de OCR como puntos en vez de comas
    pattern = re.compile(r"(\d+)\s+[:;.|]?\s*(\d{3}[., ]?\d{3}[.,]?\d*)\s+[:;.|]?\s*(\d{1,2}[., ]?\d{3}[., ]?\d{3}[.,]?\d*)")
    
    lines = text.split('\n')
    for line in lines:
        match = pattern.search(line)
        if match:
            v, este, norte = match.groups()
            # Limpieza final de caracteres extraños en los números
            este_clean = este.replace('.', '').replace(',', '').replace(' ', '')
            norte_clean = norte.replace('.', '').replace(',', '').replace(' ', '')
            
            # Asumimos que son metros, añadimos punto decimal si falta (opcional, lógica simple aquí)
            data.append({
                "Vértice": int(v),
                "Este": este_clean,
                "Norte": norte_clean,
                "Texto_Original": line.strip() # Para depuración
            })
    return pd.DataFrame(data)

# --- INTERFAZ PRINCIPAL ---

uploaded_file = st.file_uploader("Sube tu archivo (PDF o Imagen)", type=['pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    st.info("Procesando archivo... esto puede tomar unos segundos.")
    
    images = []
    
    # 1. Convertir PDF a Imagen (o leer imagen directa)
    if uploaded_file.type == "application/pdf":
        try:
            # Convertimos solo la primera página por defecto, o todas
            images_from_pdf = convert_from_bytes(uploaded_file.read(), dpi=dpi_input)
            images.extend(images_from_pdf)
            st.success(f"PDF cargado: {len(images)} páginas procesadas como imágenes.")
        except Exception as e:
            st.error(f"Error al convertir PDF. Asegúrate de tener Poppler instalado. Detalle: {e}")
    else:
        image = Image.open(uploaded_file)
        images.append(image)

    # 2. Mostrar selector de página si hay varias
    page_num = 0
    if len(images) > 1:
        page_num = st.slider("Selecciona la página donde está la tabla", 1, len(images), 1) - 1
    
    target_image = images[page_num]

    # 3. Herramienta de recorte (Simulada visualmente)
    st.write("### 1. Vista Previa y Pre-procesamiento")
    st.write("El sistema intentará leer toda la página. Si la tabla es pequeña, el OCR puede fallar.")
    
    # Procesar imagen
    processed_img = preprocess_image(target_image)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(target_image, caption="Imagen Original", use_column_width=True)
    with col2:
        st.image(processed_img, caption="Imagen Procesada para OCR (Alto Contraste)", use_column_width=True, clamp=True)

    # 4. Botón de Acción
    if st.button("🔍 Extraer Coordenadas con IA"):
        
        # Configuración Tesseract para bloques de texto numérico (psm 6 asume bloque de texto uniforme)
        custom_config = r'--oem 3 --psm 6' 
        
        # Ejecutar OCR
        text_extracted = pytesseract.image_to_string(processed_img, config=custom_config)
        
        st.write("### 2. Texto Crudo Detectado")
        with st.expander("Ver texto sin procesar (para depuración)"):
            st.text(text_extracted)
        
        # 5. Estructurar Datos
        df = parse_ocr_text(text_extracted)
        
        if not df.empty:
            st.write("### 3. Tabla Digitalizada")
            st.dataframe(df)
            
            # Conversión a CSV
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Descargar como Excel (CSV)",
                data=csv,
                file_name='vertices_extraidos.csv',
                mime='text/csv',
            )
            st.success("¡Extracción completada! Verifica los números antes de usar.")
        else:
            st.warning("⚠️ No se detectaron patrones de coordenadas claros. Intenta:\n1. Subir una captura de pantalla SOLO de la tabla.\n2. Ajustar el filtro de contraste en la barra lateral.")