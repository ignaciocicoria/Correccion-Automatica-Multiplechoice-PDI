import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


# Respuestas correctas definidas en la consigna
respuestas_correctas = {
    1: 'A', 2: 'A', 3: 'B', 4: 'A', 5: 'D', 6: 'B', 7: 'B', 8: 'C', 9: 'B', 10: 'A',
    11: 'D', 12: 'A', 13: 'C', 14: 'C', 15: 'D', 16: 'B', 17: 'A', 18: 'C', 19: 'C', 20: 'D',
    21: 'B', 22: 'A', 23: 'C', 24: 'C', 25: 'C'
}

# Almacenar resultados de todos los exámenes
resultados_finales = []

# Función para evaluar respuesta y condición de examen
def evaluar_respuestas(respuestas_detectadas, respuestas_correctas_dict, minimo_para_aprobar=20):
    """
    Recibe como argumento el diccionario de respuestas detectadas donde la clave es el número de pregunta
    y el valor la respuesta, las respuestas correctas establecidas y el mínimo de respuestas correctas
    para aprobar. Imprime en pantalla el resultado de cada pregunta y si el alumno aprobó o desaprobó el examen.
    """
    aciertos = 0
    print("Corrección del examen:")
    for i in range(1, 26):  # Preguntas 1 a 25
        correcta = respuestas_correctas_dict[i]
        detectada = respuestas_detectadas[i - 1]

        if detectada == correcta:
            print(f"Pregunta {i}: ✔ Correcta ({detectada})")
            aciertos += 1
        elif detectada == "X":
            print(f"Pregunta {i}: ✖ Sin respuesta o ambigua")
        else:
            print(f"Pregunta {i}: ✖ Incorrecta ({detectada} → correcta: {correcta})")

    print(f"\nTotal de aciertos: {aciertos}/25")
    if aciertos >= minimo_para_aprobar:
        print("✅ El alumno está APROBADO")
    else:
        print("❌ El alumno está DESAPROBADO")

# Función para contar caracteres válidos usando componentes conectadas
def contar_componentes_validas(img_bin, th_area=3):
    """
    Función que recibe como argumento una imagen de los campos del encabezado y un área mínima de la misma y 
    retorna la cantidad de componentes válidas y sus centros
    """

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        img_bin, connectivity=8, ltype=cv2.CV_32S
    )
    validos = stats[1:][stats[1:, -1] > th_area]  # Ignora fondo
    centros = centroids[1:][stats[1:, -1] > th_area]
    return len(validos), centros

# Función para validar campos
def validar_campos(campos):
    """
    Función que recibe como argumento los campos del encabezado y valida los mismos
    según los criterios establecidos. Name: Debe contener al menos dos palabras y no más de 25 caracteres.
    ID: Exactamente 8 caracteres, sin espacios. Code: Un único carácter. Date: 8 caracteres en total. Retorna el resultado
    en un diccionario.
    """
    resultados = {}

    # --- Campo: Name ---
    campo_name = campos[1]
    # Umbralado binario de la imagen
    cant_name, centros_name = contar_componentes_validas(campo_name)

    palabras = 1
    if len(centros_name) > 1:
        xs = sorted([c[0] for c in centros_name])
        difs = np.diff(xs)
        palabras += np.sum(difs > 9)  # Separación entre letras → palabras

    resultados['Name'] = "OK" if (2 <= palabras and cant_name <= 25) else "MAL"

    # --- Campo: ID ---
    campo_id = campos[3]
    # Umbralado binario de la imagen
    cant_id, centros_id = contar_componentes_validas(campo_id)

    espacios = 0
    if len(centros_id) > 1:
        xs_id = sorted([c[0] for c in centros_id])
        difs_id = np.diff(xs_id)
        espacios += np.sum(difs_id > 9)  # Separación entre letras → palabras

    resultados['ID'] = "OK" if cant_id == 8 and espacios == 0 else "MAL"

    # --- Campo: Code ---
    campo_code = campos[5]
    # Umbralado binario de la imagen
    cant_code, _ = contar_componentes_validas(campo_code)

    resultados['Code'] = "OK" if cant_code == 1 else "MAL"

    # --- Campo: Date ---
    campo_date = campos[7]
    # Umbralado binario de la image
    cant_date, _ = contar_componentes_validas(campo_date)

    resultados['Date'] = "OK" if cant_date == 8 else "MAL"

    return resultados

def agrupar_lineas(posiciones, distancia_minima=3):
    """
    Recibe como argumento las posiciones de un grupo de lineas y una distancia mínima y las agrupa en una misma línea 
    según su promedio en caso de que su distancia sea menor a la mínima.
    """
    agrupadas = []
    grupo_actual = [posiciones[0]]

    for i in range(1, len(posiciones)):
        #Si la posición actual está cerca  de la anterior, se agrega al grupo 
        if posiciones[i] - posiciones[i - 1] <= distancia_minima:
            grupo_actual.append(posiciones[i])
        #Sino se cierra el grupo y se calcula el promedio, y se pasa al siguiente grupo
        else:
            agrupadas.append(int(np.mean(grupo_actual)))
            grupo_actual = [posiciones[i]]

    agrupadas.append(int(np.mean(grupo_actual)))
    return agrupadas

# Obtener ruta del directorio actual (donde está el .py)
try:
    dir_actual = os.path.dirname(os.path.abspath(__file__))
except NameError:
    dir_actual = os.getcwd()


# Cargar imagen en escala de grises
for num in range(5):
    filename = f"multiple_choice_{num + 1}.png"
    ruta = os.path.join(dir_actual, filename)
    img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)

    print(f"📄 Evaluando exámen: {filename}")
    
    # Detectar lo que no es blanco
    no_blanco = img< 240
    no_blanco_uint8 = no_blanco.astype(np.uint8)
    
    # Suma por filas
    enc_rows = np.sum(no_blanco_uint8, axis=1)

    # Umbral horizontal
    umbral_horizontal = 300
    
    # Detección de líneas horizontales (sin agrupar)
    lineas_horizontales_raw = np.where(enc_rows > umbral_horizontal)[0]

    # Agrupar líneas cercanas
    lineas_horizontales = agrupar_lineas(lineas_horizontales_raw, distancia_minima=2)

    # Coordenadas para recorte vertical (encabezado de una sola fila)
    y_ini = lineas_horizontales[0]+3#se suma 3 para que recorte la primer línea
    y_fin = lineas_horizontales[-1]
    
    # Recorte del encabezado
    encabezado = img[y_ini:y_fin, :]

    # Graficamos el encabezado recortado
    plt.figure(figsize=(10, 8))
    plt.imshow(encabezado, cmap='gray')
    plt.title("Imagen encabeado")
    plt.axis("off")
    plt.show()
    
    # Detectar lo que no es blanco
    no_blanco_enc = encabezado < 240
    no_blanco_uint8_enc = no_blanco_enc.astype(np.uint8)

    # Suma por columnas 
    enc_cols = np.sum(no_blanco_uint8_enc, axis=0)

    # Umbrales
    umbral_vertical = 18
   
    # Detección de líneas (sin agrupar)
    lineas_verticales_raw = np.where(enc_cols > umbral_vertical)[0]

    # Agrupar líneas cercanas
    lineas_verticales = agrupar_lineas(lineas_verticales_raw, distancia_minima=3)

   # Umbralizar detectando lo que no es blanco
    no_blanco_enc = encabezado <200
    no_blanco_uint8_enc = no_blanco_enc.astype(np.uint8) * 255  # Para ver la imagen como binaria

    # Recorte de campos entre pares de líneas verticales
    campos = []
    for i in range(len(lineas_verticales) - 1):
        x_ini = lineas_verticales[i]+2#se suma dos para que recorte la primer línea
        x_fin = lineas_verticales[i + 1]
        campo = no_blanco_uint8_enc[:, x_ini:x_fin]
        campos.append(campo)
        
    #Validamos campos
    resultados = validar_campos(campos)
    print("Resultados de validación:")
    for campo, estado in resultados.items():
        print(f"{campo}: {estado}")

    #Recortamos la región de respuestas de la imagen
    img_respuestas = img[y_fin+2: , : ]
    
    #Graficamos la imagen recortada con las respuestas
    plt.figure(figsize=(10, 8))
    plt.imshow(img_respuestas, cmap='gray')
    plt.title("Imagen respuestas")
    plt.axis("off")
    plt.show()

    # Detectamos las zonas negras (donde hay letras/marcas) 
    img_zeros = img_respuestas < 240  # TRUE donde el pixel es negro
    """
    plt.figure(), plt.imshow(img_zeros, cmap='gray'), plt.title("Zonas negras (pixeles = 0)"), plt.show()
    """
    # Detectamos las filas que contienen algo 
    img_row_zeros = img_zeros.any(axis=1)  # Vector de booleanos: True donde hay negro en la fila
    img_row_zeros_idxs = np.argwhere(img_row_zeros)

    # Detectamos las columnas que contienen algo
    img_column_zeros = img_zeros.any(axis=0)  # Vector de booleanos: True donde hay negro en la columna
    img_column_zeros_idxs = np.argwhere(img_column_zeros)

    """
    xr_row = img_row_zeros * (img_respuestas.shape[1] - 1)
    yr_row = np.arange(img_respuestas.shape[0])

    xr_column = np.arange(img_respuestas.shape[1])
    yr_column = img_column_zeros * (img_respuestas.shape[0] - 1)

    # Mostrar imagen y superponer líneas rojas (filas) y azules (columnas)
    plt.figure(), plt.imshow(img_respuestas, cmap='gray')
    plt.plot(xr_row, yr_row, c='r')  # Líneas rojas para las filas
    plt.plot(xr_column, yr_column, c='b')  # Líneas azules para las columnas
    plt.title("Presencia de renglones (en rojo) y columnas (en azul)")
    plt.show()
    """
    # Obtener inicios y finales de los renglones 
    x = np.diff(img_row_zeros.astype(np.int8))#calcula la diferencia entre elementos consecutivos a lo largo de un eje dado (en este caso, las filas de la imagen).
    renglones_indxs = np.argwhere(x)#obtiene los indices donde hay cambios


    ii = np.arange(0, len(renglones_indxs), 2)
    renglones_indxs[ii] += 1  # Ajustamos los índices de inicio

    # Obtener inicios y finales de las columnas
    x2 = np.diff(img_column_zeros.astype(np.int8))
    columnas_indxs = np.argwhere(x2)

    ii2 = np.arange(0, len(columnas_indxs), 2)#Crea un array con índices desde 0 hasta el largo de renglones_indxs, con paso de 2.
    columnas_indxs[ii2] += 1  # Ajustamos los índices de inicio

    # Recortar los renglones y las columnas dentro de cada renglón
    # Ordena las columnas y reglones en una matriz con pares de coordenadas de incio y fin de cada uno(dos columnas)
    r_idxs = np.reshape(renglones_indxs, (-1, 2))
    columnas_idxs = np.reshape(columnas_indxs, (-1, 2))

    renglones = []
    #ir es el indice del reglon y idxs el inicio y fin del mismo
    for ir, idxs in enumerate(r_idxs):
        renglon_img = img_respuestas[idxs[0]:idxs[1], :]  # Imagen del renglón completo

        # Saltar las dos primeras columnas, comenzando desde la tercera columna
        columnas_idxs_reducidas = columnas_idxs[2:]  # Saltamos las dos primeras columnas

        columnas = []
        for ic, col_idxs in enumerate(columnas_idxs_reducidas):
            columna_img = renglon_img[:, col_idxs[0]:col_idxs[1]]  # Recortar cada columna dentro del renglón
            columnas.append({
                "ic": ic + 1,  # Índice dentro del renglón
                "cord": col_idxs, # coordenadas columna
                "img": columna_img  # Imagen recortada de la columna
            })

        renglones.append({
            "ir": ir + 1,  # Índice de renglón
            "cord": idxs,  # Coordenadas del renglón
            "img": renglon_img,  # Imagen completa del renglón
            "columnas": columnas  # Guardar las columnas dentro de este renglón
        })


    # Analizar cada columna y devolver las respuestas
    umbral = 0.7  # Umbral de los píxeles no nulos
    respuestas = {}

    # Definir las respuestas correspondientes para cada columna
    respuestas_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}

    for renglon in renglones:
        respuestas_renglon = []
        
        for columna in renglon["columnas"]:
            columna_img = columna["img"]
            
            # Contar los píxeles no nulos (distintos de cero)
            pixeles_no_nulos = np.sum(columna_img < 240)
            total_pixeles = columna_img.size
            
            # Calcular el porcentaje de píxeles no nulos
            porcentaje_no_nulos = pixeles_no_nulos / total_pixeles
            # Si el porcentaje supera el umbral, asignamos una respuesta
            if porcentaje_no_nulos > umbral:
                respuestas_renglon.append(respuestas_map.get(columna["ic"]))  # Mapeamos a 'A', 'B', 'C', 'D', 'E'
        
        # Guardamos las respuestas para este renglón
        if respuestas_renglon:   
            respuestas[renglon["ir"]] = respuestas_renglon


    # Convertimos el diccionario `respuestas` a una lista ordenada de respuestas detectadas
    respuestas_detectadas = []
    for i in range(1, 26):  # Preguntas 1 a 25
        marcadas = respuestas.get(i, [])
        if len(marcadas) == 1:
            respuestas_detectadas.append(marcadas[0])  # Única respuesta marcada
        else:
            respuestas_detectadas.append("X")  # Ninguna o múltiples marcadas

    # Evaluamos con la función nueva
    
    evaluar_respuestas(respuestas_detectadas, respuestas_correctas)

    # Guardamos el crop y estado de aprobación
    aprobado = sum([1 for i, r in enumerate(respuestas_detectadas, 1) if r == respuestas_correctas[i]]) >= 20
    crop_name = campos[1].copy()
    resultados_finales.append((crop_name, aprobado))


# Crear una imagen de resumen con los nombres y colores de estado
fig, axs = plt.subplots(1, len(resultados_finales), figsize=(4 * len(resultados_finales), 4))

if len(resultados_finales) == 1:
    axs = [axs]

for i, (img_crop, aprobado) in enumerate(resultados_finales):
    axs[i].imshow(img_crop, cmap='gray')
    color = 'green' if aprobado else 'red'
    axs[i].add_patch(
        patches.Rectangle(
            (0, 0), img_crop.shape[1], img_crop.shape[0],
            linewidth=4, edgecolor=color, facecolor='none'
        )
    )
    axs[i].set_title(f"Alumno {i+1}\n{'APROBADO' if aprobado else 'DESAPROBADO'}", color=color)
    axs[i].axis('off')

plt.tight_layout()
plt.show()

