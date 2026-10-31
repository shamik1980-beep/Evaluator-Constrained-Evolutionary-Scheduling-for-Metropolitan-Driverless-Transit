"""Loopback-only dashboard server; bounded requests and serial compute."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, logging
from transit import Config, Policy, simulate, optimise, experiment
ROOT=Path(__file__).parent
class Handler(BaseHTTPRequestHandler):
    def reply(self,status,data,kind='application/json'):
        raw=data.encode() if isinstance(data,str) else json.dumps(data,allow_nan=False).encode()
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(raw))); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path in ('/','/index.html'): self.reply(200,(ROOT/'index.html').read_text(),'text/html; charset=utf-8')
        elif self.path=='/health': self.reply(200,{'status':'ok'})
        else: self.reply(404,{'error':'Not found'})
    def do_POST(self):
        if self.headers.get('Host') not in ('127.0.0.1:8765','localhost:8765'): return self.reply(403,{'error':'Invalid host'})
        origin=self.headers.get('Origin')
        if origin and origin not in ('http://127.0.0.1:8765','http://localhost:8765'): return self.reply(403,{'error':'Invalid origin'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<=12000: raise ValueError('Body must be 1–12000 bytes')
            body=json.loads(self.rfile.read(n)); c=Config(**body.get('config',{})).validate()
            p=Policy(**body.get('policy',{})).validate()
            if self.path=='/api/simulate': result=simulate(c,p)
            elif self.path=='/api/optimise':
                result=optimise(c,body.get('population',8),body.get('generations',4),initial=p)
                result['simulation']=simulate(c,Policy(**result['policy']))
            elif self.path=='/api/experiment': result=experiment(c,population=6,generations=3,initial=p)
            else: return self.reply(404,{'error':'Unknown endpoint'})
            self.reply(200,result)
        except (ValueError,TypeError,KeyError) as exc: self.reply(400,{'error':str(exc)})
        except Exception:
            logging.exception('Request failed'); self.reply(500,{'error':'Internal simulation error; see server log'})

def serve():
    logging.basicConfig(level=logging.INFO)
    print('Open http://127.0.0.1:8765 — Ctrl+C to stop',flush=True)
    HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
if __name__=='__main__': serve()
