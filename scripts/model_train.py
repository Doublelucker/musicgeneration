from music21 import converter, instrument, note, chord
import glob
import numpy
import os
from keras.utils import np_utils
from keras.layers import LSTM, Dense, Dropout, Activation
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
import pickle
import click


@click.command(name='visualize', help=__doc__)
@click.option('--path', 'path',
              default="F:/music/jigs-transposed", show_default=True, help="Path to the folder with midi. It'll take everything recursively inside of that folder that ends with '.mid'"
              )
@click.option('--sequence_length', 'sequence_length',
              default=100, show_default=True, help="Length of the note sequences that the network will be trained upon."
              )
@click.option('--load_from_file', 'load_from_file',
              default=0, show_default=True, help="Whether to load notes for the network from file or create new ones from dataset. This is for repeatative execution for one dataset (because creating notes takes time)"
              )
def train(path, sequence_length, load_from_file):

    notes = []

    if load_from_file == 1:
        with open("allnotes.txt", "rb") as fp:  # Unpickling
            notes = pickle.load(fp)

    else:
        counter = 0
        for file in glob.iglob("{0}/**/*.mid".format(path), recursive=True):
            if counter < 100:
                midi = converter.parse(file)
                parts = instrument.partitionByInstrument(midi)

                if parts: # file has instrument parts
                    notes_to_parse = parts.parts[0].recurse()
                else: # file has notes in a flat structure
                    notes_to_parse = midi.flat.notes

                for element in notes_to_parse:
                    if isinstance(element, note.Note):
                        notes.append(str(element.pitch))
                    elif isinstance(element, chord.Chord):
                        notes.append('.'.join(str(n) for n in element.normalOrder))
                counter += 1

        with open("allnotes.txt", "wb") as fp:   #Pickling
            pickle.dump(notes, fp)

    n_vocab = len(numpy.unique(notes))

    # get all pitch names
    pitchnames = sorted(set(item for item in notes))

    # create a dictionary to map pitches to integers
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    network_input = []
    network_output = []

    # create input sequences and the corresponding outputs
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        network_output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # reshape the input into a format compatible with LSTM layers
    network_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
    # normalize input
    network_input = network_input / float(n_vocab)
    network_output = np_utils.to_categorical(network_output)

    with open("network.txt", "wb") as fp:  # Pickling
        pickle.dump(network_input, fp)

    model = Sequential()
    model.add(LSTM(
        256,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        return_sequences=True
    ))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(256))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    filepath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"

    checkpoint = ModelCheckpoint(
        filepath, monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    model.fit(network_input, network_output, epochs=20, batch_size=64, callbacks=callbacks_list)


if __name__ == '__main__':
    train()


