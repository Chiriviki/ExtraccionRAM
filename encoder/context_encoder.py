from scipy.sparse import hstack
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
import numpy as np

class ContextEncoder:

    def __init__(self, local_window=3):

        self.local_window = local_window

        self.void_label = "voidcontext"


    def fit(self, examples):

        # Obtiene contexto Local
        local_left_features = [self._get_ent_context(example["ent1"], example["lemmas"], example["pos"], self.local_window)
                               for example in examples]

        local_right_features = [self._get_ent_context(example["ent2"], example["lemmas"], example["pos"], self.local_window)
                                for example in examples]

        # Entrena contexto local
        self.left_onehot_encoder = OneHotEncoder(handle_unknown='ignore')
        self.left_onehot_encoder.fit(local_left_features)

        self.right_onehot_encoder = OneHotEncoder(handle_unknown='ignore')
        self.right_onehot_encoder.fit(local_right_features)


        # Entrena contexto Global
        all_tokens = [self.void_label]

        for example in examples:
            tokens_list = example["tokens"]
            all_tokens.append(" ".join(tokens_list))

        pattern = r"(?u)\b\w+\b"
        lower = True
        self.bow_vectorizer = CountVectorizer(analyzer='word', token_pattern=pattern, lowercase=lower)
        self.bow_vectorizer.fit(all_tokens)


        # Nombres de las características
        # Local
        local_features = [f"{i}_lemma" for i in range(0, self.local_window*2+1)] \
                         + [f"{i}_pos" for i in range(0, self.local_window*2+1)] + ["ent.type"] + ["ent.term"]

        local_left_features = [ f"local_left_{f}" for f in self.left_onehot_encoder.get_feature_names(local_features)]
        local_right_features = [f"local_right_{f}" for f in self.right_onehot_encoder.get_feature_names(local_features)]
        local_feature_names = np.concatenate([local_left_features, local_right_features])

        # Global
        global_features = self.bow_vectorizer.get_feature_names()
        global_f_features = [f"global_f_{feature}" for feature in global_features]
        global_b_features = [f"global_b_{feature}" for feature in global_features]
        global_a_features = [f"global_a_{feature}" for feature in global_features]
        global_feature_names = np.concatenate([global_f_features, global_b_features, global_a_features])
        self.feature_names = np.concatenate([local_feature_names, global_feature_names])

        # Indices de los contextos
        indices = {}
        indices["local_left"] = (0, len(local_left_features))
        indices["local_right"] = (
            indices["local_left"][1], indices["local_left"][1] + len(local_right_features))
        indices["global_f"] = (
            indices["local_right"][1],
            indices["local_right"][1] + len(global_f_features))
        indices["global_b"] = (
        indices["global_f"][1], indices["global_f"][1] + len(global_b_features))
        indices["global_a"] = (
        indices["global_b"][1], indices["global_b"][1] + len(global_a_features))
        self.indices = indices

    def transform(self, examples):
        # LOCAL
        local_left_features = [
            self._get_ent_context(example["ent1"], example["lemmas"], example["pos"], self.local_window)
            for example in examples]

        local_right_features = [
            self._get_ent_context(example["ent2"], example["lemmas"], example["pos"], self.local_window)
            for example in examples]

        vector_local_left = self.left_onehot_encoder.transform(local_left_features)

        vector_local_right = self.right_onehot_encoder.transform(local_right_features)

        # GLOBAL
        global_f_data, global_b_data, global_a_data = [], [], []

        for example in examples:

            tokens_list = example["tokens"]

            b = " ".join(tokens_list[example["ent1"]["end"]:example["ent2"]["start"]])
            if b.strip() == "": b = self.void_label  # Cuando está vacío añade token /VOID/

            f = " ".join(tokens_list[:example["ent1"]["start"]])
            if f.strip() == "": f = self.void_label

            a = " ".join(tokens_list[example["ent2"]["end"]:])
            if a.strip() == "": a = self.void_label


            global_f_data.append(f)
            global_b_data.append(b)
            global_a_data.append(a)

        vector_global_f = self.bow_vectorizer.transform(global_f_data)
        vector_global_b = self.bow_vectorizer.transform(global_b_data)
        vector_global_a = self.bow_vectorizer.transform(global_a_data)

        # crea matriz de características
        features_X_matrix = hstack(
            (vector_local_left, vector_local_right, vector_global_f, vector_global_b, vector_global_a)).tocsr()

        return features_X_matrix


    def _get_ent_context(self, ent, lemmas_list, pos_list, window_size):


        def _get_local_tags(tags_lst, ent_start, ent_end, window_size):
            context_L = [tags_lst[i + ent_start - window_size] if i + ent_start - window_size >= 0 else "X"
                         for i in range(0, window_size)]

            context_R = [tags_lst[i + ent_end] if i + ent_end < len(tags_lst) else "X"
                         for i in range(0, window_size)]

            return context_L + [tags_lst[ent_start]] + context_R

        lemma_context = _get_local_tags(lemmas_list, ent["start"], ent["end"], window_size)
        pos_context = _get_local_tags(pos_list, ent["start"], ent["end"], window_size)
        ent_type = ent["type"]
        ent_term = ent["term"]
        local = np.array(lemma_context + pos_context + [ent_term] + [ent_type] )
        return local

    def get_indices(self):
        return self.indices

    def get_feature_names(self):
        return self.feature_names
