'use strict';
const M=MoneyTools,$=id=>document.getElementById(id);
M.mountProfile();M.mountDonation();
let rows=[],editing=null,catalog=[];
try{rows=M.validateRecords(M.recordsRead());$('remember-records').checked=!!localStorage.getItem('nfccop.money.organizer.v1');}catch(e){$('organizer-status').textContent='Stored records could not be read. Import a backup or start a new record.';}
function tell(s,error=false){$('organizer-status').textContent=s;$('organizer-status').classList.toggle('error',error);}
function persist(){M.recordsWrite(rows,$('remember-records').checked);}
function render(){
const q=$('record-search').value.toLowerCase(),status=$('record-status').value;
const shown=rows.filter(r=>(!status||r.status===status)&&(!q||(r.title+' '+r.notes).toLowerCase().includes(q))).sort((a,b)=>(a.deadline||'9999').localeCompare(b.deadline||'9999')||a.title.localeCompare(b.title));
$('record-count').textContent=shown.length+' of '+rows.length+' saved records';
$('record-list').innerHTML=shown.map(r=>'<article class="record"><div class="record-head"><div><span class="tag">'+M.esc(r.status)+'</span>'+(M.isOverdue(r)?' <span class="tag warn">Saved deadline has passed</span>':'')+'<h3>'+M.esc(r.title)+'</h3></div><button class="secondary" data-edit="'+M.esc(r.id)+'">Edit record</button></div><p><strong>Your saved deadline:</strong> '+M.esc(M.dateLabel(r.deadline))+'</p>'+(r.deadlineNote?'<p class="small">'+M.esc(r.deadlineNote)+'</p>':'')+'<p><strong>Confirmation:</strong> '+M.esc(r.confirmation||'None saved')+'</p><p class="small">Updated '+M.esc(r.updated?.slice(0,10)||'not recorded')+'</p><ul class="doc-list">'+r.docs.map((d,i)=>'<li><label class="check"><input type="checkbox" data-doc="'+M.esc(r.id)+'" data-index="'+i+'" '+(d.done?'checked':'')+'><span>'+M.esc(d.label)+'</span></label></li>').join('')+'</ul>'+(r.notes?'<details><summary>Your notes</summary><pre>'+M.esc(r.notes)+'</pre></details>':'')+'<div class="actions">'+(r.guide?'<a class="button secondary" href="'+M.esc(r.guide)+'">Read guide</a>':'')+(r.official?'<a class="button secondary" href="'+M.esc(r.official)+'" target="_blank" rel="noopener noreferrer">Open saved official link</a>':'')+'<button class="secondary" data-export="'+M.esc(r.id)+'">Download this record</button><button class="danger" data-delete="'+M.esc(r.id)+'">Delete</button></div></article>').join('')||'<div class="panel"><h3>No records match yet</h3><p>Add an application, choose a guide below, or open “Save to my organizer” from a Money Help guide. Browsing and using the tools is free.</p></div>';
$('record-list').querySelectorAll('[data-edit]').forEach(b=>b.onclick=()=>openEdit(rows.find(r=>r.id===b.dataset.edit)));
$('record-list').querySelectorAll('[data-doc]').forEach(b=>b.onchange=()=>{const r=rows.find(r=>r.id===b.dataset.doc);r.docs[Number(b.dataset.index)].done=b.checked;r.updated=new Date().toISOString();try{persist();tell('Checklist updated.');}catch(e){tell(e.message,true);}});
$('record-list').querySelectorAll('[data-export]').forEach(b=>b.onclick=()=>M.download(M.report([rows.find(r=>r.id===b.dataset.export)],M.getProfile()),'nfccop-application-record.html'));
$('record-list').querySelectorAll('[data-delete]').forEach(b=>b.onclick=()=>{const r=rows.find(r=>r.id===b.dataset.delete);if(!confirm('Delete “'+r.title+'” from this organizer? Downloaded backups are unchanged.'))return;rows=rows.filter(x=>x.id!==r.id);try{persist();render();tell('Record deleted.');}catch(e){tell(e.message,true);}});
}
function openEdit(r=null){
editing=r?.id||null;$('entry-form').reset();
for(const k of ['title','official','guide','status','deadline','deadlineNote','confirmation','notes'])$('entry-'+k).value=r?.[k]||(k==='status'?'Planning':'');
$('entry-docs').value=(r?.docs||[]).map(d=>d.label).join('\n');
$('entry-heading').textContent=r?'Edit application record':'Add application record';$('entry-error').textContent='';$('entry-dialog').showModal();
}
$('new-entry').onclick=()=>openEdit();
$('entry-close').onclick=()=>$('entry-dialog').close();
$('entry-form').onsubmit=e=>{
e.preventDefault();if(!e.target.reportValidity())return;
try{
const previous=rows.find(r=>r.id===editing);
const r={id:editing||crypto.randomUUID(),updated:new Date().toISOString()};
for(const k of ['title','official','guide','status','deadline','deadlineNote','confirmation','notes'])r[k]=$('entry-'+k).value.trim();
for(const k of ['official','guide'])if(r[k]&&!M.safeURL(r[k]))throw Error('Use a full HTTPS web address for saved links.');
r.docs=$('entry-docs').value.split('\n').map(s=>s.trim()).filter(Boolean).slice(0,40).map(label=>({label,done:previous?.docs.some(d=>d.label===label&&d.done)||false}));
const validated=M.validateRecords([r])[0];
rows=editing?rows.map(x=>x.id===editing?validated:x):M.validateRecords([...rows,validated]);
persist();render();$('entry-dialog').close();tell('Record saved. Status is your own record, not an agency confirmation.');
}catch(err){$('entry-error').textContent=err.message;}
};
$('record-search').oninput=render;$('record-status').onchange=render;
$('remember-records').onchange=()=>{try{persist();tell($('remember-records').checked?'Organizer remembered on this device.':'Organizer kept for this tab only.');}catch(e){tell(e.message,true);}};
$('download-all').onclick=()=>{if(!rows.length){tell('Add a record first.');return;}M.download(M.report(rows,M.getProfile()),'nfccop-my-applications.html');tell('Readable organizer downloaded. It contains your private notes; keep it safe.');};
$('clear-all').onclick=()=>{if(!confirm('Clear all organizer records on this device? Keep an encrypted backup first if needed. Contact details and downloaded files are separate.'))return;rows=[];$('remember-records').checked=false;try{persist();render();tell('Organizer records cleared. Downloaded files and contact details are unchanged.');}catch(e){tell(e.message,true);}};
$('backup-export').onclick=async()=>{
const p=$('backup-password').value,c=$('backup-confirm').value;if(p!==c){tell('The backup passwords do not match.',true);return;}
const b=$('backup-export');b.disabled=true;
try{const body=await M.encryptBackup({version:1,profile:M.saveProfile(),records:rows},p);M.download(JSON.stringify(body),'nfccop-encrypted-backup.json','application/json');$('backup-password').value='';$('backup-confirm').value='';tell('Encrypted backup downloaded. Keep the password separately; NFCcop cannot reset it.');}catch(e){tell(e.message,true);}finally{b.disabled=false;}
};
$('backup-import').onclick=async()=>{
const file=$('backup-file').files[0];if(!file||file.size>16777216){tell('Choose an NFCcop encrypted backup smaller than 16 MB.',true);return;}
const b=$('backup-import');b.disabled=true;
try{
const restored=await M.decryptBackup(JSON.parse(await file.text()),$('restore-password').value);
if(!confirm('Replace this device’s current organizer with '+restored.records.length+' backup records and restore its contact profile for this tab?'))return;
rows=restored.records;persist();
try{sessionStorage.setItem('nfccop.money.profile.session.v1',JSON.stringify(restored.profile));localStorage.removeItem('nfccop.settlement.profile.v1');}catch{}
for(const k of M.KEYS)$('profile-'+k).value=restored.profile[k];
$('money-profile-remember').checked=false;$('restore-password').value='';$('backup-file').value='';render();tell('Backup restored. Contact details are not remembered across visits unless you choose that option.');
}catch(e){tell(e.message,true);}finally{b.disabled=false;}
};
async function loadCatalog(){
try{
const r=await fetch('/data/money-programs.json');if(!r.ok)throw Error('Guide list is unavailable. You can add an application manually.');
catalog=(await r.json()).programs;$('program-choice').innerHTML='<option value="">Choose a guide</option>'+catalog.map((p,i)=>'<option value="'+i+'">'+M.esc(p.title)+'</option>').join('');
const params=new URLSearchParams(location.search),guide=params.get('guide'),settlement=params.get('settlement');
if(guide){const p=catalog.find(x=>x.guide===guide);if(p){openEdit({title:p.title,guide:'https://yprivateai.com'+p.guide,status:'Planning',docs:(p.docs||[]).map(label=>({label,done:false}))});tell('Review and save this new application record. Nothing has been submitted.');}}
if(settlement){
const resp=await fetch('/data/settlements.json');if(resp.ok){const p=(await resp.json()).records.find(r=>r.id===settlement);if(p)openEdit({title:p.title,guide:'https://yprivateai.com/money-help/settlements-and-refunds.html',official:M.safeURL(p.official_url),status:'Planning',deadline:p.deadline_at?p.deadline_at.slice(0,10):'',deadlineNote:p.deadline_label||'Check official instructions; no deadline saved.',notes:p.instructions||'',docs:[{label:'Read the official eligibility rules and instructions',done:false},{label:'Keep the official submission confirmation, if a claim is required',done:false}]});}
}
}catch(e){tell(e.message,true);}
}
$('choose-program').onclick=()=>{const p=catalog[Number($('program-choice').value)];if($('program-choice').value===''||!p)return;openEdit({title:p.title,guide:'https://yprivateai.com'+p.guide,status:'Planning',docs:(p.docs||[]).map(label=>({label,done:false}))});};
render();loadCatalog();
