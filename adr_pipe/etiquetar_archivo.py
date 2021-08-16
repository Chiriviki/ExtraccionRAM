
import argparse
import json
import os

from adr_pipe import pipe
from tqdm import tqdm

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-f', '--in_file',
        help=('Localización del archivo a etiquetar. Codificación UTF-8. Cada línea es considerada un documento.')
    )

    ap.add_argument('-m', '--model', action='store_true',
                    help="Utiliza el modelo de calsificación.")

    opts = ap.parse_args()
    return opts

def doc2dic(doc):

    dic = {}

    def format_ent(entity):
        ent_dict = {}
        ent_dict["id"] = entity._.ent_id
        ent_dict["type"] = entity.label_
        ent_dict["term"] = entity._.term
        ent_dict["start"] = entity.start
        ent_dict["end"] = entity.end

        return ent_dict

    def format_rel(rel):
        rel_dict = {}
        rel_dict["type"] = rel["type"]
        rel_dict["ent1"] = rel["ent1"]._.ent_id
        rel_dict["ent2"] = rel["ent2"]._.ent_id

        return rel_dict


    dic["text"] = doc.text
    dic["tokens"] = [token.text for token in doc]
    dic["lemmas"] = [token.lemma_ for token in doc]
    dic["pos"] = [token.pos_ for token in doc]
    dic["entities"] = [format_ent(ent) for ent in doc.ents]
    dic["relations"] = [format_rel(rel) for rel in doc._.relations]

    return dic




def main():

    parametros = parse_args()

    # COmprueba que el archivo de entrada existe y es un archivo
    in_file = parametros.in_file


    if not os.path.exists(in_file):
        raise Exception("La ruta de entrada no es válida")

    if not os.path.isfile(in_file):
        raise Exception("La ruta de entrada no es un archivo válido")

    # Lee cada linea del archivo
    with open(in_file, "r", encoding="utf8") as f:
        lines = f.read().split("\n")

    model = parametros.model

    # Obtiene configuraion y crea pipeline
    nlp = pipe.crear_pipe(rf_relations=model)

    docs = list(nlp.pipe(tqdm(lines, desc="Etiquetando archivo")))

    json_array = [doc2dic(doc) for doc in docs]

    # Obtiene la ruta de salida. En la misma carpeta que la entrada, mismo nombre, pero añadiedo _tags al final y extension json
    head, tail = os.path.split(in_file)
    pre, ext = os.path.splitext(tail)

    out_file = os.path.join(head, pre + "_tags.json")

    with open(out_file, "w", encoding="utf8") as f:
        json.dump(json_array, f, ensure_ascii=False, indent=4)

    print("Finalizado. Creado en ", out_file)


if __name__ == '__main__':
    main()

