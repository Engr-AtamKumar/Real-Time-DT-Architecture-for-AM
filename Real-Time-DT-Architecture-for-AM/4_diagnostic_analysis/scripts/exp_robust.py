import sys; sys.path.insert(0,'.')
from common import *
from sklearn.ensemble import ExtraTreesRegressor
_,F=load()
j=pd.read_csv('data/jobs_windowed.csv'); w=pd.read_csv('data/windowed_plus_context.csv')
def ridge(): return models()['Ridge']
def et(): return Pipeline([('i',SimpleImputer(strategy='median')),('m',ExtraTreesRegressor(n_estimators=100,max_depth=15,min_samples_leaf=5,random_state=42,n_jobs=-1))])
configs=[('Session target, telemetry only',w,T,F),
         ('Job target, telemetry only',j,'job_progress',F),
         ('Job target + planned filament',j,'job_progress',F+['E_job_norm']),
         ('Job target, job context only',j,'job_progress',['Z_job_norm','E_job_norm'])]
rows=[]
for name,d,y,fs in configs:
    for sid in sorted(d.session_id.unique()):
        tr=d[d.session_id!=sid]; te=d[d.session_id==sid]
        if len(te)<10: continue
        b=met(te[y],np.full(len(te),tr[y].mean()))
        rows.append(dict(config=name,model='Mean baseline',session=sid,**b))
        for mn,mk in [('Ridge',ridge),('Extra Trees',et)]:
            m=mk(); m.fit(tr[fs],tr[y]); p=np.clip(m.predict(te[fs]),0,1)
            rows.append(dict(config=name,model=mn,session=sid,**met(te[y],p)))
r=pd.DataFrame(rows); r.to_csv('out/loso_results.csv',index=False)
s=r.groupby(['config','model'])[['R','R2','MAE','RMSE']].agg(['mean','std']).round(3)
print(s.to_string())
# paired: fraction of sessions where model RMSE < baseline RMSE
piv=r.pivot_table(index=['config','session'],columns='model',values='RMSE')
for c in piv.index.get_level_values(0).unique():
    p=piv.loc[c]; print(c,'ET beats baseline in',int((p['Extra Trees']<p['Mean baseline']).sum()),'/',len(p),'sessions; Ridge',int((p['Ridge']<p['Mean baseline']).sum()))
# robustness: noisy planned filament (slicer estimate error)
rng=np.random.default_rng(0); tr=j[j.session_id.isin(TRAIN)]; te=j[j.session_id.isin(TEST)].copy()
for noise in [0,0.05,0.10,0.20]:
    res=[]
    for rep in range(10):
        f=1+rng.normal(0,noise,te.job_id.nunique()); fmap=dict(zip(te.job_id.unique(),f))
        te2=te.copy(); te2['E_job_norm']=te['E_job_norm']/te['job_id'].map(fmap)
        m=ridge(); m.fit(tr[F+['E_job_norm']],tr['job_progress']); p=np.clip(m.predict(te2[F+['E_job_norm']]),0,1)
        res.append(met(te2['job_progress'],p))
    d=pd.DataFrame(res); print(f'planned-filament error sd={noise:.0%}: R2={d.R2.mean():.3f}±{d.R2.std():.3f} RMSE={d.RMSE.mean():.3f}')
