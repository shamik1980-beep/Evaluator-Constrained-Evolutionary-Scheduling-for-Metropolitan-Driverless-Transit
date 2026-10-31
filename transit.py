"""Deterministic, discrete-time metro research simulator. Units: minutes, km, kWh."""
from dataclasses import dataclass, asdict
import random, math, statistics, json, time

@dataclass(frozen=True)
class Config:
    stations: int = 10
    duration: int = 120
    fleet: int = 16
    capacity: int = 350
    demand: float = 10.0
    surge: float = 2.0
    disruption_start: int = 40
    disruption_end: int = 65
    slow_factor: float = 1.8
    seed: int = 42
    def validate(self):
        for k,lo,hi in [('stations',4,20),('duration',30,240),('fleet',4,30),('capacity',50,1000),('seed',0,1000000)]:
            v=getattr(self,k)
            if type(v) is not int or not lo<=v<=hi: raise ValueError(f'{k} must be an integer in [{lo}, {hi}]')
        for k,lo,hi in [('demand',0,50),('surge',1,5),('slow_factor',1,3)]:
            v=getattr(self,k)
            if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not lo<=v<=hi: raise ValueError(f'Invalid {k}')
        if not (type(self.disruption_start) is int and type(self.disruption_end) is int and 0<=self.disruption_start<=self.disruption_end<=self.duration): raise ValueError('Invalid disruption interval')
        return self

@dataclass(frozen=True)
class Policy:
    headway: float = 3.0
    crowd_weight: float = 0.0
    hold: float = 0.0
    eco: float = 0.0
    def validate(self):
        for key,lo,hi in [('headway',2,6),('crowd_weight',0,1),('hold',0,2),('eco',0,1)]:
            v=getattr(self,key)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi: raise ValueError(f'Invalid policy {key}')
        return self

def arrivals(c):
    """Exogenous demand sampled once, independent of scheduling decisions."""
    rng=random.Random(c.seed); out=[]
    for t in range(c.duration):
        batch=[]
        for d in range(2):
            for s in range(c.stations):
                if (d==0 and s==c.stations-1) or (d==1 and s==0): continue
                rate=c.demand*(1.0+0.4*math.sin(math.pi*t/c.duration))
                if s==c.stations//2 and c.disruption_start<=t<c.disruption_end: rate*=c.surge
                # Poisson draws, Knuth algorithm. Maximum permitted rate is modest.
                n=0; p=1.; limit=math.exp(-rate)
                while p>limit: p*=rng.random(); n+=1
                for _ in range(max(0,n-1)):
                    dest=rng.randrange(s+1,c.stations) if d==0 else rng.randrange(0,s)
                    batch.append((d,s,dest,t))
        out.append(batch)
    return out

def simulate(c=Config(), p=Policy(), trace=True):
    c.validate(); p.validate(); demand=arrivals(c)
    queues={(d,s):[] for d in range(2) for s in range(c.stations)}
    trains=[dict(id=i,station=0 if i%2==0 else c.stations-1,d=i%2,ready=0.,on=[],moving=False,origin=None,depart=None,arrival=None) for i in range(c.fleet)]
    # Directed block occupancy and platform departure separation are independently enforced.
    block_free={}; last_depart={}; last_terminal={0:-100.,1:-100.}
    waits=[]; boarded=completed=generated=0; passenger_minutes=0; energy=0.; pkm=0.; blocked=0; history=[]; departures=[]
    step=.25
    for tick in range(c.duration*4):
        t=tick*step
        if tick%4==0:
            for d,s,dest,a in demand[tick//4]: queues[d,s].append((dest,a)); generated+=1
        for tr in trains:
            if tr['moving'] and t+1e-9>=tr['arrival']:
                tr['station']+=1 if tr['d']==0 else -1
                tr['moving']=False
                remaining=[]; alight=0
                for dest,a in tr['on']:
                    if dest==tr['station']: completed+=1; alight+=1
                    else: remaining.append((dest,a))
                tr['on']=remaining
                terminal=tr['station'] in (0,c.stations-1)
                if terminal:
                    tr['d']=0 if tr['station']==0 else 1
                    tr['ready']=t+2.0
                else: tr['ready']=t+.5+p.hold*min(1,alight/c.capacity)
        # Stable order avoids platform arbitration depending on dictionary iteration.
        for tr in trains:
            if tr['moving'] or t<tr['ready']: continue
            s=tr['station']; d=tr['d']; nxt=s+(1 if d==0 else -1)
            if not 0<=nxt<c.stations: continue
            terminal=s in (0,c.stations-1)
            pressure=len(queues[d,s])/c.capacity
            target=max(2.,p.headway-p.crowd_weight*min(2.,pressure))
            if terminal and t-last_terminal[d]<target: continue
            key=(d,s)
            if t<block_free.get(key,0.) or t-last_depart.get(key,-100.)<1.5:
                blocked+=1; continue
            q=queues[d,s]; take=min(c.capacity-len(tr['on']),len(q)); selected=q[:take]; del q[:take]
            for dest,a in selected: waits.append(t-a)
            boarded+=take; tr['on'].extend(selected)
            slow=c.disruption_start<=t<c.disruption_end and s==c.stations//2
            runtime=2.*(c.slow_factor if slow else 1.)*(1+.25*p.eco)
            # Illustrative traction proxy; no regenerative-braking credit.
            load=len(tr['on']); energy+=(6.+load*.006)*(1-.18*p.eco)
            pkm+=load*1.2
            tr.update(moving=True,origin=s,depart=t,arrival=t+runtime)
            block_free[key]=tr['arrival']+.5; last_depart[key]=t
            if terminal: last_terminal[d]=t
            if trace: departures.append(dict(time=t,train=tr['id'],direction=d,station=s,load=load))
        total_queue=sum(map(len,queues.values())); passenger_minutes+=total_queue*step
        if trace and tick%4==0:
            positions=[]
            for tr in trains:
                pos=tr['station']
                if tr['moving']: pos+=(1 if tr['d']==0 else -1)*min(1,(t-tr['depart'])/(tr['arrival']-tr['depart']))
                positions.append(dict(id=tr['id'],d=tr['d'],position=pos,load=len(tr['on'])))
            history.append(dict(time=t,queues=[len(queues[d,s]) for d in range(2) for s in range(c.stations)],trains=positions))
    sorted_waits=sorted(waits)
    mean=statistics.mean(waits) if waits else None
    p95=sorted_waits[min(len(waits)-1,int(.95*len(waits)))] if waits else None
    stranded=sum(map(len,queues.values())); onboard=sum(len(tr['on']) for tr in trains)
    assert generated==completed+stranded+onboard, 'Passenger conservation failed'
    # Includes observed waiting of censored passengers, unlike boarded-only mean.
    objective=passenger_minutes/max(1,generated)+energy/max(1,generated)*.2
    return dict(config=asdict(c),policy=asdict(p),metrics=dict(generated=generated,boarded=boarded,completed=completed,waiting_at_end=stranded,onboard_at_end=onboard,mean_boarded_wait=mean,p95_boarded_wait=p95,queue_passenger_minutes=passenger_minutes,observed_wait_per_arrival=passenger_minutes/max(1,generated),energy_kwh_proxy=energy,passenger_km=pkm,energy_per_passenger_km=energy/max(1,pkm),blocked_departure_attempts=blocked,objective=objective),history=history,departures=departures)

def optimise(c, population=10, generations=6, seeds=None, initial=None):
    """Budgeted elitist GA + coordinate local search; no test-seed access."""
    if not 4<=population<=24 or not 1<=generations<=15: raise ValueError('Search budget out of range')
    seeds=seeds or [c.seed,c.seed+1]; rng=random.Random(c.seed+999); cache={}; curve=[]
    bounds=[(2,6),(0,1),(0,2),(0,1)]
    def repair(v): return [round(min(hi,max(lo,x)),4) for x,(lo,hi) in zip(v,bounds)]
    def evaluate(v):
        key=tuple(v)
        if key not in cache:
            cache[key]=statistics.mean(simulate(Config(**{**asdict(c),'seed':s}),Policy(*v),False)['metrics']['objective'] for s in seeds)
        return cache[key]
    pop=[[3,0,0,0]]
    if initial: initial.validate(); pop.append(list(asdict(initial).values()))
    while len(pop)<population: pop.append([rng.uniform(lo,hi) for lo,hi in bounds])
    start=time.perf_counter()
    for g in range(generations):
        pop=sorted(pop,key=evaluate); best=pop[0]; curve.append(dict(generation=g,best=evaluate(best)))
        children=pop[:2]
        # Local coordinate refinement around elite.
        v=best.copy(); j=g%4; v[j]+=rng.choice([-1,1])*(bounds[j][1]-bounds[j][0])*.08; children.append(repair(v))
        while len(children)<population:
            a,b=rng.sample(pop[:max(3,population//2)],2)
            child=[a[j] if rng.random()<.5 else b[j] for j in range(4)]
            j=rng.randrange(4); child[j]+=rng.gauss(0,(bounds[j][1]-bounds[j][0])*.15)
            children.append(repair(child))
        pop=children
    best=min(pop,key=evaluate)
    return dict(policy=asdict(Policy(*best)),training_objective=evaluate(best),curve=curve,evaluations=len(cache)*len(seeds),seconds=time.perf_counter()-start,training_seeds=seeds)

def experiment(c, seeds=(101,102,103), population=8, generations=4, initial=None):
    if set(seeds)&{c.seed,c.seed+1}: raise ValueError('Test seeds must be independent')
    trained=optimise(c,population,generations,initial=initial)
    policies={'Fixed timetable':Policy(),'Demand reactive':Policy(3,.8,0,0),'Evolution + local search':Policy(**trained['policy'])}
    if initial: policies['Imported LLM rule']=initial
    rows=[]
    for seed in seeds:
        for name,p in policies.items(): rows.append(dict(method=name,seed=seed,**simulate(Config(**{**asdict(c),'seed':seed}),p,False)['metrics']))
    return dict(training=trained,rows=rows,notes='Synthetic single line, two directions; training/test seeds disjoint. Energy is a proxy. No operational certification.')
