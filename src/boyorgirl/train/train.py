import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping

from utils.preprocess import preprocess
from .model import lstm_model

import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    # Load the data
    parent_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '../'))
    data_path = os.path.join(parent_path, 'data/us-names.csv')
    model_path = os.path.join(parent_path, 'models/boyorgirl.h5')
    fig_path = os.path.join(parent_path, 'train/training.png')

    names_df = pd.read_csv(data_path)
    names_df = preprocess(names_df)
    logging.info(f'Input data shape: {names_df.shape}')

    # Instantiate the model
    model = lstm_model(num_alphabets=27, name_length=50, embedding_dim=256)

    # Split Training and Test Data
    X = np.asarray(names_df['name'].values.tolist())
    y = np.asarray(names_df['gender'].values.tolist())

    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=0.2,
                                                        random_state=0)

    # Train the model
    callbacks = [
        EarlyStopping(monitor='val_accuracy',
                      min_delta=1e-3,
                      patience=5,
                      mode='max',
                      restore_best_weights=True,
                      verbose=1),
    ]

    history = model.fit(x=X_train,
                        y=y_train,
                        batch_size=64,
                        epochs=50,
                        validation_data=(X_test, y_test),
                        callbacks=callbacks)

    # Plot accuracies
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='val')
    plt.legend()
    plt.savefig(fig_path)

    # Save the model
    model.save(model_path)