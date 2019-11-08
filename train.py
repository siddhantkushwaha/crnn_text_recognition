import os
import logging

from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.optimizers import Adadelta

from data_generator import DataGenerator
from model import CRNN


def main():
    crnn = CRNN(is_train=True)

    ada = Adadelta()
    crnn.model.compile(loss=lambda y_true, y_pred: y_pred, optimizer=ada)

    batch_size = 64
    train_gen = DataGenerator(data_path='../../FUNSD_TEXT_RECOGNITION/train_data/', batch_size=batch_size)
    val_gen = DataGenerator(data_path='../../FUNSD_TEXT_RECOGNITION/val_data/', batch_size=batch_size)

    os.system('mkdir -p models')
    early_stop = EarlyStopping(monitor='val_loss', min_delta=0.001, patience=4, mode='min', verbose=1)
    checkpoint = ModelCheckpoint(filepath='models/model-{epoch:02d}--{val_loss:.3f}.h5', monitor='loss', verbose=1,
                                 mode='min', period=1, save_weights_only=True)

    with open('models/model.json', 'w') as f:
        f.write(crnn.model.to_json())

    crnn.model.fit_generator(
        generator=train_gen,
        steps_per_epoch=len(train_gen.image_paths) // batch_size,
        epochs=200,

        validation_data=val_gen,
        validation_steps=len(val_gen.image_paths) // batch_size,

        callbacks=[early_stop, checkpoint],

        workers=16,
        use_multiprocessing=True,
        max_queue_size=10,

        verbose=1,
    )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.ERROR)
    main()