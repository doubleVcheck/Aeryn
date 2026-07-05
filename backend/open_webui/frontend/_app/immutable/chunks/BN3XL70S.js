import"./CWj6FrbW.js";import{p as U,o as V,h as W,i as X,a as c,b as Y,k as Z,l as p,a$ as $,t as x,r as tt,f as C}from"./CCEZMT5x.js";import{i as et}from"./CoafPRNw.js";import{e as at,i as nt}from"./C-jZAaCX.js";import{d as _,s as ot}from"./DkTcJkBK.js";import{p as e}from"./DOmsAlow.js";var it=C('<div class="confetti svelte-rtt661"></div>'),rt=C("<div></div>");function vt(M,t){U(t,!0);const b=e(t,"size",3,10),f=e(t,"x",19,()=>[-.5,.5]),u=e(t,"y",19,()=>[.25,1]),i=e(t,"duration",3,2e3),r=e(t,"infinite",3,!1),l=e(t,"delay",19,()=>[0,50]),m=e(t,"colorRange",19,()=>[0,360]),s=e(t,"colorArray",19,()=>[]),z=e(t,"amount",3,50),d=e(t,"iterationCount",3,1),R=e(t,"fallDistance",3,"100px"),k=e(t,"rounded",3,!1),w=e(t,"cone",3,!1),A=e(t,"noGravity",3,!1),D=e(t,"xSpread",3,.15),F=e(t,"destroyOnComplete",3,!0),G=e(t,"disableForReducedMotion",3,!1);let v=$(!1);V(()=>{!F()||r()||typeof d()=="string"||setTimeout(()=>Z(v,!0),(i()+l()[1])*d())});function a(o,n){return Math.random()*(n-o)+o}function O(){return s().length?s()[Math.round(Math.random()*(s().length-1))]:`hsl(${Math.round(a(m()[0],m()[1]))}, 75%, 50%)`}var y=W(),S=X(y);{var B=o=>{var n=rt();let g;at(n,21,()=>({length:z()}),nt,(T,lt)=>{var h=it();x((j,q,E,H,I,J,K,L,N,P,Q)=>_(h,`
        --color: ${j??""};
        --skew: ${q??""}deg,${E??""}deg;
        --rotation-xyz: ${H??""}, ${I??""}, ${J??""};
        --rotation-deg: ${K??""}deg;
        --translate-y-multiplier: ${L??""};
        --translate-x-multiplier: ${N??""};
        --scale: ${P??""};
        --transition-delay: ${Q??""}ms;
        --transition-duration: ${r()?`calc(${i()}ms * var(--scale))`:`${i()}ms`};`),[()=>O(),()=>a(-45,45),()=>a(-45,45),()=>a(-10,10),()=>a(-10,10),()=>a(-10,10),()=>a(0,360),()=>a(u()[0],u()[1]),()=>a(f()[0],f()[1]),()=>.1*a(2,10),()=>a(l()[0],l()[1])]),c(T,h)}),tt(n),x(()=>{g=ot(n,1,"confetti-holder svelte-rtt661",null,g,{rounded:k(),cone:w(),"no-gravity":A(),"reduced-motion":G()}),_(n,`
    --fall-distance: ${R()??""};
    --size: ${b()??""}px;
    --x-spread: ${1-D()};
    --transition-iteration-count: ${(r()?"infinite":d())??""};`)}),c(o,n)};et(S,o=>{p(v)||o(B)})}c(M,y),Y()}export{vt as C};
//# sourceMappingURL=BN3XL70S.js.map
