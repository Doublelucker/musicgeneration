import sys
from music21 import converter, instrument, note, chord
import numpy
from keras.utils import np_utils
from keras.layers import LSTM, Dense, Dropout, Activation
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
import click
from music21 import stream
import pickle

@click.command(name='visualize', help=__doc__)
@click.option('--file_name', 'file_name',
              default="output.mid", show_default=True, help="Name of the output file"
              )
@click.option('--length', 'length',
              default=100, show_default=True, help="Length of the desired generated melody."
              )
@click.option('--weight_file_name', 'weight_file_name',
              default="weights-improvement-12-2.5445-bigger.hdf5", show_default=True,
              help="During the training phase .hdf5 files will be created."
                   " This is the name of the step you want to load."
              )
def generate(file_name, length, weight_file_name):
    with open("network.txt", "rb") as fp:
        network_input = pickle.load(fp)

    with open("allnotes.txt", "rb") as fp:  # Unpickling
        notes = pickle.load(fp)

    n_vocab = len(numpy.unique(notes))

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

    # Load the weights to each node
    model.load_weights(weight_file_name)


    start = numpy.random.randint(0, len(network_input) - 1)

    pitchnames = sorted(set(item for item in notes))

    int_to_note = dict((number, note) for number, note in enumerate(pitchnames))

    pattern = network_input[start]
    prediction_output = []

    # generate 500 notes
    for note_index in range(int(length)):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        prediction = model.predict(prediction_input, verbose=0)

        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern = numpy.append(pattern, index)
        pattern = pattern[1:len(pattern)]

    offset = 0
    output_notes = []

    # create note and chord objects based on the values generated by the model

    for pattern in prediction_output:
        # pattern is a chord
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        # pattern is a note
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        # increase offset each iteration so that notes do not stack
        offset += 0.5

    midi_stream = stream.Stream(output_notes)

    midi_stream.write('midi', fp=file_name)


if __name__ == '__main__':
    generate()
