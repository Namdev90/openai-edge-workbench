"""Capability-protected loopback GUI. No remote control or arbitrary command API."""
from __future__ import annotations
import argparse, contextlib, hmac, http.server, json, os, secrets, sys, threading, time
import urllib.parse, urllib.request, webbrowser
from pathlib import Path
from engine import Workbench, ROOT_NAME, atomic_json, assert_regular_path

ASSETS=Path(__file__).resolve().parent

class Server(http.server.ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=False


def make_server(workbench:Workbench,token:str|None=None):
    capability=token or secrets.token_urlsafe(32)
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version='EdgeWorkbench'
        def log_message(self,*args):pass  # Never log capability tokens or personal URLs.
        def response(self,status,data,content_type='application/json; charset=utf-8'):
            if not isinstance(data,bytes):data=json.dumps(data).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
            self.end_headers()
            with contextlib.suppress(BrokenPipeError,ConnectionResetError):self.wfile.write(data)
        def allowed(self,*,api=False,write=False):
            expected=f'127.0.0.1:{self.server.server_address[1]}'
            if self.headers.get('Host')!=expected:
                self.response(403,{'error':'Unexpected Host header.'});return False
            if api and not hmac.compare_digest(self.headers.get('X-Workbench-Token',''),capability):
                self.response(403,{'error':'Open the dashboard from its launcher.'});return False
            if write and self.headers.get('Origin')!='http://'+expected:
                self.response(403,{'error':'Same-origin request required.'});return False
            return True
        def do_GET(self):
            path=urllib.parse.urlsplit(self.path).path
            if not self.allowed(api=path.startswith('/api/')):return
            if path in ('/','/app.js','/style.css'):
                filename={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[path]
                kind={'/':'text/html; charset=utf-8','/app.js':'text/javascript; charset=utf-8','/style.css':'text/css; charset=utf-8'}[path]
                try:
                    content=(ASSETS/filename).read_bytes()
                    if path=='/' and workbench.options.get('dotnet'):
                        content=content.replace(b'name="dotnet">',b'name="dotnet" checked>')
                    self.response(200,content,kind)
                except OSError:self.response(500,{'error':'Dashboard asset is missing. Extract a fresh copy of the launcher.'})
            elif path=='/api/status':
                try:after=max(0,int(urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get('after',['0'])[0]))
                except ValueError:after=0
                data=workbench.snapshot(after);data['simulated']=workbench.simulate
                self.response(200,data)
            elif path=='/api/report':
                f=workbench.run_dir/'Paste-Into-ChatGPT.txt'
                # Windows readers hold a delete-sharing lock. Finish the read
                # before another report atomically replaces the file.
                with workbench.lock:
                    content=f.read_bytes() if f.is_file() else None
                if content is not None:self.response(200,content,'text/plain; charset=utf-8')
                else:self.response(404,{'error':'No report yet.'})
            else:self.response(404,{'error':'Not found.'})
        def do_POST(self):
            if not self.allowed(api=True,write=True):return
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':
                self.response(415,{'error':'JSON required.'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if length<0 or length>8192:raise ValueError('Request too large.')
                body=json.loads(self.rfile.read(length) or b'{}')
                if not isinstance(body,dict):raise ValueError('Object required.')
            except (ValueError,UnicodeDecodeError) as exc:self.response(400,{'error':str(exc)});return
            path=urllib.parse.urlsplit(self.path).path
            try:
                if path=='/api/start':
                    started=workbench.start(body)
                    self.response(200 if started else 409,{'started':started})
                elif path=='/api/stop':
                    workbench.cancel.set();workbench.log('Stop requested. The current command is allowed to finish.','warning')
                    self.response(200,{'stopping':True})
                elif path in ('/api/open-reports','/api/open-terminal'):
                    if os.name!='nt' or workbench.simulate:
                        self.response(409,{'error':'This local action requires a real Windows run.'});return
                    target=workbench.run_dir if path.endswith('reports') else workbench.root/'Open-Edge-Terminal.cmd'
                    if not target.exists():self.response(409,{'error':'The launcher is not ready yet.'});return
                    os.startfile(str(target));self.response(200,{'opened':True})
                elif path=='/api/quit':
                    if workbench.started and not workbench.finished:workbench.cancel.set()
                    self.response(200,{'closing':True,'after_current_operation':not workbench.finished})
                    def stop_server():
                        while workbench.started and not workbench.finished:time.sleep(.5)
                        self.server.shutdown()
                    threading.Thread(target=stop_server,daemon=True).start()
                else:self.response(404,{'error':'Unknown action.'})
            except (OSError,ValueError) as exc:self.response(400,{'error':str(exc)})
    server=Server(('127.0.0.1',0),Handler)
    server.capability=capability
    server.workbench=workbench
    return server


class InstanceLock:
    """OS-released lock; a process crash does not leave a permanent busy flag."""
    def __init__(self,root:Path):
        self.file=(root/'workbench.lock').open('a+b')
        self.file.seek(0);self.file.write(b'0');self.file.flush();self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:self.file.close();raise
    def close(self):self.file.close()


def existing_window(root:Path)->bool:
    try:
        record=json.loads((root/'local-session.json').read_text(encoding='utf-8'))
        port=int(record['port']);token=str(record['token'])
        if not 1<=port<=65535:return False
        origin=f'http://127.0.0.1:{port}'
        req=urllib.request.Request(origin+'/api/status',headers={'X-Workbench-Token':token})
        with urllib.request.urlopen(req,timeout=3) as r:
            if r.status!=200:return False
        webbrowser.open(origin+'/#token='+urllib.parse.quote(token));return True
    except (OSError,ValueError,KeyError):return False


def main(argv=None):
    parser=argparse.ArgumentParser(description='Local Windows maintenance dashboard')
    parser.add_argument('--root',type=Path,default=Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/ROOT_NAME)
    parser.add_argument('--simulate',action='store_true',help='Explicit no-install demo; reports are labeled simulated')
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--all-tools',action='store_true',help='Select every advertised tool pack, including the daily .NET SDK; choices remain editable in the dashboard.')
    args=parser.parse_args(argv);assert_regular_path(args.root);root=args.root.resolve();root.mkdir(parents=True,exist_ok=True)
    try:lock=InstanceLock(root)
    except OSError:
        if existing_window(root):return 0
        print('Another Workbench run owns the lock. Check its window before starting again.');return 2
    server=make_server(Workbench(root,simulate=args.simulate));port=server.server_address[1]
    if args.all_tools:server.workbench.options={name:True for name in server.workbench.options}
    session=root/'local-session.json'
    atomic_json(session,{'port':port,'token':server.capability,'pid':os.getpid()})
    with contextlib.suppress(OSError):session.chmod(0o600)
    url=f'http://127.0.0.1:{port}/#token={server.capability}'
    print('OpenAI Edge Workbench is running locally. Use Quit dashboard when finished.')
    if args.no_browser:print(f'Local GUI port: {port}. Session capability is in local-session.json; do not share that file.')
    else:webbrowser.open(url,new=1)
    try:server.serve_forever(poll_interval=.3)
    except KeyboardInterrupt:
        server.workbench.cancel.set()
        while server.workbench.started and not server.workbench.finished:time.sleep(.2)
    finally:
        server.server_close();session.unlink(missing_ok=True);lock.close()
    return 0

if __name__=='__main__':raise SystemExit(main())
