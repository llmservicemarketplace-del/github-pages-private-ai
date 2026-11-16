/* Contact/profile values stay in this browser. No form submission endpoint. */
'use strict';
const C=SettlementCore, data=JSON.parse(document.getElementById('settlement-data').textContent);
const $=id=>document.getElementById(id);
const PROFILE_KEY='nfccop.settlement.profile.v1';
let profile={},selected=null,donationDeclined=false;
function message(id,text,error=false){$(id).textContent=text;$(id).classList.toggle('error',error);}
try{const saved=localStorage.getItem(PROFILE_KEY),stored=saved||sessionStorage.getItem('nfccop.money.profile.session.v1');if(stored){profile=C.cleanProfile(JSON.parse(stored));$('remember').checked=!!saved;}}catch{}
for(const k of C.PROFILE_KEYS)$(k).value=profile[k]||'';
function saveProfile(e){e?.preventDefault();if(!$('profile-form').reportValidity())return false;profile=C.cleanProfile(Object.fromEntries(C.PROFILE_KEYS.map(k=>[k,$(k).value])));try{sessionStorage.setItem('nfccop.money.profile.session.v1',JSON.stringify(profile));if($('remember').checked)localStorage.setItem(PROFILE_KEY,JSON.stringify(profile));else localStorage.removeItem(PROFILE_KEY);message('profile-status',$('remember').checked?'Saved on this device.':'Ready for this visit. Nothing saved for next time.');}catch{message('profile-status','Ready for this visit. Browser storage is unavailable.');}return true;}
$('profile-form').addEventListener('submit',saveProfile);
$('remember').addEventListener('change',()=>{if(!$('remember').checked){try{localStorage.removeItem(PROFILE_KEY);}catch{}}});
$('forget').addEventListener('click',()=>{try{localStorage.removeItem(PROFILE_KEY);sessionStorage.removeItem('nfccop.money.profile.session.v1');}catch{}profile={};$('profile-form').reset();$('remember').checked=false;message('profile-status','Contact information cleared from this page and device. Downloaded files are not deleted.');});
const stateNames={AL:'Alabama',AK:'Alaska',AZ:'Arizona',AR:'Arkansas',CA:'California',CO:'Colorado',CT:'Connecticut',DE:'Delaware',DC:'District of Columbia',FL:'Florida',GA:'Georgia',HI:'Hawaii',ID:'Idaho',IL:'Illinois',IN:'Indiana',IA:'Iowa',KS:'Kansas',KY:'Kentucky',LA:'Louisiana',ME:'Maine',MD:'Maryland',MA:'Massachusetts',MI:'Michigan',MN:'Minnesota',MS:'Mississippi',MO:'Missouri',MT:'Montana',NE:'Nebraska',NV:'Nevada',NH:'New Hampshire',NJ:'New Jersey',NM:'New Mexico',NY:'New York',NC:'North Carolina',ND:'North Dakota',OH:'Ohio',OK:'Oklahoma',OR:'Oregon',PA:'Pennsylvania',RI:'Rhode Island',SC:'South Carolina',SD:'South Dakota',TN:'Tennessee',TX:'Texas',UT:'Utah',VT:'Vermont',VA:'Virginia',WA:'Washington',WV:'West Virginia',WI:'Wisconsin',WY:'Wyoming'};
for(const [v,n]of Object.entries(stateNames)){for(const id of ['state','state-filter']){const o=document.createElement('option');o.value=v;o.textContent=n;$(id).append(o);}}
$('state').value=profile.state||'';
const categoryNames={new_claims:'Accepting new claims',automatic:'Automatic payments',follow_up:'Existing claims / payment follow-up',upcoming:'Not open yet',closed:'Claims closed',needs_review:'Needs current verification'};
function card(r){
const bucket=C.category(r),reviewed=r.review_status==='verified',open=bucket==='new_claims';
return '<article class="card"><span class="tag">'+C.esc(categoryNames[bucket])+'</span>'+(r.receipt_required===false&&reviewed&&open?'<span class="tag">No purchase receipt required</span>':'')+(r.notice_id_required?'<span class="tag warn">Notice login/ID required online</span>':'')+(r.device_id_required?'<span class="tag warn">Device information required</span>':'')+'<h3>'+C.esc(r.title)+'</h3><p>'+C.esc(r.summary||'Read the official notice.')+'</p><div class="detail"><p><strong>Who may qualify:</strong> '+C.esc(r.eligibility||'Eligibility has not been individually reviewed.')+'</p><p><strong>Deadline:</strong> '+C.esc(r.deadline_label||'No current claim deadline verified')+'</p><p><strong>Payment:</strong> '+C.esc(r.payment||'No amount promised; consult official instructions.')+'</p><p><strong>Requirements:</strong> '+C.esc(r.requirements||'Receipt, notice-ID and other requirements have not been reviewed.')+'</p>'+((r.states||[]).includes('UNKNOWN')?'<p class="small">Location restrictions have not been reviewed. Check the official class definition.</p>':'')+'<p class="small">Official source last successfully checked: '+C.esc(r.last_checked?.slice(0,10)||'not yet')+'. '+(reviewed?'Eligibility details reviewed.':'Submission route checked; full eligibility and proof requirements need your review.')+'</p>'+(r.check_error?'<p class="small error">The latest source check failed; current intake is unconfirmed.</p>':'')+'</div><div class="actions"><a class="button secondary" data-event="external_resource_click" target="_blank" rel="noopener noreferrer" href="'+C.esc(r.official_url)+'">'+(open?'Read official claim instructions':'Read official program information')+'</a><a class="button secondary" href="/money-help/application-organizer.html?settlement='+encodeURIComponent(r.id)+'">Save to My Organizer</a>'+(open?'<button data-prepare="'+C.esc(r.id)+'">'+(C.canPrepare(r)?'Prepare my claim':'Save my preparation copy')+'</button>':'')+'</div></article>';
}
function render(){
const f={q:$('search').value.trim(),state:$('state-filter').value,type:$('type-filter').value,status:$('status-filter').value,proof:$('proof-filter').checked,noId:$('id-filter').checked};
const rows=data.records.filter(r=>C.matches(r,f)).sort((a,b)=>(a.review_status==='verified'?0:1)-(b.review_status==='verified'?0:1)||(a.deadline_date||a.deadline_at||'9999').localeCompare(b.deadline_date||b.deadline_at||'9999')||a.title.localeCompare(b.title));
$('results').innerHTML=rows.map(card).join('')||'<p class="empty">No matching programs. Try clearing a filter. An empty result does not determine your eligibility.</p>';
$('result-count').textContent=rows.length+' program'+(rows.length===1?'':'s')+' shown';
$('results').querySelectorAll('[data-prepare]').forEach(b=>b.addEventListener('click',()=>openForm(b.dataset.prepare)));
}
['search','state-filter','type-filter','status-filter','proof-filter','id-filter'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',render));
function openForm(id){if(!saveProfile()){ $('profile-form').scrollIntoView({behavior:'smooth'});return;}selected=data.records.find(r=>r.id===id);if(!selected)return;
$('claim-title').textContent=selected.title;
$('claim-eligibility').textContent=selected.eligibility;
$('claim-instructions').textContent=selected.instructions;
$('contact-review').textContent=[profile.firstName+' '+profile.lastName,profile.street,profile.city+', '+profile.state+' '+profile.zip,profile.email,profile.phone].filter(Boolean).join('\n');
$('confirm-eligible').checked=false;$('confirm-review').checked=false;
$('eligibility-check').hidden=!C.canPrepare(selected);
$('pdf-button').hidden=!C.canPrepare(selected);
$('pdf-note').hidden=!C.canPrepare(selected);
$('official-action').href=selected.official_url;
$('optional-donation').hidden=true;
$('fast-action').textContent=selected.action==='automatic'||selected.action==='instructions'?'Open the official instructions':'Copy my details & open the official form';
$('mail-address').textContent=selected.mailing_address||'';
$('mail-area').hidden=!selected.mailing_address;
$('email-action').hidden=!selected.submission_email;
if(selected.submission_email)$('email-action').href='mailto:'+selected.submission_email+'?subject='+encodeURIComponent(selected.title+' claim')+'&body='+encodeURIComponent('Please find my reviewed claim attached.\n\n'+profile.firstName+' '+profile.lastName);
message('claim-status','');$('claim-dialog').showModal();
}
$('close-dialog').addEventListener('click',()=>$('claim-dialog').close());
function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);}
$('html-button').addEventListener('click',()=>{download(new Blob([C.packet(selected,profile)],{type:'text/html;charset=utf-8'}),selected.id+'-preparation.html');message('claim-status','Preparation copy downloaded. It is not a claim submission.');offerDonation();});
$('copy-contact').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('contact-review').textContent);message('claim-status','Contact information copied. Paste it into the official form.');}catch{message('claim-status','Copy unavailable. Select the contact text above and copy it manually.',true);}});
$('pdf-button').addEventListener('click',async()=>{
if(!profile.phone){message('claim-status','Add your phone number in Your details, save it, and reopen this form. The official claim asks for it.',true);return;}
if(!C.canPrepare(selected)){message('claim-status','This template needs a fresh source check. Use the official website.',true);return;}
if(!$('confirm-eligible').checked||!$('confirm-review').checked){message('claim-status','Confirm the eligibility and review reminders first.',true);return;}
const b=$('pdf-button');b.disabled=true;message('claim-status','Preparing your PDF on this device…');
try{
const res=await fetch(selected.form.path,{cache:'no-store'});if(!res.ok)throw Error('Official template could not load. Use the official website.');
const bytes=await res.arrayBuffer();const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
if(digest!==selected.form.sha256)throw Error('The template changed. Use the official website while it is reviewed.');
const doc=await PDFLib.PDFDocument.load(bytes),font=await doc.embedFont(PDFLib.StandardFonts.Helvetica),form=doc.getForm();
for(const [key,rect]of Object.entries(selected.form.fields)){
const val=profile[key]||'';let size=10;while(size>7&&font.widthOfTextAtSize(val,size)>rect.width-8)size-=.5;
if(font.widthOfTextAtSize(val,size)>rect.width-8)throw Error('Your '+key+' is too long for the official box. Use the official form to complete it manually.');
const field=form.createTextField('nfccop_'+key);field.setText(val);field.addToPage(doc.getPages()[0],{x:rect.x,y:rect.y,width:rect.width,height:rect.height,borderWidth:0,backgroundColor:undefined,textColor:PDFLib.rgb(0,0,0),font});field.setFontSize(size);
}
form.updateFieldAppearances(font);download(new Blob([await doc.save()],{type:'application/pdf'}),selected.id+'-prefilled-claim.pdf');
message('claim-status','PDF downloaded. Review BOTH pages, select payment, sign and date, then mail it or use the official online form. Nothing has been submitted.');offerDonation();
}catch(e){message('claim-status',e.message+' Your contact information remains here.',true);}finally{b.disabled=false;}
});
render();
if(Date.now()-new Date(data.generated_at).getTime()>3*86400000){$('feed-warning').hidden=false;$('feed-warning').textContent='The daily feed has not refreshed recently. Check the official source for current deadlines and instructions.';}

function offerDonation(){
 if(donationDeclined)return;
 $('optional-donation').hidden=false;
 try{$('optional-donation').scrollIntoView({behavior:'smooth',block:'nearest'});}catch{}
}
function calculateDonation(){
 const raw=$('refund-received').value,choice=$('donation-percent').value;
 $('custom-percent-label').hidden=choice!=='custom';
 const rateText=choice==='custom'?$('custom-percent').value:choice;
 if(raw===''||rateText===''){$('donation-calculation').textContent='No donation selected.';return;}
 const amount=Number(raw),rate=Number(rateText);
 if(!Number.isFinite(amount)||!Number.isFinite(rate)||amount<0||amount>1000000||rate<0||rate>100){
 $('donation-calculation').textContent='Enter an amount from $0 to $1,000,000 and a percentage from 0 to 100.';return;
 }
 const cents=Math.round(Math.round(amount*100)*rate/100);
 $('donation-calculation').textContent='Optional donation: '+new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(cents/100)+' ('+rate+'% of '+new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(amount)+').';
}
['refund-received','donation-percent','custom-percent'].forEach(id=>$(id).addEventListener(id==='donation-percent'?'change':'input',calculateDonation));
$('skip-donation').addEventListener('click',()=>{
 donationDeclined=true;
 $('optional-donation').hidden=true;
 $('refund-received').value='';$('donation-percent').value='';$('custom-percent').value='';
 calculateDonation();
 message('claim-status','No problem. Your downloads and the official links stay available.');
});
// One-step path for every visitor: open the official page first (keeps the click's popup permission), then copy contact details.
$('fast-action').addEventListener('click',async()=>{
 if(!selected)return;
 window.open(selected.official_url,'_blank','noopener');
 // Same primary conversion the site records for clicks on official resource links. No profile data is sent.
 try{if(typeof window.gtag==='function')window.gtag('event','conversion',{send_to:'AW-18465563654/GRZgCPDR1bEdEIbIiOVE'});}catch{}
 const needsDetails=!(selected.action==='automatic'||selected.action==='instructions');
 if(needsDetails){try{await navigator.clipboard.writeText($('contact-review').textContent);message('claim-status','Official form opened in a new tab and your contact details are copied. Paste them in, then choose payment and sign there yourself. Nothing has been submitted.');}catch{message('claim-status','Official form opened in a new tab. Copy your contact details from the box above. Nothing has been submitted.');}}
 else message('claim-status','Official instructions opened in a new tab. Nothing has been submitted.');
 offerDonation();
});
$('official-action').addEventListener('click',()=>setTimeout(offerDonation,0));
// Donation pop-up: Zeffy's own embed form in an iframe, loaded only when a visitor chooses Donate. No third-party script runs on this page.
const ZEFFY_EMBED='https://www.zeffy.com/embed/donation-form/donate-to-change-lives-23839?modal=true',ZEFFY_ORIGIN='https://www.zeffy.com';
function openDonate(){
 const d=$('donate-dialog'),f=$('donate-frame');
 if(!d||!f||typeof d.showModal!=='function')return false;
 const hello=()=>{try{f.contentWindow.postMessage({id:'zeffy-iframe',open:true},ZEFFY_ORIGIN);}catch{}};
 if(!f.getAttribute('src')){f.addEventListener('load',hello);f.src=ZEFFY_EMBED+'&cachebust='+Date.now();}else hello();
 d.showModal();return true;
}
// Registered after button-conversions.js, so the donation click is counted first and the new tab is then replaced by the pop-up.
document.addEventListener('click',e=>{
 const a=e.target&&e.target.closest?e.target.closest('a[data-donate-popup]'):null;
 if(!a||e.defaultPrevented||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
 if(openDonate())e.preventDefault();
});
window.addEventListener('message',e=>{if(e.origin===ZEFFY_ORIGIN&&e.data&&e.data.id==='zeffy-iframe'&&e.data.close)$('donate-dialog').close();});
$('close-donate').addEventListener('click',()=>$('donate-dialog').close());

const buckets=data.records.reduce((a,r)=>{const k=C.category(r);a[k]=(a[k]||0)+1;return a;},{});
$('directory-summary').textContent=(buckets.new_claims||0)+' listings accepting new claims · '+(buckets.automatic||0)+' automatic-payment programs · '+(buckets.follow_up||0)+' existing-claim/follow-up programs. '+(data.discovery_pending||0)+' discovery leads await verification. Last feed refresh: '+(data.generated_at||'unknown').slice(0,10)+'.';
fetch('/data/settlement-sources.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(s=>{$('source-health').innerHTML='<ul>'+s.sources.map(x=>'<li><a target="_blank" rel="noopener noreferrer" href="'+C.esc(x.url)+'">'+C.esc(x.name)+'</a> — '+(x.status==='checked'?'checked '+C.esc((x.last_checked||'').slice(0,10))+'; '+Number(x.leads_found||0)+' leads':'could not be checked automatically; last success: '+C.esc((x.last_checked||'not yet').slice(0,10)))+'</li>').join('')+'</ul>';}).catch(()=>{$('source-health').textContent='Source status could not load. Check the official notices directly.';});
