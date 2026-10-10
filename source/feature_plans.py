"""Explicit plans and local exports; these actions never start an installation."""
from __future__ import annotations
import base64, csv, hashlib, html, io, json, os, tempfile, zipfile
from pathlib import Path
from engine import build_plan, default_options, assert_regular_path

PROFILES = [
    ('AI essentials', {}, 'Core AI tools with optional packs and paid checks off.'),
    ('Browser lab', {'browser':True}, 'Core tools plus Canary and Playwright.'),
    ('Document desk', {'toolkit':True}, 'Core tools plus documents, data and media.'),
    ('Science lab', {'science':True}, 'Core tools plus scientific Python.'),
    ('.NET lab', {'dotnet':True}, 'Core tools plus the daily .NET SDK.'),
    ('Full workshop without model requests', {k:True for k in default_options() if k!='live'}, 'Every optional pack except the quota-consuming model test.'),
    ('Documentation connection', {'docs_mcp':True}, 'Core tools plus the official documentation connection.'),
    ('Editor migration', {'migrate':True}, 'Core tools plus supported non-conflicting editor migration.'),
    ('Full workshop with connection test', {k:True for k in default_options()}, 'All optional packs, including one quota-consuming model request.'),
    ('Research builder', {'science':True,'dotnet':True}, 'Core tools plus science and .NET development.'),
]
EXTRAS = [
    ('Preview selected installation plan','List the actual steps for the current selection before starting anything.'),
    ('Inspect tool dependency map','Explain runtime dependencies and which paths remain isolated.'),
    ('Review network and approval requirements','Identify download sources, possible Windows approvals and model-quota use.'),
    ('Inspect runtime isolation boundaries','Distinguish managed tool commands from external or missing commands.'),
    ('Export checksum-pinned setup command','Create a reusable command with a pinned and verified first download.'),
    ('Export report as JSON','Download the selected diagnostic as structured JSON.'),
    ('Export report as Markdown','Download a readable operation table and warning summary.'),
    ('Export report as CSV','Download operation results for spreadsheets.'),
    ('Export portable HTML report','Download a self-contained, escaped report for local viewing.'),
    ('Export sanitized support bundle','Download a ZIP with the selected report, readable summary and checksums; no credentials.'),
    ('Export two-run comparison','Download status and managed-version changes between the selected run and its predecessor.'),
    ('Save a local selection recipe','Save the eight selected options in a Workbench-owned file, without starting installation.'),
    ('Load local selection recipe','Review saved options before explicitly applying them in the dashboard.'),
    ('Remove local selection recipe','Remove only the validated recipe written by this feature.'),
    ('Review feature execution history','Inspect recent feature jobs from this dashboard session.'),
]
FEATURES = [
    {'id':f'f{66+i:03}','title':title+' profile','description':description+' Core tools are always included; applying a profile does not start installation.','category':'Plans','effect':'preview'}
    for i,(title,_,description) in enumerate(PROFILES)
] + [
    {'id':f'f{76+i:03}','title':title,'description':description,'category':'Plans and exports','effect':'local settings' if i in (11,13) else 'local export' if 4<=i<=10 else 'read-only'}
    for i,(title,description) in enumerate(EXTRAS)
]

def options_for(payload,ctx):
    choices=payload.get('options',ctx.snapshot().get('options',default_options()))
    if not isinstance(choices,dict) or set(choices)!=set(default_options()) or any(type(v) is not bool for v in choices.values()):
        raise ValueError('The selection must contain exactly the eight supported boolean options.')
    return dict(choices)

def download(name,mime,text):
    return {'name':name,'mime':mime,'text':text}

def report_rows(report):
    return [{k:row.get(k,'') for k in ('id','name','status','expected','actual','detail')} for row in report.get('results',[]) if isinstance(row,dict)]

def markdown(report):
    def cell(value):return str(value).replace('|','\\|').replace('\r',' ').replace('\n',' ')
    lines=['# Namu AI Workbench diagnostic', '', f"Run: {report.get('run_id','unknown')}",f"Simulation: {bool(report.get('simulated'))}", '', '| Operation | Result | Detail |','| --- | --- | --- |']
    lines += ['| '+ ' | '.join(cell(row.get(k,'')) for k in ('name','status','detail'))+' |' for row in report_rows(report)]
    doctor=report.get('checks',{}).get('codex_doctor',{})
    lines += ['', '## Doctor observations', '', json.dumps(doctor,indent=2,ensure_ascii=True), '', 'Installation, local execution and cloud authorization are separate evidence.']
    return '\n'.join(lines)+'\n'

_RECIPE_OWNER = {'owner':'namu-feature-studio-v1','schema':1}

def _file_identity(info):
    return info.st_dev, info.st_ino

def _target_state(path):
    assert_regular_path(path)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError('A non-file recipe target was preserved.')
    info=path.stat()
    return (*_file_identity(info),info.st_size,info.st_mtime_ns,info.st_ctime_ns)

def _read_recipe_json(path,limit,message):
    assert_regular_path(path)
    if not path.is_file():
        raise ValueError(message)
    with path.open('rb') as stream:
        content=stream.read(limit+1)
    if len(content)>limit:
        raise ValueError(message)
    try:
        return json.loads(content)
    except (ValueError,UnicodeError):
        raise ValueError(message) from None

def _validate_recipe_owner(folder):
    assert_regular_path(folder)
    if not folder.is_dir():
        raise ValueError('Existing feature-workspace is not owned by Feature studio; preserved.')
    marker=folder/'.workbench-feature-owner.json'
    value=_read_recipe_json(marker,1024,'Existing feature-workspace is not owned by Feature studio; preserved.')
    if not isinstance(value,dict) or value!=_RECIPE_OWNER or type(value.get('schema')) is not int:
        raise ValueError('Existing feature-workspace is not owned by Feature studio; preserved.')

def _validate_new_recipe_marker(folder):
    assert_regular_path(folder)
    marker=folder/'.workbench-feature-owner.json'
    assert_regular_path(marker)
    if not folder.is_dir() or marker.exists():
        raise ValueError('A concurrently created ownership marker was preserved.')

def _write_recipe_json(path,value,validate,exclusive=False):
    """Write only our exclusive temporary file, then publish completed JSON.

    The descriptor remains attached to the newly created file; a planted legacy
    .tmp path is never opened. Ownership and observed target changes are checked
    again before publication. The first ownership marker is never replaced.
    """
    content=json.dumps(value,ensure_ascii=False,indent=2)
    validate()
    folder=path.parent
    folder_identity=_file_identity(folder.stat())
    original_target=_target_state(path)
    if exclusive and original_target is not None:
        raise ValueError('An existing ownership marker was preserved.')
    descriptor,name=tempfile.mkstemp(prefix='.workbench-recipe-',suffix='.tmp',dir=folder)
    temporary=Path(name)
    temporary_identity=_file_identity(os.fstat(descriptor))

    def check_paths():
        assert_regular_path(folder)
        assert_regular_path(temporary)
        if not folder.is_dir() or _file_identity(folder.stat())!=folder_identity:
            raise ValueError('The recipe workspace changed during saving; preserved.')
        if not temporary.is_file() or _file_identity(temporary.stat())!=temporary_identity:
            raise ValueError('The temporary recipe path changed during saving; preserved.')
        if _target_state(path)!=original_target:
            raise ValueError('The recipe target changed during saving; preserved.')
        validate()

    try:
        check_paths()
        with os.fdopen(descriptor,'w',encoding='utf-8') as stream:
            descriptor=None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        check_paths()
        if exclusive:
            # A completed marker is published atomically without overwriting a
            # marker planted after validation; hard-link creation is exclusive.
            os.link(temporary,path)
        else:
            os.replace(temporary,path)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        # Remove only the temporary inode that this call created, even on error.
        try:
            assert_regular_path(folder)
            assert_regular_path(temporary)
            if (_file_identity(folder.stat())==folder_identity and temporary.is_file()
                    and _file_identity(temporary.stat())==temporary_identity):
                temporary.unlink()
        except (OSError,ValueError):
            pass

def recipe_path(ctx,create=False):
    folder=ctx.root/'feature-workspace'; marker=folder/'.workbench-feature-owner.json'
    assert_regular_path(folder)
    if folder.exists():
        _validate_recipe_owner(folder)
    elif create:
        folder.mkdir()
        _write_recipe_json(marker,_RECIPE_OWNER,lambda:_validate_new_recipe_marker(folder),exclusive=True)
        _validate_recipe_owner(folder)
    path=folder/'selection-recipe.json';assert_regular_path(path)
    if path.exists():
        saved=_read_recipe_json(path,8192,'Oversized, unknown or externally modified recipe file was preserved.')
        if not isinstance(saved,dict) or set(saved)!={'schema','options'} or saved.get('schema')!='namu-selection-recipe/1':raise ValueError('Unknown or externally modified recipe file was preserved.')
        options_for({'options':saved['options']},ctx)
    return path

def run(feature_id,ctx,payload):
    number=int(feature_id[1:])
    if feature_id not in {x['id'] for x in FEATURES}:raise ValueError('Unknown planning feature.')
    if 66<=number<=75:
        title,enabled,_=PROFILES[number-66];choices={k:False for k in default_options()};choices.update(enabled)
        return {'summary':title+' selection ready. Review and apply it explicitly; no installation started.','options':choices,'data':{'steps':build_plan(choices),'live_request_uses_quota':choices['live']}}
    if number==76:
        choices=options_for(payload,ctx);return {'summary':'Actual installation plan for the selected options.','data':{'options':choices,'steps':build_plan(choices)}}
    if number==77:
        return {'summary':'Runtime dependency map; installed application bundles may use their own runtimes.','data':{'nightly_node':['Codex CLI','JavaScript SDKs','Playwright'],'compatible_npm_host':['npm package installation only'],'compatible_python':['OpenAI/Agents/MCP Python SDKs','document libraries','science libraries'],'uv':['Python discovery','binary-wheel resolution','hashed package installation'],'go':['official OpenAI CLI fallback only when no compatible verified binary is offered'],'original_system_tools':'Preserved; no project dependency rewrite.'}}
    if number==78:
        plan=build_plan(options_for(payload,ctx))
        return {'summary':'Selected operations may download files and request installer approval. This is a requirement review, not a byte estimate.','data':{'catalog_packages':[{'name':x['name'],'source':x['source'],'channel':x['channel'],'may_need_windows_approval':True} for x in plan if x['kind']=='winget'],'runtime_publishers':['nodejs.org','registry.npmjs.org','astral-sh Python catalog','pypi.org','Microsoft .NET'],'model_request_selected':any(x['id']=='live' for x in plan),'credentials_and_sign_in':'Existing authentication reused; missing permissions require the owner.'}}
    if number==79:
        rows=[]
        for name,tool in ctx.workbench.active.items():
            commands=[]
            for value in tool.get('command',[]):
                path=Path(value)
                try:managed=path.resolve().is_relative_to(ctx.root.resolve())
                except OSError:managed=False
                commands.append({'basename':path.name,'inside_workbench':managed,'exists':path.is_file()})
            rows.append({'tool':name,'version':tool.get('version'),'commands':commands})
        return {'summary':'Managed-runtime isolation observed from the active tool map.','data':rows}
    if number==80:
        text="& { $ErrorActionPreference='Stop'; $p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/20c323f68c15be6e91ebc4e31f173f581c940c0a/Setup.ps1' -UseBasicParsing -OutFile $p; if ((Get-FileHash $p -Algorithm SHA256).Hash -ine '2360295d3d44f19d5e39ea2f48a774833720ca4d26f9b1ccb1a86c25540cdd04') { throw 'Setup checksum mismatch' }; $old=$env:EDGE_ALL_TOOLS; try { $env:EDGE_ALL_TOOLS='1'; & \"$env:SystemRoot\\System32\\WindowsPowerShell\\v1.0\\powershell.exe\" -NoProfile -STA -ExecutionPolicy Bypass -File $p; if ($LASTEXITCODE -ne 0) { throw 'Setup failed' } } finally { $env:EDGE_ALL_TOOLS=$old } }\n"
        return {'summary':'Checksum-pinned initial-download command. It opens the existing graphical updater.','data':{'trust':'The independent initial hash is embedded here; the application updater follows published repository source.'},'download':download('Namu-Verified-Setup.txt','text/plain',text)}
    if 81<=number<=86:
        report=ctx.protect(ctx.latest_report())
        if not report:raise ValueError('No completed diagnostic report is available yet.')
        rows=report_rows(report);title=report.get('run_id','diagnostic');md=markdown(report)
        if number==81:artifact=download(title+'.json','application/json',json.dumps(report,indent=2))
        elif number==82:artifact=download(title+'.md','text/markdown',md)
        elif number==83:
            stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=['run_id','report_simulated','report_final','id','name','status','expected','actual','detail']);writer.writeheader()
            for row in rows:
                # Spreadsheet formula injection must not turn untrusted report text into code.
                values={'run_id':title,'report_simulated':bool(report.get('simulated')),'report_final':report.get('final') is True,**row}
                writer.writerow({k:("'"+str(v) if str(v).lstrip().startswith(('=','+','-','@')) else v) for k,v in values.items()})
            artifact=download(title+'.csv','text/csv',stream.getvalue())
        elif number==84:
            body=''.join('<tr>'+''.join('<td>'+html.escape(str(row[k]))+'</td>' for k in ('name','status','detail'))+'</tr>' for row in rows)
            text='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Namu diagnostic</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#101722;color:#eef6ff}td,th{border-bottom:1px solid #42516b;padding:14px;text-align:left;overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}pre{white-space:pre-wrap}</style><h1>Namu AI diagnostic</h1><p>'+html.escape(title)+'</p><p>Simulation: '+str(bool(report.get('simulated')))+'</p><table><thead><tr><th>Operation</th><th>Result</th><th>Detail</th></tr></thead><tbody>'+body+'</tbody></table><h2>Doctor observations</h2><pre>'+html.escape(json.dumps(report.get('checks',{}).get('codex_doctor',{}),indent=2))+'</pre></html>'
            artifact=download(title+'.html','text/html',text)
        elif number==85:
            files={'Diagnostic.json':json.dumps(report,indent=2).encode(),'Review.md':md.encode()}
            files['SHA256SUMS.txt']=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in files.items()).encode()
            stream=io.BytesIO()
            with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
                for name,data in files.items():bundle.writestr(name,data)
            artifact={**download(title+'-support.zip','application/zip',base64.b64encode(stream.getvalue()).decode()),'encoding':'base64'}
        else:
            history=ctx.history();selected=report.get('run_id');at=next((i for i,x in enumerate(history) if x['run_id']==selected),0)
            older=history[at+1]['report'] if at+1<len(history) else None
            if not older:raise ValueError('A previous completed run is needed for comparison.')
            changes=[];old={x.get('id'):x for x in older.get('results',[])}
            for row in rows:
                before=old.get(row['id'],{})
                if before.get('status')!=row['status'] or before.get('actual')!=row['actual']:changes.append({'id':row['id'],'before_status':before.get('status','not selected'),'after_status':row['status'],'before_version':before.get('actual'),'after_version':row['actual']})
            data=ctx.protect({'from':older.get('run_id'),'to':selected,'from_simulated':bool(older.get('simulated')),'to_simulated':bool(report.get('simulated')),'from_final':older.get('final') is True,'to_final':report.get('final') is True,'scope':'Only common IDs are directly comparable; installation scopes can differ. Simulation and real observations are separate evidence.','changes':changes})
            artifact=download(title+'-comparison.json','application/json',json.dumps(data,indent=2))
        return {'summary':'Local export is ready. Review it before sharing; no upload was made.','data':{'run_id':title,'format':artifact['mime'],'report_simulated':bool(report.get('simulated')),'report_final':report.get('final') is True},'download':artifact}
    if number==87:
        choices=options_for(payload,ctx);path=recipe_path(ctx,create=True)
        _write_recipe_json(path,{'schema':'namu-selection-recipe/1','options':choices},lambda:recipe_path(ctx))
        return {'summary':'Selection recipe saved locally. Installation was not started.','data':{'options':choices,'stored_in':'Workbench-owned feature-workspace'}}
    if number==88:
        path=recipe_path(ctx)
        if not path.is_file():raise ValueError('No saved selection recipe exists.')
        choices=options_for({'options':json.loads(path.read_text())['options']},ctx)
        return {'summary':'Saved recipe loaded for review; apply explicitly in the dashboard.','data':{'options':choices},'options':choices}
    if number==89:
        path=recipe_path(ctx)
        if path.is_file():path.unlink()
        return {'summary':'The validated local selection recipe was removed; tool settings and installation history were preserved.','data':{'recipe_present':False}}
    return {'summary':'Feature jobs from this dashboard session; no command or credential history is included.','data':ctx.activity()}
