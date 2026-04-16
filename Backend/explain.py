import shap
import pandas as pd

# Initialize explainers (do this once)
def init_explainers(rf_model, xgb_model):
    rf_explainer = shap.TreeExplainer(rf_model)
    xgb_explainer = shap.TreeExplainer(xgb_model)
    return rf_explainer, xgb_explainer


def get_explanation(data_df, rf_explainer, xgb_explainer):

    # SHAP values
    rf_shap = rf_explainer.shap_values(data_df)
    xgb_shap = xgb_explainer.shap_values(data_df)

    # Take only attack class (index 1)
    rf_values = rf_shap[1][0]
    xgb_values = xgb_shap[1][0]

    # Average importance
    combined = (rf_values + xgb_values) / 2

    # Get feature names
    features = data_df.columns
    
    # Create importance dict
    importance = dict(zip(features, combined))

    # Sort by impact
    sorted_features = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)

    # Top 3 features
    top_features = sorted_features[:3]

    return top_features