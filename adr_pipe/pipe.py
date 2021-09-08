import json
import os
import pathlib

import spacy as spacy
from spacy.vocab import Vocab
from tqdm import tqdm

from spaccc_tokenizer.spaccc_tokenizer import SPACCC_tokenizer
from quickumls.spacy_component import SpacyQuickUMLS

from negexMES.negex_component import NegexComponent
from adr_relation.adrDB_re import RelationExtraction_ADRDB
from adr_relation.adrRF_re import RelationExtraction_ADRRF


def create_vocab(path):
    if not os.path.exists(path):
        raise Exception("No existe el vocabulario en ", path)
    return Vocab().from_disk(path)


def _cargar_config():

    parent_path = pathlib.Path(__file__).parent.resolve()

    data_path = os.path.join(pathlib.Path(parent_path).parent.resolve(), "adr_tagger_data")

    with open(os.path.join(data_path, "../adr_tagger_data/config.json"), "r", encoding="utf8") as cfg_f:
        config = json.load(cfg_f)

    config["vocab_path"] = os.path.join(data_path, config["vocab_path"])
    config["quickumls_config"]["terms_fp"] = os.path.join(data_path, config["quickumls_config"]["terms_fp"])
    config["negex_config"]["negex_path"] = os.path.join(data_path, config["negex_config"]["negex_path"])
    config["relation_extractionDB_config"]["relations_fp"] = os.path.join(data_path, config["relation_extractionDB_config"]["relations_fp"])
    config["relation_extractionRF_config"]["encoder_path"] = os.path.join(data_path,
                                                                          config["relation_extractionRF_config"]["encoder_path"])
    config["relation_extractionRF_config"]["model_path"] = os.path.join(data_path,
                                                                          config["relation_extractionRF_config"][
                                                                              "model_path"])
    return config

def crear_pipe(rf_relations=True):

    config = _cargar_config()

    vocab = create_vocab(config["vocab_path"])

    quick_umls_config = config["quickumls_config"]

    negex_mes_config = config["negex_config"]

    relation_extractionRF_config = config["relation_extractionRF_config"]

    relation_extractionDB_config = config["relation_extractionDB_config"]

    nlp = spacy.blank('es', vocab=vocab)

    # Set componentes
    nlp.tokenizer = SPACCC_tokenizer(nlp.vocab)
    nlp.add_pipe("quickumls_matcher", config=quick_umls_config)
    nlp.add_pipe("negex_mes", config=negex_mes_config)


    if rf_relations:
        nlp.add_pipe("re_adrrf", config=relation_extractionRF_config)
    else:
        nlp.add_pipe("re_adrdb", config=relation_extractionDB_config)

    return nlp
