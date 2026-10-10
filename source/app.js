'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const token = new URLSearchParams(location.hash.slice(1)).get('token') || sessionStorage.getItem('edge-token');
  if (token) { sessionStorage.setItem('edge-token',token); history.replaceState(null,'',location.pathname); }
  let seq=0, timer=null, ticks=12, snapshot=null, starting=false, quitting=false;
  const rows=new Map();
  const banner=(text,kind='')=>{ $('banner').textContent=text; $('banner').className='banner '+kind; };
  async function api(path,body) {
    const options={headers:{'X-Workbench-Token':token||''},cache:'no-store'};
    if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
    const r=await fetch('/api/'+path,options);
    if(!r.ok){let error;try{error=(await r.json()).error;}catch{}throw new Error(error||'Request failed: '+r.status);}
    return path==='report'?r.text():r.json();
  }
  function pause(){if(timer){clearInterval(timer);timer=null;} $('countdown').textContent='Automatic start paused';$('pause').disabled=true;}
  function options(){return Object.fromEntries([...document.querySelectorAll('.options input')].map(x=>[x.name,x.checked]));}
  async function start(){
    if(starting||snapshot?.started)return;pause();starting=true;$('start').disabled=true;
    try{await api('start',options());$('countdown').textContent='Run started';}catch(e){banner(e.message,'error');$('start').disabled=false;}finally{starting=false;}
  }
  function display(data){
    snapshot=data;
    if(data.started){if(timer){clearInterval(timer);timer=null;} document.querySelectorAll('.options input').forEach(x=>x.disabled=true);$('start').disabled=true;$('pause').disabled=true;$('countdown').textContent=data.finished?'Run completed; inspect results':'Run in progress';}
    $('current').textContent=data.current||'Ready to discover releases';
    $('progress').max=data.total||1;$('progress').value=data.completed;
    $('progressText').textContent=`${data.completed} / ${data.total} steps completed`;
    const counts={};data.results.forEach(r=>counts[r.status]=(counts[r.status]||0)+1);
    $('resultCount').textContent=Object.entries(counts).map(([k,v])=>`${v} ${k.toLowerCase().replaceAll('_',' ')}`).join(' · ')||'No changes yet';
    $('stop').disabled=!data.started||data.finished||data.cancel_requested;
    ['copy','download','reports'].forEach(id=>$(id).disabled=!data.report_ready);
    $('terminal').disabled=!data.terminal_ready;
    if(data.simulated)banner('SIMULATION ONLY — no software is being installed or checked on your laptop.','warning');
    else if(data.finished)banner(data.cancel_requested?'Stopped. Read the partial report before restarting.':'Run finished. Read every failed or review-needed item; installation is not proof that all services work.',['FAILED','REVIEW_NEEDED','VERSION_MISMATCH','CHANNEL_NOT_VERIFIED','INSTALLED_CHECK_NEEDED','REBOOT_REQUIRED'].some(x=>counts[x])?'warning':'');
    else if(data.cancel_requested)banner('Stop requested. Waiting for the current command to finish; no further steps will start.','warning');
    else if(data.started)banner('Applying selected updates. Windows installers may display permission or sign-in prompts.');
    else banner('Experimental channels selected. Automatic setup starts after the countdown; pause to change the scope.');
    const resultMap=new Map(data.results.map(r=>[r.id,r]));
    for(const p of data.plan){
      const r=resultMap.get(p.id)||p;const status=r.status||'QUEUED';
      let row=rows.get(p.id);
      if(!row){row=document.createElement('tr');row.innerHTML='<td><div class="row-name"></div><div class="row-note"></div></td><td class="version"></td><td><span class="status"></span></td>';rows.set(p.id,row);$('results').append(row);}
      row.querySelector('.row-name').textContent=r.name;
      row.querySelector('.row-note').textContent=r.detail||r.channel||'';
      row.querySelector('.version').textContent=[r.expected,r.actual].filter(Boolean).join(' → ')||(r.versions?Object.entries(r.versions).map(([k,v])=>k+' '+v).join('; '):'Discovered during run');
      const badge=row.querySelector('.status');badge.className='status '+status.toLowerCase();badge.textContent=status.replaceAll('_',' ');
    }
    if(data.logs.length){
      if(seq===0)$('log').textContent='';
      for(const l of data.logs){const p=document.createElement('p');p.className=l.level;const time=document.createElement('span');time.className='time';time.textContent=l.time.slice(11,19);p.append(time,document.createTextNode(l.message));$('log').append(p);seq=Math.max(seq,l.seq);}
      while($('log').children.length>1200)$('log').firstChild.remove();
      if($('follow').checked)$('log').scrollTop=$('log').scrollHeight;
    }
  }
  async function poll(){if(quitting)return;try{display(await api('status?after='+seq));}catch(e){banner('Dashboard connection interrupted: '+e.message,'error');}finally{if(!quitting)setTimeout(poll,900);}}
  $('start').addEventListener('click',start);$('pause').addEventListener('click',pause);
  document.querySelectorAll('.options input').forEach(x=>x.addEventListener('change',pause));
  $('stop').addEventListener('click',async()=>{try{await api('stop',{});}catch(e){banner(e.message,'error');}});
  $('copy').addEventListener('click',async()=>{try{const text=await api('report');try{await navigator.clipboard.writeText(text);$('copyStatus').textContent='Report copied. Review it before pasting into ChatGPT.';}catch{$('reportFallback').hidden=false;$('reportFallback').value=text;$('reportFallback').select();$('copyStatus').textContent='Clipboard access was blocked. Press Ctrl+C on the selected report.';}}catch(e){banner(e.message,'error');}});
  $('download').addEventListener('click',async()=>{try{const text=await api('report');const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='Paste-Into-ChatGPT.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){banner(e.message,'error');}});
  for(const [id,action] of [['reports','open-reports'],['terminal','open-terminal']])$(id).addEventListener('click',async()=>{try{await api(action,{});}catch(e){banner(e.message,'error');}});
  $('quit').addEventListener('click',async()=>{pause();try{const r=await api('quit',{});quitting=true;banner(r.after_current_operation?'Dashboard will close after the current operation finishes. You may close this tab.':'Dashboard stopped. You may close this tab.');}catch(e){banner(e.message,'error');}});
  if(!token){pause();banner('Missing local session capability. Open the dashboard by double-clicking the downloaded launcher.','error');$('start').disabled=true;return;}
  api('status').then(data=>{display(data);if(!data.started){timer=setInterval(()=>{ticks--;$('countdown').textContent=`Automatic start in ${ticks} seconds`;if(ticks<=0)start();},1000);}poll();}).catch(e=>{pause();banner(e.message,'error');});
})();
