# ☁️ Guía Operativa de Google Colab — JullBrain V3.0

Esta guía explica paso a paso cómo ejecutar el pipeline de transformación documental de leyes venezolanas con **IBM Docling** y **IBM Granite** utilizando una **GPU NVIDIA T4 o A100 gratuita** en Google Colab.

---

## 🎯 Objetivo

Acelerar la conversión de normativas en PDF que contengan cientos de artículos sin consumir memoria ni recalentar la máquina local, persistiendo los resultados directamente en **Google Drive** y sincronizándose con **GitHub**.

---

## 📋 Requisitos Previos

1. Cuenta de Google (para acceder a Google Drive y Google Colab).
2. Conexión a internet.
3. El enlace oficial del cuaderno:
   👉 **[Abrir JullBrain en Google Colab](https://colab.research.google.com/github/julljoll/JullBrain/blob/main/JullBrain_Colab.ipynb)**

---

## 🚀 Flujo de Trabajo Paso a Paso

### Paso 1: Activar el Acelerador de Hardware (GPU)
1. En Google Colab, ve al menú superior: `Entorno de ejecución` > `Cambiar tipo de entorno de ejecución`.
2. En la opción **Acelerador de hardware**, selecciona **T4 GPU** (o A100 si tienes Colab Pro).
3. Haz clic en **Guardar**.

### Paso 2: Ejecutar la Sincronización con GitHub
1. Ejecuta la celda de la **Sección 1** para verificar que la GPU esté detectada (`nvidia-smi`).
2. Ejecuta la celda de la **Sección 2**:
   - Si es la primera vez, clonará el repositorio oficial de JullBrain.
   - Si ya existe en la sesión, ejecutará `git pull origin main` automáticamente.

### Paso 3: Instalar Dependencias
1. Ejecuta la **Sección 3** (`pip install -q -r requirements_colab.txt`).
2. Tardará entre 60 y 90 segundos la primera vez para descargar PyTorch CUDA, Docling y Sentence-Transformers.

### Paso 4: (Opcional) Montar Google Drive
1. En la **Sección 4**, ejecuta la celda para vincular tu Google Drive.
2. Google te pedirá autorización para acceder a tus archivos de Drive.
3. Se crearán automáticamente las siguientes carpetas en tu Google Drive:
   - `Mi unidad > JullBrain > leyes_pdf`: Coloca aquí cualquier nuevo PDF que quieras transformar.
   - `Mi unidad > JullBrain > output_rag`: Aquí se guardarán los resultados procesados.
   - `Mi unidad > JullBrain > embeddings`: Aquí se guardarán los vectores semánticos.

### Paso 5: Conversión Integral y Post-Procesado
1. **Sección 6:** Ejecuta la conversión con IBM Docling (`convert_normativas.py`).
2. **Sección 7:** Aplica el control de jerarquía legal (`convert_normativas.py --post-process-only`).
3. **Sección 8:** Ejecuta el validador cruzado forense (`validator.py`).
4. **Sección 9:** Genera los embeddings con IBM Granite (`granite_embedder.py`).

### Paso 6: Respaldo y Exportación
1. **Sección 10 y 11:** Genera el manifiesto forense SHA-256 y copia todo a Google Drive.
2. **Sección 14:** Exporta el archivo `normativas_ragflow_export.jsonl` para importarlo directamente en tu base de datos vectorial de RAGFlow.

---

## ⚠️ Consejos y Solución de Problemas

- **¿La sesión de Colab se desconectó?**
  Colab tiene un tiempo de desconexión por inactividad. Gracias al respaldo automático en Google Drive (Paso 6), tus leyes procesadas no se perderán.
- **¿Quieres agregar una nueva ley?**
  Súbela a tu carpeta `Mi unidad/JullBrain/leyes_pdf` y ejecuta la Sección 4 y 6 en Colab.
- **¿Hiciste un cambio en el código en tu PC?**
  Haz `git commit` y `git push origin main`. Al volver a Colab y ejecutar la Sección 2, los cambios se descargarán automáticamente.
