# imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image, ImageOps
import numpy as np
import os
from string import ascii_lowercase

from pathlib import Path

class CaptchaBreaker:

    def __init__(self, model_path):
        self._model = keras.models.load_model(model_path)
        self._characters = list(ascii_lowercase)
        # encodes characters to integers
        self._char_to_num = layers.StringLookup(vocabulary=list(self._characters))
        # decodes integers back to characters
        self._num_to_char = layers.StringLookup(vocabulary=self._char_to_num.get_vocabulary(), invert=True)
        self._IMG_WIDTH = 175
        self._IMG_HEIGHT = 70
        self._BATCH_SIZE = 70
        self._MAX_LENGTH = 4

    def load_model(self, path):
        self._model = keras.models.load_model(path)

    def _encode_single_sample(self, image, label):
        img = tf.io.read_file(image)
        img = tf.io.decode_png(img, channels=1)
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = tf.transpose(img, perm=[1, 0, 2])
        label = self._char_to_num(tf.strings.unicode_split(label, input_encoding="UTF-8"))
        return {"image": img, "label": label}

    def _create_dataset(self, path):
        data_dir = Path(path)
        self._to_black_and_white(data_dir)
        captcha_images = list(map(str, list(data_dir.glob("*.png"))))
        captcha_labels = ["0000" for img in captcha_images]
        # creates dataset object
        dataset = tf.data.Dataset.from_tensor_slices((captcha_images, captcha_labels))
        dataset = (
            dataset.map(
                self._encode_single_sample, num_parallel_calls=tf.data.AUTOTUNE
            )
                .batch(self._BATCH_SIZE)
                .prefetch(buffer_size=tf.data.AUTOTUNE)
        )
        return dataset

    def _decode_batch_predictions(self, pred):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :self._MAX_LENGTH]
        output_text = []
        for res in results:
            res = tf.strings.reduce_join(self._num_to_char(res)).numpy().decode("utf-8")
            output_text.append(res)
        return output_text

    def _to_black_and_white(self, path):
        images = list(map(str, list(path.glob("*.png"))))
        for image in images:
            name = image.split(os.sep)[2]
            print(name)
            im = Image.open(image)
            im = ImageOps.grayscale(im)
            w, h = im.size
            for x in range(w):
                for y in range(h):
                    pixel = im.getpixel((x, y))
                    if pixel > 200:
                        im.putpixel((x, y), (255))
                    else:
                        im.putpixel((x, y), (0))
            im.save(f"{path}{os.sep}{name}")

    def predict(self, path):
        # gets prediction model
        prediction_model = keras.models.Model(self._model.get_layer(name="image").input, self._model.get_layer(name="dense2").output)
        dataset = self._create_dataset(path)
        for batch in dataset.take(1):
            batch_images = batch["image"]
            preds = prediction_model.predict(batch_images)
            pred_texts = self._decode_batch_predictions(preds)
        best_prediction = self._best_prediction(pred_texts)
        return best_prediction

    def _best_prediction(self, predictions):
        unique_preds = list(set(predictions))
        scores = []
        for pred in unique_preds:
            count = predictions.count(pred)
            scores.append(count)
        best_prediction = unique_preds[scores.index(max(scores))]
        return best_prediction
