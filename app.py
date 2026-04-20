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

    # 2. Lógica de Plurales/Singulares (Mapeo automático de tus 38 variables)
    if es_plural:
        plural_dict = {
            'EL_LOS': 'LOS', 'AUTORIZANTE_AUTORIZANTES': 'AUTORIZANTES',
            'DENOMINADO_DENOMINADA_DENOMINADOS': 'DENOMINADOS',
            'AL_A_LOS': 'A LOS', 'DEL_DE_LOS': 'DE LOS',
            'UNICO_UNICOS': 'UNICOS', 'EXCLUSIVO_EXCLUSIVOS': 'EXCLUSIVOS',
            'TITULAR_TITULARES': 'TITULARES', 'MANDANTE_MANDANTES': 'MANDANTES',
            'autoriza_autorizan': 'autorizan', 'declara_declaran': 'declaran',
            'encuentra_encuentran': 'encuentran', 'inhibido_inhibidos': 'inhibidos',
            'informado_informados': 'informados', 'faculta_facultan': 'facultan',
            'sea_sean': 'sean', 'abonará_abonarán': 'abonarán',
            'vendiera_vendieran': 'vendieran', 'deberá_deberán': 'deberán',
            'presentara_presentaran': 'presentaran', 'retractare_retractaren': 'retractaren',
            'acepta_aceptan': 'aceptan', 'manifiesta_manifiestan': 'manifiestan',
            'constituyen_constituye': 'constituyen', 'corresponderles_corresponderle': 'corresponderles',
            'su_sus': 'sus', 'respectiva_respectivas': 'respectivas',
            'dirección_direcciones': 'direcciones', 'postal_postales': 'postales',
            'correo_correos': 'correos', 'electrónico_electrónicos': 'electrónicos',
            'mencionado_mencionados': 'mencionados'
        }
    else:
        # Lógica de género para el singular
        s_gen = "A" if genero == "Femenino" else "O"
        art_gen = "LA" if genero == "Femenino" else "EL"
        plural_dict = {
            'EL_LOS': art_gen, 'AUTORIZANTE_AUTORIZANTES': 'AUTORIZANTE',
            'DENOMINADO_DENOMINADA_DENOMINADOS': f'DENOMINAD{s_gen}',
            'AL_A_LOS': 'AL', 'DEL_DE_LOS': 'DEL',
            'UNICO_UNICOS': 'UNICO', 'EXCLUSIVO_EXCLUSIVOS': 'EXCLUSIVO',
            'TITULAR_TITULARES': 'TITULAR', 'MANDANTE_MANDANTES': 'MANDANTE',
            'autoriza_autorizan': 'autoriza', 'declara_declaran': 'declaran',
            'encuentra_encuentran': 'encuentra', 'inhibido_inhibidos': 'inhibido',
            'informado_informados': 'informado', 'faculta_facultan': 'faculta',
            'sea_sean': 'sea', 'abonará_abonarán': 'abonará',
            'vendiera_vendieran': 'vendiera', 'deberá_deberán': 'deberá',
            'presentara_presentaran': 'presentara', 'retractare_retractaren': 'retractare',
            'acepta_aceptan': 'acepta', 'manifiesta_manifiestan': 'manifiesta',
            'constituyen_constituye': 'constituye', 'corresponderles_corresponderle': 'corresponderle',
            'su_sus': 'su', 'respectiva_respectivas': 'respectiva',
            'dirección_direcciones': 'dirección', 'postal_postales': 'postal',
            'correo_correos': 'correo', 'electrónico_electrónicos': 'electrónico',
            'mencionado_mencionados': 'mencionado'
        }
hoy = datetime.now()

#  Traductor de meses
    meses_es = {
        "January": "Enero", "February": "Febrero", "March": "Marzo", 
        "April": "Abril", "May": "Mayo", "June": "Junio",
        "July": "Julio", "August": "Agosto", "September": "Septiembre",
        "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }
    nombre_mes_ingles = hoy.strftime("%B")  # Esto saca "April"
    mes_castellano = meses_es.get(nombre_mes_ingles, nombre_mes_ingles) # Esto lo convierte a "Abril"
    
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
        'dia_firma': hoy.day, 'mes_firma': mes_castellano, 'ano_firma': hoy.year,
        'propietarios_extras': otros_propietarios
    }

    doc.render(contexto)
    
    # 4. Descarga
    output = BytesIO()
    doc.save(output)
    st.download_button("📥 Descargar Autorización", output.getvalue(), f"Autorizacion_{nombre}.docx")
