// Llenador genérico de formularios. Reemplaza __PROFILE__ con el JSON del perfil en inglés y pégalo en javascript_tool.
// Llena lo común, marca solo casillas obligatorias de términos (nunca marketing) y devuelve FILLED / MISSING. No envía el formulario.
(async()=>{await new Promise(r=>setTimeout(r,1500));
const P=__PROFILE__; // {first,last,full,email,company,title,phone,li,city,state,country,web,diet,industry} en inglés
const docs=[document,...[...document.querySelectorAll('iframe')].map(f=>{try{return f.contentDocument}catch(e){return null}}).filter(Boolean)];
const lab=e=>{let t=(e.labels&&e.labels[0]&&e.labels[0].innerText)||e.getAttribute('aria-label')||e.placeholder||'';if(!t){const c=e.closest('.hs-form-field,.form-group,.mktoFormRow,.field,div');t=c?c.innerText.slice(0,80):''}return (t+' '+(e.name||'')+' '+(e.id||'')).toLowerCase().replace(/\s+/g,' ')};
const setv=(e,v)=>{const pr=e.tagName=='SELECT'?HTMLSelectElement.prototype:e.tagName=='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(pr,'value').set.call(e,v);['input','change','blur'].forEach(t=>e.dispatchEvent(new Event(t,{bubbles:true})))};
const pick=(e,res)=>{for(const re of res){const o=[...e.options].find(o=>re.test(o.text)&&o.value);if(o){setv(e,o.value);return o.text}}return null};
const out=[],miss=[];
for(const d of docs)for(const e of d.querySelectorAll('input,select,textarea')){
 if(['hidden','submit','button','search','file','password'].includes(e.type))continue;
 if(e.offsetParent===null&&e.type!=='checkbox')continue;
 const l=lab(e);let v=null;
 if(e.type==='checkbox'||e.type==='radio'){if(e.type==='checkbox'&&/(i agree|agree to|accept|terms|privacy policy|21 years|over 21|i confirm|acknowledge)/.test(l)&&!/(marketing|newsletter|promotional|offers|updates|subscribe|communications from)/.test(l)){if(!e.checked)e.click();out.push('[x] '+l.slice(0,50))}else if(e.required&&!e.checked)miss.push('?'+e.type+': '+l.slice(0,70));continue}
 if(e.value&&e.tagName!=='SELECT')continue;
 if(e.tagName==='SELECT'){
  if(/country/.test(l))v=pick(e,[/^bolivia/i]);
  else if(/state|province|region/.test(l))v=pick(e,[/santa cruz/i,/outside|other|n\/a|not applicable|non-us|international/i]);
  else if(/size|employees|headcount/.test(l))v=pick(e,[/^1\s*[-–]/,/less than|<|under|^1-|^0/i,/\d/]);
  else if(/level|seniority/.test(l))v=pick(e,[/^manager/i,/manager/i]);
  else if(/function|department|role|job area/.test(l))v=pick(e,[/^IT\b|information tech|infrastructure|cloud/i,/engineer/i]);
  else if(/industry/.test(l))v=pick(e,[/logist|transport/i,/wholesale|trade|distribution/i,/other/i]);
  else if(/diet/.test(l))v=pick(e,[/^none|no restriction|^no$/i]);
  else if(/hear|source|referr/.test(l))v=pick(e,[/colleague|word of mouth|friend/i,/conference parties/i,/other/i]);
  else if(/aws (customer|relationship)|use aws|on aws/.test(l))v=pick(e,[/production/i,/^yes/i,/customer/i]);
  else if(/re:?invent|attending/.test(l))v=pick(e,[/^no/i]);
  else if(/cloud provider|primary cloud|main cloud/.test(l))v=pick(e,[/^aws|amazon/i]);
  else if(/spend|budget/.test(l))v=pick(e,[/less than|under|<|^\$?0/i]);
  if(v)out.push(l.slice(0,40)+' => '+v);else if(e.required||/\*/.test(l))miss.push('SEL: '+l.slice(0,70)+' ['+[...e.options].slice(0,8).map(o=>o.text).join('/')+']');continue}
 if(/first|fname|given/.test(l))v=P.first;else if(/last|lname|surname|family/.test(l))v=P.last;
 else if(/e-?mail/.test(l))v=P.email;else if(/linkedin/.test(l))v=P.li;
 else if(/phone|mobile|cell/.test(l))v=P.phone;
 else if(/website|company url|domain/.test(l))v=P.web;
 else if(/company|organi[sz]ation|employer|account name/.test(l))v=P.company;
 else if(/job title|title|position|role/.test(l))v=P.title;
 else if(/full name|^ ?name|your name/.test(l))v=P.full;
 else if(/city/.test(l))v=P.city;else if(/state|province/.test(l))v=P.state;else if(/country/.test(l))v=P.country;
 else if(/diet|allerg|food/.test(l))v=P.diet;else if(/industry/.test(l))v=P.industry;
 if(v){setv(e,v);out.push(l.slice(0,40)+' => '+v)}else miss.push((e.required?'REQ ':'')+e.tagName+': '+l.slice(0,90))}
return location.host+'\nFILLED:\n'+out.join('\n')+'\nMISSING:\n'+miss.join('\n')})()
