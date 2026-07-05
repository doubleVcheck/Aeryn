import"./CWj6FrbW.js";import"./69_IOA4Y.js";import{p as ze,g as Ke,w as ge,x as G,y as Je,i as Qe,k as _,l as d,n as u,c as s,r as o,t as k,z as i,q as K,a as $,d as f,b as Ve,e as xe,s as Xe,m as q,B as J,u as T,f as E}from"./CCEZMT5x.js";import{i as Ze}from"./CoafPRNw.js";import{a as C,r as Q}from"./DkTcJkBK.js";import{b as V}from"./DNyK6Ik9.js";import{b as ye}from"./CkHRTKW8.js";import{p as et}from"./Bfc47y5P.js";import{i as tt}from"./BRiQdy-g.js";import{p as h}from"./DOmsAlow.js";import{t as be}from"./BX0jcCQO.js";import{g as rt}from"./DsRP2z98.js";import{u as at}from"./DZ69qBGg.js";import{u as st}from"./BjaZYii1.js";import{n as X,e as ot,f as it}from"./hrh6gINI.js";import{C as lt}from"./z8_mTs2x.js";import{C as nt}from"./D95y9esO.js";import{C as dt}from"./-vo3AilG.js";import{T as S}from"./DTAlVNmN.js";import{A as ut,L as ct}from"./rO3g8i8R.js";var mt=E('<button class="w-full text-left text-sm py-1.5 px-1 rounded-lg dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-gray-850" type="button"><!></button>'),ft=E('<input class="w-full text-2xl bg-transparent outline-hidden" type="text" required=""/>'),vt=E('<div class="text-sm text-gray-500 shrink-0"> </div>'),pt=E('<input class="w-full text-sm disabled:text-gray-500 bg-transparent outline-hidden" type="text" required=""/>'),_t=E('<input class="w-full text-sm bg-transparent outline-hidden" type="text" required=""/>'),ht=E('<div class="text-sm text-gray-500"><div class=" bg-yellow-500/20 text-yellow-700 dark:text-yellow-200 rounded-lg px-4 py-3"><div> </div> <ul class=" mt-1 list-disc pl-4 text-xs"><li> </li> <li> </li></ul></div> <div class="my-3"> </div></div>'),gt=E('<!> <div class=" flex flex-col justify-between w-full overflow-y-auto h-full"><div class="mx-auto w-full md:px-0 h-full"><form class=" flex flex-col max-h-[100dvh] h-full"><div class="flex flex-col flex-1 overflow-auto h-0 rounded-lg"><div class="w-full mb-2 flex flex-col gap-0.5"><div class="flex w-full items-center"><div class=" shrink-0 mr-2"><!></div> <div class="flex-1"><!></div> <div class="self-center shrink-0"><button class="bg-gray-50 hover:bg-gray-100 text-black dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-white transition px-2 py-1 rounded-full flex gap-1 items-center" type="button"><!> <div class="text-sm font-medium shrink-0"> </div></button></div></div> <div class=" flex gap-2 px-1 items-center"><!> <!></div></div> <div class="mb-2 flex-1 overflow-auto h-0 rounded-lg"><!></div> <div class="pb-3 flex justify-between"><div class="flex-1 pr-3"><div class="text-xs text-gray-500 line-clamp-2"><span class=" font-semibold dark:text-gray-200"> </span> <br/>— <span class=" font-medium dark:text-gray-400"> </span></div></div> <button class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full" type="submit"> </button></div></div></form></div></div> <!>',1);function Ut(we,v){ze(v,!1);const p=()=>xe(at,"$user",Z),e=()=>xe($e,"$i18n",Z),[Z,ke]=Xe(),$e=Ke("i18n");let P=q(null),M=q(!1),F=q(!1),g=h(v,"edit",8,!1),ee=h(v,"clone",8,!1),Te=h(v,"onSave",8,()=>{}),x=h(v,"id",12,""),y=h(v,"name",12,""),b=h(v,"meta",28,()=>({description:""})),w=h(v,"content",12,""),I=h(v,"accessGrants",28,()=>[]),A=q("");const Ce=()=>{_(A,w())};let D=q(),Ee=`import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        pass

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions
	
    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """

        # Do not include a descrption for __user__ as it should not be shown in the tool's specification
        # The session user object will be passed as a parameter when the function is called

        print(__user__)
        result = ""

        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        if result == "":
            result = "User: Unknown"

        return result

    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        """

        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")  # Using 12-hour format with AM/PM
        current_date = now.strftime(
            "%A, %B %d, %Y"
        )  # Full weekday, month name, day, and year

        return f"Current Date and Time = {current_date}, {current_time}"

    def calculator(
        self,
        equation: str = Field(
            ..., description="The mathematical equation to calculate."
        ),
    ) -> str:
        """
        Calculate the result of an equation.
        """

        # Avoid using eval in production code
        # https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
        try:
            result = eval(equation)
            return f"{equation} = {result}"
        except Exception as e:
            print(e)
            return "Invalid equation"

    def get_current_weather(
        self,
        city: str = Field(
            "New York, NY", description="Get the current weather for a given city."
        ),
    ) -> str:
        """
        Get the current weather for a given city.
        """

        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return (
                "API key is not set in the environment variable 'OPENWEATHER_API_KEY'."
            )

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # Optional: Use 'imperial' for Fahrenheit
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            data = response.json()

            if data.get("cod") != 200:
                return f"Error fetching weather data: {data.get('message')}"

            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return f"Weather in {city}: {temperature}°C"
        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
`;const qe=async()=>{Te()({id:x(),name:y(),meta:b(),content:w(),access_grants:I()})},te=async()=>{if(d(D)){w(d(A)),await J();const r=await d(D).formatPythonCodeHandler();await J(),w(d(A)),await J(),r||console.warn("Code formatting failed or was skipped, saving unformatted code"),qe()}};ge(()=>G(w()),()=>{w()&&Ce()}),ge(()=>(G(y()),G(g()),G(ee()),X),()=>{y()&&!g()&&!ee()&&x(X(y()))}),Je(),tt();var re=gt(),ae=Qe(re);{let r=T(()=>(p(),i(()=>{var t,a,n,m;return((n=(a=(t=p())==null?void 0:t.permissions)==null?void 0:a.sharing)==null?void 0:n.tools)||((m=p())==null?void 0:m.role)==="admin"}))),l=T(()=>(p(),i(()=>{var t,a,n,m;return((n=(a=(t=p())==null?void 0:t.permissions)==null?void 0:a.sharing)==null?void 0:n.public_tools)||((m=p())==null?void 0:m.role)==="admin"}))),c=T(()=>(p(),i(()=>{var t,a,n,m;return(((n=(a=(t=p())==null?void 0:t.permissions)==null?void 0:a.access_grants)==null?void 0:n.allow_users)??!0)||((m=p())==null?void 0:m.role)==="admin"})));ut(ae,{accessRoles:["read","write"],get share(){return d(r)},get sharePublic(){return d(l)},get shareUsers(){return d(c)},onChange:async()=>{if(g()&&x())try{await st(localStorage.token,x(),I()),be.success(e().t("Saved"))}catch(t){be.error(`${t}`)}},get show(){return d(F)},set show(t){_(F,t)},get accessGrants(){return I()},set accessGrants(t){I(t)},$$legacy:!0})}var H=u(ae,2),se=s(H),N=s(se),oe=s(N),U=s(oe),W=s(U),j=s(W),Pe=s(j);{let r=T(()=>(e(),i(()=>e().t("Back"))));S(Pe,{get content(){return d(r)},children:(l,c)=>{var t=mt(),a=s(t);dt(a,{strokeWidth:"2.5"}),o(t),k(n=>C(t,"aria-label",n),[()=>(e(),i(()=>e().t("Back")))]),K("click",t,()=>{rt("/workspace/tools")}),$(l,t)},$$slots:{default:!0}})}o(j);var B=u(j,2),Ie=s(B);{let r=T(()=>(e(),i(()=>e().t("e.g. My Tools"))));S(Ie,{get content(){return d(r)},placement:"top-start",children:(l,c)=>{var t=ft();Q(t),k((a,n)=>{C(t,"placeholder",a),C(t,"aria-label",n)},[()=>(e(),i(()=>e().t("Tool Name"))),()=>(e(),i(()=>e().t("Tool Name")))]),V(t,y),$(l,t)},$$slots:{default:!0}})}o(B);var ie=u(B,2),R=s(ie),le=s(R);ct(le,{strokeWidth:"2.5",className:"size-3.5"});var ne=u(le,2),Ae=s(ne,!0);o(ne),o(R),o(ie),o(W);var de=u(W,2),ue=s(de);{var De=r=>{var l=vt(),c=s(l,!0);o(l),k(()=>f(c,x())),$(r,l)},Ne=r=>{{let l=T(()=>(e(),i(()=>e().t("e.g. my_tools"))));S(r,{className:"w-full",get content(){return d(l)},placement:"top-start",children:(c,t)=>{var a=pt();Q(a),k((n,m)=>{C(a,"placeholder",n),C(a,"aria-label",m),a.disabled=g()},[()=>(e(),i(()=>e().t("Tool ID"))),()=>(e(),i(()=>e().t("Tool ID")))]),V(a,x),$(c,a)},$$slots:{default:!0}})}};Ze(ue,r=>{g()?r(De):r(Ne,-1)})}var Ge=u(ue,2);{let r=T(()=>(e(),i(()=>e().t("e.g. Tools for performing various operations"))));S(Ge,{className:"w-full self-center items-center flex",get content(){return d(r)},placement:"top-start",children:(l,c)=>{var t=_t();Q(t),k((a,n)=>{C(t,"placeholder",a),C(t,"aria-label",n)},[()=>(e(),i(()=>e().t("Tool Description"))),()=>(e(),i(()=>e().t("Tool Description")))]),V(t,()=>b().description,a=>b(b().description=a,!0)),$(l,t)},$$slots:{default:!0}})}o(de),o(U);var Y=u(U,2),Se=s(Y);ye(lt(Se,{get value(){return w()},lang:"python",boilerplate:Ee,onChange:r=>{if(_(A,r),!g()){const l=ot(r);l.title&&!y()&&(y(it(l.title)),x(X(l.title))),l.description&&!b().description&&b({...b(),description:l.description})}},onSave:async()=>{d(P)&&d(P).requestSubmit()},$$legacy:!0}),r=>_(D,r),()=>d(D)),o(Y);var ce=u(Y,2),L=s(ce),me=s(L),O=s(me),Me=s(O,!0);o(O);var fe=u(O),ve=u(fe,3),Fe=s(ve,!0);o(ve),o(me),o(L);var pe=u(L,2),He=s(pe,!0);o(pe),o(ce),o(oe),o(N),ye(N,r=>_(P,r),()=>d(P)),o(se),o(H);var Ue=u(H,2);nt(Ue,{get show(){return d(M)},set show(r){_(M,r)},$$events:{confirm:()=>{te()}},children:(r,l)=>{var c=ht(),t=s(c),a=s(t),n=s(a,!0);o(a);var m=u(a,2),z=s(m),We=s(z,!0);o(z);var _e=u(z,2),je=s(_e,!0);o(_e),o(m),o(t);var he=u(t,2),Be=s(he,!0);o(he),o(c),k((Re,Ye,Le,Oe)=>{f(n,Re),f(We,Ye),f(je,Le),f(Be,Oe)},[()=>(e(),i(()=>e().t("Please carefully review the following warnings:"))),()=>(e(),i(()=>e().t("Tools have a function calling system that allows arbitrary code execution."))),()=>(e(),i(()=>e().t("Do not install tools from sources you do not fully trust."))),()=>(e(),i(()=>e().t("I acknowledge that I have read and I understand the implications of my action. I am aware of the risks associated with executing arbitrary code and I have verified the trustworthiness of the source.")))]),$(r,c)},$$slots:{default:!0},$$legacy:!0}),k((r,l,c,t,a)=>{f(Ae,r),f(Me,l),f(fe,` ${c??""} `),f(Fe,t),f(He,a)},[()=>(e(),i(()=>e().t("Access"))),()=>(e(),i(()=>e().t("Warning:"))),()=>(e(),i(()=>e().t("Tools are a function calling system with arbitrary code execution"))),()=>(e(),i(()=>e().t("don't install random tools from sources you don't trust."))),()=>(e(),i(()=>e().t("Save")))]),K("click",R,()=>{_(F,!0)}),K("submit",N,et(()=>{g()?te():_(M,!0)})),$(we,re),Ve(),ke()}export{Ut as T};
//# sourceMappingURL=BtjYsB1n.js.map
