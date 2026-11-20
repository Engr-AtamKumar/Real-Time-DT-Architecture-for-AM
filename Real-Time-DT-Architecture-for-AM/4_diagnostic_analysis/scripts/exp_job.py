import sys; sys.path.insert(0,'.')
from common import *
w=pd.read_csv('data/windowed_plus_context.csv'); _,F=load()
w['window_start']=pd.to_datetime(w['window_start'])
w=w.sort_values(['session_id','window_start']).reset_index(drop=True)
heated=w['T_Hotend_Setpoint_max']>=150
# job segmentation within session: new job if Z_min drops >5mm, or previous window not heated
prev_z=w.groupby('session_id')['Z_Setpoint_min'].shift()
prev_heat=heated.groupby(w['session_id']).shift().fillna(False).astype(bool)
newjob=(w.groupby('session_id').cumcount()==0)|(w['Z_Setpoint_min']-prev_z< -5)|(~prev_heat & heated)
w['job_id']=newjob.cumsum()
j=w[heated].copy()
gj=j.groupby('job_id')
j['n_job']=gj['session_id'].transform('size')
j=j[j['n_job']>=10].copy(); gj=j.groupby('job_id')
j['k']=gj.cumcount(); j['job_progress']=j['k']/(j['n_job']-1)
j['Z_job_norm']=j['Z_Setpoint_mean']/gj['Z_Setpoint_max'].transform('max')
E0=gj['E_Setpoint_mean'].transform('first'); E1=gj['E_Setpoint_mean'].transform('last')
j['E_job_norm']=(j['E_Setpoint_mean']-E0)/(E1-E0).replace(0,np.nan)
print('jobs kept:',j.job_id.nunique(),' windows:',len(j))
print('jobs per session:',j.groupby('session_id').job_id.nunique().to_dict())
print('job length (min) describe:',j.groupby('job_id').size().describe().round(1).to_dict())
# monotonicity of E within job
mono=gj.apply(lambda g: np.corrcoef(g['E_Setpoint_mean'],np.arange(len(g)))[0,1] if g['E_Setpoint_mean'].std()>0 else np.nan)
print('within-job r(E, time) median:',np.nanmedian(mono).round(3),' r(Z,time) median:',np.nanmedian(gj.apply(lambda g: np.corrcoef(g['Z_Setpoint_mean'],np.arange(len(g)))[0,1] if g['Z_Setpoint_mean'].std()>0 else np.nan)).round(3))
JT='job_progress'
sets={'J0 telemetry only':F,'J1 + planned part height (Z/Z_final)':F+['Z_job_norm'],'J2 + planned filament (E/E_total)':F+['E_job_norm'],'J3 + both':F+['Z_job_norm','E_job_norm'],'J4 job context only':['Z_job_norm','E_job_norm']}
mods={'Ridge':models()['Ridge'],'Extra Trees':models()['Extra Trees'],'HistGradientBoosting':models()['HistGradientBoosting']}
tr=j[j.session_id.isin(TRAIN)]; te=j[j.session_id.isin(TEST)]
rows=[dict(set='Training-mean baseline',model='-',**met(te[JT],np.full(len(te),tr[JT].mean())))]
for sn,fs in sets.items():
    for mn,m in mods.items():
        m.fit(tr[fs],tr[JT]); p=np.clip(m.predict(te[fs]),0,1)
        rows.append(dict(set=sn,model=mn,**met(te[JT],p)))
r=pd.DataFrame(rows); print(r.round(3).to_string()); r.to_csv('out/job_ladder_holdout.csv',index=False)
j.to_csv('data/jobs_windowed.csv',index=False)
