import{R as D,S as K,T as U,o as l,c as d,U as y,V as t,L as k,W as w,v,t as S,_ as E,r as b,l as F,k as T,a as C,b as o,d as c,F as A,D as M,w as I,A as N,X as R,i as L,J as $,s as r,e as J,Y as O}from"./index-ZunxwIPK.js";var W=function(i){var n=i.dt;return`
.p-chip {
    display: inline-flex;
    align-items: center;
    background: `.concat(n("chip.background"),`;
    color: `).concat(n("chip.color"),`;
    border-radius: `).concat(n("chip.border.radius"),`;
    padding-block: `).concat(n("chip.padding.y"),`;
    padding-inline: `).concat(n("chip.padding.x"),`;
    gap: `).concat(n("chip.gap"),`;
}

.p-chip-icon {
    color: `).concat(n("chip.icon.color"),`;
    font-size: `).concat(n("chip.icon.font.size"),`;
    width: `).concat(n("chip.icon.size"),`;
    height: `).concat(n("chip.icon.size"),`;
}

.p-chip-image {
    border-radius: 50%;
    width: `).concat(n("chip.image.width"),`;
    height: `).concat(n("chip.image.height"),`;
    margin-inline-start: calc(-1 * `).concat(n("chip.padding.y"),`);
}

.p-chip:has(.p-chip-remove-icon) {
    padding-inline-end: `).concat(n("chip.padding.y"),`;
}

.p-chip:has(.p-chip-image) {
    padding-block-start: calc(`).concat(n("chip.padding.y"),` / 2);
    padding-block-end: calc(`).concat(n("chip.padding.y"),` / 2);
}

.p-chip-remove-icon {
    cursor: pointer;
    font-size: `).concat(n("chip.remove.icon.size"),`;
    width: `).concat(n("chip.remove.icon.size"),`;
    height: `).concat(n("chip.remove.icon.size"),`;
    color: `).concat(n("chip.remove.icon.color"),`;
    border-radius: 50%;
    transition: outline-color `).concat(n("chip.transition.duration"),", box-shadow ").concat(n("chip.transition.duration"),`;
    outline-color: transparent;
}

.p-chip-remove-icon:focus-visible {
    box-shadow: `).concat(n("chip.remove.icon.focus.ring.shadow"),`;
    outline: `).concat(n("chip.remove.icon.focus.ring.width")," ").concat(n("chip.remove.icon.focus.ring.style")," ").concat(n("chip.remove.icon.focus.ring.color"),`;
    outline-offset: `).concat(n("chip.remove.icon.focus.ring.offset"),`;
}
`)},X={root:"p-chip p-component",image:"p-chip-image",icon:"p-chip-icon",label:"p-chip-label",removeIcon:"p-chip-remove-icon"},Y=D.extend({name:"chip",theme:W,classes:X}),j={name:"BaseChip",extends:U,props:{label:{type:String,default:null},icon:{type:String,default:null},image:{type:String,default:null},removable:{type:Boolean,default:!1},removeIcon:{type:String,default:void 0}},style:Y,provide:function(){return{$pcChip:this,$parentInstance:this}}},f={name:"Chip",extends:j,inheritAttrs:!1,emits:["remove"],data:function(){return{visible:!0}},methods:{onKeydown:function(i){(i.key==="Enter"||i.key==="Backspace")&&this.close(i)},close:function(i){this.visible=!1,this.$emit("remove",i)}},components:{TimesCircleIcon:K}},q=["aria-label"],G=["src"];function H(e,i,n,h,p,s){return p.visible?(l(),d("div",t({key:0,class:e.cx("root"),"aria-label":e.label},e.ptmi("root")),[y(e.$slots,"default",{},function(){return[e.image?(l(),d("img",t({key:0,src:e.image},e.ptm("image"),{class:e.cx("image")}),null,16,G)):e.$slots.icon?(l(),k(w(e.$slots.icon),t({key:1,class:e.cx("icon")},e.ptm("icon")),null,16,["class"])):e.icon?(l(),d("span",t({key:2,class:[e.cx("icon"),e.icon]},e.ptm("icon")),null,16)):v("",!0),e.label?(l(),d("div",t({key:3,class:e.cx("label")},e.ptm("label")),S(e.label),17)):v("",!0)]}),e.removable?y(e.$slots,"removeicon",{key:0,removeCallback:s.close,keydownCallback:s.onKeydown},function(){return[(l(),k(w(e.removeIcon?"span":"TimesCircleIcon"),t({tabindex:"0",class:[e.cx("removeIcon"),e.removeIcon],onClick:s.close,onKeydown:s.onKeydown},e.ptm("removeIcon")),null,16,["class","onClick","onKeydown"]))]}):v("",!0)],16,q)):v("",!0)}f.render=H;const P={class:"mb-2 filtro-chips"},Q={__name:"UbicacionImeis",setup(e){const i=O(),n=b(null),h=b([]),p=b(!0),s=b(null),z=[{label:"Todos",value:null},{label:"Disponibles",value:"Disponible"},{label:"Vendidos",value:"Vendido"}],B=async()=>{p.value=!0;const u=await N();n.value=u.find(m=>m.id==i.params.id),h.value=await R(i.params.id),p.value=!1},V=F(()=>s.value?h.value.filter(u=>u.status===s.value):h.value);return T(B),(u,m)=>{var g;return l(),d("div",null,[C("h2",null,"IMEIs en la bodega: "+S((g=n.value)==null?void 0:g.nombre),1),o(c(L),{label:"Volver",icon:"pi pi-arrow-left",onClick:m[0]||(m[0]=a=>u.$router.back()),class:"mb-3"}),C("div",P,[(l(),d(A,null,M(z,a=>o(c(f),{key:a.value,label:a.label,class:$(["chip-filtro",{"chip-activo":s.value===a.value},a.value==="Disponible"?"chip-disponible":a.value==="Vendido"?"chip-vendido":"chip-todos"]),onClick:Z=>s.value=a.value},null,8,["label","class","onClick"])),64))]),o(c(J),{value:V.value,loading:p.value},{default:I(()=>[o(c(r),{field:"imei",header:"IMEI"}),o(c(r),{field:"articulo_nombre",header:"Artículo"}),o(c(r),{field:"sku",header:"SKU"}),o(c(r),{field:"status",header:"Estado"},{body:I(a=>[o(c(f),{label:a.data.status,class:$([a.data.status==="Disponible"?"chip-disponible":a.data.status==="Vendido"?"chip-vendido":"chip-otro"])},null,8,["label","class"])]),_:1}),o(c(r),{field:"date",header:"Fecha registro"}),o(c(r),{field:"registeredBy",header:"Registró"})]),_:1},8,["value","loading"])])}}},x=E(Q,[["__scopeId","data-v-f5dfe010"]]);export{x as default};
