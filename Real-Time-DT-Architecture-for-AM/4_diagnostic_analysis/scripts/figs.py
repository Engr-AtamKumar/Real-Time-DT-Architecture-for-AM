import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':8,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.6,'xtick.major.width':0.6,'ytick.major.width':0.6})
B,O,G,GR='#2a78d6','#eb6834','#008300','#8a8986'
w=pd.read_csv('data/windowed_plus_context.csv'); T='synthetic_session_progress'
# ---------- Fig 6 diagnosis
feat=[('E_Setpoint_mean','Extruder position E'),('Z_Setpoint_mean','Z-axis setpoint'),('T_Hotend_Setpoint_mean','Hotend setpoint'),('T_Bed_Setpoint_mean','Bed setpoint'),('Power_Bed_mean','Bed power'),('StepperOnOff_mean','Stepper status'),('X_Setpoint_mean','X-axis setpoint'),('Power_Hotend_mean','Hotend power')]
rows=[]
for f,lab in feat:
    rs=np.array([g[[f,T]].corr().iloc[0,1] for _,g in w.groupby('session_id') if g[f].std()>0])
    rows.append((lab,w[[f,T]].corr().iloc[0,1],np.median(rs),np.percentile(rs,25),np.percentile(rs,75)))
d=pd.DataFrame(rows,columns=['f','pooled','med','q1','q3'])
r=pd.read_csv('out/loso_results.csv'); x=r[(r.config=='Session target, telemetry only')&(r.model=='Extra Trees')].set_index('session')
x['idle']=w.groupby('session_id').idle.mean()
fig,ax=plt.subplots(1,2,figsize=(7.16,3.1),gridspec_kw={'width_ratios':[1.15,1]})
a=ax[0]; y=np.arange(len(d))[::-1]
a.hlines(y,d.q1,d.q3,color=B,lw=2,alpha=0.45)
a.plot(d.med,y,'o',color=B,ms=5,label='Within-session (median, IQR over 22 sessions)')
a.plot(d.pooled,y,'s',color=O,ms=5,label='Pooled across sessions')
a.axvline(0,color='black',lw=0.6); a.set_yticks(y); a.set_yticklabels(d.f); a.set_xlim(-0.75,1.05)
a.set_xlabel('Pearson $r$ with session-progress target'); a.set_title('(a) Within-session vs. pooled association',loc='left')
a.legend(loc='upper center',bbox_to_anchor=(0.42,-0.2),frameon=False,ncol=1)
a=ax[1]; te=x.index.isin([18,19,20,21,22])
a.axhline(0,color=GR,lw=0.8,ls='--'); a.text(0.76,0.04,'mean baseline',color='#52514e',fontsize=7)
a.scatter(x.idle[~te],x.R2[~te],s=22,color=B,edgecolor='white',lw=0.6,label='Sessions 0–17',zorder=3)
a.scatter(x.idle[te],x.R2[te],s=26,color=O,marker='D',edgecolor='white',lw=0.6,label='Sessions 18–22 (original test set)',zorder=3)
for s in [18,19,20,21,22]: a.annotate(str(s),(x.idle[s],x.R2[s]),xytext=(4,-2),textcoords='offset points',fontsize=7)
rho,p=stats.spearmanr(x.idle,x.R2)
a.text(0.97,0.97,f'Spearman $\\rho$ = {rho:.2f}, $p$ = {p:.3f}',transform=a.transAxes,ha='right',va='top',fontsize=7.5)
a.set_xlabel('Idle share of session (hotend setpoint < 100 °C)'); a.set_ylabel('Extra Trees $R^2$ (leave-one-session-out)')
a.set_title('(b) Cross-session error grows with idle share',loc='left'); a.legend(loc='upper center',bbox_to_anchor=(0.5,-0.2),frameon=False,ncol=1)
plt.tight_layout(); plt.savefig('fig/fig_diagnosis.png',dpi=600,bbox_inches='tight'); plt.savefig('fig/fig_diagnosis.pdf',bbox_inches='tight'); plt.close()
# ---------- Fig 7 target design ladder
h=pd.read_csv('out/context_ladder_holdout.csv'); jh=pd.read_csv('out/job_ladder_holdout.csv')
et=lambda df,s: df[(df.set==s)&(df.model=='Extra Trees')].iloc[0]
items=[('Session target, telemetry only\n(Experiment B)',et(h,'S0 telemetry only (Exp. B)')),
       ('Job target, telemetry only',et(jh,'J0 telemetry only')),
       ('Job target + planned part height',et(jh,'J1 + planned part height (Z/Z_final)')),
       ('Job target + planned filament',et(jh,'J2 + planned filament (E/E_total)')),
       ('Job target, job context only',et(jh,'J4 job context only'))]
base_s=h[h.set=='Training-mean baseline'].RMSE.iloc[0]; base_j=jh[jh.set=='Training-mean baseline'].RMSE.iloc[0]
lo=r.groupby(['config','model']).R2.mean()
fig,ax=plt.subplots(1,2,figsize=(7.16,2.3),gridspec_kw={'width_ratios':[1.5,1]})
a=ax[0]; y=np.arange(len(items))[::-1]; vals=[i[1].RMSE for i in items]
cols=[O,B,B,G,G]
a.barh(y,vals,height=0.55,color=cols,edgecolor='white')
for yy,v,i in zip(y,vals,items): a.text(v+0.006,yy,f'{v:.3f}  ($R^2$ = {i[1].R2:+.2f})',va='center',fontsize=7)
a.axvline(base_s,color=GR,ls='--',lw=0.8); a.text(base_s+0.003,y[0]+0.45,'mean baseline ≈ 0.29',fontsize=7,color='#52514e')
a.set_yticks(y); a.set_yticklabels([i[0] for i in items]); a.set_xlim(0,0.56); a.set_xlabel('RMSE on held-out sessions 18–22 (Extra Trees)')
a.set_title('(a) Fixed session holdout',loc='left')
a=ax[1]; cfg=[('Session\ntarget','Session target, telemetry only',O),('Job\ntarget','Job target, telemetry only',B),('Job target\n+ plan','Job target + planned filament',G)]
q=r[r.model=='Extra Trees']
data=[q[q.config==c].R2.clip(lower=-1.5).values for _,c,_ in cfg]
bp=a.boxplot(data,widths=0.45,patch_artist=True,medianprops=dict(color='black',lw=1),flierprops=dict(ms=3))
for patch,(_,_,c) in zip(bp['boxes'],cfg): patch.set_facecolor(c); patch.set_alpha(0.55); patch.set_edgecolor(c)
for k,(_,c,_) in enumerate(cfg): 
    v=q[q.config==c]; a.text(k+1,1.12,f'{(v.R2>0).sum()}/22 > 0',ha='center',fontsize=7)
a.axhline(0,color=GR,ls='--',lw=0.8); a.set_xticks([1,2,3]); a.set_xticklabels([c[0] for c in cfg]); a.set_ylim(-1.6,1.35)
a.set_ylabel('Per-session $R^2$ (leave-one-session-out)'); a.set_title('(b) Leave-one-session-out, 22 folds',loc='left')
plt.tight_layout(); plt.savefig('fig/fig_target_design.png',dpi=600,bbox_inches='tight'); plt.savefig('fig/fig_target_design.pdf',bbox_inches='tight'); plt.close()
# ---------- Fig 8 health indicators
hi=pd.read_csv('out/health_indicator_sessions.csv'); hi=hi[hi.n>=30]
fig,ax=plt.subplots(1,2,figsize=(7.16,2.2))
for a,col,lab in [(ax[0],'trk_rms','Hotend tracking error, RMS (°C)'),(ax[1],'spw','Hotend specific power (W/K)')]:
    for reg,c,m in [('standard (~205-225/60 C)',B,'o'),('high-temp (~243/90 C)',O,'D')]:
        g=hi[hi.regime==reg]; a.plot(g.cum_h,g[col],m+'-',color=c,ms=4.5,lw=1,label='Standard regime (≈205–225 °C / 60 °C)' if c==B else 'High-temperature regime (≈243 °C / 90 °C)')
    a.set_xlabel('Cumulative operating hours'); a.set_ylabel(lab)
ax[0].set_ylim(0,1.0); ax[1].set_ylim(0.3,0.8)
ax[0].set_title('(a) Thermal tracking quality per session',loc='left'); ax[1].set_title('(b) Heating effort per kelvin above ambient',loc='left')
h_,l_=ax[0].get_legend_handles_labels(); fig.legend(h_,l_,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(0.5,-0.06))
plt.tight_layout(rect=(0,0.06,1,1)); plt.savefig('fig/fig_health_indicator.png',dpi=600,bbox_inches='tight'); plt.savefig('fig/fig_health_indicator.pdf',bbox_inches='tight'); plt.close()
print('ok')
