import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
import logging
from typing import List
import tensorflow as tf

logging.basicConfig(level=logging.INFO)

class CustomOpTfPredictor:
    def __init__(self, model_dir):
        # Load the model during the init function to speed up predictions
        self.imported = tf.saved_model.load(model_dir)

        # Load the model signatures
        self.f = self.imported.signatures["serving_default"]
        
    def predict(self, instances, **kwargs):       
        # Input Pre-Process
        x_processed = self.to_tensor_format(instances)

        # Predict
        predictions = tf.map_fn(lambda x:self.f(x)["dense"], x_processed)
        predictions = tf.map_fn(lambda pred: tf.squeeze(pred), predictions)

        # Classes
        class_names = tf.constant(["F", "M"], dtype=tf.string)

        # Predictions are output from sigmoid so float32 in range 0 -> 1
        # Round to integers for predicted class and string lookup for class name
        prediction_integers = tf.cast(tf.math.round(predictions), tf.int32) 
        predicted_classes = tf.map_fn(lambda idx: class_names[idx], prediction_integers, dtype=tf.string)

        # Convert sigmoid output for probability
        # 1 (male) will remain at logit output
        # 0 (female) will be 1.0 - logit to give probability
        def to_probability(logit):
            return 1.0 - logit if logit < 0.5 else logit
        class_probability = tf.map_fn(to_probability, predictions, dtype=tf.float32)
        
        predicted_classes = predicted_classes.numpy().tolist()
        class_probability = class_probability.numpy().tolist()

        return [
            {
                "Name": instances[idx],
                "Gender": gender.decode("utf-8"), 
                "Probability": round(class_probability[idx], 2)
            } for idx, gender in enumerate(predicted_classes)
        ]
    
    # Pre processing
    def to_tensor_format(self, input_names):
        # Convert name to number
        input_name = tf.constant(input_names)
        return tf.map_fn(
            lambda name: self.x_preprocess([name]), input_name, dtype=tf.float32
        )

    def dynamic_padding(self, inp, min_size):
        """Pad after the name with spaces to make all names min_size long"""
        # https://stackoverflow.com/questions/42334646/tensorflow-pad-unknown-size-tensor-to-a-specific-size
        pad_size = min_size - tf.shape(inp)[0]
        paddings = [[0, pad_size]] # Pad behind the name with spaces to align with padding from to_tensor default_value
        return tf.pad(inp, paddings, mode="CONSTANT", constant_values=" ")

    def x_preprocess(self, x):
        """Preprocess the names
            1. Lowercase all letters
            2. Split on characters
            3. Pad if necessary with spaces after the names till all names are filter_size long. If longer than filter_size then limit to first filter_size chars
            4. Convert letters to numbers and subtract 96 (UTF value of a -1) to make a=1
            5. Make any <0 or >26 numbers as 0 to remove special characters and space"""

        # 1. Lowercase all letters
        x_processed = tf.strings.lower(x)

        # 2. Split on characters
        x_processed = tf.strings.unicode_split(x_processed, input_encoding="UTF-8").to_tensor(default_value=" ") 
        #TODO: in TF2.0 can add an argument shape=[batch_size,100] to do padding/pruning here
        
        # 3. Pad if necessary with spaces after the names till all names are filter_size long. If longer than filter_size then limit to first filter_size chars
        filter_size=100
        x_processed = tf.cond(tf.less(tf.shape(x_processed)[1], filter_size), 
                            true_fn=lambda: tf.map_fn(lambda inp_name: self.dynamic_padding(inp_name, filter_size), x_processed), 
                            false_fn=lambda: tf.map_fn(lambda inp_name: tf.slice(inp_name, tf.constant([0]), tf.constant([100])), x_processed))
        
        # 4. Convert letters to numbers and subtract 96 (UTF value of a -1) to make a=1
        x_processed = tf.strings.unicode_decode(x_processed, 'UTF-8')-96

        # 5. Make any <0 or >26 numbers as 0 to remove special characters and space
        x_processed = tf.map_fn(lambda item: (tf.map_fn(lambda subitem: 0 if (subitem[0]<0 or subitem[0]>26)else subitem[0], item)), x_processed.to_tensor())

        
        # Unique to predictor.py
        x_processed = tf.cast(x_processed, tf.float32)
        
        return x_processed

app = FastAPI()

model_dir = 'models/1'
pred_model = CustomOpTfPredictor(model_dir)


@app.post('/predict')
def predict(instances: List[str]):
    # https://stackoverflow.com/questions/60844846/read-a-body-json-list-with-fastapi
    logger.info(instances)
    return pred_model.predict(instances)

@app.get('/')
def health_check():
    return {'message': 'This is the homepage of the API', 'success': True, 'status': 200}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port='80')