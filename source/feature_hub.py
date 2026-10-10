"""Fixed, capability-protected feature jobs. No arbitrary command/path interface."""
from __future__ import annotations
import collections, copy, json, os, shutil, subprocess, threading, urllib.request, urllib.parse, uuid
from pathlib import Path
from engine import VERSION, redact, assert_regular_path
import feature_plans, feature_diagnostics, feature_reports

CLIENT_FEATURES=[
    ('Search feature library','Search feature names and descriptions.'),
    ('Filter feature categories','Focus on diagnostics, reports, plans or dashboard features.'),
    ('Pin favorite features','Keep chosen feature IDs as browser-local favorites.'),
    ('View favorites only','Show a personalized feature list.'),
    ('Choose display density','Switch between compact and comfortable feature cards.'),
    ('Adjust dashboard text size','Scale dashboard text for comfortable reading.'),
    ('Choose reduced motion','Reduce dashboard transitions independently of system preference.'),
    ('Search live operation log','Find words in the current run log.'),
    ('Filter log severity','Show selected information, warning or error entries.'),
    ('Open keyboard command palette','Search and run features from a keyboard-accessible palette.'),
]
FEATURES=feature_diagnostics.FEATURES+feature_reports.FEATURES+feature_plans.FEATURES+[
    {'id':f'f{91+i:03}','title':title,'description':description,'category':'Dashboard','effect':'browser preference','client':True} for i,(title,description) in enumerate(CLIENT_FEATURES)
]
if len(FEATURES)!=100 or {x['id'] for x in FEATURES}!={f'f{i:03}' for i in range(1,101)}:
    raise RuntimeError('Feature catalog must contain exactly 100 unique, contiguous features.')

def protect(value):
    if isinstance(value,str):return redact(value)
    if isinstance(value,dict):
        import re
        sensitive={'accesstoken','refreshtoken','idtoken','apikey','password','clientsecret','authorization','cookie','setcookie','credentials','token','secret'}
        return {redact(k):'[REDACTED]' if re.sub(r'[^a-z0-9]','',str(k).lower()) in sensitive else protect(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [protect(x) for x in value]
    return value

class FeatureContext:
    def __init__(self,service,payload):
        self.service=service;self.workbench=service.workbench;self.root=self.workbench.root
        self.simulate=self.workbench.simulate;self.payload=payload;self._history=None
    def snapshot(self):return self.workbench.snapshot()
    def protect(self,value):return protect(value)
    def safe_path(self,path):assert_regular_path(path);return Path(path)
    def activity(self):return self.service.activity()
    def history(self):
        if self._history is not None:return self._history
        rows=[];folder=self.safe_path(self.root/'reports')
        if folder.is_dir():
            import re
            directories=sorted((p for p in folder.iterdir() if re.fullmatch(r'\d{8}-\d{6}-[a-f0-9]+',p.name)),key=lambda p:p.name,reverse=True)
            for directory in directories[:200]:
                try:
                    path=self.safe_path(directory/'Diagnostic.json')
                    if not path.is_file() or path.stat().st_size>2*1024*1024:continue
                    with self.workbench.lock:data=json.loads(path.read_text(encoding='utf-8-sig'))
                    if not isinstance(data,dict) or data.get('final') is not True or not isinstance(data.get('finished_utc'),str) or not data['finished_utc']:continue
                    if data.get('run_id')!=directory.name:continue
                    if not isinstance(data.get('results',[]),list):continue
                    rows.append({'run_id':directory.name,'version':data.get('workbench_version','unknown'),'finished_utc':data['finished_utc'],'step_count':len(data.get('results',[])),'report':data})
                    if len(rows)==60:break
                except (OSError,ValueError):continue
        self._history=rows;return rows
    def latest_report(self):
        history=self.history();requested=self.payload.get('run_id')
        if requested:
            row=next((x for x in history if x['run_id']==requested),None)
            if not row:raise ValueError('Selected completed report is unavailable. Refresh the report list.')
            return row['report']
        return history[0]['report'] if history else {}
    def command(self,argv,timeout=20):
        # argv is supplied only by a registered handler; request payloads cannot supply commands.
        args=[str(x) for x in argv]
        if not args:raise ValueError('Empty diagnostic command.')
        if self.simulate:return {'exit_code':None,'output':'SIMULATED: command not executed.','simulated':True}
        if Path(args[0]).is_absolute():self.safe_path(Path(args[0]))
        else:
            found=self.workbench.find(args[0])
            if not found:return {'exit_code':None,'output':'Diagnostic executable not found.'}
            args[0]=str(found)
        if args[0].lower().endswith(('.cmd','.bat')):
            from engine import ps_literal
            args=self.workbench.ps_args('& '+' '.join(ps_literal(x) for x in args)+'; exit $LASTEXITCODE')
        env=self.workbench.env.copy()
        try:
            result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=min(max(int(timeout),1),45),env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),cwd=self.root)
            return {'exit_code':result.returncode,'output':redact((result.stdout+'\n'+result.stderr)[-24000:])}
        except subprocess.TimeoutExpired:return {'exit_code':None,'output':'Diagnostic timed out; no success inferred.'}
        except OSError as exc:return {'exit_code':None,'output':redact(str(exc))}
    def fetch_json(self,url):
        if self.simulate:raise ValueError('Network catalogs are not fetched in simulation.')
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or parsed.hostname not in ('nodejs.org','api.github.com','registry.npmjs.org','builds.dotnet.microsoft.com') or parsed.username or parsed.password:
            raise ValueError('Catalog URL is outside the official read-only allowlist.')
        if parsed.port not in (None,443):raise ValueError('Catalog requires the official HTTPS port.')
        is_npm=parsed.hostname=='registry.npmjs.org'
        limit=(8 if is_npm else 2)*1024*1024
        request=urllib.request.Request(url,headers={'User-Agent':'Namu-Feature-Studio/'+VERSION,'Accept':'application/vnd.npm.install-v1+json' if is_npm else 'application/json'})
        class OfficialRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                target=urllib.parse.urlsplit(newurl)
                if target.scheme!='https' or target.hostname!=parsed.hostname or target.port not in (None,443) or target.username or target.password:raise ValueError('Catalog redirect escaped the official host.')
                return super().redirect_request(req,fp,code,msg,headers,newurl)
        with urllib.request.build_opener(OfficialRedirect()).open(request,timeout=20) as response:
            data=response.read(limit+1)
            if len(data)>limit:raise ValueError('Catalog is too large for this bounded check.')
            return json.loads(data)

class FeatureService:
    def __init__(self,workbench):self.workbench=workbench;self.lock=threading.RLock();self.jobs=collections.OrderedDict()
    def catalog(self):return {'version':VERSION,'features':FEATURES,'count':100}
    def history(self):
        ctx=FeatureContext(self,{})
        return {'reports':[{k:x[k] for k in ('run_id','version','finished_utc','step_count')} for x in ctx.history()], 'default_run_id':ctx.history()[0]['run_id'] if ctx.history() else None,'limit':60}
    def activity(self):
        with self.lock:return [{k:j[k] for k in ('id','feature_id','state')} for j in self.jobs.values()]
    def get(self,job_id):
        with self.lock:
            if job_id not in self.jobs:raise KeyError('Feature job was not found or has expired.')
            return copy.deepcopy(self.jobs[job_id])
    def start(self,feature_id,payload):
        if not isinstance(payload,dict) or set(payload)-{'run_id','options'}:raise ValueError('Unsupported feature input. No paths or commands are accepted.')
        if 'run_id' in payload and (not isinstance(payload['run_id'],str) or len(payload['run_id'])>80):raise ValueError('Invalid report selection.')
        definition=next((x for x in FEATURES if x['id']==feature_id),None)
        if not definition:raise ValueError('Unknown feature.')
        if definition.get('client'):raise ValueError('This capability is a dashboard control, not a server job.')
        with self.lock:
            if sum(j['state']=='running' for j in self.jobs.values())>=2:raise RuntimeError('Two feature jobs are already running. Wait for one to finish.')
            # Settings changes wait for installation; read-only analysis remains available.
            if feature_id in ('f087','f089') and self.workbench.started and not self.workbench.finished:raise RuntimeError('Wait for the installation to finish before changing saved recipes.')
            while len(self.jobs)>=30:
                old=next((k for k,j in self.jobs.items() if j['state']!='running'),None)
                if old is None:break
                del self.jobs[old]
            identity=uuid.uuid4().hex;self.jobs[identity]={'id':identity,'feature_id':feature_id,'state':'running'}
        def execute():
            try:
                ctx=FeatureContext(self,payload)
                module=feature_diagnostics if int(feature_id[1:])<=30 else feature_reports if int(feature_id[1:])<=65 else feature_plans
                result=module.run(feature_id,ctx,payload)
                if not isinstance(result,dict) or not isinstance(result.get('summary'),str):raise ValueError('Feature did not return a valid result.')
                # Registered exporters sanitize structured content before serialization.
                # Redacting serialized JSON again can remove quotes; touching base64 can
                # corrupt ZIP bytes. Never interpret exports as executable instructions.
                artifact=result.pop('download',None)
                result=protect(result);result['simulated']=bool(ctx.simulate)
                if artifact is not None:
                    if not isinstance(artifact,dict) or set(artifact)-{'name','mime','text','encoding'} or not all(isinstance(artifact.get(k),str) for k in ('name','mime','text')) or len(artifact['text'])>12*1024*1024:
                        raise ValueError('Invalid or oversized local export.')
                    result['download']={**artifact,'name':redact(artifact['name'])}
                with self.lock:self.jobs[identity].update(state='complete',result=result)
            except Exception as exc:
                with self.lock:self.jobs[identity].update(state='failed',error=redact(str(exc))[:1500])
        threading.Thread(target=execute,daemon=True).start();return {'id':identity}
