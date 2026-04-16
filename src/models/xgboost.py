from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
from ..data.fetch_data import load_raw_parquet
import joblib

def RunXGBoostModel(path):
    df = load_raw_parquet(path)
    features = ['RSI', 'MACD_norm', 'MACDh_norm', 'MACDs_norm', 'garch_vol_forecast', 'hmm_regimes', 'prob_bull', 'prob_bear', 'prob_chop', 'returns']

    data_clean = df[features + ['target_label']].dropna()
    X = data_clean[features]
    y = data_clean['target_label']

    tscv = TimeSeriesSplit(n_splits=5)

    params = {
        'objective': 'multi:softmax',
        'num_class': 3,
        'max_depth': 6,
        'learning_rate': 0.05,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'eval_metric': 'mlogloss',
        'random_state': 42
    }

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        # We map -1, 0, 1 to 0, 1, 2 because XGBoost classes must start at 0
        y_train_mapped = y_train + 1
        y_test_mapped = y_test + 1

        # Initialize and Fit
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train_mapped)
        
        # Predict
        preds = model.predict(X_test)
        
        # Print results for this fold
        print(f"--- Results for Fold ending {X_test.index[-1].date()} ---")
        print(classification_report(y_test_mapped, preds))

        # Save the final model
        """
        final_model = xgb.XGBClassifier(**params)
        final_model.fit(X, y + 1)

        joblib.dump(final_model, "XGBOOST1.pkl")
        """

RunXGBoostModel("data/processed/SPY_1d_clean.parquet")