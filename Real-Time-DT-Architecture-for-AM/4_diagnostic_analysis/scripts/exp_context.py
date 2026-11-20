import sys; sys.path.insert(0,'.')
from common import *
from sklearn.ensemble import ExtraTreesRegressor
w,F=load()
w=w.sort_values(['session_id','window_start']).copy()
g=w.groupby('session_id')
# job-context features
w['E_rel']=w['E_Setpoint_mean']-g['E_Setpoint_mean'].transform('first')          # causal: extrusion so far this session
w['E_norm']=w['E_rel']/(g['E_Setpoint_mean'].transform('last')-g['E_Setpoint_mean'].transform('first')).replace(0,np.nan)  # needs planned total (slicer metadata)
w['Z_norm']=w['Z_Setpoint_mean']/g['Z_Setpoint_max'].transform('max')            # needs planned part height (G-code)
w['idle']=(w['T_Hotend_Setpoint_max']<100).astype(int)
# jobs per session: Z drops
w['zdrop']=(g['Z_Setpoint_min'].diff()< -5).astype(int)
print('jobs/session (Z resets+1):', (g['zdrop'].sum()+1).to_dict())
print('idle fraction per session:', g['idle'].mean().round(2).to_dict())
sets={'S0 telemetry only (Exp. B)':F,
      'S1 + causal extrusion-since-start':F+['E_rel'],
      'S2 + planned part height (Z/Z_final)':F+['Z_norm'],
      'S3 + planned filament (E/E_total)':F+['E_norm'],
      'S4 + both planned job context':F+['Z_norm','E_norm'],
      'S5 job context only (2 features)':['Z_norm','E_norm']}
mods={'Ridge':models()['Ridge'],'Extra Trees':models()['Extra Trees'],'HistGradientBoosting':models()['HistGradientBoosting']}
rows=[]
tr=w[w.session_id.isin(TRAIN)]; te=w[w.session_id.isin(TEST)]
base=met(te[T],np.full(len(te),tr[T].mean()))
rows.append(dict(set='Training-mean baseline',model='-',split='holdout',**base))
for sn,fs in sets.items():
    for mn,m in mods.items():
        m.fit(tr[fs],tr[T]); p=np.clip(m.predict(te[fs]),0,1)
        rows.append(dict(set=sn,model=mn,split='holdout',**met(te[T],p)))
r=pd.DataFrame(rows); print(r.round(3).to_string())
r.to_csv('out/context_ladder_holdout.csv',index=False)
w.to_csv('data/windowed_plus_context.csv',index=False)
