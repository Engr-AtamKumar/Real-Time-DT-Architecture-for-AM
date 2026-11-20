import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':8,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'legend.fontsize':7.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.6})
B,O,GR='#2a78d6','#eb6834','#8a8986'
s=pd.read_csv('benchmark_summary.csv'); N=s.printers.tolist()
fig,ax=plt.subplots(1,2,figsize=(7.16,2.5))
a=ax[0]
data=[np.clip(pd.read_csv(f'latency_samples_{n:02d}_printers.csv').e2e_ms.values,0.1,None) for n in N]
bp=a.boxplot(data,whis=(5,95),widths=0.5,patch_artist=True,showfliers=False,medianprops=dict(color='black',lw=1))
for p in bp['boxes']: p.set_facecolor(B); p.set_alpha(0.55); p.set_edgecolor(B)
a.set_yscale('log'); a.set_xticks(range(1,len(N)+1)); a.set_xticklabels([f'{n}\n({r:.0f}/s)' for n,r in zip(N,s.offered_rate_msg_s)])
for y,l in [(100,'100 ms'),(1000,'1 s (thermal sampling)')]:
    a.axhline(y,color=GR,ls='--',lw=0.7); a.text(5.45,y*1.15,l,fontsize=6.8,color='#52514e',ha='right')
a.set_xlabel('Virtual printers (offered messages/s)'); a.set_ylabel('End-to-end latency (ms), log scale')
a.set_title('(a) Publish-to-database latency',loc='left')
a=ax[1]
a.plot(N,s.offered_rate_msg_s,'o-',color=GR,lw=1.2,ms=4,label='Offered load')
a.plot(N,s.throughput_rows_s,'s-',color=O,lw=1.5,ms=4,label='Sustained insert throughput')
for n,v in zip(N,s.throughput_rows_s): a.annotate(f'{v:.0f}',(n,v),xytext=(5,-11),textcoords='offset points',fontsize=7)
a.set_xlabel('Virtual printers'); a.set_ylabel('Messages or rows per second'); a.set_xticks(N)
a.set_title('(b) Throughput (no message loss)',loc='left'); a.legend(frameon=False,loc='upper left')
plt.tight_layout(); plt.savefig('fig_benchmark.pdf',bbox_inches='tight'); plt.savefig('fig_benchmark.png',dpi=600,bbox_inches='tight')
print(s[['printers','offered_rate_msg_s','throughput_rows_s','e2e_p50_ms','e2e_p95_ms','e2e_p99_ms','mqtt_to_nodered_p95_ms','nodered_to_db_p95_ms','sync_err_p50_ms','sync_err_p95_ms','grafana_query_p50_ms','grafana_query_p95_ms','db_size_mb']].round(1).to_string())
