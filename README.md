# Correccion-Automatica-Multiplechoice

## Descripción
Proyecto de procesamiento de imágenes en Python que permite corregir automáticamente exámenes multiple choice a partir de imágenes escaneadas, detectando respuestas correctas e incorrectas y validando los campos del encabezado (Name, ID, Code y Date).
El sistema identifica las marcas mediante análisis de líneas, segmentación y componentes conectadas, generando una imagen resumen con los alumnos aprobados y desaprobados.

##  Flujo del proyecto

### 1️⃣ Detección y validación del encabezado
- Se detectan las líneas de separación mediante umbrales horizontales y verticales.  
- Se recortan los campos del encabezado: **Name, ID, Code, Date**.  
- Cada campo es validado usando **componentes conectadas**, comprobando longitud, cantidad de caracteres y formato.

### 2️⃣ Segmentación de respuestas
- Se recorta la región inferior de la imagen (zona de respuestas).  
- Se detectan filas y columnas de la grilla analizando los cambios de intensidad en cada eje.  
- Se agrupan líneas cercanas para aislar casillas de respuesta.

### 3️⃣ Identificación de marcas
- Cada celda es analizada según el porcentaje de píxeles negros.  
- Si la densidad supera un umbral (0.7), se marca como respuesta seleccionada.  
- Se gestionan casos ambiguos (múltiples marcas o ninguna).

### 4️⃣ Evaluación y resultado
- Las respuestas detectadas se comparan con la plantilla oficial de soluciones.  
- El sistema determina si el alumno aprueba o desaprueba (mínimo 20 respuestas correctas).  
- Se genera una **imagen resumen** con el nombre del alumno y un marco de color:
  - 🟩 Verde → Aprobado  
  - 🟥 Rojo → Desaprobado

---

##  Estructura del repositorio

```
📂 Correccion-automatica-multiplechoice-PDI/
│
├── correccion_automatica.py # Script principal del proyecto
├── requirements.txt # Dependencias necesarias
├── README.md # Documentación del proyecto
│
└── input/ # Carpeta con las imágenes de exámenes (.png)
```
---

## Instalación y ejecución

### 1️⃣ Clonar el repositorio
git clone https://github.com/usuario/Exam-AutoGrader-PDI.git
cd Exam-AutoGrader-PDI

### 2️⃣ Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # En Windows
source venv/bin/activate   # En Linux / macOS

### 3️⃣ Instalar dependencias
pip install -r requirements.txt

### 4️⃣ Ejecutar el script principal
python exam_autograder.py
