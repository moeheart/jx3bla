"""Exploratory eight-sector model checks for observed formal-server circle births.

No raw source changes. The two initial logs discovered the rule; additional logs
are explicitly separated. Model compatibility does not identify server code.
Only numpy and Python standard library are required.
"""
from pathlib import Path
import hashlib
import json
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
SEED = 2026110408
REPS = 10000
BATCH = 250
CENTER = np.array([7408.0, 53794.0])


def ks_uniform(a):
    s = np.sort(a, axis=1)
    n = s.shape[1]
    return np.maximum(np.max(np.arange(1,n+1)/n-s,axis=1), np.max(s-np.arange(n)/n,axis=1))


def generate(rng, batch, n, avoid, histories, radial_mode='area'):
    points = np.zeros((batch,n,2))
    for j in range(n):
        slot = j % 8
        r0, r1 = (0.0,14.0) if slot < 4 else (14.0,22.0)
        pending = np.arange(batch)
        while len(pending):
            u = rng.random(len(pending))
            radius = np.sqrt(r0*r0+(r1*r1-r0*r0)*u) if radial_mode == 'area' else r0+(r1-r0)*u
            angle = (slot % 4 + rng.random(len(pending)))*np.pi/2
            proposal = np.stack((radius*np.cos(angle),radius*np.sin(angle)),axis=1)
            if avoid:
                previous = points[pending[:,None],np.array(histories[j],dtype=int)[None,:]]
                good = np.all(np.sum((previous-proposal[:,None])**2,axis=2)>=16,axis=1)
            else:
                good = np.ones(len(pending),dtype=bool)
            points[pending[good],j] = proposal[good]
            pending = pending[~good]
    return points


def stats(groups, histories):
    close, minimum, radii, local_angles = [], [], [], []
    for pts, history in zip(groups,histories):
        n = pts.shape[1]
        ii,jj = np.triu_indices(n,1)
        keep = np.array([i in history[j] for i,j in zip(ii,jj)])
        ds = np.sqrt(np.sum((pts[:,ii[keep]]-pts[:,jj[keep]])**2,axis=-1))
        close.append((ds<4).sum(axis=1))
        minimum.append(ds.min(axis=1))
        r2 = np.sum(pts*pts,axis=2)
        inner = (np.arange(n)%8)<4
        r0 = np.where(inner,0.,196.)
        area = np.where(inner,196.,288.)
        radii.append((r2-r0)/area)
        angles = np.mod(np.arctan2(pts[:,:,1],pts[:,:,0]),2*np.pi)
        local_angles.append(angles/(np.pi/2)-(np.arange(n)%4)[None,:])
    r = np.concatenate(radii,axis=1)
    a = np.concatenate(local_angles,axis=1)
    return {'active_close_pairs_lt4':np.sum(close,axis=0),
            'active_minimum_distance':np.min(minimum,axis=0),
            'mean_within_band_area_fraction':r.mean(axis=1),
            'within_band_radial_ks':ks_uniform(r),
            'mean_within_quadrant_angle_fraction':a.mean(axis=1),
            'within_quadrant_angular_ks':ks_uniform(a)}


def summary(a, observed, tail='two-sided'):
    low, high = int(np.count_nonzero(a<=observed)), int(np.count_nonzero(a>=observed))
    k = low if tail=='lower' else high if tail=='upper' else min(low,high)
    return {'observed':float(observed),'null_mean':float(a.mean()),
            'null_reference_95':np.quantile(a,[.025,.975]).tolist(),
            'tail':tail,'exceedances':k,'replicates':len(a),
            'p_plus_one':min(1.,(k+1)/(len(a)+1)*(2 if tail=='two-sided' else 1)),
            'zero_hit_tail_probability_upper95':1-.05**(1/len(a)) if not k else None}


def main():
    output = HERE.parents[2] / "build" / "research" / HERE.name
    output.mkdir(parents=True, exist_ok=True)
    source = HERE/'evidence.json'
    d = json.loads(source.read_text(encoding='utf8'))
    assert d['circles'], 'Final evidence is not ready'
    discovered_battles = {b['battle_id'] for b in d['battles'] if b['discovery_set']}
    groups, points, violations, rows, slot_rows = [], [], [], [], []
    for p in d['phases']:
        cs = sorted([c for c in d['circles'] if c['battle_id']==p['battle_id'] and c['phase']==p['phase']],key=lambda c:c['order'])
        if not cs:
            continue
        xy = (np.array([[c['x'],c['y']] for c in cs])-CENTER)/64
        groups.append((p,cs,xy)); points.append(xy[None])
        radius = np.linalg.norm(xy,axis=1)
        angle = np.mod(np.arctan2(xy[:,1],xy[:,0]),2*np.pi)
        quadrant = np.floor(angle/(np.pi/2)).astype(int)
        row = {'battle_id':p['battle_id'],'phase':p['phase'],'n':len(cs),
               'discovery_set':p['battle_id'] in discovered_battles,'quadrant_violations':0,'band_violations':0}
        for j,c in enumerate(cs):
            slot = (c['order']-1)%8
            qok = quadrant[j] == slot%4
            rok = 0<=radius[j]<14 if slot<4 else 14<=radius[j]<=22
            row['quadrant_violations'] += not qok
            row['band_violations'] += not rok
            if not(qok and rok):
                violations.append({'battle_id':c['battle_id'],'phase':c['phase'],'order':c['order'],
                                   'x':c['x'],'y':c['y'],'radius':radius[j],'quadrant':int(quadrant[j])})
            slot_rows.append({'slot':slot+1,'radius':float(radius[j]),'angle_degrees':float(angle[j]*180/np.pi),
                             'angle_fraction':float(angle[j]/(np.pi/2)-slot%4),
                             'x':c['x'],'y':c['y'],'color':c['color']})
        rows.append(row)
    histories = [[[i for i in range(j) if (cs[i]['despawn_ms'] is None or cs[i]['despawn_ms']>c['spawn_ms'])]
                  for j,c in enumerate(cs)] for _,cs,_ in groups]
    observed = {k:float(v[0]) for k,v in stats(points,histories).items()}
    # Direct lifecycle check; simulations use last seven only if exactly equivalent.
    total_pairs, active_pairs, active_close, all_close = 0,0,0,0
    active_min = float('inf'); active_nearest = None; lifecycle_mismatches = []
    lag_info = {lag:[] for lag in range(1,40)}
    for p,cs,xy in groups:
        for j,c in enumerate(cs):
            active = {i for i in range(j) if (cs[i]['despawn_ms'] is None or cs[i]['despawn_ms']>c['spawn_ms'])}
            expected = set(range(max(0,j-7),j))
            if active!=expected:
                lifecycle_mismatches.append({'battle':p['battle_id'],'phase':p['phase'],'order':j+1,'active_orders':[i+1 for i in sorted(active)]})
            for i in range(j):
                dist = float(np.linalg.norm(xy[j]-xy[i])); total_pairs+=1
                all_close += dist<4
                lag_info[j-i].append(dist)
                if i in active:
                    active_pairs+=1; active_close += dist<4
                    if dist<active_min:
                        active_min = dist
                        active_nearest = {'battle_id':p['battle_id'],'phase':p['phase'],'orders':[i+1,j+1],'distance':dist,
                                          'lines':[cs[i]['first_record_line'],cs[j]['first_record_line']]}
    result = {'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'seed':SEED,'replicates':REPS,'center_raw':CENTER.tolist(),'scale_xy':64,
              'scope':'Formal-server accessible JCL snapshot; model discovery used the two initial logs',
              'model_candidates':{'slot_sequence':'inner quadrants 1,2,3,4, then outer quadrants 1,2,3,4; repeat every eight births',
                                  'radial_boundary_chi':14,'maximum_radius_chi':22,'active_exclusion_candidate_chi':4},
              'limits':['14 and 22 are exploratory round-number candidates, not exact identified server constants.',
                        'Same-turn additional logs confirm geometry but are not an independent preregistered study.',
                        'Model p values are diagnostic under the stipulated generator, not probabilities that server code is correct.',
                        'Simulation fixes observed phase lengths and active-history indices, and does not model fight termination or repeated-team dependence.',
                        'Simulated coordinates are continuous, unlike integer-unit JCL coordinates.'],
              'phase_rules':rows,'violations':violations,'observed':observed,
              'lifecycle':{'same_round_pairs':total_pairs,'same_round_close_lt4':all_close,'active_pairs':active_pairs,
                           'active_close_lt4':active_close,'active_nearest':active_nearest,'history7_mismatches':lifecycle_mismatches},
              'split_counts':{},'slots':[],'lag_distance':{},'models':{}}
    for name, selected in [('discovery_initial_two',[r for r in rows if r['discovery_set']]),
                           ('additional_logs',[r for r in rows if not r['discovery_set']]),
                           ('chronological_first_battle',[r for r in rows if r['battle_id']==rows[0]['battle_id']]),
                           ('chronological_later_battles',[r for r in rows if r['battle_id']!=rows[0]['battle_id']])]:
        result['split_counts'][name] = {'circles':sum(r['n'] for r in selected),'phases':len(selected),
                                       'quadrant_violations':sum(r['quadrant_violations'] for r in selected),
                                       'band_violations':sum(r['band_violations'] for r in selected)}
    for slot in range(1,9):
        ss = [r for r in slot_rows if r['slot']==slot]
        result['slots'].append({'slot':slot,'n':len(ss),'unique_xy':len({(r['x'],r['y']) for r in ss}),
                                'radius_range':[min(r['radius'] for r in ss),max(r['radius'] for r in ss)],
                                'angle_range_degrees':[min(r['angle_degrees'] for r in ss),max(r['angle_degrees'] for r in ss)],
                                'colors':dict(Counter(r['color'] for r in ss))})
    for lag, distances in lag_info.items():
        if distances:
            result['lag_distance'][lag] = {'pairs':len(distances),'mean':float(np.mean(distances)),
                                          'min':float(min(distances)),'below4':int(sum(x<4 for x in distances))}
    lengths = [len(cs) for _,cs,_ in groups]
    for mi,(name,avoid,radial) in enumerate([('slot_area_no_avoidance',False,'area'),
                                           ('slot_area_active4',True,'area'),
                                           ('slot_radius_active4',True,'radius')]):
        rng = np.random.default_rng(SEED+mi)
        accumulated = {key:[] for key in observed}
        for low in range(0,REPS,BATCH):
            batch = min(BATCH,REPS-low)
            simulated = [generate(rng,batch,n,avoid,history,radial) for n,history in zip(lengths,histories)]
            for key,values in stats(simulated,histories).items():
                accumulated[key].append(values)
        accumulated = {key:np.concatenate(values) for key,values in accumulated.items()}
        directions = {key:'two-sided' for key in observed}
        directions.update(active_close_pairs_lt4='lower',active_minimum_distance='upper',within_band_radial_ks='upper',within_quadrant_angular_ks='upper')
        if radial == 'radius':
            # A smaller discrepancy from area-uniformity is itself anomalous
            # under the radius-uniform alternative; do not test only the upper tail.
            directions['within_band_radial_ks'] = 'two-sided'
        result['models'][name] = {key:summary(values,observed[key],directions[key]) for key,values in accumulated.items()}
        print(name,json.dumps(result['models'][name],ensure_ascii=False),flush=True)
    (output/'candidate-model-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print('Saved candidate-model-results.json',len(d['circles']),len(d['phases']),flush=True)


if __name__=='__main__':
    main()
