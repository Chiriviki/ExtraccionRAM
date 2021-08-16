from adr_pipe import pipe
import json

with open("adr_pipe/config.json", "r", encoding="utf8") as cfg_f:
    config = json.load(cfg_f)

nlp = pipe.crear_pipe(rf_relations=True)

text = "no tiene tos pero el ibuprofeno le produce mareos"

doc = nlp(text)

print("\n---------Característcias léxicas-----------")
for token in doc:
    print(token, token.lemma_, token.pos_)

print("\n----------Entidades----------")
for entity in doc.ents:
    print(entity, entity.label_, entity._.negex)

print("\n----------Relaciones-------------")

for relation in doc._.relations:
    print(relation)
