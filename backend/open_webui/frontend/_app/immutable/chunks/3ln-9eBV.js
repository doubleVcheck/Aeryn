import"./CWj6FrbW.js";import"./69_IOA4Y.js";import{p as Be,g as Ie,m as L,o as Fe,l as o,k as d,v as Ve,w as se,x as je,y as Ne,c as w,r as v,n as Z,t as ce,z as J,a as A,d as Oe,q as le,b as Ue,s as Ge,B as de,f as z,e as P,a9 as $e}from"./CCEZMT5x.js";import{i as He}from"./CoafPRNw.js";import{e as Xe,i as Ke}from"./C-jZAaCX.js";import{s as W,d as Ze}from"./DkTcJkBK.js";import{b as Je}from"./Dforll3k.js";import{i as Pe}from"./BRiQdy-g.js";import{p as h}from"./DOmsAlow.js";import{t as q}from"./BX0jcCQO.js";import{c as Qe,b as Ye}from"./DZ69qBGg.js";import{o as et}from"./hrh6gINI.js";import{t as tt}from"./H_1NwN-J.js";import{X as ot}from"./DnEvEpP_.js";import{d as fe}from"./BC4znSyB.js";import{l as rt}from"./Bp9Sdq8c.js";var at=z('<div class="flex items-center h-full"><div></div></div>'),it=z(`<div class=" text-gray-500 rounded-full cursor-not-allowed"><svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><style>.spinner_OSmW {
								transform-origin: center;
								animation: spinner_T6mA 0.75s step-end infinite;
							}
							@keyframes spinner_T6mA {
								8.3% {
									transform: rotate(30deg);
								}
								16.6% {
									transform: rotate(60deg);
								}
								25% {
									transform: rotate(90deg);
								}
								33.3% {
									transform: rotate(120deg);
								}
								41.6% {
									transform: rotate(150deg);
								}
								50% {
									transform: rotate(180deg);
								}
								58.3% {
									transform: rotate(210deg);
								}
								66.6% {
									transform: rotate(240deg);
								}
								75% {
									transform: rotate(270deg);
								}
								83.3% {
									transform: rotate(300deg);
								}
								91.6% {
									transform: rotate(330deg);
								}
								100% {
									transform: rotate(360deg);
								}
							}</style><g class="spinner_OSmW"><rect x="11" y="1" width="2" height="5" opacity=".14"></rect><rect x="11" y="1" width="2" height="5" transform="rotate(30 12 12)" opacity=".29"></rect><rect x="11" y="1" width="2" height="5" transform="rotate(60 12 12)" opacity=".43"></rect><rect x="11" y="1" width="2" height="5" transform="rotate(90 12 12)" opacity=".57"></rect><rect x="11" y="1" width="2" height="5" transform="rotate(120 12 12)" opacity=".71"></rect><rect x="11" y="1" width="2" height="5" transform="rotate(150 12 12)" opacity=".86"></rect><rect x="11" y="1" width="2" height="5" transform="rotate(180 12 12)"></rect></g></svg></div>`),nt=z('<button id="confirm-recording-button" type="button" class="p-1.5 bg-indigo-500 text-white dark:bg-indigo-500 dark:text-blue-950 rounded-full"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="size-4"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"></path></svg></button>'),st=z('<div><div class="flex items-center mr-1"><button type="button"><!></button></div> <div class="flex flex-1 self-center items-center justify-between ml-2 mx-1 overflow-hidden h-6" dir="rtl"><div class="flex items-center gap-0.5 h-6 w-full max-w-full overflow-hidden overflow-x-hidden flex-wrap"></div></div> <div class="flex"><div class="  mx-1.5 pr-1 flex justify-center items-center"><div> </div></div> <div class="flex items-center"><!></div></div></div>');function St(ue,u){Be(u,!1);const Q=()=>P(Qe,"$config",F),B=()=>P(Ye,"$settings",F),I=()=>P(me,"$i18n",F),[F,ge]=Ge();fe.extend(rt);const me=Ie("i18n");let g=h(u,"recording",12,!1),Y=h(u,"transcribe",8,!0),ve=h(u,"displayMedia",8,!1),pe=h(u,"echoCancellation",8,!0),we=h(u,"noiseSuppression",8,!0),he=h(u,"autoGainControl",8,!0),ye=h(u,"className",8," p-2.5 w-full max-w-full"),V=h(u,"onCancel",8,()=>{}),j=h(u,"onConfirm",8,e=>{}),l=L(!1),R=!1,E=L(0),N=null,O="";const be=()=>{N=setInterval(()=>{$e(E)},1e3)},ke=()=>{clearInterval(N),d(E,0)},xe=e=>{const t=Math.floor(e/60),a=e%60,i=a<10?`0${a}`:a;return`${t}:${i}`};let _=null;const ee=async()=>{if("wakeLock"in navigator)try{_=await navigator.wakeLock.request("screen"),_.addEventListener("release",()=>{})}catch(e){}},U=async()=>{if(_){try{await _.release()}catch(e){}_=null}};let f,p,m,x=[];const _e=-45;let b=300,n=L(Array(b).fill(0));const Se=e=>{let t=0;for(let a=0;a<e.length;a++){const i=(e[a]-128)/128;t+=i*i}return Math.sqrt(t/e.length)},Me=e=>{e=e*10;const a=Math.pow(e,1.5);return Math.min(1,Math.max(.01,a))},Ce=e=>{const t=new AudioContext,a=t.createMediaStreamSource(e),i=t.createAnalyser();i.minDecibels=_e,a.connect(i);const r=i.frequencyBinCount,s=new Uint8Array(r),c=new Uint8Array(i.fftSize);(()=>{const y=()=>{if(!(!g()||o(l))){if(g()&&!o(l)){i.getByteTimeDomainData(c),i.getByteFrequencyData(s);const C=Se(c);o(n).push(Me(C)),o(n).length>=b&&o(n).shift(),d(n,o(n))}window.requestAnimationFrame(y)}};window.requestAnimationFrame(y)})()},Le=async(e,t="wav")=>{var i,r,s,c,k,y;await de();const a=et(e,`Recording-${fe().format("L LT")}.${t}`);if(Y()){if(Q().audio.stt.engine==="web"||(((s=(r=(i=B())==null?void 0:i.audio)==null?void 0:r.stt)==null?void 0:s.engine)??"")==="web")return;const C=await tt(localStorage.token,a,(y=(k=(c=B())==null?void 0:c.audio)==null?void 0:k.stt)==null?void 0:y.language).catch(ze=>(q.error(`${ze}`),null));C&&j()(C)}else j()({file:a,blob:e})},Re=async()=>{var t,a,i;d(l,!0);try{if(ve()){const r=await navigator.mediaDevices.getDisplayMedia({audio:!0});f=new MediaStream;for(const s of r.getAudioTracks())f.addTrack(s);for(const s of r.getVideoTracks())s.stop()}else f=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:pe(),noiseSuppression:we(),autoGainControl:he()}})}catch(r){q.error(I().t("Error accessing media devices.")),d(l,!1),g(!1);return}const e=["audio/webm; codecs=opus","audio/webm","audio/ogg; codecs=opus","audio/mp4","audio/wav"];m=new MediaRecorder(f,{mimeType:e.find(r=>MediaRecorder.isTypeSupported(r))}),m.onstart=async()=>{d(l,!1),be(),await ee(),x=[],Ce(f)},m.ondataavailable=r=>x.push(r.data),m.onstop=async()=>{var r;if(R){let s=((r=x[0])==null?void 0:r.type)||m.mimeType||"audio/webm",c=s.split("/")[1].split(";")[0]||"webm";s.startsWith("audio/")||(c="webm");const k=new Blob(x,{type:s});await Le(k,c),R=!1,d(l,!1)}x=[],g(!1)};try{m.start()}catch(r){q.error(I().t("Error starting recording.")),d(l,!1),g(!1);return}if(Y()&&(Q().audio.stt.engine==="web"||(((i=(a=(t=B())==null?void 0:t.audio)==null?void 0:a.stt)==null?void 0:i.engine)??"")==="web")&&("SpeechRecognition"in window||"webkitSpeechRecognition"in window)){p=new(window.SpeechRecognition||window.webkitSpeechRecognition),p.continuous=!0;const r=2e3;let s;p.start(),p.onresult=async c=>{var y;clearTimeout(s);const k=c.results[Object.keys(c.results).length-1][0].transcript;O=`${O}${k}`,await de(),(y=document.getElementById("chat-input"))==null||y.focus(),s=setTimeout(()=>{p.stop()},r)},p.onend=function(){te(),j()({text:O}),R=!1,d(l,!1)},p.onerror=function(c){q.error(I().t("Speech recognition error: {{error}}",{error:c.error})),V()(),T()}}},T=async()=>{g()&&m&&await m.stop(),p&&p.stop(),await U(),ke(),x=[],d(n,Array(b).fill(0)),f&&f.getTracks().forEach(t=>t.stop()),f=null},te=async()=>{d(l,!0),R=!0,g()&&m&&await m.stop(),clearInterval(N),await U(),f&&f.getTracks().forEach(t=>t.stop()),f=null};let G,$=L(),Ee=L(300);const oe=e=>{e.key==="Escape"&&(e.preventDefault(),T(),V()())},re=async()=>{g()&&document.visibilityState==="visible"&&await ee()};Fe(()=>{window.addEventListener("keydown",oe),document.addEventListener("visibilitychange",re),G=new ResizeObserver(()=>{b=Math.floor(window.innerWidth/4),o(n).length>b?d(n,o(n).slice(o(n).length-b)):d(n,Array(b-o(n).length).fill(0).concat(o(n)))}),G.observe(document.body)}),Ve(()=>{window.removeEventListener("keydown",oe),document.removeEventListener("visibilitychange",re),U(),G.disconnect()}),se(()=>je(g()),()=>{g()?Re():T()}),se(()=>o($),()=>{d(Ee,Math.floor(o($)/5))}),Ne(),Pe();var S=st(),H=w(S),D=w(H),Te=w(D);ot(Te,{className:"size-4"}),v(D),v(H);var M=Z(H,2),ae=w(M);Xe(ae,5,()=>(o(n),J(()=>o(n).slice().reverse())),Ke,(e,t)=>{var a=at(),i=w(a);v(a),ce(r=>{W(i,1,`w-[2px] shrink-0
                    
                    ${o(l)?" bg-gray-500 dark:bg-gray-400   ":"bg-indigo-500 dark:bg-indigo-400  "} 
                    
                    inline-block h-full`),Ze(i,`height: ${r??""}%;`)},[()=>(o(t),J(()=>Math.min(100,Math.max(14,o(t)*100))))]),A(e,a)}),v(ae),v(M);var ie=Z(M,2),X=w(ie),K=w(X),De=w(K,!0);v(K),v(X);var ne=Z(X,2),Ae=w(ne);{var We=e=>{var t=it();A(e,t)},qe=e=>{var t=nt();le("click",t,async()=>{await te()}),A(e,t)};He(Ae,e=>{o(l)?e(We):e(qe,-1)})}v(ne),v(ie),v(S),ce(e=>{W(S,1,`${o(l)?" bg-gray-100/50 dark:bg-gray-850/50":"bg-indigo-300/10 dark:bg-indigo-500/10 "} rounded-full flex justify-between ${ye()??""}`,"svelte-nkn4fu"),W(D,1,`p-1.5

            ${o(l)?" bg-gray-200 dark:bg-gray-700/50":"bg-indigo-400/20 text-indigo-600 dark:text-indigo-300 "} 


             rounded-full`),M.dir=M.dir,W(K,1,`text-sm
        
        
        ${o(l)?" text-gray-500  dark:text-gray-400  ":" text-indigo-400 "} 
       font-medium flex-1 mx-auto text-center`),Oe(De,e)},[()=>(o(E),J(()=>xe(o(E))))]),le("click",D,async()=>{T(),V()()}),Je(S,"clientWidth",e=>d($,e)),A(ue,S),Ue(),ge()}export{St as V};
//# sourceMappingURL=3ln-9eBV.js.map
