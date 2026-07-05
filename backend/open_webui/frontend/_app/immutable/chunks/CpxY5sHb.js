import{g as ye,s as ge,q as pe,p as ve,a as xe,b as Te,_ as c,c as ut,d as be,l as st,j as we,i as _e,y as De,u as Ce}from"./BcSOeY0I.js";import{c as Yt,g as Ot,d as j}from"./BC4znSyB.js";import{d as Se}from"./DfIywdCw.js";import{s as vt}from"./BX5WB7ra.js";import{t as Ee,m as Me,a as Ie,i as Ae,b as jt,c as qt,d as Le,e as Fe,f as Ye,g as Oe,h as We,j as Ve,k as ze,l as Ut,n as Zt,o as Qt,s as Kt,p as Jt}from"./CrATNjtF.js";import{l as Pe}from"./CrKpsNbG.js";function Re(t){return t}var Tt=1,St=2,Mt=3,xt=4,te=1e-6;function Ne(t){return"translate("+t+",0)"}function Be(t){return"translate(0,"+t+")"}function $e(t){return r=>+t(r)}function He(t,r){return r=Math.max(0,t.bandwidth()-r*2)/2,t.round()&&(r=Math.round(r)),s=>+t(s)+r}function Ge(){return!this.__axis}function ne(t,r){var s=[],n=null,a=null,h=6,u=6,p=3,D=typeof window<"u"&&window.devicePixelRatio>1?0:.5,E=t===Tt||t===xt?-1:1,g=t===xt||t===St?"x":"y",F=t===Tt||t===Mt?Ne:Be;function C(w){var H=n??(r.ticks?r.ticks.apply(r,s):r.domain()),I=a??(r.tickFormat?r.tickFormat.apply(r,s):Re),_=Math.max(h,0)+p,M=r.range(),O=+M[0]+D,W=+M[M.length-1]+D,P=(r.bandwidth?He:$e)(r.copy(),D),R=w.selection?w.selection():w,G=R.selectAll(".domain").data([null]),z=R.selectAll(".tick").data(H,r).order(),N=z.exit(),k=z.enter().append("g").attr("class","tick"),T=z.select("line"),b=z.select("text");G=G.merge(G.enter().insert("path",".tick").attr("class","domain").attr("stroke","currentColor")),z=z.merge(k),T=T.merge(k.append("line").attr("stroke","currentColor").attr(g+"2",E*h)),b=b.merge(k.append("text").attr("fill","currentColor").attr(g,E*_).attr("dy",t===Tt?"0em":t===Mt?"0.71em":"0.32em")),w!==R&&(G=G.transition(w),z=z.transition(w),T=T.transition(w),b=b.transition(w),N=N.transition(w).attr("opacity",te).attr("transform",function(y){return isFinite(y=P(y))?F(y+D):this.getAttribute("transform")}),k.attr("opacity",te).attr("transform",function(y){var m=this.parentNode.__axis;return F((m&&isFinite(m=m(y))?m:P(y))+D)})),N.remove(),G.attr("d",t===xt||t===St?u?"M"+E*u+","+O+"H"+D+"V"+W+"H"+E*u:"M"+D+","+O+"V"+W:u?"M"+O+","+E*u+"V"+D+"H"+W+"V"+E*u:"M"+O+","+D+"H"+W),z.attr("opacity",1).attr("transform",function(y){return F(P(y)+D)}),T.attr(g+"2",E*h),b.attr(g,E*_).text(I),R.filter(Ge).attr("fill","none").attr("font-size",10).attr("font-family","sans-serif").attr("text-anchor",t===St?"start":t===xt?"end":"middle"),R.each(function(){this.__axis=P})}return C.scale=function(w){return arguments.length?(r=w,C):r},C.ticks=function(){return s=Array.from(arguments),C},C.tickArguments=function(w){return arguments.length?(s=w==null?[]:Array.from(w),C):s.slice()},C.tickValues=function(w){return arguments.length?(n=w==null?null:Array.from(w),C):n&&n.slice()},C.tickFormat=function(w){return arguments.length?(a=w,C):a},C.tickSize=function(w){return arguments.length?(h=u=+w,C):h},C.tickSizeInner=function(w){return arguments.length?(h=+w,C):h},C.tickSizeOuter=function(w){return arguments.length?(u=+w,C):u},C.tickPadding=function(w){return arguments.length?(p=+w,C):p},C.offset=function(w){return arguments.length?(D=+w,C):D},C}function Xe(t){return ne(Tt,t)}function je(t){return ne(Mt,t)}var se={exports:{}};(function(t,r){(function(s,n){t.exports=n()})(Yt,function(){var s="day";return function(n,a,h){var u=function(E){return E.add(4-E.isoWeekday(),s)},p=a.prototype;p.isoWeekYear=function(){return u(this).year()},p.isoWeek=function(E){if(!this.$utils().u(E))return this.add(7*(E-this.isoWeek()),s);var g,F,C,w,H=u(this),I=(g=this.isoWeekYear(),F=this.$u,C=(F?h.utc:h)().year(g).startOf("year"),w=4-C.isoWeekday(),C.isoWeekday()>4&&(w+=7),C.add(w,s));return H.diff(I,"week")+1},p.isoWeekday=function(E){return this.$utils().u(E)?this.day()||7:this.day(this.day()%7?E:E-7)};var D=p.startOf;p.startOf=function(E,g){var F=this.$utils(),C=!!F.u(g)||g;return F.p(E)==="isoweek"?C?this.date(this.date()-(this.isoWeekday()-1)).startOf("day"):this.date(this.date()-1-(this.isoWeekday()-1)+7).endOf("day"):D.bind(this)(E,g)}}})})(se);var qe=se.exports;const Ue=Ot(qe);var ae={exports:{}};(function(t,r){(function(s,n){t.exports=n()})(Yt,function(){var s={LTS:"h:mm:ss A",LT:"h:mm A",L:"MM/DD/YYYY",LL:"MMMM D, YYYY",LLL:"MMMM D, YYYY h:mm A",LLLL:"dddd, MMMM D, YYYY h:mm A"},n=/(\[[^[]*\])|([-_:/.,()\s]+)|(A|a|Q|YYYY|YY?|ww?|MM?M?M?|Do|DD?|hh?|HH?|mm?|ss?|S{1,3}|z|ZZ?)/g,a=/\d/,h=/\d\d/,u=/\d\d?/,p=/\d*[^-_:/,()\s\d]+/,D={},E=function(_){return(_=+_)+(_>68?1900:2e3)},g=function(_){return function(M){this[_]=+M}},F=[/[+-]\d\d:?(\d\d)?|Z/,function(_){(this.zone||(this.zone={})).offset=function(M){if(!M||M==="Z")return 0;var O=M.match(/([+-]|\d\d)/g),W=60*O[1]+(+O[2]||0);return W===0?0:O[0]==="+"?-W:W}(_)}],C=function(_){var M=D[_];return M&&(M.indexOf?M:M.s.concat(M.f))},w=function(_,M){var O,W=D.meridiem;if(W){for(var P=1;P<=24;P+=1)if(_.indexOf(W(P,0,M))>-1){O=P>12;break}}else O=_===(M?"pm":"PM");return O},H={A:[p,function(_){this.afternoon=w(_,!1)}],a:[p,function(_){this.afternoon=w(_,!0)}],Q:[a,function(_){this.month=3*(_-1)+1}],S:[a,function(_){this.milliseconds=100*+_}],SS:[h,function(_){this.milliseconds=10*+_}],SSS:[/\d{3}/,function(_){this.milliseconds=+_}],s:[u,g("seconds")],ss:[u,g("seconds")],m:[u,g("minutes")],mm:[u,g("minutes")],H:[u,g("hours")],h:[u,g("hours")],HH:[u,g("hours")],hh:[u,g("hours")],D:[u,g("day")],DD:[h,g("day")],Do:[p,function(_){var M=D.ordinal,O=_.match(/\d+/);if(this.day=O[0],M)for(var W=1;W<=31;W+=1)M(W).replace(/\[|\]/g,"")===_&&(this.day=W)}],w:[u,g("week")],ww:[h,g("week")],M:[u,g("month")],MM:[h,g("month")],MMM:[p,function(_){var M=C("months"),O=(C("monthsShort")||M.map(function(W){return W.slice(0,3)})).indexOf(_)+1;if(O<1)throw new Error;this.month=O%12||O}],MMMM:[p,function(_){var M=C("months").indexOf(_)+1;if(M<1)throw new Error;this.month=M%12||M}],Y:[/[+-]?\d+/,g("year")],YY:[h,function(_){this.year=E(_)}],YYYY:[/\d{4}/,g("year")],Z:F,ZZ:F};function I(_){var M,O;M=_,O=D&&D.formats;for(var W=(_=M.replace(/(\[[^\]]+])|(LTS?|l{1,4}|L{1,4})/g,function(T,b,y){var m=y&&y.toUpperCase();return b||O[y]||s[y]||O[m].replace(/(\[[^\]]+])|(MMMM|MM|DD|dddd)/g,function(o,l,d){return l||d.slice(1)})})).match(n),P=W.length,R=0;R<P;R+=1){var G=W[R],z=H[G],N=z&&z[0],k=z&&z[1];W[R]=k?{regex:N,parser:k}:G.replace(/^\[|\]$/g,"")}return function(T){for(var b={},y=0,m=0;y<P;y+=1){var o=W[y];if(typeof o=="string")m+=o.length;else{var l=o.regex,d=o.parser,f=T.slice(m),x=l.exec(f)[0];d.call(b,x),T=T.replace(x,"")}}return function(i){var V=i.afternoon;if(V!==void 0){var e=i.hours;V?e<12&&(i.hours+=12):e===12&&(i.hours=0),delete i.afternoon}}(b),b}}return function(_,M,O){O.p.customParseFormat=!0,_&&_.parseTwoDigitYear&&(E=_.parseTwoDigitYear);var W=M.prototype,P=W.parse;W.parse=function(R){var G=R.date,z=R.utc,N=R.args;this.$u=z;var k=N[1];if(typeof k=="string"){var T=N[2]===!0,b=N[3]===!0,y=T||b,m=N[2];b&&(m=N[2]),D=this.$locale(),!T&&m&&(D=O.Ls[m]),this.$d=function(f,x,i,V){try{if(["x","X"].indexOf(x)>-1)return new Date((x==="X"?1e3:1)*f);var e=I(x)(f),v=e.year,Y=e.month,L=e.day,A=e.hours,X=e.minutes,S=e.seconds,Q=e.milliseconds,rt=e.zone,ot=e.week,ht=new Date,mt=L||(v||Y?1:ht.getDate()),ct=v||ht.getFullYear(),B=0;v&&!Y||(B=Y>0?Y-1:ht.getMonth());var Z,q=A||0,nt=X||0,K=S||0,it=Q||0;return rt?new Date(Date.UTC(ct,B,mt,q,nt,K,it+60*rt.offset*1e3)):i?new Date(Date.UTC(ct,B,mt,q,nt,K,it)):(Z=new Date(ct,B,mt,q,nt,K,it),ot&&(Z=V(Z).week(ot).toDate()),Z)}catch{return new Date("")}}(G,k,z,O),this.init(),m&&m!==!0&&(this.$L=this.locale(m).$L),y&&G!=this.format(k)&&(this.$d=new Date("")),D={}}else if(k instanceof Array)for(var o=k.length,l=1;l<=o;l+=1){N[1]=k[l-1];var d=O.apply(this,N);if(d.isValid()){this.$d=d.$d,this.$L=d.$L,this.init();break}l===o&&(this.$d=new Date(""))}else P.call(this,R)}}})})(ae);var Ze=ae.exports;const Qe=Ot(Ze);var oe={exports:{}};(function(t,r){(function(s,n){t.exports=n()})(Yt,function(){return function(s,n){var a=n.prototype,h=a.format;a.format=function(u){var p=this,D=this.$locale();if(!this.isValid())return h.bind(this)(u);var E=this.$utils(),g=(u||"YYYY-MM-DDTHH:mm:ssZ").replace(/\[([^\]]+)]|Q|wo|ww|w|WW|W|zzz|z|gggg|GGGG|Do|X|x|k{1,2}|S/g,function(F){switch(F){case"Q":return Math.ceil((p.$M+1)/3);case"Do":return D.ordinal(p.$D);case"gggg":return p.weekYear();case"GGGG":return p.isoWeekYear();case"wo":return D.ordinal(p.week(),"W");case"w":case"ww":return E.s(p.week(),F==="w"?1:2,"0");case"W":case"WW":return E.s(p.isoWeek(),F==="W"?1:2,"0");case"k":case"kk":return E.s(String(p.$H===0?24:p.$H),F==="k"?1:2,"0");case"X":return Math.floor(p.$d.getTime()/1e3);case"x":return p.$d.getTime();case"z":return"["+p.offsetName()+"]";case"zzz":return"["+p.offsetName("long")+"]";default:return F}});return h.bind(this)(g)}}})})(oe);var Ke=oe.exports;const Je=Ot(Ke);var It=function(){var t=c(function(m,o,l,d){for(l=l||{},d=m.length;d--;l[m[d]]=o);return l},"o"),r=[6,8,10,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,33,35,36,38,40],s=[1,26],n=[1,27],a=[1,28],h=[1,29],u=[1,30],p=[1,31],D=[1,32],E=[1,33],g=[1,34],F=[1,9],C=[1,10],w=[1,11],H=[1,12],I=[1,13],_=[1,14],M=[1,15],O=[1,16],W=[1,19],P=[1,20],R=[1,21],G=[1,22],z=[1,23],N=[1,25],k=[1,35],T={trace:c(function(){},"trace"),yy:{},symbols_:{error:2,start:3,gantt:4,document:5,EOF:6,line:7,SPACE:8,statement:9,NL:10,weekday:11,weekday_monday:12,weekday_tuesday:13,weekday_wednesday:14,weekday_thursday:15,weekday_friday:16,weekday_saturday:17,weekday_sunday:18,weekend:19,weekend_friday:20,weekend_saturday:21,dateFormat:22,inclusiveEndDates:23,topAxis:24,axisFormat:25,tickInterval:26,excludes:27,includes:28,todayMarker:29,title:30,acc_title:31,acc_title_value:32,acc_descr:33,acc_descr_value:34,acc_descr_multiline_value:35,section:36,clickStatement:37,taskTxt:38,taskData:39,click:40,callbackname:41,callbackargs:42,href:43,clickStatementDebug:44,$accept:0,$end:1},terminals_:{2:"error",4:"gantt",6:"EOF",8:"SPACE",10:"NL",12:"weekday_monday",13:"weekday_tuesday",14:"weekday_wednesday",15:"weekday_thursday",16:"weekday_friday",17:"weekday_saturday",18:"weekday_sunday",20:"weekend_friday",21:"weekend_saturday",22:"dateFormat",23:"inclusiveEndDates",24:"topAxis",25:"axisFormat",26:"tickInterval",27:"excludes",28:"includes",29:"todayMarker",30:"title",31:"acc_title",32:"acc_title_value",33:"acc_descr",34:"acc_descr_value",35:"acc_descr_multiline_value",36:"section",38:"taskTxt",39:"taskData",40:"click",41:"callbackname",42:"callbackargs",43:"href"},productions_:[0,[3,3],[5,0],[5,2],[7,2],[7,1],[7,1],[7,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[19,1],[19,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,2],[9,2],[9,1],[9,1],[9,1],[9,2],[37,2],[37,3],[37,3],[37,4],[37,3],[37,4],[37,2],[44,2],[44,3],[44,3],[44,4],[44,3],[44,4],[44,2]],performAction:c(function(o,l,d,f,x,i,V){var e=i.length-1;switch(x){case 1:return i[e-1];case 2:this.$=[];break;case 3:i[e-1].push(i[e]),this.$=i[e-1];break;case 4:case 5:this.$=i[e];break;case 6:case 7:this.$=[];break;case 8:f.setWeekday("monday");break;case 9:f.setWeekday("tuesday");break;case 10:f.setWeekday("wednesday");break;case 11:f.setWeekday("thursday");break;case 12:f.setWeekday("friday");break;case 13:f.setWeekday("saturday");break;case 14:f.setWeekday("sunday");break;case 15:f.setWeekend("friday");break;case 16:f.setWeekend("saturday");break;case 17:f.setDateFormat(i[e].substr(11)),this.$=i[e].substr(11);break;case 18:f.enableInclusiveEndDates(),this.$=i[e].substr(18);break;case 19:f.TopAxis(),this.$=i[e].substr(8);break;case 20:f.setAxisFormat(i[e].substr(11)),this.$=i[e].substr(11);break;case 21:f.setTickInterval(i[e].substr(13)),this.$=i[e].substr(13);break;case 22:f.setExcludes(i[e].substr(9)),this.$=i[e].substr(9);break;case 23:f.setIncludes(i[e].substr(9)),this.$=i[e].substr(9);break;case 24:f.setTodayMarker(i[e].substr(12)),this.$=i[e].substr(12);break;case 27:f.setDiagramTitle(i[e].substr(6)),this.$=i[e].substr(6);break;case 28:this.$=i[e].trim(),f.setAccTitle(this.$);break;case 29:case 30:this.$=i[e].trim(),f.setAccDescription(this.$);break;case 31:f.addSection(i[e].substr(8)),this.$=i[e].substr(8);break;case 33:f.addTask(i[e-1],i[e]),this.$="task";break;case 34:this.$=i[e-1],f.setClickEvent(i[e-1],i[e],null);break;case 35:this.$=i[e-2],f.setClickEvent(i[e-2],i[e-1],i[e]);break;case 36:this.$=i[e-2],f.setClickEvent(i[e-2],i[e-1],null),f.setLink(i[e-2],i[e]);break;case 37:this.$=i[e-3],f.setClickEvent(i[e-3],i[e-2],i[e-1]),f.setLink(i[e-3],i[e]);break;case 38:this.$=i[e-2],f.setClickEvent(i[e-2],i[e],null),f.setLink(i[e-2],i[e-1]);break;case 39:this.$=i[e-3],f.setClickEvent(i[e-3],i[e-1],i[e]),f.setLink(i[e-3],i[e-2]);break;case 40:this.$=i[e-1],f.setLink(i[e-1],i[e]);break;case 41:case 47:this.$=i[e-1]+" "+i[e];break;case 42:case 43:case 45:this.$=i[e-2]+" "+i[e-1]+" "+i[e];break;case 44:case 46:this.$=i[e-3]+" "+i[e-2]+" "+i[e-1]+" "+i[e];break}},"anonymous"),table:[{3:1,4:[1,2]},{1:[3]},t(r,[2,2],{5:3}),{6:[1,4],7:5,8:[1,6],9:7,10:[1,8],11:17,12:s,13:n,14:a,15:h,16:u,17:p,18:D,19:18,20:E,21:g,22:F,23:C,24:w,25:H,26:I,27:_,28:M,29:O,30:W,31:P,33:R,35:G,36:z,37:24,38:N,40:k},t(r,[2,7],{1:[2,1]}),t(r,[2,3]),{9:36,11:17,12:s,13:n,14:a,15:h,16:u,17:p,18:D,19:18,20:E,21:g,22:F,23:C,24:w,25:H,26:I,27:_,28:M,29:O,30:W,31:P,33:R,35:G,36:z,37:24,38:N,40:k},t(r,[2,5]),t(r,[2,6]),t(r,[2,17]),t(r,[2,18]),t(r,[2,19]),t(r,[2,20]),t(r,[2,21]),t(r,[2,22]),t(r,[2,23]),t(r,[2,24]),t(r,[2,25]),t(r,[2,26]),t(r,[2,27]),{32:[1,37]},{34:[1,38]},t(r,[2,30]),t(r,[2,31]),t(r,[2,32]),{39:[1,39]},t(r,[2,8]),t(r,[2,9]),t(r,[2,10]),t(r,[2,11]),t(r,[2,12]),t(r,[2,13]),t(r,[2,14]),t(r,[2,15]),t(r,[2,16]),{41:[1,40],43:[1,41]},t(r,[2,4]),t(r,[2,28]),t(r,[2,29]),t(r,[2,33]),t(r,[2,34],{42:[1,42],43:[1,43]}),t(r,[2,40],{41:[1,44]}),t(r,[2,35],{43:[1,45]}),t(r,[2,36]),t(r,[2,38],{42:[1,46]}),t(r,[2,37]),t(r,[2,39])],defaultActions:{},parseError:c(function(o,l){if(l.recoverable)this.trace(o);else{var d=new Error(o);throw d.hash=l,d}},"parseError"),parse:c(function(o){var l=this,d=[0],f=[],x=[null],i=[],V=this.table,e="",v=0,Y=0,L=2,A=1,X=i.slice.call(arguments,1),S=Object.create(this.lexer),Q={yy:{}};for(var rt in this.yy)Object.prototype.hasOwnProperty.call(this.yy,rt)&&(Q.yy[rt]=this.yy[rt]);S.setInput(o,Q.yy),Q.yy.lexer=S,Q.yy.parser=this,typeof S.yylloc>"u"&&(S.yylloc={});var ot=S.yylloc;i.push(ot);var ht=S.options&&S.options.ranges;typeof Q.yy.parseError=="function"?this.parseError=Q.yy.parseError:this.parseError=Object.getPrototypeOf(this).parseError;function mt(U){d.length=d.length-2*U,x.length=x.length-U,i.length=i.length-U}c(mt,"popStack");function ct(){var U;return U=f.pop()||S.lex()||A,typeof U!="number"&&(U instanceof Array&&(f=U,U=f.pop()),U=l.symbols_[U]||U),U}c(ct,"lex");for(var B,Z,q,nt,K={},it,J,Xt,pt;;){if(Z=d[d.length-1],this.defaultActions[Z]?q=this.defaultActions[Z]:((B===null||typeof B>"u")&&(B=ct()),q=V[Z]&&V[Z][B]),typeof q>"u"||!q.length||!q[0]){var Ct="";pt=[];for(it in V[Z])this.terminals_[it]&&it>L&&pt.push("'"+this.terminals_[it]+"'");S.showPosition?Ct="Parse error on line "+(v+1)+`:
`+S.showPosition()+`
Expecting `+pt.join(", ")+", got '"+(this.terminals_[B]||B)+"'":Ct="Parse error on line "+(v+1)+": Unexpected "+(B==A?"end of input":"'"+(this.terminals_[B]||B)+"'"),this.parseError(Ct,{text:S.match,token:this.terminals_[B]||B,line:S.yylineno,loc:ot,expected:pt})}if(q[0]instanceof Array&&q.length>1)throw new Error("Parse Error: multiple actions possible at state: "+Z+", token: "+B);switch(q[0]){case 1:d.push(B),x.push(S.yytext),i.push(S.yylloc),d.push(q[1]),B=null,Y=S.yyleng,e=S.yytext,v=S.yylineno,ot=S.yylloc;break;case 2:if(J=this.productions_[q[1]][1],K.$=x[x.length-J],K._$={first_line:i[i.length-(J||1)].first_line,last_line:i[i.length-1].last_line,first_column:i[i.length-(J||1)].first_column,last_column:i[i.length-1].last_column},ht&&(K._$.range=[i[i.length-(J||1)].range[0],i[i.length-1].range[1]]),nt=this.performAction.apply(K,[e,Y,v,Q.yy,q[1],x,i].concat(X)),typeof nt<"u")return nt;J&&(d=d.slice(0,-1*J*2),x=x.slice(0,-1*J),i=i.slice(0,-1*J)),d.push(this.productions_[q[1]][0]),x.push(K.$),i.push(K._$),Xt=V[d[d.length-2]][d[d.length-1]],d.push(Xt);break;case 3:return!0}}return!0},"parse")},b=function(){var m={EOF:1,parseError:c(function(l,d){if(this.yy.parser)this.yy.parser.parseError(l,d);else throw new Error(l)},"parseError"),setInput:c(function(o,l){return this.yy=l||this.yy||{},this._input=o,this._more=this._backtrack=this.done=!1,this.yylineno=this.yyleng=0,this.yytext=this.matched=this.match="",this.conditionStack=["INITIAL"],this.yylloc={first_line:1,first_column:0,last_line:1,last_column:0},this.options.ranges&&(this.yylloc.range=[0,0]),this.offset=0,this},"setInput"),input:c(function(){var o=this._input[0];this.yytext+=o,this.yyleng++,this.offset++,this.match+=o,this.matched+=o;var l=o.match(/(?:\r\n?|\n).*/g);return l?(this.yylineno++,this.yylloc.last_line++):this.yylloc.last_column++,this.options.ranges&&this.yylloc.range[1]++,this._input=this._input.slice(1),o},"input"),unput:c(function(o){var l=o.length,d=o.split(/(?:\r\n?|\n)/g);this._input=o+this._input,this.yytext=this.yytext.substr(0,this.yytext.length-l),this.offset-=l;var f=this.match.split(/(?:\r\n?|\n)/g);this.match=this.match.substr(0,this.match.length-1),this.matched=this.matched.substr(0,this.matched.length-1),d.length-1&&(this.yylineno-=d.length-1);var x=this.yylloc.range;return this.yylloc={first_line:this.yylloc.first_line,last_line:this.yylineno+1,first_column:this.yylloc.first_column,last_column:d?(d.length===f.length?this.yylloc.first_column:0)+f[f.length-d.length].length-d[0].length:this.yylloc.first_column-l},this.options.ranges&&(this.yylloc.range=[x[0],x[0]+this.yyleng-l]),this.yyleng=this.yytext.length,this},"unput"),more:c(function(){return this._more=!0,this},"more"),reject:c(function(){if(this.options.backtrack_lexer)this._backtrack=!0;else return this.parseError("Lexical error on line "+(this.yylineno+1)+`. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
`+this.showPosition(),{text:"",token:null,line:this.yylineno});return this},"reject"),less:c(function(o){this.unput(this.match.slice(o))},"less"),pastInput:c(function(){var o=this.matched.substr(0,this.matched.length-this.match.length);return(o.length>20?"...":"")+o.substr(-20).replace(/\n/g,"")},"pastInput"),upcomingInput:c(function(){var o=this.match;return o.length<20&&(o+=this._input.substr(0,20-o.length)),(o.substr(0,20)+(o.length>20?"...":"")).replace(/\n/g,"")},"upcomingInput"),showPosition:c(function(){var o=this.pastInput(),l=new Array(o.length+1).join("-");return o+this.upcomingInput()+`
`+l+"^"},"showPosition"),test_match:c(function(o,l){var d,f,x;if(this.options.backtrack_lexer&&(x={yylineno:this.yylineno,yylloc:{first_line:this.yylloc.first_line,last_line:this.last_line,first_column:this.yylloc.first_column,last_column:this.yylloc.last_column},yytext:this.yytext,match:this.match,matches:this.matches,matched:this.matched,yyleng:this.yyleng,offset:this.offset,_more:this._more,_input:this._input,yy:this.yy,conditionStack:this.conditionStack.slice(0),done:this.done},this.options.ranges&&(x.yylloc.range=this.yylloc.range.slice(0))),f=o[0].match(/(?:\r\n?|\n).*/g),f&&(this.yylineno+=f.length),this.yylloc={first_line:this.yylloc.last_line,last_line:this.yylineno+1,first_column:this.yylloc.last_column,last_column:f?f[f.length-1].length-f[f.length-1].match(/\r?\n?/)[0].length:this.yylloc.last_column+o[0].length},this.yytext+=o[0],this.match+=o[0],this.matches=o,this.yyleng=this.yytext.length,this.options.ranges&&(this.yylloc.range=[this.offset,this.offset+=this.yyleng]),this._more=!1,this._backtrack=!1,this._input=this._input.slice(o[0].length),this.matched+=o[0],d=this.performAction.call(this,this.yy,this,l,this.conditionStack[this.conditionStack.length-1]),this.done&&this._input&&(this.done=!1),d)return d;if(this._backtrack){for(var i in x)this[i]=x[i];return!1}return!1},"test_match"),next:c(function(){if(this.done)return this.EOF;this._input||(this.done=!0);var o,l,d,f;this._more||(this.yytext="",this.match="");for(var x=this._currentRules(),i=0;i<x.length;i++)if(d=this._input.match(this.rules[x[i]]),d&&(!l||d[0].length>l[0].length)){if(l=d,f=i,this.options.backtrack_lexer){if(o=this.test_match(d,x[i]),o!==!1)return o;if(this._backtrack){l=!1;continue}else return!1}else if(!this.options.flex)break}return l?(o=this.test_match(l,x[f]),o!==!1?o:!1):this._input===""?this.EOF:this.parseError("Lexical error on line "+(this.yylineno+1)+`. Unrecognized text.
`+this.showPosition(),{text:"",token:null,line:this.yylineno})},"next"),lex:c(function(){var l=this.next();return l||this.lex()},"lex"),begin:c(function(l){this.conditionStack.push(l)},"begin"),popState:c(function(){var l=this.conditionStack.length-1;return l>0?this.conditionStack.pop():this.conditionStack[0]},"popState"),_currentRules:c(function(){return this.conditionStack.length&&this.conditionStack[this.conditionStack.length-1]?this.conditions[this.conditionStack[this.conditionStack.length-1]].rules:this.conditions.INITIAL.rules},"_currentRules"),topState:c(function(l){return l=this.conditionStack.length-1-Math.abs(l||0),l>=0?this.conditionStack[l]:"INITIAL"},"topState"),pushState:c(function(l){this.begin(l)},"pushState"),stateStackSize:c(function(){return this.conditionStack.length},"stateStackSize"),options:{"case-insensitive":!0},performAction:c(function(l,d,f,x){switch(f){case 0:return this.begin("open_directive"),"open_directive";case 1:return this.begin("acc_title"),31;case 2:return this.popState(),"acc_title_value";case 3:return this.begin("acc_descr"),33;case 4:return this.popState(),"acc_descr_value";case 5:this.begin("acc_descr_multiline");break;case 6:this.popState();break;case 7:return"acc_descr_multiline_value";case 8:break;case 9:break;case 10:break;case 11:return 10;case 12:break;case 13:break;case 14:this.begin("href");break;case 15:this.popState();break;case 16:return 43;case 17:this.begin("callbackname");break;case 18:this.popState();break;case 19:this.popState(),this.begin("callbackargs");break;case 20:return 41;case 21:this.popState();break;case 22:return 42;case 23:this.begin("click");break;case 24:this.popState();break;case 25:return 40;case 26:return 4;case 27:return 22;case 28:return 23;case 29:return 24;case 30:return 25;case 31:return 26;case 32:return 28;case 33:return 27;case 34:return 29;case 35:return 12;case 36:return 13;case 37:return 14;case 38:return 15;case 39:return 16;case 40:return 17;case 41:return 18;case 42:return 20;case 43:return 21;case 44:return"date";case 45:return 30;case 46:return"accDescription";case 47:return 36;case 48:return 38;case 49:return 39;case 50:return":";case 51:return 6;case 52:return"INVALID"}},"anonymous"),rules:[/^(?:%%\{)/i,/^(?:accTitle\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*\{\s*)/i,/^(?:[\}])/i,/^(?:[^\}]*)/i,/^(?:%%(?!\{)*[^\n]*)/i,/^(?:[^\}]%%*[^\n]*)/i,/^(?:%%*[^\n]*[\n]*)/i,/^(?:[\n]+)/i,/^(?:\s+)/i,/^(?:%[^\n]*)/i,/^(?:href[\s]+["])/i,/^(?:["])/i,/^(?:[^"]*)/i,/^(?:call[\s]+)/i,/^(?:\([\s]*\))/i,/^(?:\()/i,/^(?:[^(]*)/i,/^(?:\))/i,/^(?:[^)]*)/i,/^(?:click[\s]+)/i,/^(?:[\s\n])/i,/^(?:[^\s\n]*)/i,/^(?:gantt\b)/i,/^(?:dateFormat\s[^#\n;]+)/i,/^(?:inclusiveEndDates\b)/i,/^(?:topAxis\b)/i,/^(?:axisFormat\s[^#\n;]+)/i,/^(?:tickInterval\s[^#\n;]+)/i,/^(?:includes\s[^#\n;]+)/i,/^(?:excludes\s[^#\n;]+)/i,/^(?:todayMarker\s[^\n;]+)/i,/^(?:weekday\s+monday\b)/i,/^(?:weekday\s+tuesday\b)/i,/^(?:weekday\s+wednesday\b)/i,/^(?:weekday\s+thursday\b)/i,/^(?:weekday\s+friday\b)/i,/^(?:weekday\s+saturday\b)/i,/^(?:weekday\s+sunday\b)/i,/^(?:weekend\s+friday\b)/i,/^(?:weekend\s+saturday\b)/i,/^(?:\d\d\d\d-\d\d-\d\d\b)/i,/^(?:title\s[^\n]+)/i,/^(?:accDescription\s[^#\n;]+)/i,/^(?:section\s[^\n]+)/i,/^(?:[^:\n]+)/i,/^(?::[^#\n;]+)/i,/^(?::)/i,/^(?:$)/i,/^(?:.)/i],conditions:{acc_descr_multiline:{rules:[6,7],inclusive:!1},acc_descr:{rules:[4],inclusive:!1},acc_title:{rules:[2],inclusive:!1},callbackargs:{rules:[21,22],inclusive:!1},callbackname:{rules:[18,19,20],inclusive:!1},href:{rules:[15,16],inclusive:!1},click:{rules:[24,25],inclusive:!1},INITIAL:{rules:[0,1,3,5,8,9,10,11,12,13,14,17,23,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52],inclusive:!0}}};return m}();T.lexer=b;function y(){this.yy={}}return c(y,"Parser"),y.prototype=T,T.Parser=y,new y}();It.parser=It;var tr=It;j.extend(Ue);j.extend(Qe);j.extend(Je);var ee={friday:5,saturday:6},tt="",Wt="",Vt=void 0,zt="",kt=[],yt=[],Pt=new Map,Rt=[],_t=[],ft="",Nt="",ce=["active","done","crit","milestone","vert"],Bt=[],lt="",gt=!1,$t=!1,Ht="sunday",Dt="saturday",At=0,er=c(function(){Rt=[],_t=[],ft="",Bt=[],bt=0,Ft=void 0,wt=void 0,$=[],tt="",Wt="",Nt="",Vt=void 0,zt="",kt=[],yt=[],gt=!1,$t=!1,At=0,Pt=new Map,lt="",De(),Ht="sunday",Dt="saturday"},"clear"),rr=c(function(t){lt=t},"setDiagramId"),ir=c(function(t){Wt=t},"setAxisFormat"),nr=c(function(){return Wt},"getAxisFormat"),sr=c(function(t){Vt=t},"setTickInterval"),ar=c(function(){return Vt},"getTickInterval"),or=c(function(t){zt=t},"setTodayMarker"),cr=c(function(){return zt},"getTodayMarker"),lr=c(function(t){tt=t},"setDateFormat"),ur=c(function(){gt=!0},"enableInclusiveEndDates"),dr=c(function(){return gt},"endDatesAreInclusive"),fr=c(function(){$t=!0},"enableTopAxis"),hr=c(function(){return $t},"topAxisEnabled"),mr=c(function(t){Nt=t},"setDisplayMode"),kr=c(function(){return Nt},"getDisplayMode"),yr=c(function(){return tt},"getDateFormat"),gr=c(function(t){kt=t.toLowerCase().split(/[\s,]+/)},"setIncludes"),pr=c(function(){return kt},"getIncludes"),vr=c(function(t){yt=t.toLowerCase().split(/[\s,]+/)},"setExcludes"),xr=c(function(){return yt},"getExcludes"),Tr=c(function(){return Pt},"getLinks"),br=c(function(t){ft=t,Rt.push(t)},"addSection"),wr=c(function(){return Rt},"getSections"),_r=c(function(){let t=re();const r=10;let s=0;for(;!t&&s<r;)t=re(),s++;return _t=$,_t},"getTasks"),le=c(function(t,r,s,n){const a=t.format(r.trim()),h=t.format("YYYY-MM-DD");return n.includes(a)||n.includes(h)?!1:s.includes("weekends")&&(t.isoWeekday()===ee[Dt]||t.isoWeekday()===ee[Dt]+1)||s.includes(t.format("dddd").toLowerCase())?!0:s.includes(a)||s.includes(h)},"isInvalidDate"),Dr=c(function(t){Ht=t},"setWeekday"),Cr=c(function(){return Ht},"getWeekday"),Sr=c(function(t){Dt=t},"setWeekend"),ue=c(function(t,r,s,n){if(!s.length||t.manualEndTime)return;let a;t.startTime instanceof Date?a=j(t.startTime):a=j(t.startTime,r,!0),a=a.add(1,"d");let h;t.endTime instanceof Date?h=j(t.endTime):h=j(t.endTime,r,!0);const[u,p]=Er(a,h,r,s,n);t.endTime=u.toDate(),t.renderEndTime=p},"checkTaskDates"),Er=c(function(t,r,s,n,a){let h=!1,u=null;const p=r.add(1e4,"d");for(;t<=r;){if(h||(u=r.toDate()),h=le(t,s,n,a),h&&(r=r.add(1,"d"),r>p))throw new Error("Failed to find a valid date that was not excluded by `excludes` after 10,000 iterations.");t=t.add(1,"d")}return[r,u]},"fixTaskDates"),Lt=c(function(t,r,s){if(s=s.trim(),c(p=>{const D=p.trim();return D==="x"||D==="X"},"isTimestampFormat")(r)&&/^\d+$/.test(s))return new Date(Number(s));const h=/^after\s+(?<ids>[\d\w- ]+)/.exec(s);if(h!==null){let p=null;for(const E of h.groups.ids.split(" ")){let g=at(E);g!==void 0&&(!p||g.endTime>p.endTime)&&(p=g)}if(p)return p.endTime;const D=new Date;return D.setHours(0,0,0,0),D}let u=j(s,r.trim(),!0);if(u.isValid())return u.toDate();{st.debug("Invalid date:"+s),st.debug("With date format:"+r.trim());const p=new Date(s);if(p===void 0||isNaN(p.getTime())||p.getFullYear()<-1e4||p.getFullYear()>1e4)throw new Error("Invalid date:"+s);return p}},"getStartDate"),de=c(function(t){const r=/^(\d+(?:\.\d+)?)([Mdhmswy]|ms)$/.exec(t.trim());return r!==null?[Number.parseFloat(r[1]),r[2]]:[NaN,"ms"]},"parseDuration"),fe=c(function(t,r,s,n=!1){s=s.trim();const h=/^until\s+(?<ids>[\d\w- ]+)/.exec(s);if(h!==null){let g=null;for(const C of h.groups.ids.split(" ")){let w=at(C);w!==void 0&&(!g||w.startTime<g.startTime)&&(g=w)}if(g)return g.startTime;const F=new Date;return F.setHours(0,0,0,0),F}let u=j(s,r.trim(),!0);if(u.isValid())return n&&(u=u.add(1,"d")),u.toDate();let p=j(t);const[D,E]=de(s);if(!Number.isNaN(D)){const g=p.add(D,E);g.isValid()&&(p=g)}return p.toDate()},"getEndDate"),bt=0,dt=c(function(t){return t===void 0?(bt=bt+1,"task"+bt):t},"parseId"),Mr=c(function(t,r){let s;r.substr(0,1)===":"?s=r.substr(1,r.length):s=r;const n=s.split(","),a={};Gt(n,a,ce);for(let u=0;u<n.length;u++)n[u]=n[u].trim();let h="";switch(n.length){case 1:a.id=dt(),a.startTime=t.endTime,h=n[0];break;case 2:a.id=dt(),a.startTime=Lt(void 0,tt,n[0]),h=n[1];break;case 3:a.id=dt(n[0]),a.startTime=Lt(void 0,tt,n[1]),h=n[2];break}return h&&(a.endTime=fe(a.startTime,tt,h,gt),a.manualEndTime=j(h,"YYYY-MM-DD",!0).isValid(),ue(a,tt,yt,kt)),a},"compileData"),Ir=c(function(t,r){let s;r.substr(0,1)===":"?s=r.substr(1,r.length):s=r;const n=s.split(","),a={};Gt(n,a,ce);for(let h=0;h<n.length;h++)n[h]=n[h].trim();switch(n.length){case 1:a.id=dt(),a.startTime={type:"prevTaskEnd",id:t},a.endTime={data:n[0]};break;case 2:a.id=dt(),a.startTime={type:"getStartDate",startData:n[0]},a.endTime={data:n[1]};break;case 3:a.id=dt(n[0]),a.startTime={type:"getStartDate",startData:n[1]},a.endTime={data:n[2]};break}return a},"parseData"),Ft,wt,$=[],he={},Ar=c(function(t,r){const s={section:ft,type:ft,processed:!1,manualEndTime:!1,renderEndTime:null,raw:{data:r},task:t,classes:[]},n=Ir(wt,r);s.raw.startTime=n.startTime,s.raw.endTime=n.endTime,s.id=n.id,s.prevTaskId=wt,s.active=n.active,s.done=n.done,s.crit=n.crit,s.milestone=n.milestone,s.vert=n.vert,s.order=At,At++;const a=$.push(s);wt=s.id,he[s.id]=a-1},"addTask"),at=c(function(t){const r=he[t];return $[r]},"findTaskById"),Lr=c(function(t,r){const s={section:ft,type:ft,description:t,task:t,classes:[]},n=Mr(Ft,r);s.startTime=n.startTime,s.endTime=n.endTime,s.id=n.id,s.active=n.active,s.done=n.done,s.crit=n.crit,s.milestone=n.milestone,s.vert=n.vert,Ft=s,_t.push(s)},"addTaskOrg"),re=c(function(){const t=c(function(s){const n=$[s];let a="";switch($[s].raw.startTime.type){case"prevTaskEnd":{const h=at(n.prevTaskId);n.startTime=h.endTime;break}case"getStartDate":a=Lt(void 0,tt,$[s].raw.startTime.startData),a&&($[s].startTime=a);break}return $[s].startTime&&($[s].endTime=fe($[s].startTime,tt,$[s].raw.endTime.data,gt),$[s].endTime&&($[s].processed=!0,$[s].manualEndTime=j($[s].raw.endTime.data,"YYYY-MM-DD",!0).isValid(),ue($[s],tt,yt,kt))),$[s].processed},"compileTask");let r=!0;for(const[s,n]of $.entries())t(s),r=r&&n.processed;return r},"compileTasks"),Fr=c(function(t,r){let s=r;ut().securityLevel!=="loose"&&(s=_e(r)),t.split(",").forEach(function(n){at(n)!==void 0&&(ke(n,()=>{window.open(s,"_self")}),Pt.set(n,s))}),me(t,"clickable")},"setLink"),me=c(function(t,r){t.split(",").forEach(function(s){let n=at(s);n!==void 0&&n.classes.push(r)})},"setClass"),Yr=c(function(t,r,s){if(ut().securityLevel!=="loose"||r===void 0)return;let n=[];if(typeof s=="string"){n=s.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);for(let h=0;h<n.length;h++){let u=n[h].trim();u.startsWith('"')&&u.endsWith('"')&&(u=u.substr(1,u.length-2)),n[h]=u}}n.length===0&&n.push(t),at(t)!==void 0&&ke(t,()=>{Ce.runFunc(r,...n)})},"setClickFun"),ke=c(function(t,r){Bt.push(function(){const s=lt?`${lt}-${t}`:t,n=document.querySelector(`[id="${s}"]`);n!==null&&n.addEventListener("click",function(){r()})},function(){const s=lt?`${lt}-${t}`:t,n=document.querySelector(`[id="${s}-text"]`);n!==null&&n.addEventListener("click",function(){r()})})},"pushFun"),Or=c(function(t,r,s){t.split(",").forEach(function(n){Yr(n,r,s)}),me(t,"clickable")},"setClickEvent"),Wr=c(function(t){Bt.forEach(function(r){r(t)})},"bindFunctions"),Vr={getConfig:c(()=>ut().gantt,"getConfig"),clear:er,setDateFormat:lr,getDateFormat:yr,enableInclusiveEndDates:ur,endDatesAreInclusive:dr,enableTopAxis:fr,topAxisEnabled:hr,setAxisFormat:ir,getAxisFormat:nr,setTickInterval:sr,getTickInterval:ar,setTodayMarker:or,getTodayMarker:cr,setAccTitle:Te,getAccTitle:xe,setDiagramTitle:ve,getDiagramTitle:pe,setDiagramId:rr,setDisplayMode:mr,getDisplayMode:kr,setAccDescription:ge,getAccDescription:ye,addSection:br,getSections:wr,getTasks:_r,addTask:Ar,findTaskById:at,addTaskOrg:Lr,setIncludes:gr,getIncludes:pr,setExcludes:vr,getExcludes:xr,setClickEvent:Or,setLink:Fr,getLinks:Tr,bindFunctions:Wr,parseDuration:de,isInvalidDate:le,setWeekday:Dr,getWeekday:Cr,setWeekend:Sr};function Gt(t,r,s){let n=!0;for(;n;)n=!1,s.forEach(function(a){const h="^\\s*"+a+"\\s*$",u=new RegExp(h);t[0].match(u)&&(r[a]=!0,t.shift(1),n=!0)})}c(Gt,"getTaskTags");j.extend(Se);var zr=c(function(){st.debug("Something is calling, setConf, remove the call")},"setConf"),ie={monday:ze,tuesday:Ve,wednesday:We,thursday:Oe,friday:Ye,saturday:Fe,sunday:Le},Pr=c((t,r)=>{let s=[...t].map(()=>-1/0),n=[...t].sort((h,u)=>h.startTime-u.startTime||h.order-u.order),a=0;for(const h of n)for(let u=0;u<s.length;u++)if(h.startTime>=s[u]){s[u]=h.endTime,h.order=u+r,u>a&&(a=u);break}return a},"getMaxIntersections"),et,Et=1e4,Rr=c(function(t,r,s,n){const a=ut().gantt;n.db.setDiagramId(r);const h=ut().securityLevel;let u;h==="sandbox"&&(u=vt("#i"+r));const p=h==="sandbox"?vt(u.nodes()[0].contentDocument.body):vt("body"),D=h==="sandbox"?u.nodes()[0].contentDocument:document,E=D.getElementById(r);et=E.parentElement.offsetWidth,et===void 0&&(et=1200),a.useWidth!==void 0&&(et=a.useWidth);const g=n.db.getTasks();let F=[];for(const k of g)F.push(k.type);F=N(F);const C={};let w=2*a.topPadding;if(n.db.getDisplayMode()==="compact"||a.displayMode==="compact"){const k={};for(const b of g)k[b.section]===void 0?k[b.section]=[b]:k[b.section].push(b);let T=0;for(const b of Object.keys(k)){const y=Pr(k[b],T)+1;T+=y,w+=y*(a.barHeight+a.barGap),C[b]=y}}else{w+=g.length*(a.barHeight+a.barGap);for(const k of F)C[k]=g.filter(T=>T.type===k).length}E.setAttribute("viewBox","0 0 "+et+" "+w);const H=p.select(`[id="${r}"]`),I=Ee().domain([Me(g,function(k){return k.startTime}),Ie(g,function(k){return k.endTime})]).rangeRound([0,et-a.leftPadding-a.rightPadding]);function _(k,T){const b=k.startTime,y=T.startTime;let m=0;return b>y?m=1:b<y&&(m=-1),m}c(_,"taskCompare"),g.sort(_),M(g,et,w),be(H,w,et,a.useMaxWidth),H.append("text").text(n.db.getDiagramTitle()).attr("x",et/2).attr("y",a.titleTopMargin).attr("class","titleText");function M(k,T,b){const y=a.barHeight,m=y+a.barGap,o=a.topPadding,l=a.leftPadding,d=Pe().domain([0,F.length]).range(["#00B9FA","#F95002"]).interpolate(Ae);W(m,o,l,T,b,k,n.db.getExcludes(),n.db.getIncludes()),R(l,o,T,b),O(k,m,o,l,y,d,T),G(m,o),z(l,o,T,b)}c(M,"makeGantt");function O(k,T,b,y,m,o,l){k.sort((e,v)=>e.vert===v.vert?0:e.vert?1:-1);const f=[...new Set(k.map(e=>e.order))].map(e=>k.find(v=>v.order===e));H.append("g").selectAll("rect").data(f).enter().append("rect").attr("x",0).attr("y",function(e,v){return v=e.order,v*T+b-2}).attr("width",function(){return l-a.rightPadding/2}).attr("height",T).attr("class",function(e){for(const[v,Y]of F.entries())if(e.type===Y)return"section section"+v%a.numberSectionStyles;return"section section0"}).enter();const x=H.append("g").selectAll("rect").data(k).enter(),i=n.db.getLinks();if(x.append("rect").attr("id",function(e){return r+"-"+e.id}).attr("rx",3).attr("ry",3).attr("x",function(e){return e.milestone?I(e.startTime)+y+.5*(I(e.endTime)-I(e.startTime))-.5*m:I(e.startTime)+y}).attr("y",function(e,v){return v=e.order,e.vert?a.gridLineStartPadding:v*T+b}).attr("width",function(e){return e.milestone?m:e.vert?.08*m:I(e.renderEndTime||e.endTime)-I(e.startTime)}).attr("height",function(e){return e.vert?g.length*(a.barHeight+a.barGap)+a.barHeight*2:m}).attr("transform-origin",function(e,v){return v=e.order,(I(e.startTime)+y+.5*(I(e.endTime)-I(e.startTime))).toString()+"px "+(v*T+b+.5*m).toString()+"px"}).attr("class",function(e){const v="task";let Y="";e.classes.length>0&&(Y=e.classes.join(" "));let L=0;for(const[X,S]of F.entries())e.type===S&&(L=X%a.numberSectionStyles);let A="";return e.active?e.crit?A+=" activeCrit":A=" active":e.done?e.crit?A=" doneCrit":A=" done":e.crit&&(A+=" crit"),A.length===0&&(A=" task"),e.milestone&&(A=" milestone "+A),e.vert&&(A=" vert "+A),A+=L,A+=" "+Y,v+A}),x.append("text").attr("id",function(e){return r+"-"+e.id+"-text"}).text(function(e){return e.task}).attr("font-size",a.fontSize).attr("x",function(e){let v=I(e.startTime),Y=I(e.renderEndTime||e.endTime);if(e.milestone&&(v+=.5*(I(e.endTime)-I(e.startTime))-.5*m,Y=v+m),e.vert)return I(e.startTime)+y;const L=this.getBBox().width;return L>Y-v?Y+L+1.5*a.leftPadding>l?v+y-5:Y+y+5:(Y-v)/2+v+y}).attr("y",function(e,v){return e.vert?a.gridLineStartPadding+g.length*(a.barHeight+a.barGap)+60:(v=e.order,v*T+a.barHeight/2+(a.fontSize/2-2)+b)}).attr("text-height",m).attr("class",function(e){const v=I(e.startTime);let Y=I(e.endTime);e.milestone&&(Y=v+m);const L=this.getBBox().width;let A="";e.classes.length>0&&(A=e.classes.join(" "));let X=0;for(const[Q,rt]of F.entries())e.type===rt&&(X=Q%a.numberSectionStyles);let S="";return e.active&&(e.crit?S="activeCritText"+X:S="activeText"+X),e.done?e.crit?S=S+" doneCritText"+X:S=S+" doneText"+X:e.crit&&(S=S+" critText"+X),e.milestone&&(S+=" milestoneText"),e.vert&&(S+=" vertText"),L>Y-v?Y+L+1.5*a.leftPadding>l?A+" taskTextOutsideLeft taskTextOutside"+X+" "+S:A+" taskTextOutsideRight taskTextOutside"+X+" "+S+" width-"+L:A+" taskText taskText"+X+" "+S+" width-"+L}),ut().securityLevel==="sandbox"){let e;e=vt("#i"+r);const v=e.nodes()[0].contentDocument;x.filter(function(Y){return i.has(Y.id)}).each(function(Y){var L=v.querySelector("#"+CSS.escape(r+"-"+Y.id)),A=v.querySelector("#"+CSS.escape(r+"-"+Y.id+"-text"));const X=L.parentNode;var S=v.createElement("a");S.setAttribute("xlink:href",i.get(Y.id)),S.setAttribute("target","_top"),X.appendChild(S),S.appendChild(L),S.appendChild(A)})}}c(O,"drawRects");function W(k,T,b,y,m,o,l,d){if(l.length===0&&d.length===0)return;let f,x;for(const{startTime:L,endTime:A}of o)(f===void 0||L<f)&&(f=L),(x===void 0||A>x)&&(x=A);if(!f||!x)return;if(j(x).diff(j(f),"year")>5){st.warn("The difference between the min and max time is more than 5 years. This will cause performance issues. Skipping drawing exclude days.");return}const i=n.db.getDateFormat(),V=[];let e=null,v=j(f);for(;v.valueOf()<=x;)n.db.isInvalidDate(v,i,l,d)?e?e.end=v:e={start:v,end:v}:e&&(V.push(e),e=null),v=v.add(1,"d");H.append("g").selectAll("rect").data(V).enter().append("rect").attr("id",L=>r+"-exclude-"+L.start.format("YYYY-MM-DD")).attr("x",L=>I(L.start.startOf("day"))+b).attr("y",a.gridLineStartPadding).attr("width",L=>I(L.end.endOf("day"))-I(L.start.startOf("day"))).attr("height",m-T-a.gridLineStartPadding).attr("transform-origin",function(L,A){return(I(L.start)+b+.5*(I(L.end)-I(L.start))).toString()+"px "+(A*k+.5*m).toString()+"px"}).attr("class","exclude-range")}c(W,"drawExcludeDays");function P(k,T,b,y){if(b<=0||k>T)return 1/0;const m=T-k,o=j.duration({[y??"day"]:b}).asMilliseconds();return o<=0?1/0:Math.ceil(m/o)}c(P,"getEstimatedTickCount");function R(k,T,b,y){const m=n.db.getDateFormat(),o=n.db.getAxisFormat();let l;o?l=o:m==="D"?l="%d":l=a.axisFormat??"%Y-%m-%d";let d=je(I).tickSize(-y+T+a.gridLineStartPadding).tickFormat(jt(l));const x=/^([1-9]\d*)(millisecond|second|minute|hour|day|week|month)$/.exec(n.db.getTickInterval()||a.tickInterval);if(x!==null){const i=parseInt(x[1],10);if(isNaN(i)||i<=0)st.warn(`Invalid tick interval value: "${x[1]}". Skipping custom tick interval.`);else{const V=x[2],e=n.db.getWeekday()||a.weekday,v=I.domain(),Y=v[0],L=v[1],A=P(Y,L,i,V);if(A>Et)st.warn(`The tick interval "${i}${V}" would generate ${A} ticks, which exceeds the maximum allowed (${Et}). This may indicate an invalid date or time range. Skipping custom tick interval.`);else switch(V){case"millisecond":d.ticks(Jt.every(i));break;case"second":d.ticks(Kt.every(i));break;case"minute":d.ticks(Qt.every(i));break;case"hour":d.ticks(Zt.every(i));break;case"day":d.ticks(Ut.every(i));break;case"week":d.ticks(ie[e].every(i));break;case"month":d.ticks(qt.every(i));break}}}if(H.append("g").attr("class","grid").attr("transform","translate("+k+", "+(y-50)+")").call(d).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10).attr("dy","1em"),n.db.topAxisEnabled()||a.topAxis){let i=Xe(I).tickSize(-y+T+a.gridLineStartPadding).tickFormat(jt(l));if(x!==null){const V=parseInt(x[1],10);if(isNaN(V)||V<=0)st.warn(`Invalid tick interval value: "${x[1]}". Skipping custom tick interval.`);else{const e=x[2],v=n.db.getWeekday()||a.weekday,Y=I.domain(),L=Y[0],A=Y[1];if(P(L,A,V,e)<=Et)switch(e){case"millisecond":i.ticks(Jt.every(V));break;case"second":i.ticks(Kt.every(V));break;case"minute":i.ticks(Qt.every(V));break;case"hour":i.ticks(Zt.every(V));break;case"day":i.ticks(Ut.every(V));break;case"week":i.ticks(ie[v].every(V));break;case"month":i.ticks(qt.every(V));break}}}H.append("g").attr("class","grid").attr("transform","translate("+k+", "+T+")").call(i).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10)}}c(R,"makeGrid");function G(k,T){let b=0;const y=Object.keys(C).map(m=>[m,C[m]]);H.append("g").selectAll("text").data(y).enter().append(function(m){const o=m[0].split(we.lineBreakRegex),l=-(o.length-1)/2,d=D.createElementNS("http://www.w3.org/2000/svg","text");d.setAttribute("dy",l+"em");for(const[f,x]of o.entries()){const i=D.createElementNS("http://www.w3.org/2000/svg","tspan");i.setAttribute("alignment-baseline","central"),i.setAttribute("x","10"),f>0&&i.setAttribute("dy","1em"),i.textContent=x,d.appendChild(i)}return d}).attr("x",10).attr("y",function(m,o){if(o>0)for(let l=0;l<o;l++)return b+=y[o-1][1],m[1]*k/2+b*k+T;else return m[1]*k/2+T}).attr("font-size",a.sectionFontSize).attr("class",function(m){for(const[o,l]of F.entries())if(m[0]===l)return"sectionTitle sectionTitle"+o%a.numberSectionStyles;return"sectionTitle"})}c(G,"vertLabels");function z(k,T,b,y){const m=n.db.getTodayMarker();if(m==="off")return;const o=H.append("g").attr("class","today"),l=new Date,d=o.append("line");d.attr("x1",I(l)+k).attr("x2",I(l)+k).attr("y1",a.titleTopMargin).attr("y2",y-a.titleTopMargin).attr("class","today"),m!==""&&d.attr("style",m.replace(/,/g,";"))}c(z,"drawToday");function N(k){const T={},b=[];for(let y=0,m=k.length;y<m;++y)Object.prototype.hasOwnProperty.call(T,k[y])||(T[k[y]]=!0,b.push(k[y]));return b}c(N,"checkUnique")},"draw"),Nr={setConf:zr,draw:Rr},Br=c(t=>`
  .mermaid-main-font {
        font-family: ${t.fontFamily};
  }

  .exclude-range {
    fill: ${t.excludeBkgColor};
  }

  .section {
    stroke: none;
    opacity: 0.2;
  }

  .section0 {
    fill: ${t.sectionBkgColor};
  }

  .section2 {
    fill: ${t.sectionBkgColor2};
  }

  .section1,
  .section3 {
    fill: ${t.altSectionBkgColor};
    opacity: 0.2;
  }

  .sectionTitle0 {
    fill: ${t.titleColor};
  }

  .sectionTitle1 {
    fill: ${t.titleColor};
  }

  .sectionTitle2 {
    fill: ${t.titleColor};
  }

  .sectionTitle3 {
    fill: ${t.titleColor};
  }

  .sectionTitle {
    text-anchor: start;
    font-family: ${t.fontFamily};
  }


  /* Grid and axis */

  .grid .tick {
    stroke: ${t.gridColor};
    opacity: 0.8;
    shape-rendering: crispEdges;
  }

  .grid .tick text {
    font-family: ${t.fontFamily};
    fill: ${t.textColor};
  }

  .grid path {
    stroke-width: 0;
  }


  /* Today line */

  .today {
    fill: none;
    stroke: ${t.todayLineColor};
    stroke-width: 2px;
  }


  /* Task styling */

  /* Default task */

  .task {
    stroke-width: 2;
  }

  .taskText {
    text-anchor: middle;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideRight {
    fill: ${t.taskTextDarkColor};
    text-anchor: start;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideLeft {
    fill: ${t.taskTextDarkColor};
    text-anchor: end;
  }


  /* Special case clickable */

  .task.clickable {
    cursor: pointer;
  }

  .taskText.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideLeft.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideRight.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }


  /* Specific task settings for the sections*/

  .taskText0,
  .taskText1,
  .taskText2,
  .taskText3 {
    fill: ${t.taskTextColor};
  }

  .task0,
  .task1,
  .task2,
  .task3 {
    fill: ${t.taskBkgColor};
    stroke: ${t.taskBorderColor};
  }

  .taskTextOutside0,
  .taskTextOutside2
  {
    fill: ${t.taskTextOutsideColor};
  }

  .taskTextOutside1,
  .taskTextOutside3 {
    fill: ${t.taskTextOutsideColor};
  }


  /* Active task */

  .active0,
  .active1,
  .active2,
  .active3 {
    fill: ${t.activeTaskBkgColor};
    stroke: ${t.activeTaskBorderColor};
  }

  .activeText0,
  .activeText1,
  .activeText2,
  .activeText3 {
    fill: ${t.taskTextDarkColor} !important;
  }


  /* Completed task */

  .done0,
  .done1,
  .done2,
  .done3 {
    stroke: ${t.doneTaskBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
  }

  .doneText0,
  .doneText1,
  .doneText2,
  .doneText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  /* Done task text displayed outside the bar sits against the diagram background,
     not against the done-task bar, so it must use the outside/contrast color. */
  .doneText0.taskTextOutsideLeft,
  .doneText0.taskTextOutsideRight,
  .doneText1.taskTextOutsideLeft,
  .doneText1.taskTextOutsideRight,
  .doneText2.taskTextOutsideLeft,
  .doneText2.taskTextOutsideRight,
  .doneText3.taskTextOutsideLeft,
  .doneText3.taskTextOutsideRight {
    fill: ${t.taskTextOutsideColor} !important;
  }


  /* Tasks on the critical line */

  .crit0,
  .crit1,
  .crit2,
  .crit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.critBkgColor};
    stroke-width: 2;
  }

  .activeCrit0,
  .activeCrit1,
  .activeCrit2,
  .activeCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.activeTaskBkgColor};
    stroke-width: 2;
  }

  .doneCrit0,
  .doneCrit1,
  .doneCrit2,
  .doneCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
    cursor: pointer;
    shape-rendering: crispEdges;
  }

  .milestone {
    transform: rotate(45deg) scale(0.8,0.8);
  }

  .milestoneText {
    font-style: italic;
  }
  .doneCritText0,
  .doneCritText1,
  .doneCritText2,
  .doneCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  /* Done-crit task text outside the bar — same reasoning as doneText above. */
  .doneCritText0.taskTextOutsideLeft,
  .doneCritText0.taskTextOutsideRight,
  .doneCritText1.taskTextOutsideLeft,
  .doneCritText1.taskTextOutsideRight,
  .doneCritText2.taskTextOutsideLeft,
  .doneCritText2.taskTextOutsideRight,
  .doneCritText3.taskTextOutsideLeft,
  .doneCritText3.taskTextOutsideRight {
    fill: ${t.taskTextOutsideColor} !important;
  }

  .vert {
    stroke: ${t.vertLineColor};
  }

  .vertText {
    font-size: 15px;
    text-anchor: middle;
    fill: ${t.vertLineColor} !important;
  }

  .activeCritText0,
  .activeCritText1,
  .activeCritText2,
  .activeCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  .titleText {
    text-anchor: middle;
    font-size: 18px;
    fill: ${t.titleColor||t.textColor};
    font-family: ${t.fontFamily};
  }
`,"getStyles"),$r=Br,Zr={parser:tr,db:Vr,renderer:Nr,styles:$r};export{Zr as diagram};
//# sourceMappingURL=CpxY5sHb.js.map
