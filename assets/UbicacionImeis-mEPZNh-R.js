import{J as V,K as D,L as E,o as l,c as d,M as y,N as t,G as k,O as w,q as v,t as S,_ as U,r as b,l as F,k as M,a as C,b as o,d as c,F as N,y as T,w as I,i as A,C as $,s as r,e as L,P as O}from"./index-BypK6ZTZ.js";import{g as R,c as q}from"./ubicacionesService-g8Nyy4A9.js";var G=function(i){var n=i.dt;return`
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
`)},J={root:"p-chip p-component",image:"p-chip-image",icon:"p-chip-icon",label:"p-chip-label",removeIcon:"p-chip-remove-icon"},P=V.extend({name:"chip",theme:G,classes:J}),j={name:"BaseChip",extends:E,props:{label:{type:String,default:null},icon:{type:String,default:null},image:{type:String,default:null},removable:{type:Boolean,default:!1},removeIcon:{type:String,default:void 0}},style:P,provide:function(){return{$pcChip:this,$parentInstance:this}}},f={name:"Chip",extends:j,inheritAttrs:!1,emits:["remove"],data:function(){return{visible:!0}},methods:{onKeydown:function(i){(i.key==="Enter"||i.key==="Backspace")&&this.close(i)},close:function(i){this.visible=!1,this.$emit("remove",i)}},components:{TimesCircleIcon:D}},H=["aria-label"],Q=["src"];function W(e,i,n,h,p,s){return p.visible?(l(),d("div",t({key:0,class:e.cx("root"),"aria-label":e.label},e.ptmi("root")),[y(e.$slots,"default",{},function(){return[e.image?(l(),d("img",t({key:0,src:e.image},e.ptm("image"),{class:e.cx("image")}),null,16,Q)):e.$slots.icon?(l(),k(w(e.$slots.icon),t({key:1,class:e.cx("icon")},e.ptm("icon")),null,16,["class"])):e.icon?(l(),d("span",t({key:2,class:[e.cx("icon"),e.icon]},e.ptm("icon")),null,16)):v("",!0),e.label?(l(),d("div",t({key:3,class:e.cx("label")},e.ptm("label")),S(e.label),17)):v("",!0)]}),e.removable?y(e.$slots,"removeicon",{key:0,removeCallback:s.close,keydownCallback:s.onKeydown},function(){return[(l(),k(w(e.removeIcon?"span":"TimesCircleIcon"),t({tabindex:"0",class:[e.cx("removeIcon"),e.removeIcon],onClick:s.close,onKeydown:s.onKeydown},e.ptm("removeIcon")),null,16,["class","onClick","onKeydown"]))]}):v("",!0)],16,H)):v("",!0)}f.render=W;const X={class:"mb-2 filtro-chips"},Y={__name:"UbicacionImeis",setup(e){const i=O(),n=b(null),h=b([]),p=b(!0),s=b(null),z=[{label:"Todos",value:null},{label:"Disponibles",value:"Disponible"},{label:"Vendidos",value:"Vendido"}],B=async()=>{p.value=!0;const u=await R();n.value=u.find(m=>m.id==i.params.id),h.value=await q(i.params.id),p.value=!1},K=F(()=>s.value?h.value.filter(u=>u.status===s.value):h.value);return M(B),(u,m)=>{var g;return l(),d("div",null,[C("h2",null,"IMEIs en la bodega: "+S((g=n.value)==null?void 0:g.nombre),1),o(c(A),{label:"Volver",icon:"pi pi-arrow-left",onClick:m[0]||(m[0]=a=>u.$router.back()),class:"mb-3"}),C("div",X,[(l(),d(N,null,T(z,a=>o(c(f),{key:a.value,label:a.label,class:$(["chip-filtro",{"chip-activo":s.value===a.value},a.value==="Disponible"?"chip-disponible":a.value==="Vendido"?"chip-vendido":"chip-todos"]),onClick:Z=>s.value=a.value},null,8,["label","class","onClick"])),64))]),o(c(L),{value:K.value,loading:p.value},{default:I(()=>[o(c(r),{field:"imei",header:"IMEI"}),o(c(r),{field:"articulo_nombre",header:"Artículo"}),o(c(r),{field:"sku",header:"SKU"}),o(c(r),{field:"status",header:"Estado"},{body:I(a=>[o(c(f),{label:a.data.status,class:$([a.data.status==="Disponible"?"chip-disponible":a.data.status==="Vendido"?"chip-vendido":"chip-otro"])},null,8,["label","class"])]),_:1}),o(c(r),{field:"date",header:"Fecha registro"}),o(c(r),{field:"registeredBy",header:"Registró"})]),_:1},8,["value","loading"])])}}},ee=U(Y,[["__scopeId","data-v-f5dfe010"]]);export{ee as default};
