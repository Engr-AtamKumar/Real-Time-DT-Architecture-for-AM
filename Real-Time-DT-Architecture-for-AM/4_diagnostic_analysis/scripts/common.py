import numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
T='synthetic_session_progress'
TRAIN=[0,1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17]; TEST=[18,19,20,21,22]
def load():
    w=pd.read_csv(__import__('os').path.join(__import__('os').environ.get('DT_RESULTS_DIR','results'),'windowed_results','windowed_features_1min.csv'))
    w=w.dropna(subset=[T])
    feats=[c for c in w.select_dtypes('number').columns if c not in [T,'session_id'] and w[c].nunique(dropna=True)>1]
    return w,feats
def models(seed=42):
    imp=lambda:SimpleImputer(strategy='median')
    return {
     'Linear Regression':Pipeline([('i',imp()),('s',StandardScaler()),('m',LinearRegression())]),
     'Ridge':Pipeline([('i',imp()),('s',StandardScaler()),('m',Ridge(alpha=1.0))]),
     'Decision Tree':Pipeline([('i',imp()),('m',DecisionTreeRegressor(max_depth=8,min_samples_leaf=10,random_state=seed))]),
     'Random Forest':Pipeline([('i',imp()),('m',RandomForestRegressor(n_estimators=150,max_depth=15,min_samples_leaf=5,random_state=seed,n_jobs=-1))]),
     'Extra Trees':Pipeline([('i',imp()),('m',ExtraTreesRegressor(n_estimators=150,max_depth=15,min_samples_leaf=5,random_state=seed,n_jobs=-1))]),
     'Gradient Boosting':Pipeline([('i',imp()),('m',GradientBoostingRegressor(n_estimators=150,learning_rate=0.05,max_depth=3,random_state=seed))]),
     'HistGradientBoosting':Pipeline([('i',imp()),('m',HistGradientBoostingRegressor(max_iter=200,learning_rate=0.05,max_leaf_nodes=31,l2_regularization=1.0,random_state=seed))]),
    }
def met(y,p):
    y=np.asarray(y);p=np.asarray(p)
    r=np.corrcoef(y,p)[0,1] if np.std(p)>0 else np.nan
    return dict(R=r,R2=r2_score(y,p),MAE=mean_absolute_error(y,p),RMSE=np.sqrt(mean_squared_error(y,p)))
