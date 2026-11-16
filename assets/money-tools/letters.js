'use strict';
const M=MoneyTools,$=id=>document.getElementById(id);M.mountProfile();M.mountDonation();
let draft='';
const titles={duplicate:'Duplicate charge',refund:'Missing refund',subscription:'Subscription cancellation or charge',billing:'Other billing error'};
function generate(){
const p=M.saveProfile(),kind=$('letter-kind').value,company=$('company').value.trim(),date=$('charge-date').value,amount=$('charge-amount').value,facts=$('letter-facts').value.trim(),request=$('requested-fix').value.trim(),ref=$('reference-last4').value.trim();
const sender=[p.firstName+' '+p.lastName,p.street,[p.city,p.state,p.zip].filter(Boolean).join(' '),p.email,p.phone].map(s=>s.trim()).filter(Boolean).join('\n');
draft=[new Date().toLocaleDateString(),sender,company,$('company-address').value.trim(),'Re: '+titles[kind]+(ref?' - reference ending '+ref:''),'To the billing or customer service team:','I am requesting a review of '+(kind==='duplicate'?'a charge that appears to have been duplicated':kind==='refund'?'a refund that has not arrived':kind==='subscription'?'a subscription cancellation or related charge':'a billing error')+'.',date?'Transaction or billing date: '+M.dateLabel(date):'',amount?'Amount in question: $'+Number(amount).toFixed(2):'','What happened:\n'+facts,'Requested resolution:\n'+request,'Please investigate and respond in writing with the outcome and any correction. If you believe the charge is correct, please provide an explanation and supporting records.','Supporting documents to include (copies only):\n'+($('attachments').value.trim()||'I will include relevant copies where available.'),'Thank you,',[p.firstName,p.lastName].filter(Boolean).join(' ')||'[Add your name before sending]'].filter(Boolean).join('\n\n');
$('letter-preview').textContent=draft;$('letter-output').hidden=false;
$('letter-result').textContent='Draft prepared locally. Review the text and recipient before sending.';
}
$('letter-form').onsubmit=e=>{e.preventDefault();if(e.target.reportValidity())generate();};
$('download-letter').onclick=()=>{if(!draft)return;M.download(M.pageDoc('Billing review request','<h1>Billing review request</h1><pre>'+M.esc(draft)+'</pre>'),'nfccop-billing-letter.html');$('letter-result').textContent='Letter downloaded. Open it and use Print / Save as PDF if needed. It has not been sent.';};
$('download-text').onclick=()=>{if(draft)M.download(draft,'nfccop-billing-letter.txt','text/plain;charset=utf-8');};
$('copy-letter').onclick=async()=>{try{await navigator.clipboard.writeText(draft);$('letter-result').textContent='Letter copied. Paste it into the company’s accepted submission channel.';}catch{$('letter-result').textContent='Select the preview text and copy it manually.';}};
$('email-letter').onclick=()=>{
const email=$('recipient-email').value.trim();
if(!email||!$('recipient-email').checkValidity()){$('letter-result').textContent='Enter and verify the recipient email first.';return;}
if(draft.length>6000){$('letter-result').textContent='This draft is too long for a reliable email link. Download or copy it into your email app.';return;}
location.href='mailto:'+email+'?subject='+encodeURIComponent('Billing review request')+'&body='+encodeURIComponent(draft);
$('letter-result').textContent='Email draft requested. Review it and attach supporting files yourself; nothing has been sent by this site.';
};
$('save-letter-record').onclick=()=>{try{const r=M.addRecord({title:'Billing dispute: '+$('company').value.trim(),guide:'https://yprivateai.com/money-help/billing-dispute-letter.html',notes:'Draft prepared. Review the recipient and accepted delivery method. Transaction date: '+$('charge-date').value+'. Amount in question: '+$('charge-amount').value+'.\n\n'+$('letter-facts').value.trim(),docs:[{label:'Review and send the letter through an accepted channel',done:false},{label:'Keep a copy and proof of delivery',done:false}],status:'Gathering documents'});$('letter-result').textContent='Organizer record saved. The letter has not been sent. Open My Organizer to track it.';}catch(e){$('letter-result').textContent=e.message;}};
