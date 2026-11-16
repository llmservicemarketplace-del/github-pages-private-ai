/* Contact/profile values stay in this browser. No form submission endpoint. */
'use strict';
const C=SettlementCore, data=JSON.parse(document.getElementById('settlement-data').textContent);
const $=id=>document.getElementById(id);
const PROFILE_KEY='nfccop.settlement.profile.v1';
let profile={},selected=null,donationAsked=false;
function message(id,text,error=false){$(id).textContent=text;$(id).classList.toggle('error',error);}
try{const stored=localStorage.getItem(PROFILE_KEY);if(stored){profile=C.cleanProfile(JSON.parse(stored));$('remember').checked=true;}}catch{}
for(const k of C.PROFILE_KEYS)$(k).value=profile[k]||'';
function saveProfile(e){e?.preventDefault();if(!$('profile-form').reportValidity())return false;profile=C.cleanProfile(Object.fromEntries(C.PROFILE_KEYS.map(k=>[k,$(k).value])));try{if($('remember').checked)localStorage.setItem(PROFILE_KEY,JSON.stringify(profile));else localStorage.removeItem(PROFILE_KEY);message('profile-status',$('remember').checked?'Saved on this device.':'Ready for this visit. Nothing saved for next time.');}catch{message('profile-status','Ready for this visit. Browser storage is unavailable.');}return true;}
$('profile-form').addEventListener('submit',saveProfile);
$('remember').addEventListener('change',()=>{if(!$('remember').checked){try{localStorage.removeItem(PROFILE_KEY);}catch{}}});
$('forget').addEventListener('click',()=>{try{localStorage.removeItem(PROFILE_KEY);}catch{}profile={};$('profile-form').reset();$('remember').checked=false;message('profile-status','Contact information cleared from this page and device. Downloaded files are not deleted.');});
const stateNames={AL:'Alabama',AK:'Alaska',AZ:'Arizona',AR:'Arkansas',CA:'California',CO:'Colorado',CT:'Connecticut',DE:'Delaware',DC:'District of Columbia',FL:'Florida',GA:'Georgia',HI:'Hawaii',ID:'Idaho',IL:'Illinois',IN:'Indiana',IA:'Iowa',KS:'Kansas',KY:'Kentucky',LA:'Louisiana',ME:'Maine',MD:'Maryland',MA:'Massachusetts',MI:'Michigan',MN:'Minnesota',MS:'Mississippi',MO:'Missouri',MT:'Montana',NE:'Nebraska',NV:'Nevada',NH:'New Hampshire',NJ:'New Jersey',NM:'New Mexico',NY:'New York',NC:'North Carolina',ND:'North Dakota',OH:'Ohio',OK:'Oklahoma',OR:'Oregon',PA:'Pennsylvania',RI:'Rhode Island',SC:'South Carolina',SD:'South Dakota',TN:'Tennessee',TX:'Texas',UT:'Utah',VT:'Vermont',VA:'Virginia',WA:'Washington',WV:'West Virginia',WI:'Wisconsin',WY:'Wyoming'};
for(const [v,n]of Object.entries(stateNames)){for(const id of ['state','state-filter']){const o=document.createElement('option');o.value=v;o.textContent=n;$(id).append(o);}}
$('state').value=profile.state||'';
function card(r){
const closed=C.expired(r),needsReview=r.review_status!=='verified'||C.stale(r);
const tag=closed?(r.directory_active===false?'No longer on FTC active list':'Claims closed'):r.action==='automatic'?'Automatic payments':r.type==='ftc'?'Check FTC instructions':'Claim required';
return '<article class="card"><span class="tag'+(closed?' gray':'')+'">'+C.esc(tag)+'</span><span class="tag gray">'+(r.type==='ftc'?'FTC refund':'Class-action settlement')+'</span>'+(r.receipt_required===false&&!needsReview?'<span class="tag">No receipt required</span>':'')+(needsReview?'<span class="tag warn">Verify current details</span>':'')+'<h3>'+C.esc(r.title)+'</h3><p>'+C.esc(r.summary)+'</p><div class="detail"><p><strong>Who may qualify:</strong> '+C.esc(r.eligibility)+'</p><p><strong>Deadline:</strong> '+C.esc(r.deadline_label||'See official instructions; no claim deadline listed here')+'</p><p><strong>Payment:</strong> '+C.esc(r.payment||'See official program details; no amount promised')+'</p><p><strong>Requirements:</strong> '+C.esc(r.requirements||'Check the official program for eligibility and any documentation requirements.')+'</p><p class="small">Official source checked '+C.esc(r.last_checked?.slice(0,10)||'not yet')+'. '+(r.review_status==='verified'?'Eligibility details reviewed '+C.esc(r.last_verified.slice(0,10))+'.':'Official FTC listing; read its eligibility instructions.')+'</p></div><div class="actions"><a class="button secondary" target="_blank" rel="noopener noreferrer" href="'+C.esc(r.official_url)+'">Open official '+(r.type==='ftc'?'instructions':'claim website')+'</a>'+(!closed?'<button data-prepare="'+C.esc(r.id)+'">'+(C.canPrepare(r)?'Prepare my claim':'Save my preparation copy')+'</button>':'')+'</div></article>';
}
function render(){
const f={q:$('search').value.trim(),state:$('state-filter').value,type:$('type-filter').value,status:$('status-filter').value,proof:$('proof-filter').checked};
const rows=data.records.filter(r=>C.matches(r,f)).sort((a,b)=>(a.deadline_at||'9999').localeCompare(b.deadline_at||'9999')||a.title.localeCompare(b.title));
$('results').innerHTML=rows.map(card).join('')||'<p class="empty">No matching programs. Try clearing a filter. An empty result does not determine your eligibility.</p>';
$('result-count').textContent=rows.length+' program'+(rows.length===1?'':'s')+' shown';
$('results').querySelectorAll('[data-prepare]').forEach(b=>b.addEventListener('click',()=>openForm(b.dataset.prepare)));
}
['search','state-filter','type-filter','status-filter','proof-filter'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',render));
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
 if(donationAsked)return;
 donationAsked=true;
 $('optional-donation').hidden=false;
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
 $('optional-donation').hidden=true;
 $('refund-received').value='';$('donation-percent').value='';$('custom-percent').value='';
 calculateDonation();
 message('claim-status','No donation selected. Your downloads and official submission options remain available.');
});
