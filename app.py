from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Available models
MODELS = {
    'Linear Regression': 'linear_regression',
    'Random Forest': 'random_forest',
    'SVM': 'svm',
    'Decision Tree': 'decision_tree'
}

# Model implementations
MODEL_IMPLEMENTATIONS = {
    'linear_regression': LinearRegression(),
    'random_forest': RandomForestRegressor(),
    'svm': SVR(),
    'decision_tree': DecisionTreeRegressor()
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

def preprocess_data(df):
    """Preprocess the dataframe by handling categorical variables."""
    df_processed = df.copy()
    label_encoders = {}
    for column in df_processed.columns:
        if df_processed[column].dtype == 'object':
            label_encoders[column] = LabelEncoder()
            df_processed[column] = label_encoders[column].fit_transform(df_processed[column].astype(str))
    return df_processed

def create_performance_plots(results, X_test, y_test, predictions):
    """Create multiple performance visualization plots"""
    plots = {}
    
    # 1. Bar plot of R² scores
    plt.figure(figsize=(10, 6))
    model_names = [results[model]['name'] for model in results.keys()]
    r2_scores = [results[model]['r2_score'] for model in results.keys()]
    
    plt.bar(model_names, r2_scores)
    plt.title('Model R² Score Comparison')
    plt.xlabel('Models')
    plt.ylabel('R² Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots['r2_comparison'] = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    # 2. Error Metrics Comparison
    plt.figure(figsize=(12, 6))
    metrics = ['mse', 'rmse', 'mae']
    metric_values = {
        model_name: [results[model_id][metric] for metric in metrics]
        for model_id, model_name in zip(results.keys(), model_names)
    }
    
    x = np.arange(len(metrics))
    width = 0.8 / len(model_names)
    
    for i, (model, values) in enumerate(metric_values.items()):
        plt.bar(x + i * width, values, width, label=model)
    
    plt.xlabel('Metrics')
    plt.ylabel('Value')
    plt.title('Error Metrics Comparison')
    plt.xticks(x + width * (len(model_names) - 1) / 2, metrics)
    plt.legend()
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots['error_metrics'] = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    # 3. Actual vs Predicted Values
    for model_id in results.keys():
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, predictions[model_id], alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title(f'Actual vs Predicted Values - {results[model_id]["name"]}')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plots[f'actual_vs_predicted_{model_id}'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

    return plots

def create_comparison_table(results):
    """Create a pandas DataFrame comparing all model metrics"""
    metrics = ['r2_score', 'mse', 'rmse', 'mae', 'cv_score_mean', 'cv_score_std']
    data = {
        results[model]['name']: [results[model].get(metric, 'N/A') for metric in metrics]
        for model in results.keys()
    }
    df = pd.DataFrame(data, index=metrics)
    return df.to_html(classes='table table-striped', float_format=lambda x: '{:.4f}'.format(x) if isinstance(x, float) else x)

@app.route('/')
def index():
    return render_template('index.html', models=MODELS)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath)
            if len(df.columns) < 2:
                os.remove(filepath)
                return jsonify({'error': 'CSV file must have at least 2 columns'}), 400
            return jsonify({'message': 'File uploaded successfully', 'filename': filename})
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400

@app.route('/train', methods=['POST'])
def train_models():
    try:
        data = request.get_json()
        selected_models = data.get('models', [])
        
        if not selected_models:
            return jsonify({'error': 'No models selected'}), 400
        
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        if not files:
            return jsonify({'error': 'No dataset found. Please upload a CSV file first'}), 400
        
        latest_file = max([os.path.join(app.config['UPLOAD_FOLDER'], f) for f in files], key=os.path.getmtime)
        
        # Load and preprocess data
        df = pd.read_csv(latest_file)
        df_processed = preprocess_data(df)
        
        X = df_processed.iloc[:, :-1]
        y = df_processed.iloc[:, -1]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        results = {}
        predictions = {}
        
        for model_id in selected_models:
            if model_id in MODEL_IMPLEMENTATIONS:
                model = MODEL_IMPLEMENTATIONS[model_id]
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                predictions[model_id] = y_pred
                
                # Calculate metrics
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
                
                results[model_id] = {
                    'name': next(name for name, id in MODELS.items() if id == model_id),
                    'r2_score': r2_score(y_test, y_pred),
                    'mse': mean_squared_error(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'mae': mean_absolute_error(y_test, y_pred),
                    'cv_score_mean': cv_scores.mean(),
                    'cv_score_std': cv_scores.std()
                }
        
        # Create visualizations
        plots = create_performance_plots(results, X_test_scaled, y_test, predictions)
        
        # Create comparison table
        comparison_table = create_comparison_table(results)
        
        return jsonify({
            'message': 'Models trained successfully',
            'results': results,
            'plots': plots,
            'comparison_table': comparison_table
        })
    
    except Exception as e:
        return jsonify({'error': f'Error training models: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 