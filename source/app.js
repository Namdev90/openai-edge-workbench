'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const storageRead=(key,fallback)=>{try{return localStorage.getItem(key)??fallback;}catch{return fallback;}};
  const storageWrite=(key,value)=>{try{localStorage.setItem(key,value);return true;}catch{return false;}};
  let token=new URLSearchParams(location.hash.slice(1)).get('token');
  try{token=token||sessionStorage.getItem('edge-token');if(token)sessionStorage.setItem('edge-token',token);}catch{}
  if(token)history.replaceState(null,'',location.pathname);
  let seq=0,timer=null,ticks=12,snapshot=null,starting=false,quitting=false,optionsSynced=false;
  let catalog=[],catalogLoaded=false,featureBusy=false,currentFeatureResult=null,paletteMatches=[],paletteIndex=0;
  let aiProviders=[],aiLocalProvider=null,aiSimulation=true,aiPreview=null,aiBusy=false,aiRevision=0;
  const rows=new Map(),logEntries=[];
  const featurePattern=/^f(?:00[1-9]|0[1-9][0-9]|100)$/;
  let favorites=new Set();
  try{const saved=JSON.parse(storageRead('namu-feature-favorites','[]'));if(Array.isArray(saved))favorites=new Set(saved.filter(x=>typeof x==='string'&&featurePattern.test(x)));}catch{}
  const make=(tag,className,text)=>{const element=document.createElement(tag);if(className)element.className=className;if(text!==undefined)element.textContent=String(text);return element;};
  const banner=(text,kind='')=>{if($('banner').textContent!==text)$('banner').textContent=text;$('banner').className='banner '+kind;};
  async function api(path,body){
    const request={headers:{'X-Workbench-Token':token||''},cache:'no-store'};
    if(body!==undefined){request.method='POST';request.headers['Content-Type']='application/json';request.body=JSON.stringify(body);}
    const response=await fetch('/api/'+path,request);
    if(!response.ok){let error;try{error=(await response.json()).error;}catch{}throw new Error(error||'Request failed: '+response.status);}
    return path==='report'?response.text():response.json();
  }
  function pause(){if(timer){clearInterval(timer);timer=null;}$('countdown').textContent='Automatic start paused';$('pause').disabled=true;}
  function options(){return Object.fromEntries([...document.querySelectorAll('.options input')].map(x=>[x.name,x.checked]));}
  async function start(){
    if(starting||snapshot?.started)return;pause();starting=true;$('start').disabled=true;
    try{await api('start',options());$('countdown').textContent='Run started';}catch(error){banner(error.message,'error');$('start').disabled=false;}finally{starting=false;}
  }
  function display(data){
    snapshot=data;
    if(!optionsSynced&&data.options){document.querySelectorAll('.options input').forEach(x=>{if(typeof data.options[x.name]==='boolean')x.checked=data.options[x.name];});optionsSynced=true;}
    if(data.started){if(timer){clearInterval(timer);timer=null;}document.querySelectorAll('.options input').forEach(x=>x.disabled=true);$('start').disabled=true;$('pause').disabled=true;$('countdown').textContent=data.finished?'Run completed; inspect results':'Run in progress';}
    $('current').textContent=data.current||'Ready to discover releases';
    $('progress').max=data.total||1;$('progress').value=data.completed;
    $('progressText').textContent=`${data.completed} / ${data.total} steps completed`;
    const counts={};data.results.forEach(result=>counts[result.status]=(counts[result.status]||0)+1);
    $('resultCount').textContent=Object.entries(counts).map(([key,value])=>`${value} ${key.toLowerCase().replaceAll('_',' ')}`).join(' · ')||'No changes yet';
    $('overviewSteps').textContent=String(data.completed||0);
    $('overviewVerified').textContent=String(counts.VERIFIED||0);
    const attention=['FAILED','REVIEW_NEEDED','VERSION_MISMATCH','CHANNEL_NOT_VERIFIED','INSTALLED_CHECK_NEEDED','REBOOT_REQUIRED'];
    $('overviewAttention').textContent=String(attention.reduce((sum,key)=>sum+(counts[key]||0),0));
    $('stop').disabled=!data.started||data.finished||data.cancel_requested;
    ['copy','download','reports'].forEach(id=>$(id).disabled=!data.report_ready);$('terminal').disabled=!data.terminal_ready;
    $('featureApply').disabled=Boolean(data.started||starting);
    if(data.simulated)banner('SIMULATION ONLY — no software is being installed or checked on your laptop.','warning');
    else if(data.finished)banner(data.cancel_requested?'Stopped. Read the partial report before restarting.':'Run finished. Inspect every failed or review-needed item; installation alone does not verify all services.',attention.some(key=>counts[key])?'warning':'');
    else if(data.cancel_requested)banner('Stop requested. Waiting for the current command to finish; no further steps will start.','warning');
    else if(data.started)banner('Applying selected updates. Windows installers may display permission or sign-in prompts.');
    else banner('Experimental channels selected. Automatic setup starts after the countdown; pause to change the scope.');
    const resultMap=new Map(data.results.map(result=>[result.id,result]));
    for(const planned of data.plan){
      const result=resultMap.get(planned.id)||planned,status=result.status||'QUEUED';let row=rows.get(planned.id);
      if(!row){row=make('tr');const nameCell=make('td'),versionCell=make('td','version'),statusCell=make('td');nameCell.append(make('div','row-name'),make('div','row-note'));statusCell.append(make('span','status'));row.append(nameCell,versionCell,statusCell);rows.set(planned.id,row);$('results').append(row);}
      row.querySelector('.row-name').textContent=result.name;
      row.querySelector('.row-note').textContent=result.detail||result.channel||'';
      row.querySelector('.version').textContent=[result.expected,result.actual].filter(Boolean).join(' → ')||(result.versions?Object.entries(result.versions).map(([key,value])=>key+' '+value).join('; '):'Discovered during run');
      const badge=row.querySelector('.status');badge.className='status '+status.toLowerCase();badge.textContent=status.replaceAll('_',' ');
    }
    if(data.logs.length){
      for(const line of data.logs){if(line.seq<=seq)continue;logEntries.push(line);seq=Math.max(seq,line.seq);}
      if(logEntries.length>1200)logEntries.splice(0,logEntries.length-1200);renderLogs();
    }
  }
  function renderLogs(){
    const search=$('logSearch').value.trim().toLowerCase(),severity=$('logSeverity').value;
    const selected=logEntries.filter(line=>(!search||String(line.message).toLowerCase().includes(search))&&(!severity||(line.level==='warn'?'warning':line.level)===severity));
    const fragment=document.createDocumentFragment();
    for(const line of selected){const level=['info','warning','warn','error'].includes(line.level)?line.level:'info';const p=make('p',level),time=make('span','time',String(line.time).slice(11,19));p.append(time,document.createTextNode(String(line.message)));fragment.append(p);}
    if(!selected.length)fragment.append(make('p','muted',logEntries.length?'No messages match these filters.':'Actual command output will appear here.'));
    $('log').replaceChildren(fragment);$('logCount').textContent=`${selected.length} of ${logEntries.length} messages`;
    if($('follow').checked)$('log').scrollTop=$('log').scrollHeight;
  }
  async function poll(){if(quitting)return;try{display(await api('status?after='+seq));}catch(error){banner('Dashboard connection interrupted: '+error.message,'error');}finally{if(!quitting)setTimeout(poll,900);}}
  function saveFavorites(){const persisted=storageWrite('namu-feature-favorites',JSON.stringify([...favorites]));if(!persisted)$('featureResultNotice').textContent='Browser storage is unavailable. Saved features last for this session only.';}
  function filteredFeatures(search=$('featureSearch').value,category=$('featureCategory').value,savedOnly=$('favoritesOnly').checked){
    const query=search.trim().toLowerCase();return catalog.filter(feature=>(!category||feature.category===category)&&(!savedOnly||favorites.has(feature.id))&&(!query||[feature.id,feature.title,feature.description,feature.category].join(' ').toLowerCase().includes(query)));
  }
  function toggleFavorite(id){if(!catalog.some(feature=>feature.id===id))return;if(favorites.has(id))favorites.delete(id);else favorites.add(id);saveFavorites();renderFeatures();}
  function renderFeatures(){
    const selected=filteredFeatures(),fragment=document.createDocumentFragment();
    for(const feature of selected){
      const card=make('article','feature-card');card.dataset.featureId=feature.id;
      const top=make('div','feature-card-top'),favorite=make('button','favorite-button',favorites.has(feature.id)?'★':'☆');favorite.type='button';favorite.setAttribute('aria-label',(favorites.has(feature.id)?'Unsave ':'Save ')+feature.title);favorite.setAttribute('aria-pressed',String(favorites.has(feature.id)));favorite.addEventListener('click',()=>{toggleFavorite(feature.id);$('featureGrid').querySelector(`[data-feature-id="${feature.id}"] .favorite-button`)?.focus();});
      top.append(make('span','feature-id',feature.id),favorite);
      const metadata=make('div','feature-meta');metadata.append(make('span','feature-category',feature.category),make('span','feature-effect',feature.client?'Browser preference':feature.effect||'Local check'));
      const button=make('button','feature-run',feature.client?'Open control':'Run feature');button.type='button';button.disabled=featureBusy&&!feature.client;button.setAttribute('aria-label',(feature.client?'Open control: ':'Run feature: ')+feature.title);button.addEventListener('click',()=>runFeature(feature));
      card.append(top,make('h3','',feature.title),make('p','',feature.description),metadata,button);fragment.append(card);
    }
    $('featureGrid').replaceChildren(fragment);$('featureEmpty').hidden=Boolean(selected.length)||!catalogLoaded;
    if(catalogLoaded)$('featureCount').textContent=`${selected.length} of ${catalog.length} features · ${new Set(selected.map(feature=>feature.category)).size} categories in view`;
    $('favoritesCount').textContent=`${favorites.size} saved`;if($('commandPalette').open)renderPalette();
  }
  async function loadFeatures(){
    try{const response=await api('features');if(!Array.isArray(response.features))throw new Error('The engine returned an invalid feature catalog.');
      const seen=new Set();catalog=response.features.filter(feature=>{if(!feature||!featurePattern.test(feature.id)||seen.has(feature.id)||typeof feature.title!=='string'||typeof feature.description!=='string'||typeof feature.category!=='string')return false;seen.add(feature.id);return true;});catalogLoaded=true;
      favorites=new Set([...favorites].filter(id=>seen.has(id)));const categoryFragment=document.createDocumentFragment();categoryFragment.append(new Option('All categories',''));[...new Set(catalog.map(feature=>feature.category))].sort().forEach(category=>categoryFragment.append(new Option(category,category)));$('featureCategory').replaceChildren(categoryFragment);
      $('overviewFeatures').textContent=String(catalog.length);$('overviewFeatures').nextElementSibling.textContent='available in this catalog';renderFeatures();
      if(catalog.length!==100)$('featureCount').textContent+=` · Expected 100; received ${catalog.length}.`;
    }catch(error){$('featureCount').textContent='Feature catalog unavailable: '+error.message;$('overviewFeatures').textContent='Unavailable';}
    try{const historyData=await api('features/history');if(Array.isArray(historyData.reports)){const items=document.createDocumentFragment();items.append(new Option('Most recent completed report',''));for(const report of historyData.reports){if(typeof report.run_id!=='string')continue;const label=`${report.run_id} · ${report.step_count??'?'} steps`;items.append(new Option(label,report.run_id));}$('featureReport').replaceChildren(items);if(typeof historyData.default_run_id==='string'&&historyData.reports.some(report=>report.run_id===historyData.default_run_id))$('featureReport').value=historyData.default_run_id;if(aiPreview&&aiPreview.run_id!==$('featureReport').value){resetAiPreview();displayAiProvider();}}}
    catch(error){$('featureReport').title='Saved reports unavailable: '+error.message;}
  }
  function selectedAiProvider(){return aiProviders.find(provider=>provider.id===$('aiProvider').value);}
  function aiNotice(text){if($('aiStatus').textContent!==text)$('aiStatus').textContent=text;}
  function updateAiControls(){
    const provider=selectedAiProvider();$('aiPreview').disabled=aiBusy||!provider;
    $('aiLocalAsk').disabled=aiBusy||!aiLocalProvider;
    $('aiConnect').disabled=aiBusy||aiSimulation||!provider||!$('aiSessionKey').value.trim();
    $('aiReviewed').disabled=aiBusy;$('aiFreeAccount').disabled=aiBusy;
    const contextMatches=aiPreview&&aiPreview.provider===provider?.id&&aiPreview.run_id===$('featureReport').value;
    $('aiAsk').disabled=aiBusy||aiSimulation||snapshot?.simulated===true||aiPreview?.simulated===true||provider?.key_ready!==true||!contextMatches||!$('aiReviewed').checked||!$('aiFreeAccount').checked;
  }
  function resetAiPreview(){
    aiRevision++;aiPreview=null;$('aiPreviewPanel').hidden=true;$('aiReviewed').checked=false;$('aiFreeAccount').checked=false;$('aiExcerpt').textContent='';$('aiPreviewHash').textContent='';updateAiControls();
    if(!aiBusy)aiNotice('Preview the selected report excerpt before approving any external request.');
  }
  function displayAiProvider(){
    const provider=selectedAiProvider();$('aiModel').textContent=provider?.model||'—';$('aiEnvKey').textContent=provider?.env_key||'—';$('aiKeyStatus').textContent=provider?.key_ready===true?'Available to the local engine':'Optional service key not connected';
    $('aiFreeLimits').textContent=provider?.free_limits||'Free-tier account setup, quotas and provider restrictions apply.';$('aiDocs').hidden=true;$('aiDocs').removeAttribute('href');
    if(provider?.docs_url){try{const url=new URL(provider.docs_url);if(url.protocol==='https:'&&!url.username&&!url.password){$('aiDocs').href=url.href;$('aiDocs').hidden=false;}}catch{}}
    updateAiControls();if(aiSimulation)aiNotice('Simulation: local excerpt preview is available; external AI requests are disabled.');else if(provider?.key_ready!==true)aiNotice('Built-in guidance works now. To try this optional provider, use its official setup link and connect a free-tier service key. Preview remains available.');
  }
  async function loadAiProviders(){
    try{const response=await api('ai/providers');if(!Array.isArray(response.providers)||typeof response.simulation!=='boolean')throw new Error('The engine returned invalid AI provider information.');
      const chosen=$('aiProvider').value,seen=new Set();const available=response.providers.filter(provider=>{if(!provider||typeof provider.id!=='string'||!/^[a-z][a-z0-9_-]{1,31}$/.test(provider.id)||seen.has(provider.id)||typeof provider.name!=='string'||typeof provider.model!=='string'||(provider.id!=='local'&&typeof provider.env_key!=='string'))return false;seen.add(provider.id);return true;});aiSimulation=response.simulation;aiLocalProvider=available.find(provider=>provider.id==='local')||null;aiProviders=available.filter(provider=>provider.id!=='local');
      const fragment=document.createDocumentFragment();for(const provider of aiProviders)fragment.append(new Option(provider.name,provider.id));if(!aiProviders.length)fragment.append(new Option('No cloud providers available',''));$('aiProvider').replaceChildren(fragment);if(aiProviders.some(provider=>provider.id===chosen))$('aiProvider').value=chosen;$('aiProvider').disabled=!aiProviders.length;displayAiProvider();$('aiLocalStatus').textContent=aiLocalProvider?'No key, account or upload required. Explains the completed report selected in Feature studio.':'Built-in report guidance is unavailable in this engine.';
    }catch(error){$('aiProvider').disabled=true;$('aiPreview').disabled=true;$('aiAsk').disabled=true;$('aiLocalAsk').disabled=true;aiNotice('Optional AI helper unavailable: '+error.message);$('aiLocalStatus').textContent='Report guidance unavailable: '+error.message;}
  }
  async function previewAiExcerpt(){
    if(aiBusy||!selectedAiProvider())return;if(!snapshot?.started)pause();resetAiPreview();const provider=selectedAiProvider(),runId=$('featureReport').value,revision=aiRevision;aiBusy=true;updateAiControls();aiNotice('Preparing a local redacted excerpt. No external request is being made.');
    try{const payload={provider:provider.id};if(runId)payload.run_id=runId;const preview=await api('ai/preview',payload);
      if(revision!==aiRevision)return;if(preview.provider!==provider.id||typeof preview.excerpt!=='string'||typeof preview.sha256!=='string'||!/^[a-f0-9]{64}$/i.test(preview.sha256)||typeof preview.simulated!=='boolean')throw new Error('The engine returned an invalid excerpt preview. Nothing was sent.');
      aiPreview={provider:provider.id,run_id:runId,sha256:preview.sha256.toLowerCase(),simulated:preview.simulated};$('aiExcerpt').textContent=preview.excerpt;$('aiPreviewHash').textContent='SHA-256 · '+aiPreview.sha256;$('aiPreviewPanel').hidden=false;
      aiNotice(preview.simulated?'SIMULATED REPORT: review is available, but external AI requests are disabled.':provider.key_ready===true?'Review the excerpt and both consent statements to enable one request.':'Excerpt prepared locally. Connect an optional free-tier service key to use this provider. Built-in guidance needs no key.');
    }catch(error){if(revision===aiRevision)aiNotice('Excerpt preview failed: '+error.message);}finally{aiBusy=false;updateAiControls();}
  }
  async function askAiProvider(){
    updateAiControls();if($('aiAsk').disabled||!aiPreview||aiPreview.simulated)return;if(!snapshot?.started)pause();const preview={...aiPreview},provider=selectedAiProvider();aiBusy=true;updateAiControls();$('aiResultPanel').hidden=false;$('aiResultTitle').textContent='AI explanation';$('aiResultKind').textContent='UNVERIFIED ADVICE';$('aiAdviceNote').textContent='This explanation can be wrong. Compare it with the diagnostic evidence and official documentation. Workbench does not execute suggested commands, change settings or apply repairs from this response.';$('aiResultMeta').textContent=provider.name+' · '+provider.model;$('aiResultText').textContent='Waiting for the selected provider…';$('aiResultLimits').textContent='';aiNotice('Sending one approved excerpt to '+provider.name+'. No retries or provider fallback will be made.');
    try{const payload={provider:preview.provider,preview_sha256:preview.sha256,allow_external:true,free_account:true};if(preview.run_id)payload.run_id=preview.run_id;const job=await api('ai/ask',payload);if(typeof job.id!=='string'||!/^[A-Za-z0-9_-]{1,100}$/.test(job.id))throw new Error('The engine returned an invalid AI job identifier.');
      for(let attempt=0;attempt<120;attempt++){if(quitting)throw new Error('Dashboard is closing.');const outcome=await api('ai/jobs/'+encodeURIComponent(job.id));if(outcome.state==='complete'){if(!outcome.result||typeof outcome.result.text!=='string')throw new Error('The provider returned no readable explanation.');$('aiResultText').textContent=outcome.result.text;$('aiResultMeta').textContent=String(outcome.result.provider||provider.name)+' · '+String(outcome.result.model||provider.model);const limits=outcome.result.limitations;$('aiResultLimits').textContent=Array.isArray(limits)?limits.map(String).join(' '):String(limits||'Provider output is unverified advice.');aiNotice('AI explanation received. It is unverified advice; no commands or repairs were executed.');return;}if(outcome.state==='failed')throw new Error(outcome.error||'The provider request failed.');if(outcome.state!=='running')throw new Error('The engine returned an unknown AI job state.');await new Promise(resolve=>setTimeout(resolve,1000));}
      throw new Error('No completed response was observed within two minutes. No retry was made; the request may still be running.');
    }catch(error){$('aiResultTitle').textContent='AI request needs attention';$('aiResultText').textContent=error.message;aiNotice('AI request failed or remains unverified. No retry, fallback or repair was performed.');}
    finally{aiBusy=false;$('aiReviewed').checked=false;$('aiFreeAccount').checked=false;updateAiControls();}
  }
  async function connectAiSession(){
    updateAiControls();if($('aiConnect').disabled)return;const provider=selectedAiProvider(),key=$('aiSessionKey').value.trim();$('aiSessionKey').value='';aiBusy=true;updateAiControls();resetAiPreview();aiNotice('Connecting the optional key to this local dashboard session.');
    try{await api('ai/connect',{provider:provider.id,key});await loadAiProviders();aiNotice('Service key connected for this dashboard session. Preview the excerpt before sharing it.');}catch(error){aiNotice('Could not connect this optional service key: '+error.message);}finally{$('aiSessionKey').value='';aiBusy=false;updateAiControls();}
  }
  async function askLocalGuidance(){
    if(aiBusy||!aiLocalProvider)return;if(!snapshot?.started)pause();aiBusy=true;updateAiControls();$('aiResultPanel').hidden=false;$('aiResultTitle').textContent='Built-in guidance';$('aiResultKind').textContent='LOCAL REPORT RULES';$('aiResultMeta').textContent='Built-in guidance · No upload';$('aiResultText').textContent='Reading recorded report evidence…';$('aiResultLimits').textContent='';$('aiAdviceNote').textContent='This guidance summarizes recorded evidence with fixed rules. Incomplete checks remain incomplete. No suggested commands or repairs are executed.';$('aiLocalStatus').textContent='Preparing built-in guidance locally. No account, key or network request is needed.';
    try{const payload={provider:'local'};if($('featureReport').value)payload.run_id=$('featureReport').value;const job=await api('ai/ask',payload);if(typeof job.id!=='string'||!/^[A-Za-z0-9_-]{1,100}$/.test(job.id))throw new Error('The engine returned an invalid guidance job identifier.');
      for(let attempt=0;attempt<120;attempt++){if(quitting)throw new Error('Dashboard is closing.');const outcome=await api('ai/jobs/'+encodeURIComponent(job.id));if(outcome.state==='complete'){if(!outcome.result||typeof outcome.result.text!=='string')throw new Error('The engine returned no readable report guidance.');$('aiResultText').textContent=outcome.result.text;$('aiResultMeta').textContent='Built-in guidance · Local report rules'+(outcome.result.simulated?' · SIMULATED REPORT':'');const limits=outcome.result.limitations;$('aiResultLimits').textContent=Array.isArray(limits)?limits.map(String).join(' '):String(limits||'Guidance covers recorded evidence only.');$('aiLocalStatus').textContent='Guidance prepared locally. No upload or repair was performed.';return;}if(outcome.state==='failed')throw new Error(outcome.error||'Report guidance could not be prepared.');if(outcome.state!=='running')throw new Error('The engine returned an unknown guidance job state.');await new Promise(resolve=>setTimeout(resolve,500));}
      throw new Error('No completed guidance was observed within one minute.');
    }catch(error){$('aiResultText').textContent=error.message;$('aiLocalStatus').textContent='Guidance could not be verified. Installation and other features remain available.';}finally{aiBusy=false;updateAiControls();}
  }
  function updatePreferences(){
    const density=$('featureDensity').value==='compact'?'compact':'comfortable';document.body.classList.toggle('compact',density==='compact');storageWrite('namu-density',density);
    const scale=Math.min(125,Math.max(90,Number($('fontScale').value)||100));document.documentElement.style.setProperty('--font-scale',String(scale/100));$('fontScaleValue').textContent=scale+'%';storageWrite('namu-font-scale',String(scale));
    document.documentElement.classList.toggle('reduced-motion',$('reduceMotion').checked);storageWrite('namu-reduced-motion',String($('reduceMotion').checked));
  }
  function openPreference(id){document.querySelector('.display-settings').open=true;$(id).focus();$(id).scrollIntoView({block:'center'});}
  function showFeatureResult(feature,state,result,error){
    currentFeatureResult=result||null;$('featureResult').hidden=false;$('featureResultTitle').textContent=feature.title;$('featureJobState').textContent=state;
    $('featureResultSummary').textContent=error||result?.summary||(state==='running'?'The local engine is running this action…':'No result returned.');
    $('featureResultData').textContent=result?.data===undefined?'':JSON.stringify(result.data,null,2);
    const warnings=Array.isArray(result?.warnings)?result.warnings:[],fragment=document.createDocumentFragment();warnings.forEach(warning=>fragment.append(make('li','',warning)));$('featureResultWarnings').replaceChildren(fragment);$('featureResultWarnings').hidden=!warnings.length;
    $('featureCopy').disabled=!result;$('featureSave').hidden=!result?.download;$('featureApply').hidden=!result?.options;$('featureApply').disabled=Boolean(snapshot?.started||starting);$('featureResultNotice').textContent=result?.options?'Apply these selections before starting installation. Applying them pauses automatic start.':state==='complete'?'Review the result and any warnings before acting.':'';
  }
  function runClientFeature(feature){
    let summary;const settings={};
    switch(feature.id){
      case 'f091':$('featureSearch').focus();summary='Search is ready. Type a feature name, description, category or ID.';break;
      case 'f092':$('featureCategory').focus();summary='Category filter is ready. Choose a category to narrow the catalog.';break;
      case 'f093':toggleFavorite(feature.id);summary=favorites.has(feature.id)?'Saved this feature. Use the star on any feature to save or unsave it.':'Removed this feature from your saved list.';settings.saved_ids=[...favorites];break;
      case 'f094':$('favoritesOnly').checked=!$('favoritesOnly').checked;renderFeatures();summary=$('favoritesOnly').checked?'Showing saved features only.':'Showing the complete filtered catalog.';settings.saved_only=$('favoritesOnly').checked;break;
      case 'f095':$('featureDensity').value=$('featureDensity').value==='compact'?'comfortable':'compact';updatePreferences();summary='Card density changed to '+$('featureDensity').value+'.';settings.density=$('featureDensity').value;break;
      case 'f096':openPreference('fontScale');summary='Text size is ready to adjust from 90% to 125%.';break;
      case 'f097':$('reduceMotion').checked=!$('reduceMotion').checked;updatePreferences();summary=$('reduceMotion').checked?'Reduced motion enabled.':'Following your operating system motion preference.';settings.reduced_motion=$('reduceMotion').checked;break;
      case 'f098':$('logSearch').focus();$('activity').scrollIntoView({block:'start'});summary='Log search is ready. Type a word to filter the retained messages.';break;
      case 'f099':$('logSeverity').focus();$('activity').scrollIntoView({block:'start'});summary='Log severity filter is ready. Choose information, warnings or errors.';break;
      case 'f100':openPalette();summary='Keyboard command palette opened.';break;
      default:summary='Use the available workspace control for this capability.';
    }
    showFeatureResult(feature,'complete',{summary,data:{feature_id:feature.id,scope:'This browser only',...settings}});
  }
  async function runFeature(feature){
    if(!snapshot?.started)pause();if(feature.client){runClientFeature(feature);return;}if(featureBusy)return;
    featureBusy=true;renderFeatures();showFeatureResult(feature,'running');$('featureResult').scrollIntoView({block:'center'});
    try{const payload={};if(['f076','f078','f087'].includes(feature.id))payload.options=options();if($('featureReport').value)payload.run_id=$('featureReport').value;const job=await api('features/run',{id:feature.id,payload});if(typeof job.id!=='string'||!/^[A-Za-z0-9_-]{1,100}$/.test(job.id))throw new Error('The engine returned an invalid job identifier.');
      for(let attempt=0;attempt<120;attempt++){if(quitting)throw new Error('Dashboard is closing.');const outcome=await api('features/jobs/'+encodeURIComponent(job.id));if(outcome.state==='complete'){showFeatureResult(feature,'complete',outcome.result);return;}if(outcome.state==='failed')throw new Error(outcome.error||'The action failed.');if(outcome.state!=='running')throw new Error('The engine returned an unknown job state.');await new Promise(resolve=>setTimeout(resolve,1500));}
      throw new Error('This action is still running after three minutes. The result has not been verified; do not repeat a modifying action while it is running.');
    }catch(error){showFeatureResult(feature,'failed',null,error.message);}finally{featureBusy=false;renderFeatures();}
  }
  function saveDownload(download){
    const name=String(download.name||'Namu-Workbench-result.txt').replace(/[\\/<>:"|?*\u0000-\u001f]/g,'_').slice(0,150)||'Workbench-result.txt';let body=String(download.text??'');
    if(download.encoding==='base64'){const decoded=atob(body);body=Uint8Array.from(decoded,char=>char.charCodeAt(0));}
    const url=URL.createObjectURL(new Blob([body],{type:typeof download.mime==='string'?download.mime:'text/plain;charset=utf-8'})),link=make('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function renderPalette(){
    paletteMatches=filteredFeatures($('paletteSearch').value,'',false).slice(0,30);paletteIndex=Math.max(0,Math.min(paletteIndex,paletteMatches.length-1));const fragment=document.createDocumentFragment();
    paletteMatches.forEach((feature,index)=>{const command=make('button','palette-command');command.type='button';command.id='palette-'+feature.id;command.setAttribute('role','option');command.setAttribute('aria-selected',String(index===paletteIndex));command.tabIndex=-1;command.append(make('strong','',feature.title),make('small','',feature.id+' · '+feature.category+' · '+(feature.client?'Browser control':feature.effect||'Local check')));command.addEventListener('click',()=>{closePalette();runFeature(feature);});fragment.append(command);});
    $('paletteList').replaceChildren(fragment);$('paletteEmpty').hidden=Boolean(paletteMatches.length);if(paletteMatches[paletteIndex])$('paletteSearch').setAttribute('aria-activedescendant','palette-'+paletteMatches[paletteIndex].id);else $('paletteSearch').removeAttribute('aria-activedescendant');
  }
  function openPalette(){if(!snapshot?.started)pause();$('paletteSearch').value='';paletteIndex=0;renderPalette();if(!$('commandPalette').open)$('commandPalette').showModal();$('paletteSearch').focus();}
  function closePalette(){if($('commandPalette').open)$('commandPalette').close();$('paletteOpen').focus();}
  $('featureGrid').before($('featureResult'));
  const density=storageRead('namu-density','comfortable');$('featureDensity').value=density==='compact'?'compact':'comfortable';
  const fontScale=Number(storageRead('namu-font-scale','100'));$('fontScale').value=Number.isFinite(fontScale)?String(Math.max(90,Math.min(125,fontScale))):'100';
  $('reduceMotion').checked=storageRead('namu-reduced-motion','false')==='true';updatePreferences();
  $('studio').addEventListener('focusin',()=>{if(!snapshot?.started)pause();});
  $('aiStudio').addEventListener('focusin',()=>{if(!snapshot?.started)pause();});
  $('aiProvider').addEventListener('change',()=>{$('aiSessionKey').value='';resetAiPreview();displayAiProvider();});$('featureReport').addEventListener('change',()=>{resetAiPreview();displayAiProvider();});
  $('aiReviewed').addEventListener('change',updateAiControls);$('aiFreeAccount').addEventListener('change',updateAiControls);$('aiPreview').addEventListener('click',previewAiExcerpt);$('aiAsk').addEventListener('click',askAiProvider);
  $('aiSessionKey').addEventListener('input',updateAiControls);$('aiConnect').addEventListener('click',connectAiSession);$('aiLocalAsk').addEventListener('click',askLocalGuidance);
  ['featureSearch','featureCategory','favoritesOnly'].forEach(id=>$(id).addEventListener(id==='featureSearch'?'input':'change',renderFeatures));
  ['featureDensity','fontScale','reduceMotion'].forEach(id=>$(id).addEventListener(id==='fontScale'?'input':'change',updatePreferences));
  $('logSearch').addEventListener('input',renderLogs);$('logSeverity').addEventListener('change',renderLogs);
  $('paletteOpen').addEventListener('click',openPalette);$('paletteClose').addEventListener('click',closePalette);$('paletteSearch').addEventListener('input',()=>{paletteIndex=0;renderPalette();});
  $('commandPalette').addEventListener('cancel',event=>{event.preventDefault();closePalette();});
  $('paletteSearch').setAttribute('role','combobox');$('paletteSearch').setAttribute('aria-controls','paletteList');$('paletteSearch').setAttribute('aria-expanded','true');
  $('paletteSearch').addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();closePalette();}else if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();if(paletteMatches.length){paletteIndex=(paletteIndex+(event.key==='ArrowDown'?1:-1)+paletteMatches.length)%paletteMatches.length;renderPalette();$( 'palette-'+paletteMatches[paletteIndex].id)?.scrollIntoView({block:'nearest'});}}else if(event.key==='Enter'&&paletteMatches[paletteIndex]){event.preventDefault();const feature=paletteMatches[paletteIndex];closePalette();runFeature(feature);}});
  document.addEventListener('keydown',event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();$('commandPalette').open?closePalette():openPalette();}});
  $('featureCopy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(JSON.stringify(currentFeatureResult,null,2));$('featureResultNotice').textContent='Result JSON copied. Review private information before sharing.';}catch{$('featureResultNotice').textContent='Clipboard access is unavailable. Select the result text and copy it manually.';}});
  $('featureSave').addEventListener('click',()=>{try{if(currentFeatureResult?.download){saveDownload(currentFeatureResult.download);$('featureResultNotice').textContent='Download prepared. Review the file before sharing.';}}catch(error){$('featureResultNotice').textContent='Download could not be prepared: '+error.message;}});
  $('featureApply').addEventListener('click',()=>{if(snapshot?.started||starting||!currentFeatureResult?.options)return;pause();document.querySelectorAll('.options input').forEach(input=>{if(typeof currentFeatureResult.options[input.name]==='boolean')input.checked=currentFeatureResult.options[input.name];});$('featureResultNotice').textContent='Installation selections applied. Review the toolkit and press Start now when ready.';$('setup').scrollIntoView({block:'start'});$('start').focus();});
  $('start').addEventListener('click',start);$('pause').addEventListener('click',pause);document.querySelectorAll('.options input').forEach(input=>input.addEventListener('change',pause));
  $('stop').addEventListener('click',async()=>{try{await api('stop',{});}catch(error){banner(error.message,'error');}});
  $('copy').addEventListener('click',async()=>{try{const text=await api('report');try{await navigator.clipboard.writeText(text);$('copyStatus').textContent='Report copied. Review it before sharing.';}catch{$('reportFallback').hidden=false;$('reportFallback').value=text;$('reportFallback').select();$('copyStatus').textContent='Clipboard access was blocked. Press Ctrl+C on the selected report.';}}catch(error){banner(error.message,'error');}});
  $('download').addEventListener('click',async()=>{try{saveDownload({name:'Paste-Into-ChatGPT.txt',mime:'text/plain;charset=utf-8',text:await api('report')});}catch(error){banner(error.message,'error');}});
  for(const [id,action]of[['reports','open-reports'],['terminal','open-terminal']])$(id).addEventListener('click',async()=>{try{await api(action,{});}catch(error){banner(error.message,'error');}});
  $('quit').addEventListener('click',async()=>{pause();try{const result=await api('quit',{});quitting=true;banner(result.after_current_operation?'Dashboard will close after the current operation finishes. You may close this tab.':'Dashboard stopped. You may close this tab.');}catch(error){banner(error.message,'error');}});
  if(!token){pause();banner('Missing local session capability. Open the dashboard with the Workbench launcher.','error');$('start').disabled=true;return;}
  api('status').then(data=>{display(data);if(!data.started&&!$('pause').disabled){timer=setInterval(()=>{ticks--;$('countdown').textContent=`Automatic start in ${ticks} seconds`;if(ticks<=0)start();},1000);}poll();}).catch(error=>{pause();banner(error.message,'error');});loadFeatures();loadAiProviders();
})();
