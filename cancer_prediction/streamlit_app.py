import os
import pickle

import numpy as np
import pandas as pd
import streamlit as st

from cancer_prediction.cancer_model import CancerModel

st.set_page_config(page_title='Cancer Diagnosis Prediction', layout='wide')

MODELS_DIR = 'models'

def list_saved_models(directory):
    """List all '.pkl' files in the given directory."""
    return [file for file in os.listdir(directory) if file.endswith('.pkl')]

@st.cache_resource
def load_model(path='cancer_model.pkl'):
    model = CancerModel()
    model.load(path)
    return model

def train_and_save_model(train_data: pd.DataFrame, filename: str = 'cancer_model.pkl') -> CancerModel:
    """_summary_

    Args:
        train_data (pd.DataFrame): _description_
        filename (str, optional): _description_. Defaults to 'cancer_model.pkl'.

    Returns:
        CancerModel: _description_
    """
    model = CancerModel()
    filename = os.path.join(MODELS_DIR, filename)
    X = train_data.drop('target', axis=1)
    y = train_data['target']
    model.fit(X, y)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    model.save(filename)
    return model

st.title('Cancer Diagnosis Prediction')

# Sidebar for navigation
app_mode = st.sidebar.selectbox("Choose an option", ["Home", "Train a new model", "Load model and predict", "Manual data entry for prediction"])

if app_mode == "Home":
    st.write("Welcome to the Cancer Diagnosis Prediction Application. Use the sidebar to navigate through the application.")

elif app_mode == "Train a new model":
    st.header("Train a new model")
    uploaded_file = st.file_uploader("Upload your dataset (CSV format)", type="csv")
    model_name = st.text_input("Enter a name for your model (without extension)", value="cancer_model")

    if uploaded_file is not None and model_name:
        data = pd.read_csv(uploaded_file)
        if st.button('Train Model'):
            # Append .pkl extension if not provided
            if not model_name.endswith('.pkl'):
                model_name += '.pkl'
            train_and_save_model(data, model_name)
            st.success(f'Model "{model_name}" trained and saved successfully.')


if app_mode == "Load model and predict" or app_mode == "Manual data entry for prediction":
    st.header("Select a model for prediction")
    model_files = list_saved_models(MODELS_DIR)
    selected_model_file = st.selectbox("Select a model file", model_files)
    path = os.path.join(MODELS_DIR, selected_model_file)
    model = load_model(path)
    
    if app_mode == "Load model and predict":
        uploaded_file = st.file_uploader("Upload your dataset for prediction (CSV format)", type="csv")
        if uploaded_file is not None:
            test_data = pd.read_csv(uploaded_file)
            predictions, accuracy = model.predict(test_data.drop('target', axis=1)), model.accuracy(test_data.drop('target', axis=1), test_data['target'])
            st.write("Predictions:", predictions)
            st.write("Accuracy:", accuracy)
            
    elif app_mode == "Manual data entry for prediction":
        st.header("Manual data entry for prediction")
        
        # Define your features names here based on the model's training dataset
        feature_names = model.feature_names  # Replace these with actual feature names

        # Create a dictionary to store user inputs
        input_data = {}
        
        # Dynamically generate input fields for each feature
        for feature in feature_names:
            # You might want to customize the `step` parameter based on the feature's data type and expected range
            input_data[feature] = st.number_input(f"Enter {feature}:", step=0.01)

        if st.button('Predict'):
            # Prepare the data for prediction (ensure it matches the model's expected input format)
            input_df = pd.DataFrame([input_data])
            
            # Perform the prediction
            prediction = model.predict(input_df)
            
            # Display the prediction result
            st.write(f"Prediction: {prediction[0][0]} with confidence: {prediction[0][1]}")
