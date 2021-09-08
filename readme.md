# Instalación

###Requisitos mínimos

- Python 3.8: https://www.python.org/downloads/
- pip 20.2.3: https://pypi.org/project/pip/
- Java JRE 13: https://java.com/es/download/
- Docker 20: https://docs.docker.com/engine/install/


### Instalación PoS Tagger

1. Descargar [archivos de instalación](https://1drv.ms/u/s!Ahp4NIuNip6AhvlZRxSMLeBrAtNrCg?e=1ecYYz)
2. Descomprimir mediante `tar xzvf posTagger.tar.gz`
3. Situarse en la carpeta `SPACCC_POS-TAGGER`
4. Construir el contenedor ejecutando: `docker build -t med-tagger:1.0.0 .`

Durante este proceso se descargan e instalan todos los requisitos (incluido Freeling) en un contenedor Docker, por lo que puede llegar tardar bastante tiempo.

Es importante utilizar los archivos distribuidos en esta herramienta, y no los disponibles en la página de descarga de SPACCC, pues han quedado desactualizados en los últimos meses.

### Instalación ADR-Tagger

La herramienta se distribuye empaquetado en un archivo de tipo `tar.gz`.

1. Descargar los archivos [aquí](https://1drv.ms/u/s!Ahp4NIuNip6Ahvla_qyroRGYSTk0zg?e=DOIeXx)
2. Ejecutar `pip install --use-feature=2020-resolver <ruta_ADR-Tagger>`

Mediante este comando se descargan e instalan todas las dependencias Python y se añade la ruta de la herramienta al `PATH` de ejecución. Es importante usar el parámetro `--use-2020-resolver` para que Spacy quede correctamente instalado.


# Uso de la herramienta

### Uso como herramienta

Para el etiquetado de un archivo ejecutar en la consola de comandos.

```python -m adr_pipe.etiquetar_archivo --model -f ruta/<nombre_archivo>.txt```

Donde `<nombre_archivo>` es la ruta al archivo a ejecutar. El archivo debe estar en texto plano y en codificacion UTF-8. La herramienta interpreta cada línea del archivo como un documento independiente.

Para utilizar el modelo de clasificación es necesario indica el parámetro `--model`. En caso de usar la proyección de la BBDD no indicar ningún parámetro.

La salida será un archivo con nombre `nombrearchivo_tags.json`


### Uso como paquete Python

A continuaión se muestra un ejemplo de la herramienta como paquete python

```python
# Importa
from adr_pipe.pipe import crear_pipe

# Crea pipeline
nlp = crear_pipe(rf_relations=True) # El parámetro indica si utilizar clasificador o no

# Procesa el texto
text = "no tiene tos pero el ibuprofeno le produce mareos"
doc = nlp(text)

# Ejemplo de acceso a los atributos
print("\n---------Característcias léxicas-----------")
for token in doc:
    print(token, token.lemma_, token.pos_)

print("\n----------Entidades----------")
for entity in doc.ents:
    print(entity, entity.label_, entity._.negex)

print("\n----------Relaciones-------------")

for relation in doc._.relations:
    print(relation)
```

Producirá la siguiente salida

```
---------Característcias léxicas-----------
no no ADV
tiene tener VERB
tos tos NOUN
pero pero CONJ
el el DET
ibuprofeno ibuprofeno NOUN
le le PRON
produce producir VERB
mareos mareo NOUN

----------Entidades----------
tos EFFECT True
ibuprofeno DRUG False
mareos EFFECT False

----------Relaciones-------------
{'ent1': ibuprofeno, 'ent2': mareos, 'type': 'ADR'}
```

### Parámetros de etiquetado

En el archivo `data/config.json` se pueden modificar los parámetros de etiquetado. Consultar memoria técnica para el uso de estos parámetros.

