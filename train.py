import pickle
from label_data import label_data
from keras.models import Sequential
from keras.utils import to_categorical
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import LabelEncoder
from keras.preprocessing.text import Tokenizer
from keras.layers import Embedding, LSTM, Dense
from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from log_processing import read_log_file, handle_missing_data

def split_data(df, tokenizer):
    """Split data into training and testing sets."""
    X_train_log, X_test_log, y_train, y_test = train_test_split(df['log'], to_categorical(df['Anomaly Type']), test_size=0.2, random_state=42)

    X_train = tokenizer.texts_to_sequences(X_train_log)
    X_train = pad_sequences(X_train)

    X_test = tokenizer.texts_to_sequences(X_test_log)
    X_test = pad_sequences(X_test)

    return X_train, X_test, y_train, y_test

def train_model(df):
    """Train an LSTM model for anomaly detection."""
    df = label_data(df)

    # Encode the 'Anomaly Type' column
    label_encoder = LabelEncoder()
    df['Anomaly Type'] = label_encoder.fit_transform(df['Anomaly Type'])

    # Tokenize the 'log' column
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(df['log'])

    # Save Tokenizer and LabelEncoder to files
    with open('tokenizer.pkl', 'wb') as tokenizer_file:
        pickle.dump(tokenizer, tokenizer_file)

    with open('label_encoder.pkl', 'wb') as label_encoder_file:
        pickle.dump(label_encoder, label_encoder_file)

    X_train, X_test, y_train, y_test = split_data(df, tokenizer)

    # Define the LSTM model
    model = Sequential()
    model.add(Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=100, input_length=X_train.shape[1]))
    model.add(LSTM(100))
    model.add(Dense(len(label_encoder.classes_), activation='softmax'))

    # Compile the model
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Model checkpoints to save the best model
    checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', mode='min', save_best_only=True, verbose=1)

    # Train the model
    model.fit(X_train, y_train, epochs=5, batch_size=64, validation_split=0.2, callbacks=[checkpoint])

    # Evaluate the model
    _, accuracy = model.evaluate(X_test, y_test)
    print(f"Accuracy: {accuracy}")

    # Save the final model
    model.save('final_model.h5')

    return accuracy

if __name__ == "__main__":
    # Add path to the .txt file
    file_path = '/content/drive/MyDrive/model/server_logs.txt'  

    # Read and preprocess the DataFrame
    df = read_log_file(file_path)
    df = handle_missing_data(df)
    
    # Train the model and save it
    train_model(df)
  
