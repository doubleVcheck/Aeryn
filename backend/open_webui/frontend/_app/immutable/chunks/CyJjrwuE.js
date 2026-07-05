import"./CWj6FrbW.js";import"./69_IOA4Y.js";import{p as Ge,g as Je,w as pe,x as T,y as Ke,i as Qe,c as r,r as a,q as J,a as m,l as d,n as u,t as b,z as n,k as f,d as c,b as Re,e as Xe,s as Ye,m as k,B as K,u as C,f as h}from"./CCEZMT5x.js";import{i as me}from"./CoafPRNw.js";import{r as Q,a as E,b as Ze}from"./DkTcJkBK.js";import{b as R}from"./DNyK6Ik9.js";import{b as he}from"./CkHRTKW8.js";import{p as et}from"./Bfc47y5P.js";import{i as tt}from"./BRiQdy-g.js";import{p as w}from"./DOmsAlow.js";import{g as rt}from"./DsRP2z98.js";import{n as X,e as at,f as it}from"./hrh6gINI.js";import{C as st}from"./z8_mTs2x.js";import{C as ot}from"./D95y9esO.js";import{B as nt}from"./u_leMV1Z.js";import{T as q}from"./DTAlVNmN.js";import{C as lt}from"./-vo3AilG.js";var dt=h('<button class="w-full text-left text-sm py-1.5 px-1 rounded-lg dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-gray-850" type="button"><!></button>'),ut=h('<input class="w-full text-2xl font-medium bg-transparent outline-hidden font-primary" type="text" required=""/>'),ct=h('<select class="text-xs bg-transparent border border-gray-100 dark:border-gray-800 rounded-lg px-2 py-1 outline-hidden"><option> </option><option> </option></select>'),ft=h('<div class="text-sm text-gray-500 shrink-0"> </div>'),vt=h('<input class="w-full text-sm disabled:text-gray-500 bg-transparent outline-hidden" type="text" required=""/>'),_t=h('<input class="w-full text-sm bg-transparent outline-hidden" type="text" required=""/>'),pt=h('<div class="text-sm text-gray-500"><div class=" bg-yellow-500/20 text-yellow-700 dark:text-yellow-200 rounded-lg px-4 py-3"><div> </div> <ul class=" mt-1 list-disc pl-4 text-xs"><li> </li> <li> </li></ul></div> <div class="my-3"> </div></div>'),mt=h('<div class=" flex flex-col justify-between w-full overflow-y-auto h-full"><div class="mx-auto w-full md:px-0 h-full"><form class=" flex flex-col max-h-[100dvh] h-full"><div class="flex flex-col flex-1 overflow-auto h-0 rounded-lg"><div class="w-full mb-2 flex flex-col gap-0.5"><div class="flex w-full items-center"><div class=" shrink-0 mr-2"><!></div> <div class="flex-1"><!></div> <div class="flex items-center gap-2"><!> <!></div></div> <div class=" flex gap-2 px-1 items-center"><!> <!></div></div> <div class="mb-2 flex-1 overflow-auto h-0 rounded-lg"><!></div> <div class="pb-3 flex justify-between"><div class="flex-1 pr-3"><div class="text-xs text-gray-500 line-clamp-2"><span class=" font-semibold dark:text-gray-200"> </span> <br/>— <span class=" font-medium dark:text-gray-400"> </span></div></div> <button class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full" type="submit"> </button></div></div></form></div></div> <!>',1);function Et(ge,v){Ge(v,!1);const e=()=>Xe(be,"$i18n",xe),[xe,ye]=Ye(),be=Je("i18n");let P=k(null),S=k(!1),we=w(v,"onSave",8,()=>{}),g=w(v,"edit",8,!1),Y=w(v,"clone",8,!1),$=w(v,"id",12,""),x=w(v,"name",12,""),y=w(v,"meta",28,()=>({description:""})),_=w(v,"content",12,""),F=k("");const ke=()=>{f(F,_())};let B=k(),A=k("filter");const Z=`"""
title: Example Filter
author: zanellm-ui
author_url: https://github.com/zephyrzane
funding_url: https://github.com/zephyrzane
version: 0.1
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )
        max_turns: int = Field(
            default=8, description="Maximum allowable conversation turns for a user."
        )
        pass

    class UserValves(BaseModel):
        max_turns: int = Field(
            default=4, description="Maximum allowable conversation turns for a user."
        )
        pass

    def __init__(self):
        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom
        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.
        # Alternatively, you can remove the files directly from the body in from the inlet hook
        # self.file_handler = True

        # Initialize 'valves' with specific configurations. Using 'Valves' instance helps encapsulate settings,
        # which ensures settings are managed cohesively and not confused with operational flags like 'file_handler'.
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify the request body or validate it before processing by the chat completion API.
        # This function is the pre-processor for the API where various checks on the input can be performed.
        # It can also modify the request before sending it to the API.
        print(f"inlet:{__name__}")
        print(f"inlet:body:{body}")
        print(f"inlet:user:{__user__}")

        if __user__.get("role", "admin") in ["user", "admin"]:
            messages = body.get("messages", [])

            max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)
            if len(messages) > max_turns:
                raise Exception(
                    f"Conversation turn limit exceeded. Max turns: {max_turns}"
                )

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.
        print(f"outlet:{__name__}")
        print(f"outlet:body:{body}")
        print(f"outlet:user:{__user__}")

        return body
`,$e=`"""
title: Example Event
author: zanellm-ui
author_url: https://github.com/zephyrzane
funding_url: https://github.com/zephyrzane
version: 0.1
"""

from pydantic import BaseModel


class Event:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    async def event(
        self,
        event: dict,
        __event_id__: str = None,
        __event_name__: str = None,
        __id__: str = None,
        __app__=None,
        __request__=None,
    ):
        print(f"event:{__name__}")
        print(f"event:id:{__event_id__}")
        print(f"event:name:{__event_name__}")
        print(f"event:payload:{event}")
`;let M=k(Z);const Fe=t=>{f(A,t),f(M,t==="event"?$e:Z),_(d(M)),f(F,d(M))},Ie=t=>{Fe(t==="event"?"event":"filter")},ze=async()=>{we()({id:$(),name:x(),meta:y(),content:_()})},ee=async()=>{if(d(B)){_(d(F)),await K();const t=await d(B).formatPythonCodeHandler();await K(),_(d(F)),await K(),t||console.warn("Code formatting failed or was skipped, saving unformatted code"),ze()}};pe(()=>T(_()),()=>{_()&&ke()}),pe(()=>(T(x()),T(g()),T(Y()),X),()=>{x()&&!g()&&!Y()&&$(X(x()))}),Ke(),tt();var te=mt(),V=Qe(te),re=r(V),N=r(re),ae=r(N),D=r(ae),H=r(D),O=r(H),Ce=r(O);{let t=C(()=>(e(),n(()=>e().t("Back"))));q(Ce,{get content(){return d(t)},children:(i,l)=>{var s=dt(),o=r(s);lt(o,{strokeWidth:"2.5"}),a(s),J("click",s,()=>{rt("/admin/functions")}),m(i,s)},$$slots:{default:!0}})}a(O);var U=u(O,2),Pe=r(U);{let t=C(()=>(e(),n(()=>e().t("e.g. My Filter"))));q(Pe,{get content(){return d(t)},placement:"top-start",children:(i,l)=>{var s=ut();Q(s),b(o=>E(s,"placeholder",o),[()=>(e(),n(()=>e().t("Function Name")))]),R(s,x),m(i,s)},$$slots:{default:!0}})}a(U);var ie=u(U,2),se=r(ie);{var Be=t=>{var i=ct(),l=r(i),s=r(l,!0);a(l),l.value=l.__value="filter";var o=u(l),I=r(o,!0);a(o),o.value=o.__value="event",a(i),b((p,z,G)=>{E(i,"aria-label",p),c(s,z),c(I,G)},[()=>(e(),n(()=>e().t("Function starter"))),()=>(e(),n(()=>e().t("Filter"))),()=>(e(),n(()=>e().t("Event")))]),Ze(i,()=>d(A),p=>f(A,p)),J("change",i,p=>Ie(p.currentTarget.value)),m(t,i)};me(se,t=>{g()||t(Be)})}var Me=u(se,2);{let t=C(()=>(e(),n(()=>e().t("Function"))));nt(Me,{type:"muted",get content(){return d(t)}})}a(ie),a(H);var oe=u(H,2),ne=r(oe);{var Ne=t=>{var i=ft(),l=r(i,!0);a(i),b(()=>c(l,$())),m(t,i)},Te=t=>{{let i=C(()=>(e(),n(()=>e().t("e.g. my_filter"))));q(t,{className:"w-full",get content(){return d(i)},placement:"top-start",children:(l,s)=>{var o=vt();Q(o),b(I=>{E(o,"placeholder",I),o.disabled=g()},[()=>(e(),n(()=>e().t("Function ID")))]),R(o,$),m(l,o)},$$slots:{default:!0}})}};me(ne,t=>{g()?t(Ne):t(Te,-1)})}var Ee=u(ne,2);{let t=C(()=>(e(),n(()=>e().t("e.g. A filter to remove profanity from text"))));q(Ee,{className:"w-full self-center items-center flex",get content(){return d(t)},placement:"top-start",children:(i,l)=>{var s=_t();Q(s),b(o=>E(s,"placeholder",o),[()=>(e(),n(()=>e().t("Function Description")))]),R(s,()=>y().description,o=>y(y().description=o,!0)),m(i,s)},$$slots:{default:!0}})}a(oe),a(D);var W=u(D,2),qe=r(W);he(st(qe,{get value(){return _()},lang:"python",get boilerplate(){return d(M)},onChange:t=>{if(f(F,t),!g()){const i=at(t);i.title&&!x()&&(x(it(i.title)),$(X(i.title))),i.description&&!y().description&&y({...y(),description:i.description})}},onSave:async()=>{d(P)&&d(P).requestSubmit()},$$legacy:!0}),t=>f(B,t),()=>d(B)),a(W);var le=u(W,2),j=r(le),de=r(j),L=r(de),Se=r(L,!0);a(L);var ue=u(L),ce=u(ue,3),Ae=r(ce,!0);a(ce),a(de),a(j);var fe=u(j,2),Ve=r(fe,!0);a(fe),a(le),a(ae),a(N),he(N,t=>f(P,t),()=>d(P)),a(re),a(V);var De=u(V,2);ot(De,{get show(){return d(S)},set show(t){f(S,t)},$$events:{confirm:()=>{ee()}},children:(t,i)=>{var l=pt(),s=r(l),o=r(s),I=r(o,!0);a(o);var p=u(o,2),z=r(p),G=r(z,!0);a(z);var ve=u(z,2),He=r(ve,!0);a(ve),a(p),a(s);var _e=u(s,2),Oe=r(_e,!0);a(_e),a(l),b((Ue,We,je,Le)=>{c(I,Ue),c(G,We),c(He,je),c(Oe,Le)},[()=>(e(),n(()=>e().t("Please carefully review the following warnings:"))),()=>(e(),n(()=>e().t("Functions allow arbitrary code execution."))),()=>(e(),n(()=>e().t("Do not install functions from sources you do not fully trust."))),()=>(e(),n(()=>e().t("I acknowledge that I have read and I understand the implications of my action. I am aware of the risks associated with executing arbitrary code and I have verified the trustworthiness of the source.")))]),m(t,l)},$$slots:{default:!0},$$legacy:!0}),b((t,i,l,s)=>{c(Se,t),c(ue,` ${i??""} `),c(Ae,l),c(Ve,s)},[()=>(e(),n(()=>e().t("Warning:"))),()=>(e(),n(()=>e().t("Functions allow arbitrary code execution."))),()=>(e(),n(()=>e().t("don't install random functions from sources you don't trust."))),()=>(e(),n(()=>e().t("Save")))]),J("submit",N,et(()=>{g()?ee():f(S,!0)})),m(ge,te),Re(),ye()}export{Et as F};
//# sourceMappingURL=CyJjrwuE.js.map
