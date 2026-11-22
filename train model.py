import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)
import pandas as pd

df = pd.read_csv("data.csv")

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nTarget distribution:")
print(df["fake"].value_counts())

print("\nTarget percentage:")
print(df["fake"].value_counts(normalize=True) * 100)

print("\nData types:")
print(df.dtypes)

# Select features
X = df[
    [
        "brand",
        "price",
        "country_of_origin",
        "manufacturer_verified",
        "packaging_quality",
        "qr_valid",
        "batch_number_valid",
        "expiry_valid",
        "seller_verified",
        "label_quality",
        "country_match",
        "duplicate_product"
    ]
]

# Target variable
y = df["fake"]

print("\nFeatures (X):")
print(X.head())

print("\nTarget (y):")
print(y.head())

print("\nX shape:", X.shape)
print("y shape:", y.shape)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining data shape:", X_train.shape)
print("Testing data shape:", X_test.shape)

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())


# Categorical and numerical features
categorical_features = ["brand", "country_of_origin"]

numerical_features = [
    "price",
    "manufacturer_verified",
    "packaging_quality",
    "qr_valid",
    "batch_number_valid",
    "expiry_valid",
    "seller_verified",
    "label_quality",
    "country_match",
    "duplicate_product"
]

# Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("numerical", "passthrough", numerical_features)
    ]
)

# Fit preprocessing only on training data
X_train_processed = preprocessor.fit_transform(X_train)

# Transform test data using the same preprocessing
X_test_processed = preprocessor.transform(X_test)

print("\nProcessed training shape:", X_train_processed.shape)
print("Processed testing shape:", X_test_processed.shape)

# Create Logistic Regression model
model = LogisticRegression(max_iter=1000)

# Train the model
model.fit(X_train_processed, y_train)

print("\nModel training completed successfully.")


# Make predictions on test data
y_pred = model.predict(X_test_processed)

# Get probability of being fake
y_prob = model.predict_proba(X_test_processed)[:, 1]

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

print("\nModel Evaluation")
print("----------------")
print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)
print("ROC-AUC  :", auc)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# Feature importance for Logistic Regression

feature_names = preprocessor.get_feature_names_out()

coefficients = model.coef_[0]

feature_importance = pd.DataFrame({
    "Feature": feature_names,
    "Coefficient": coefficients
})

feature_importance["Absolute_Importance"] = (
    feature_importance["Coefficient"].abs()
)

feature_importance = feature_importance.sort_values(
    by="Absolute_Importance",
    ascending=False
)

print("\nTop Feature Influences:")
print(feature_importance.head(10))


# Save trained model and preprocessing object
joblib.dump(model, "fake_product_model.pkl")
joblib.dump(preprocessor, "preprocessor.pkl")

print("\nModel and preprocessor saved successfully.")