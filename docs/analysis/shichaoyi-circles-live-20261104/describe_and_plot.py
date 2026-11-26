"""Descriptive statistics and standalone figures for the live-only snapshot."""
from pathlib import Path
from collections import Counter
import json
import math
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]))
from tools.MineShiChaoyiCircles import write_csv


def summary(values):
    a=np.array(values,dtype=float)
    return {'n':len(a),'min':float(a.min()),'p25':float(np.quantile(a,.25)),
            'median':float(np.median(a)),'mean':float(a.mean()),
            'p75':float(np.quantile(a,.75)),'max':float(a.max())} if len(a) else None


def main():
    output = HERE.parents[2] / "build" / "research" / HERE.name
    output.mkdir(parents=True, exist_ok=True)
    data=json.loads((HERE/'evidence.json').read_text(encoding='utf-8'))
    cs,ps=data['circles'],data['phases']
    pairs,waves=[],[]
    for c in cs:
        c['slot']=(c['order']-1)%8+1
        c['angle_deg']=math.degrees(math.atan2(c['y_chi'],c['x_chi']))%360
        c['observed_quadrant']=int(c['angle_deg']//90)+1
        c['expected_quadrant']=(c['order']-1)%4+1
        c['expected_band']='inner' if c['slot']<=4 else 'outer'
        c['slot_matches']=(c['observed_quadrant']==c['expected_quadrant'] and
                           ((c['radius_chi']<14) if c['slot']<=4 else (14<=c['radius_chi']<=22)))
    for p in ps:
        rows=sorted([c for c in cs if c['battle_id']==p['battle_id'] and c['phase']==p['phase']],key=lambda c:c['order'])
        wp=[]
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                row={'battle_id':a['battle_id'],'phase':a['phase'],'order_a':a['order'],'order_b':b['order'],
                     'lag':b['order']-a['order'],'color_a':a['color'],'color_b':b['color'],
                     'distance_chi':math.hypot(a['x_chi']-b['x_chi'],a['y_chi']-b['y_chi']),
                     'delta_spawn_s':(b['spawn_ms']-a['spawn_ms'])/1000,
                     'overlap_observed':a['despawn_ms'] is not None and b['spawn_ms']<a['despawn_ms'],
                     'a_exit_before_b_spawn_s':(b['spawn_ms']-a['despawn_ms'])/1000 if a['despawn_ms'] else None,
                     'source_line_a':a['first_record_line'],'source_line_b':b['first_record_line']}
                pairs.append(row);wp.append(row)
        waves.append({**{k:p[k] for k in ['battle_id','phase','n_circles','red','white','status','first_delay_s','n_resolved_observed']},
                      'r_min':min(c['radius_chi'] for c in rows),'r_max':max(c['radius_chi'] for c in rows),
                      'minimum_distance':min(r['distance_chi'] for r in wp),
                      'minimum_overlapping_distance':min(r['distance_chi'] for r in wp if r['overlap_observed']),
                      'slot_matches':sum(c['slot_matches'] for c in rows),
                      'spawn_interval_mean_s':(rows[-1]['spawn_ms']-rows[0]['spawn_ms'])/(len(rows)-1)/1000,
                      'first8_xy_raw':[[c['x'],c['y']] for c in rows[:8]]})
    slots=[]
    for slot in range(1,9):
        ss=[c for c in cs if c['slot']==slot]
        slots.append({'slot':slot,'n':len(ss),'red':sum(c['color']=='red' for c in ss),
                      'white':sum(c['color']=='white' for c in ss),
                      'x_min':min(c['x'] for c in ss),'x_max':max(c['x'] for c in ss),
                      'y_min':min(c['y'] for c in ss),'y_max':max(c['y'] for c in ss),
                      'radius':summary([c['radius_chi'] for c in ss]),
                      'local_angle_deg':summary([c['angle_deg']%90 for c in ss])})
    near=[r for r in pairs if r['distance_chi']<4]
    active=[r for r in pairs if r['overlap_observed']]
    intervals=[r['delta_spawn_s'] for r in pairs if r['lag']==1]
    result={'n_circles':len(cs),'n_phases':len(ps),'full40':sum(p['n_circles']==40 for p in ps),
            'color_totals':dict(Counter(c['color'] for c in cs)),
            'unique_xy':len({(c['x'],c['y']) for c in cs}),'all_slots_match':all(c['slot_matches'] for c in cs),
            'slot_mismatch_rows':[c for c in cs if not c['slot_matches']],
            'radius':summary([c['radius_chi'] for c in cs]),
            'inner_radius':summary([c['radius_chi'] for c in cs if c['slot']<=4]),
            'outer_radius':summary([c['radius_chi'] for c in cs if c['slot']>4]),
            'coordinate_ranges':{'x':[min(c['x'] for c in cs),max(c['x'] for c in cs)],
                                 'y':[min(c['y'] for c in cs),max(c['y'] for c in cs)]},
            'pairs_total':len(pairs),'pairs_lt4':len(near),'pairs_lt4_same_color':sum(r['color_a']==r['color_b'] for r in near),
            'minimum_pair':min(pairs,key=lambda r:r['distance_chi']),
            'overlapping_pairs':len(active),'overlapping_pairs_lt4':sum(r['distance_chi']<4 for r in active),
            'minimum_overlapping_pair':min(active,key=lambda r:r['distance_chi']),
            'interval_s':summary(intervals),'first_delay_s':summary([p['first_delay_s'] for p in ps]),
            'lifetime_s':summary([c['lifetime_s'] for c in cs if c['lifetime_s'] is not None]),
            'slots':slots,'waves':waves,
            'lag_summary':[{'lag':lag,'n':len(rr),'mean_distance':np.mean([r['distance_chi'] for r in rr]),
                            'lt4':sum(r['distance_chi']<4 for r in rr)} for lag in range(1,40)
                           if (rr:=[r for r in pairs if r['lag']==lag])]}
    (output/'descriptive-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    write_csv(output/'coordinates.csv',cs)
    write_csv(output/'point-pairs.csv',pairs)
    write_csv(output/'wave-summary.csv',waves)
    plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],'axes.unicode_minus':False,
                         'font.size':11,'figure.facecolor':'white','axes.facecolor':'#fbfcfe'})
    palette=['#009c91','#247ac6','#745bc4','#d15a91','#50bb9e','#78abdb','#aa8fdb','#e591b7']
    fig,(ax,ax2)=plt.subplots(1,2,figsize=(15,7),gridspec_kw={'width_ratios':[1,1.05]})
    for slot in range(1,9):
        ss=[c for c in cs if c['slot']==slot]
        q=(slot-1)%4
        outer=slot>4
        ax.add_patch(Wedge((0,0),22 if outer else 14,q*90,(q+1)*90,
                           width=8 if outer else 14,facecolor=palette[slot-1],alpha=.07,edgecolor='none'))
        ax.scatter([c['x_chi'] for c in ss],[c['y_chi'] for c in ss],s=18,color=palette[slot-1],alpha=.8,linewidths=0)
        angle=math.radians(q*90+45);r=25 if outer else 8
        ax.text(r*math.cos(angle),r*math.sin(angle),str(slot),fontsize=18,weight='bold',ha='center',va='center',
                color=palette[slot-1],bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=1))
    for r in [14,22]:ax.add_patch(Circle((0,0),r,fill=False,color='#6d7c8d',lw=1,ls='--'))
    ax.axhline(0,color='#bdc5cf',lw=.7);ax.axvline(0,color='#bdc5cf',lw=.7)
    ax.scatter([0],[0],marker='+',color='black',s=80)
    ax.set(xlim=(-27,27),ylim=(-27,27),xlabel='相对中心 x（尺）',ylabel='相对中心 y（尺）',aspect='equal')
    ax.set_title('416个实际落点，按周期位置1—8着色',loc='left',pad=14,fontsize=14)
    for slot in range(1,9):
        ss=[c for c in cs if c['slot']==slot]
        ax2.scatter([c['order'] for c in ss],[c['radius_chi'] for c in ss],s=23,color=palette[slot-1],alpha=.8,linewidths=.3,edgecolors='white')
    ax2.axhline(14,color='#53657a',ls='--',lw=1,label='14尺候选分界')
    ax2.axhline(22,color='#53657a',ls=':',lw=1,label='22尺候选外界')
    for left in range(1,41,8):
        ax2.axvspan(left-.5,left+3.5,color='#dce9f4',alpha=.45)
    ax2.set(xlim=(.5,40.5),ylim=(0,23.5),xlabel='每轮生成序号',ylabel='到中心的距离（尺）')
    ax2.set_xticks([1,4,8,12,16,20,24,28,32,36,40])
    ax2.set_title('每8圈重复：内侧4圈 → 外侧4圈',loc='left',pad=14,fontsize=14)
    ax2.grid(axis='y',alpha=.15);ax2.legend(loc='lower right',frameon=False,fontsize=10)
    fig.suptitle('正式服25人普通史朝义：生成区域存在固定的8圈周期',x=.065,ha='left',fontsize=19,weight='bold')
    fig.text(.065,.035,'4场有圈记录 · 11轮 · 416个圈全部符合区域周期。颜色表示1—8区域顺序，不表示红白圈。\n中心原始坐标(7408, 53794)，64单位=1尺；坐标轴尚未与游戏小地图方向对齐。14/22尺为数据支持的候选边界。',fontsize=10,linespacing=1.6)
    fig.tight_layout(rect=(.025,.13,.99,.92));fig.savefig(output/'generation-pattern.png',dpi=165);plt.close(fig)
    ncols=4;nrows=math.ceil(len(ps)/ncols)
    fig,axes=plt.subplots(nrows,ncols,figsize=(16,4.4*nrows),sharex=True,sharey=True)
    for ax,p in zip(axes.flat,ps):
        rows=sorted([c for c in cs if c['battle_id']==p['battle_id'] and c['phase']==p['phase']],key=lambda c:c['order'])
        for c in rows:
            ax.scatter(c['x_chi'],c['y_chi'],s=150,facecolors='#ed7478' if c['color']=='red' else 'white',edgecolors='#526275',lw=.8)
            ax.text(c['x_chi'],c['y_chi'],str(c['order']),ha='center',va='center',fontsize=5.9)
        for r in [14,22]:ax.add_patch(Circle((0,0),r,fill=False,color='#8a99aa',ls='--',lw=.7))
        ax.axhline(0,color='#c4ccd6',lw=.5);ax.axvline(0,color='#c4ccd6',lw=.5)
        ax.set(xlim=(-24,24),ylim=(-24,24),aspect='equal')
        ax.set_title(f"{p['battle_id']} 第{p['phase']}轮 · {p['red']}红{p['white']}白",fontsize=11)
    for ax in list(axes.flat)[len(ps):]:ax.axis('off')
    fig.suptitle('全部11轮生成坐标｜圈内数字为本轮生成序号',fontsize=18,weight='bold',y=.99)
    fig.text(.06,.017,'单位：尺；中心(7408,53794)。红/白为圈颜色，绘图标记大小不代表判定半径。末尾不足40的轮次保留实际观测数量。',fontsize=11)
    fig.tight_layout(rect=(.025,.04,.99,.965));fig.savefig(output/'all-waves.png',dpi=170);plt.close(fig)
    print(json.dumps({k:result[k] for k in ['n_circles','n_phases','full40','color_totals','unique_xy','all_slots_match','radius','inner_radius','outer_radius','pairs_total','pairs_lt4','overlapping_pairs','overlapping_pairs_lt4','minimum_overlapping_pair','minimum_pair','interval_s']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
