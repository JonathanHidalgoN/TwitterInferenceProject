import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from tensorflow.keras.layers import TextVectorization
from pickle import load as load_pickle

def load_vectorizer(path):
    """
    Load a TextVectorization layer from a pickle file.
    Args:
        path: Path to the pickle file.
    Returns:
        A TextVectorization layer.
    """
    vectorizer = TextVectorization(max_tokens=20000, output_sequence_length=100)
    vectorizer.adapt(np.array([""]))
    weights = load_pickle(open(path, "rb"))["weights"]
    vectorizer.set_weights(weights)

    return vectorizer

def load_text_idx(path):
    """
    Load a text index from a pickle file.
    Args:
        path: Path to the pickle file.
    Returns:
        A dict mapping tokens to indices.
    """
    with open(path, "rb") as f:
        text_idx = load_pickle(f)
    return text_idx

class PositionalEmbedding(layers.Layer):
    def __init__(self, sequence_length, input_dim, output_dim, **kwargs):
        super().__init__(**kwargs)
        #Two embedding layers one for word, independent of the position.
        self.token_embeddings = layers.Embedding(
            input_dim=input_dim, output_dim=output_dim)
        #The other for the position of the word.
        self.position_embeddings = layers.Embedding(
            input_dim=sequence_length, output_dim=output_dim)
        #Number of characters per word
        self.sequence_length = sequence_length
        #How many unique words
        self.input_dim = input_dim
        #Dim of the embedding
        self.output_dim = output_dim

    def call(self, inputs):
        length = tf.shape(inputs)[-1]
        positions = tf.range(start=0, limit=length, delta=1)
        #Create embedding space for words
        embedded_tokens = self.token_embeddings(inputs)
        #Create embedding position space
        embedded_positions = self.position_embeddings(positions)
        #Add both of them
        return embedded_tokens + embedded_positions

    def compute_mask(self, inputs, mask=None):
        #Layer should be able to generate mask, so we can ignore 0's. This method is called
        #automatically by framework.
        return tf.math.not_equal(inputs, 0)

    def get_config(self):
      #When a custom layer is created we need to add get_config method to update layer info
      #this method has to return a dict with the config
        config = super(PositionalEmbedding, self).get_config()
        config.update({
            "output_dim": self.output_dim,
            "sequence_length": self.sequence_length,
            "input_dim": self.input_dim,
        })
        return config

def sample_next(predictions, temperature=1.0):
  predictions = np.asarray(predictions).astype("float64")
  predictions = np.log(predictions) / temperature
  exp_preds = np.exp(predictions)
  predictions = exp_preds / np.sum(exp_preds)
  probas = np.random.multinomial(1, predictions, 1)
  return np.argmax(probas)



class TextGenerator(keras.callbacks.Callback):
    def __init__(self,
               prompt,
               generate_lenght,
               model_input_length,
               temperatures = (1.,),
               print_freq = 1):
        self.prompt = prompt
        self.generate_length = generate_lenght
        self.model_input_length = model_input_length
        self.temperatures = temperatures
        self.print_freq = print_freq
        self.text_vectorization = None
        self.tokens_index = None
        self.text_vectorization_path = "app/text_generation/text_vectorization.pkl"
        self.tokens_index_path = "app/text_generation/tokens_index"
        self.load_text_vectorization()
        self.load_tokens_index()

    def load_text_vectorization(self):
        self.text_vectorization = load_vectorizer(self.text_vectorization_path)

    def load_tokens_index(self):
        self.tokens_index = load_text_idx(self.tokens_index_path)

    def on_epoch_end(self,epoch,logs = None):
        if (epoch + 1) % self.print_freq != 0:
            return
        for temperature in self.temperatures:
            print("== Generating with temperature", temperature)
            sentence = self.prompt
            for i in range(self.generate_length):
                tokenized_sentence = self.text_vectorization([sentence])
                predictions = self.model(tokenized_sentence)
                next_token = sample_next(predictions[0,i,:])
                sampled_token = self.tokens_index[next_token]
                sentence +=  " " + sampled_token
            print(sentence)

class TransformerDecoder(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        #Number of heads
        self.num_heads = num_heads
        self.attention_1 = layers.MultiHeadAttention(
          num_heads=num_heads, key_dim=embed_dim)
        self.attention_2 = layers.MultiHeadAttention(
          num_heads=num_heads, key_dim=embed_dim)
        #Study more
        self.dense_proj = keras.Sequential(
            [layers.Dense(dense_dim, activation="relu"),
             layers.Dense(embed_dim),]
        )
        #Layer normalization, study this more
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()
        self.layernorm_3 = layers.LayerNormalization()
        #Needed by the framework, used to propagate masking from input to output
        self.supports_masking = True

    def get_config(self):
      #Already explained
        config = super(TransformerDecoder, self).get_config()
        config.update({
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "dense_dim": self.dense_dim,
        })
        return config

    def get_causal_attention_mask(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size, sequence_length = input_shape[0], input_shape[1]
        #tf.range creates a 1 dim tensor ex. [0,1,2,.....n]
        #Adding tf.nexaxis add a new axis, this do not slice
        i = tf.range(sequence_length)[:, tf.newaxis] #Ex [1,2] -> [[1,2]]
        j = tf.range(sequence_length)
        mask = tf.cast(i >= j, dtype="int32") 
        mask = tf.reshape(mask, (1, input_shape[1], input_shape[1]))
        mult = tf.concat(
            [tf.expand_dims(batch_size, -1),
             tf.constant([1, 1], dtype=tf.int32)], axis=0)
        return tf.tile(mask, mult)

    def call(self, inputs, encoder_outputs, mask=None):
        causal_mask = self.get_causal_attention_mask(inputs)
        if mask is not None:
            padding_mask = tf.cast(
                mask[:, tf.newaxis, :], dtype="int32")
            padding_mask = tf.minimum(padding_mask, causal_mask)
        attention_output_1 = self.attention_1(
            query=inputs,
            value=inputs,
            key=inputs,
            attention_mask=causal_mask)
        attention_output_1 = self.layernorm_1(inputs + attention_output_1)
        attention_output_2 = self.attention_2(
            query=attention_output_1,
            value=encoder_outputs,
            key=encoder_outputs,
            attention_mask=padding_mask,
        )
        attention_output_2 = self.layernorm_2(
            attention_output_1 + attention_output_2)
        proj_output = self.dense_proj(attention_output_2)
        return self.layernorm_3(attention_output_2 + proj_output)


def load_model(path):
    """
    Load model from path
    Args:
        path: where the model is saved
    Returns:
        keras model
    """
    custom = {"PositionalEmbedding":PositionalEmbedding, "TransformerDecoder":TransformerDecoder}
    model = keras.models.load_model(path, custom_objects=custom)
    return model

def generate_text(model, prompt, generate_length, temperature = 1.0):
    """
    Generate text using the model
    Args:
        model: keras model
        prompt: string
        generate_length: int
        temperature: float, between 0 and 1
    Returns:
        Generated string
    """
    text_vectorization_path = "app/text_generation/text_vectorization.pkl"
    tokens_index_path = "app/text_generation/tokens_index"
    text_vectorization = load_vectorizer(text_vectorization_path)
    tokens_index = load_text_idx(tokens_index_path)
    sentence = prompt
    for i in range(generate_length):
        tokenized_sentence = text_vectorization([sentence])
        predictions = model(tokenized_sentence)
        next_token = sample_next(predictions[0,i,:], temperature)
        sampled_token = tokens_index[next_token]
        sentence +=  " " + sampled_token
    return sentence

if __name__ == "__main__":
    model = load_model("app/text_generation/model2022-11-13 22_35_35.364060.h5")
    print(generate_text(model, "I love", 100, 0.7)) 
