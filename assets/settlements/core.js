/* NFCcop settlement finder. No personal information is sent to a server. */
(function(root){
'use strict';
const PROFILE_KEYS=['firstName','lastName','street','city','state','zip','email','phone'];
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function cleanProfile(p){return Object.fromEntries(PROFILE_KEYS.map(k=>[k,String(p?.[k]??'').trim().slice(0,k==='street'?160:100)]));}
function expired(r,now=new Date()){return r.availability==='closed'||r.directory_active===false||(r.deadline_date&&r.deadline_date<now.toISOString().slice(0,10))||!!r.deadline_at&&new Date(r.deadline_at).getTime()<now.getTime();}
function stale(r,now=new Date()){return !r.last_checked||!Number.isFinite(Date.parse(r.last_checked))||now.getTime()-new Date(r.last_checked).getTime()>7*86400000;}
function category(r,now=new Date()){if(expired(r,now))return 'closed';if(stale(r,now)||r.source_status==='unavailable'||!['verified','action_verified'].includes(r.review_status))return 'needs_review';return r.availability||'needs_review';}
function canPrepare(r,now=new Date()){return category(r,now)==='new_claims'&&r.review_status==='verified'&&!!r.form;}
function matches(r,f,now=new Date()){
const bucket=category(r,now);
return (f.status==='all'||bucket===(f.status==='open'?'new_claims':f.status))&&
(!f.q||(r.title+' '+r.summary+' '+r.eligibility).toLowerCase().includes(f.q.toLowerCase()))&&
(!f.state||(r.states||[]).includes('ALL')||(r.states||[]).includes('UNKNOWN')||(r.states||[]).includes(f.state))&&
(!f.type||r.type===f.type)&&(!f.noId||(r.notice_id_required===false&&r.device_id_required!==true&&r.review_status==='verified'&&category(r,now)==='new_claims'))&&(!f.proof||(r.receipt_required===false&&r.review_status==='verified'&&category(r,now)==='new_claims'));
}
function packet(r,p){
const rows=PROFILE_KEYS.map(k=>'<tr><th>'+esc(k.replace(/([A-Z])/g,' $1'))+'</th><td>'+esc(p[k])+'</td></tr>').join('');
return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(r.title)+' - preparation copy</title><style>body{font:17px/1.6 system-ui;max-width:760px;margin:35px auto;padding:20px;color:#172c37}th,td{padding:8px;text-align:left;border-bottom:1px solid #ddd}table{width:100%}.notice{padding:16px;background:#fff2d8}a{overflow-wrap:anywhere}@media print{body{margin:0}}</style><h1>'+esc(r.title)+'</h1><p class="notice"><strong>Preparation copy - NOT a submitted claim or an accepted substitute for an official claim form.</strong></p><h2>Your contact information</h2><table>'+rows+'</table><h2>Who may qualify</h2><p>'+esc(r.eligibility)+'</p><h2>What to do next</h2><p>'+esc(r.instructions)+'</p><p>Deadline: '+esc(r.deadline_label||'Follow the official instructions')+'</p><p><a href="'+esc(r.official_url)+'">Open official website</a></p><p>'+esc(r.official_url)+'</p>'+(r.form?'<p>Download the official PDF separately from NFCcop or the administrator. Review both pages, choose a payment method, sign and date it yourself, and use the accepted submission instructions.</p>':'')+'<p>No eligibility declaration or signature has been completed for you. Keep your official confirmation after submitting.</p><p>Prepared with NFCcop. Personal details are contained in this file; keep it private.</p></html>';
}
const api={PROFILE_KEYS,esc,cleanProfile,expired,stale,category,canPrepare,matches,packet};
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SettlementCore=api;
})(typeof globalThis!=='undefined'?globalThis:this);
