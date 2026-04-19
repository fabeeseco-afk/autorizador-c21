import streamlit as st
from docxtpl import DocxTemplate
from num2words import num2words
import requests
from io import BytesIO
from datetime import datetime

# CONFIGURACIÓN INICIAL
ID_PLANTILLA = "1gi3_4XdX8i55GZRAmFGKsOTVy88Gbbz9"
URL_DRIVE = f"https://docs.google.com/uc?export=download&id={ID_PLANTILLA}"

st.set_page_config(page_title="Generador C21 Sociaville", layout="centered")
st.title("📄 Generador de Autorizaciones")

# --- FUNCIONES DE AUTOMATIZACIÓN ---
def numero_a_letras(numero):
    return num2words(numero, lang='es').upper()

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("Configuración General")
    es_plural = st.toggle("¿Es más de un propietario?", value=False)
    genero = st.radio("Género del firmante principal:", ["Masculino", "Femenino"])
    comision = st.selectbox("Comisión %:", [3, 5])

# Datos del Propietario Principal
st.subheader("Datos del Propietario 1")
nombre = st.text_input("Nombre y Apellido")
dni = st.text_input("DNI")
estado_civil = st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"])
domicilio = st.text_input("Domicilio Real")
email = st.text_input("Email")
telefono = st.text_input("Teléfono")

# Lógica de "Firmantes Infinitos"
otros_propietarios = []
if es_plural:
    st.subheader("Otros Propietarios")
    cantidad = st.number_input("¿Cuántos más?", min_value=1, step=1)
    for i in range(cantidad):
        col1, col2 = st.columns(2)
        with col1:
            n = st.text_input(f"Nombre Propietario {i+2}", key=f"n_{i}")
        with col2:
            d = st.text_input(f"DNI Propietario {i+2}", key=f"d_{i}")
        otros_propietarios.append({"nombre": n, "dni": d})

st.divider()
st.subheader("Datos del Inmueble")
direccion_inmueble = st.text_input("Dirección del Inmueble")
ciudad = st.text_input("Ciudad", value="Villa Carlos Paz")
precio_val = st.number_input("Precio de Venta (Solo números)", min_value=0)

# --- PROCESAMIENTO ---
if st.button("GENERAR DOCUMENTO"):
    # 1. Descargar la plantilla de Drive
    respuesta = requests.get(URL_DRIVE)
    doc = DocxTemplate(BytesIO(respuesta.content))

    # 2. Lógica de Plurales/Singulares (Mapeo automático)
    if es_plural:
        plural_dict = {
            'EL_LOS': 'LOS', 'AUTORIZANTE_AUTORIZANTES': 'AUTORIZANTES',
            'autoriza_autorizan': 'autorizan', 'su_sus': 'sus',
            'UNICO_UNICOS': 'UNICOS', 'TITULAR_TITULARES': 'TITULARES'
            # (Aquí agregarías el resto de las 38 variables que listaste)
        }
    else:
        plural_dict = {
            'EL_LOS': 'EL', 'AUTORIZANTE_AUTORIZANTES': 'AUTORIZANTE',
            'autoriza_autorizan': 'autoriza', 'su_sus': 'su',
            'UNICO_UNICOS': 'UNICO', 'TITULAR_TITULARES': 'TITULAR'
        }

    # 3. Preparar el contexto (Lo que se inyecta al Word)
    hoy = datetime.now()
    contexto = {
        **plural_dict,
        'nombre': nombre, 'dni': dni, 'estado_civil': estado_civil,
        'domicilio': domicilio, 'email': email, 'teléfono': telefono,
        'direccion_inmueble': direccion_inmueble, 'ciudad': ciudad,
        'precio_numeros': f"{precio_val:,.0f}".replace(",", "."),
        'precio_letras': numero_a_letras(precio_val),
        'porcentaje_numero': comision,
        'porcentaje_letras': numero_a_letras(comision),
        'dia_firma': hoy.day, 'mes_firma': hoy.strftime("%B"), 'ano_firma': hoy.year,
        'propietarios_extras': otros_propietarios
    }

    doc.render(contexto)
    
    # 4. Descarga
    output = BytesIO()
    doc.save(output)
    st.download_button("📥 Descargar Autorización", output.getvalue(), f"Autorizacion_{nombre}.docx")
