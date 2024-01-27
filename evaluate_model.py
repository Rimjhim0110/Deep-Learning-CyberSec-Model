import pickle
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from keras.preprocessing.text import Tokenizer
from data_preprocessing import read_data, handle_missing_data
from tensorflow.keras.preprocessing.sequence import pad_sequences

def load_and_preprocess_data(file_path):
    # Read and preprocess the DataFrame
    df = read_data(file_path)
    df = handle_missing_data(df)
    return df

def load_and_apply_model(model_path, tokenizer_path, label_encoder_path, df):
    # Load the pre-trained model
    model = load_model(model_path)

    # Load Tokenizer and LabelEncoder
    with open(tokenizer_path, 'rb') as tokenizer_file:
        tokenizer = pickle.load(tokenizer_file)
    with open(label_encoder_path, 'rb') as label_encoder_file:
        label_encoder = pickle.load(label_encoder_file)

    # Tokenize and pad the new data
    X = tokenizer.texts_to_sequences(df['log'])
    X = pad_sequences(X, maxlen=model.input_shape[1])

    # Make predictions
    predictions = model.predict(X)

    # Decode the predicted values back to original labels and add them to the DataFrame
    decoded_predictions = label_encoder.inverse_transform(predictions.argmax(axis=1))
    df['Prediction'] = decoded_predictions

    return df

def save_results_to_csv(df, output_file='result.csv'):
    # Save the result to a CSV file
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    # Add path to your .txt file
    file_path = '/content/drive/MyDrive/model/server_logs.txt'

    # Load and preprocess data
    df = load_and_preprocess_data(file_path)

    # Add the paths where the model, tokenizer, and label_encoder get saved
    model_path = '/content/model.h5'
    tokenizer_path = 'tokenizer.pkl'
    label_encoder_path = 'label_encoder.pkl'

    # Load and apply the model to the data
    df = load_and_apply_model(model_path, tokenizer_path, label_encoder_path, df)

    # Save the results to a CSV file
    save_results_to_csv(df, output_file='result.csv')
