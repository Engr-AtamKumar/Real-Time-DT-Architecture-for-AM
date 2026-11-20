import sys; sys.path.insert(0,'.')
from common import *
from scipy import stats
w=pd.read_csv('data/windowed_plus_context.csv'); w['window_start']=pd.to_datetime(w['window_start'])
ss=pd.read_csv(__import__('os').path.join(__import__('os').environ.get('DT_RESULTS_DIR','results'),'session_summary.csv'))
cum=dict(zip(ss.session_id,ss.cumulative_operating_hours-ss.duration_hours))  # hours before session start
# steady printing windows: setpoint constant, heated, actual within 15 C of setpoint
st=w[(w.T_Hotend_Setpoint_std==0)&(w.T_Hotend_Setpoint_mean>=180)&((w.T_Hotend_Actual_mean-w.T_Hotend_Setpoint_mean).abs()<15)&(w.T_Bed_Setpoint_std==0)].copy()
st['track_err']=st.T_Hotend_Actual_mean-st.T_Hotend_Setpoint_mean
st['track_rms']=np.sqrt(st.T_Hotend_Actual_std**2+st.track_err**2)
st['spec_power']=st.Power_Hotend_mean/(st.T_Hotend_Setpoint_mean-st.T_Ambient_Actual_mean)
st['bed_spec_power']=st.Power_Bed_mean/(st.T_Bed_Setpoint_mean-st.T_Ambient_Actual_mean).replace(0,np.nan)
st['regime']=np.where(st.T_Hotend_Setpoint_mean>=235,'high-temp (~243/90 C)','standard (~205-225/60 C)')
st['cum_hours']=st.session_id.map(cum)+(st.window_start-st.groupby('session_id').window_start.transform('min')).dt.total_seconds()/3600
print('steady windows:',len(st),'of',len(w))
agg=st.groupby(['session_id','regime']).agg(cum_h=('cum_hours','median'),n=('track_err','size'),err_med=('track_err','median'),err_abs=('track_err',lambda x:x.abs().median()),trk_rms=('track_rms','median'),spw=('spec_power','median'),bspw=('bed_spec_power','median'),amb=('T_Ambient_Actual_mean','median')).reset_index()
print(agg.round(3).to_string())
agg.to_csv('out/health_indicator_sessions.csv',index=False)
for reg,g in agg.groupby('regime'):
    for col in ['trk_rms','spw','bspw']:
        rho,p=stats.spearmanr(g.cum_h,g[col]); sl=stats.linregress(g.cum_h,g[col])
        print(reg,col,'n=',len(g),'spearman rho=%.2f p=%.3f slope/100h=%.4f'%(rho,p,sl.slope*100))
st.to_csv('data/steady_windows.csv',index=False)
