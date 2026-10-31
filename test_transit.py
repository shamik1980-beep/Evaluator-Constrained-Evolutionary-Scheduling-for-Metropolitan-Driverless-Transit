import unittest
from transit import *
class TransitTests(unittest.TestCase):
 def test_reproducible(self):
  c=Config(duration=30,disruption_start=10,disruption_end=20)
  self.assertEqual(simulate(c),simulate(c))
 def test_zero_demand(self):
  r=simulate(Config(duration=30,demand=0,disruption_start=10,disruption_end=20))
  self.assertEqual(r['metrics']['generated'],0)
  self.assertIsNone(r['metrics']['mean_boarded_wait'])
 def test_separation_and_capacity(self):
  c=Config(duration=30,fleet=30,disruption_start=10,disruption_end=20)
  r=simulate(c,Policy(2,1,0,0)); last={}
  for e in r['departures']:
   k=e['direction'],e['station']
   if k in last:
    previous=last[k]; slow=c.disruption_start<=previous<c.disruption_end and e['station']==c.stations//2
    self.assertGreaterEqual(e['time']-previous,2*(c.slow_factor if slow else 1)+.5-1e-8)
   last[k]=e['time'];self.assertLessEqual(e['load'],c.capacity)
 def test_validation(self):
  for kwargs in [dict(demand=float('nan')),dict(stations=2),dict(fleet=True)]:
   with self.assertRaises(ValueError): Config(**kwargs).validate()
  with self.assertRaises(ValueError):Policy(headway=0).validate()
 def test_search(self):
  c=Config(duration=30,demand=2,disruption_start=10,disruption_end=20)
  a=optimise(c,4,2);b=optimise(c,4,2)
  self.assertEqual(a['policy'],b['policy']);Policy(**a['policy']).validate()
  with self.assertRaises(ValueError):experiment(c,seeds=[42])
if __name__=='__main__':unittest.main()
