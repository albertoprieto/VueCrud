import{M as fe,N,U as ne,Z as X,O as U,P as E,Q as he,R as me,S as be,T as ve,V as ye,W as ge,X as Oe,Y as we,$ as Ie,a0 as ie,a1 as ke,g as K,a2 as Ce,a3 as Se,a4 as Le,a5 as Me,a6 as xe,a7 as j,a8 as Ve,o as d,c as h,D as z,I as G,a9 as Ke,v as M,aa as m,J as x,K as D,ab as S,b as c,w as L,a as f,ac as De,t as T,ad as Te,ae as Ae,p as Y,E as Ee,af as Fe,_ as Pe,r as V,l as _,k as Be,ag as le,d as p,i as C,s as F,e as ze,j as Re}from"./index-d7sXuZmh.js";import{s as Ue}from"./index-Defi0bxo.js";import{g as je,u as Ge,a as $e,d as He}from"./clientesService-DVqbXDqc.js";var Ne=function(e){var o=e.dt;return`
.p-autocomplete {
    display: inline-flex;
}

.p-autocomplete-loader {
    position: absolute;
    top: 50%;
    margin-top: -0.5rem;
    inset-inline-end: `.concat(o("autocomplete.padding.x"),`;
}

.p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-loader {
    inset-inline-end: calc(`).concat(o("autocomplete.dropdown.width")," + ").concat(o("autocomplete.padding.x"),`);
}

.p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-input {
    flex: 1 1 auto;
    width: 1%;
}

.p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-input,
.p-autocomplete:has(.p-autocomplete-dropdown) .p-autocomplete-input-multiple {
    border-start-end-radius: 0;
    border-end-end-radius: 0;
}

.p-autocomplete-dropdown {
    cursor: pointer;
    display: inline-flex;
    user-select: none;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
    width: `).concat(o("autocomplete.dropdown.width"),`;
    border-start-end-radius: `).concat(o("autocomplete.dropdown.border.radius"),`;
    border-end-end-radius: `).concat(o("autocomplete.dropdown.border.radius"),`;
    background: `).concat(o("autocomplete.dropdown.background"),`;
    border: 1px solid `).concat(o("autocomplete.dropdown.border.color"),`;
    border-inline-start: 0 none;
    color: `).concat(o("autocomplete.dropdown.color"),`;
    transition: background `).concat(o("autocomplete.transition.duration"),", color ").concat(o("autocomplete.transition.duration"),", border-color ").concat(o("autocomplete.transition.duration"),", outline-color ").concat(o("autocomplete.transition.duration"),", box-shadow ").concat(o("autocomplete.transition.duration"),`;
    outline-color: transparent;
}

.p-autocomplete-dropdown:not(:disabled):hover {
    background: `).concat(o("autocomplete.dropdown.hover.background"),`;
    border-color: `).concat(o("autocomplete.dropdown.hover.border.color"),`;
    color: `).concat(o("autocomplete.dropdown.hover.color"),`;
}

.p-autocomplete-dropdown:not(:disabled):active {
    background: `).concat(o("autocomplete.dropdown.active.background"),`;
    border-color: `).concat(o("autocomplete.dropdown.active.border.color"),`;
    color: `).concat(o("autocomplete.dropdown.active.color"),`;
}

.p-autocomplete-dropdown:focus-visible {
    box-shadow: `).concat(o("autocomplete.dropdown.focus.ring.shadow"),`;
    outline: `).concat(o("autocomplete.dropdown.focus.ring.width")," ").concat(o("autocomplete.dropdown.focus.ring.style")," ").concat(o("autocomplete.dropdown.focus.ring.color"),`;
    outline-offset: `).concat(o("autocomplete.dropdown.focus.ring.offset"),`;
}

.p-autocomplete .p-autocomplete-overlay {
    min-width: 100%;
}

.p-autocomplete-overlay {
    position: absolute;
    top: 0;
    left: 0;
    background: `).concat(o("autocomplete.overlay.background"),`;
    color: `).concat(o("autocomplete.overlay.color"),`;
    border: 1px solid `).concat(o("autocomplete.overlay.border.color"),`;
    border-radius: `).concat(o("autocomplete.overlay.border.radius"),`;
    box-shadow: `).concat(o("autocomplete.overlay.shadow"),`;
}

.p-autocomplete-list-container {
    overflow: auto;
}

.p-autocomplete-list {
    margin: 0;
    list-style-type: none;
    display: flex;
    flex-direction: column;
    gap: `).concat(o("autocomplete.list.gap"),`;
    padding: `).concat(o("autocomplete.list.padding"),`;
}

.p-autocomplete-option {
    cursor: pointer;
    white-space: nowrap;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    padding: `).concat(o("autocomplete.option.padding"),`;
    border: 0 none;
    color: `).concat(o("autocomplete.option.color"),`;
    background: transparent;
    transition: background `).concat(o("autocomplete.transition.duration"),", color ").concat(o("autocomplete.transition.duration"),", border-color ").concat(o("autocomplete.transition.duration"),`;
    border-radius: `).concat(o("autocomplete.option.border.radius"),`;
}

.p-autocomplete-option:not(.p-autocomplete-option-selected):not(.p-disabled).p-focus {
    background: `).concat(o("autocomplete.option.focus.background"),`;
    color: `).concat(o("autocomplete.option.focus.color"),`;
}

.p-autocomplete-option-selected {
    background: `).concat(o("autocomplete.option.selected.background"),`;
    color: `).concat(o("autocomplete.option.selected.color"),`;
}

.p-autocomplete-option-selected.p-focus {
    background: `).concat(o("autocomplete.option.selected.focus.background"),`;
    color: `).concat(o("autocomplete.option.selected.focus.color"),`;
}

.p-autocomplete-option-group {
    margin: 0;
    padding: `).concat(o("autocomplete.option.group.padding"),`;
    color: `).concat(o("autocomplete.option.group.color"),`;
    background: `).concat(o("autocomplete.option.group.background"),`;
    font-weight: `).concat(o("autocomplete.option.group.font.weight"),`;
}

.p-autocomplete-input-multiple {
    margin: 0;
    list-style-type: none;
    cursor: text;
    overflow: hidden;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    padding: calc(`).concat(o("autocomplete.padding.y")," / 2) ").concat(o("autocomplete.padding.x"),`;
    gap: calc(`).concat(o("autocomplete.padding.y"),` / 2);
    color: `).concat(o("autocomplete.color"),`;
    background: `).concat(o("autocomplete.background"),`;
    border: 1px solid `).concat(o("autocomplete.border.color"),`;
    border-radius: `).concat(o("autocomplete.border.radius"),`;
    width: 100%;
    transition: background `).concat(o("autocomplete.transition.duration"),", color ").concat(o("autocomplete.transition.duration"),", border-color ").concat(o("autocomplete.transition.duration"),", outline-color ").concat(o("autocomplete.transition.duration"),", box-shadow ").concat(o("autocomplete.transition.duration"),`;
    outline-color: transparent;
    box-shadow: `).concat(o("autocomplete.shadow"),`;
}

.p-autocomplete:not(.p-disabled):hover .p-autocomplete-input-multiple {
    border-color: `).concat(o("autocomplete.hover.border.color"),`;
}

.p-autocomplete:not(.p-disabled).p-focus .p-autocomplete-input-multiple {
    border-color: `).concat(o("autocomplete.focus.border.color"),`;
    box-shadow: `).concat(o("autocomplete.focus.ring.shadow"),`;
    outline: `).concat(o("autocomplete.focus.ring.width")," ").concat(o("autocomplete.focus.ring.style")," ").concat(o("autocomplete.focus.ring.color"),`;
    outline-offset: `).concat(o("autocomplete.focus.ring.offset"),`;
}

.p-autocomplete.p-invalid .p-autocomplete-input-multiple {
    border-color: `).concat(o("autocomplete.invalid.border.color"),`;
}

.p-variant-filled.p-autocomplete-input-multiple {
    background: `).concat(o("autocomplete.filled.background"),`;
}

.p-autocomplete:not(.p-disabled):hover .p-variant-filled.p-autocomplete-input-multiple {
    background: `).concat(o("autocomplete.filled.hover.background"),`;
}

.p-autocomplete:not(.p-disabled).p-focus .p-variant-filled.p-autocomplete-input-multiple  {
    background: `).concat(o("autocomplete.filled.focus.background"),`;
}

.p-autocomplete.p-disabled .p-autocomplete-input-multiple {
    opacity: 1;
    background: `).concat(o("autocomplete.disabled.background"),`;
    color: `).concat(o("autocomplete.disabled.color"),`;
}

.p-autocomplete-chip.p-chip {
    padding-block-start: calc(`).concat(o("autocomplete.padding.y"),` / 2);
    padding-block-end: calc(`).concat(o("autocomplete.padding.y"),` / 2);
    border-radius: `).concat(o("autocomplete.chip.border.radius"),`;
}

.p-autocomplete-input-multiple:has(.p-autocomplete-chip) {
    padding-inline-start: calc(`).concat(o("autocomplete.padding.y"),` / 2);
    padding-inline-end: calc(`).concat(o("autocomplete.padding.y"),` / 2);
}

.p-autocomplete-chip-item.p-focus .p-autocomplete-chip {
    background: `).concat(o("autocomplete.chip.focus.background"),`;
    color: `).concat(o("autocomplete.chip.focus.color"),`;
}

.p-autocomplete-input-chip {
    flex: 1 1 auto;
    display: inline-flex;
    padding-block-start: calc(`).concat(o("autocomplete.padding.y"),` / 2);
    padding-block-end: calc(`).concat(o("autocomplete.padding.y"),` / 2);
}

.p-autocomplete-input-chip input {
    border: 0 none;
    outline: 0 none;
    background: transparent;
    margin: 0;
    padding: 0;
    box-shadow: none;
    border-radius: 0;
    width: 100%;
    font-family: inherit;
    font-feature-settings: inherit;
    font-size: 1rem;
    color: inherit;
}

.p-autocomplete-input-chip input::placeholder {
    color: `).concat(o("autocomplete.placeholder.color"),`;
}

.p-autocomplete.p-invalid .p-autocomplete-input-chip input::placeholder {
    color: `).concat(o("autocomplete.invalid.placeholder.color"),`;
}

.p-autocomplete-empty-message {
    padding: `).concat(o("autocomplete.empty.message.padding"),`;
}

.p-autocomplete-fluid {
    display: flex;
}

.p-autocomplete-fluid:has(.p-autocomplete-dropdown) .p-autocomplete-input {
    width: 1%;
}

.p-autocomplete:has(.p-inputtext-sm) .p-autocomplete-dropdown {
    width: `).concat(o("autocomplete.dropdown.sm.width"),`;
}

.p-autocomplete:has(.p-inputtext-sm) .p-autocomplete-dropdown .p-icon {
    font-size: `).concat(o("form.field.sm.font.size"),`;
    width: `).concat(o("form.field.sm.font.size"),`;
    height: `).concat(o("form.field.sm.font.size"),`;
}

.p-autocomplete:has(.p-inputtext-lg) .p-autocomplete-dropdown {
    width: `).concat(o("autocomplete.dropdown.lg.width"),`;
}

.p-autocomplete:has(.p-inputtext-lg) .p-autocomplete-dropdown .p-icon {
    font-size: `).concat(o("form.field.lg.font.size"),`;
    width: `).concat(o("form.field.lg.font.size"),`;
    height: `).concat(o("form.field.lg.font.size"),`;
}
`)},qe={root:{position:"relative"}},We={root:function(e){var o=e.instance,n=e.props;return["p-autocomplete p-component p-inputwrapper",{"p-disabled":n.disabled,"p-invalid":o.$invalid,"p-focus":o.focused,"p-inputwrapper-filled":o.$filled||N(o.inputValue),"p-inputwrapper-focus":o.focused,"p-autocomplete-open":o.overlayVisible,"p-autocomplete-fluid":o.$fluid}]},pcInputText:"p-autocomplete-input",inputMultiple:function(e){e.props;var o=e.instance;return["p-autocomplete-input-multiple",{"p-variant-filled":o.$variant==="filled"}]},chipItem:function(e){var o=e.instance,n=e.i;return["p-autocomplete-chip-item",{"p-focus":o.focusedMultipleOptionIndex===n}]},pcChip:"p-autocomplete-chip",chipIcon:"p-autocomplete-chip-icon",inputChip:"p-autocomplete-input-chip",loader:"p-autocomplete-loader",dropdown:"p-autocomplete-dropdown",overlay:"p-autocomplete-overlay p-component",listContainer:"p-autocomplete-list-container",list:"p-autocomplete-list",optionGroup:"p-autocomplete-option-group",option:function(e){var o=e.instance,n=e.option,s=e.i,i=e.getItemOptions;return["p-autocomplete-option",{"p-autocomplete-option-selected":o.isSelected(n),"p-focus":o.focusedOptionIndex===o.getOptionIndex(s,i),"p-disabled":o.isOptionDisabled(n)}]},emptyMessage:"p-autocomplete-empty-message"},Ze=fe.extend({name:"autocomplete",theme:Ne,classes:We,inlineStyles:qe}),Je={name:"BaseAutoComplete",extends:Fe,props:{suggestions:{type:Array,default:null},optionLabel:null,optionDisabled:null,optionGroupLabel:null,optionGroupChildren:null,scrollHeight:{type:String,default:"14rem"},dropdown:{type:Boolean,default:!1},dropdownMode:{type:String,default:"blank"},multiple:{type:Boolean,default:!1},loading:{type:Boolean,default:!1},placeholder:{type:String,default:null},dataKey:{type:String,default:null},minLength:{type:Number,default:1},delay:{type:Number,default:300},appendTo:{type:[String,Object],default:"body"},forceSelection:{type:Boolean,default:!1},completeOnFocus:{type:Boolean,default:!1},inputId:{type:String,default:null},inputStyle:{type:Object,default:null},inputClass:{type:[String,Object],default:null},panelStyle:{type:Object,default:null},panelClass:{type:[String,Object],default:null},overlayStyle:{type:Object,default:null},overlayClass:{type:[String,Object],default:null},dropdownIcon:{type:String,default:null},dropdownClass:{type:[String,Object],default:null},loader:{type:String,default:null},loadingIcon:{type:String,default:null},removeTokenIcon:{type:String,default:null},chipIcon:{type:String,default:null},virtualScrollerOptions:{type:Object,default:null},autoOptionFocus:{type:Boolean,default:!1},selectOnFocus:{type:Boolean,default:!1},focusOnHover:{type:Boolean,default:!0},searchLocale:{type:String,default:void 0},searchMessage:{type:String,default:null},selectionMessage:{type:String,default:null},emptySelectionMessage:{type:String,default:null},emptySearchMessage:{type:String,default:null},showEmptyMessage:{type:Boolean,default:!0},tabindex:{type:Number,default:0},typeahead:{type:Boolean,default:!0},ariaLabel:{type:String,default:null},ariaLabelledby:{type:String,default:null}},style:Ze,provide:function(){return{$pcAutoComplete:this,$parentInstance:this}}};function ee(t){"@babel/helpers - typeof";return ee=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},ee(t)}function ae(t){return _e(t)||Ye(t)||Xe(t)||Qe()}function Qe(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Xe(t,e){if(t){if(typeof t=="string")return te(t,e);var o={}.toString.call(t).slice(8,-1);return o==="Object"&&t.constructor&&(o=t.constructor.name),o==="Map"||o==="Set"?Array.from(t):o==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(o)?te(t,e):void 0}}function Ye(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function _e(t){if(Array.isArray(t))return te(t)}function te(t,e){(e==null||e>t.length)&&(e=t.length);for(var o=0,n=Array(e);o<e;o++)n[o]=t[o];return n}var oe={name:"AutoComplete",extends:Je,inheritAttrs:!1,emits:["change","focus","blur","item-select","item-unselect","option-select","option-unselect","dropdown-click","clear","complete","before-show","before-hide","show","hide"],inject:{$pcFluid:{default:null}},outsideClickListener:null,resizeListener:null,scrollHandler:null,overlay:null,virtualScroller:null,searchTimeout:null,dirty:!1,data:function(){return{id:this.$attrs.id,clicked:!1,focused:!1,focusedOptionIndex:-1,focusedMultipleOptionIndex:-1,overlayVisible:!1,searching:!1}},watch:{"$attrs.id":function(e){this.id=e||ne()},suggestions:function(){this.searching&&(this.show(),this.focusedOptionIndex=this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1,this.searching=!1,!this.showEmptyMessage&&this.visibleOptions.length===0&&this.hide()),this.autoUpdateModel()}},mounted:function(){this.id=this.id||ne(),this.autoUpdateModel()},updated:function(){this.overlayVisible&&this.alignOverlay()},beforeUnmount:function(){this.unbindOutsideClickListener(),this.unbindResizeListener(),this.scrollHandler&&(this.scrollHandler.destroy(),this.scrollHandler=null),this.overlay&&(X.clear(this.overlay),this.overlay=null)},methods:{getOptionIndex:function(e,o){return this.virtualScrollerDisabled?e:o&&o(e).index},getOptionLabel:function(e){return this.optionLabel?U(e,this.optionLabel):e},getOptionValue:function(e){return e},getOptionRenderKey:function(e,o){return(this.dataKey?U(e,this.dataKey):this.getOptionLabel(e))+"_"+o},getPTOptions:function(e,o,n,s){return this.ptm(s,{context:{selected:this.isSelected(e),focused:this.focusedOptionIndex===this.getOptionIndex(n,o),disabled:this.isOptionDisabled(e)}})},isOptionDisabled:function(e){return this.optionDisabled?U(e,this.optionDisabled):!1},isOptionGroup:function(e){return this.optionGroupLabel&&e.optionGroup&&e.group},getOptionGroupLabel:function(e){return U(e,this.optionGroupLabel)},getOptionGroupChildren:function(e){return U(e,this.optionGroupChildren)},getAriaPosInset:function(e){var o=this;return(this.optionGroupLabel?e-this.visibleOptions.slice(0,e).filter(function(n){return o.isOptionGroup(n)}).length:e)+1},show:function(e){this.$emit("before-show"),this.dirty=!0,this.overlayVisible=!0,this.focusedOptionIndex=this.focusedOptionIndex!==-1?this.focusedOptionIndex:this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1,e&&E(this.multiple?this.$refs.focusInput:this.$refs.focusInput.$el)},hide:function(e){var o=this,n=function(){o.$emit("before-hide"),o.dirty=e,o.overlayVisible=!1,o.clicked=!1,o.focusedOptionIndex=-1,e&&E(o.multiple?o.$refs.focusInput:o.$refs.focusInput.$el)};setTimeout(function(){n()},0)},onFocus:function(e){this.disabled||(!this.dirty&&this.completeOnFocus&&this.search(e,e.target.value,"focus"),this.dirty=!0,this.focused=!0,this.overlayVisible&&(this.focusedOptionIndex=this.focusedOptionIndex!==-1?this.focusedOptionIndex:this.overlayVisible&&this.autoOptionFocus?this.findFirstFocusedOptionIndex():-1,this.scrollInView(this.focusedOptionIndex)),this.$emit("focus",e))},onBlur:function(e){var o,n;this.dirty=!1,this.focused=!1,this.focusedOptionIndex=-1,this.$emit("blur",e),(o=(n=this.formField).onBlur)===null||o===void 0||o.call(n)},onKeyDown:function(e){if(this.disabled){e.preventDefault();return}switch(e.code){case"ArrowDown":this.onArrowDownKey(e);break;case"ArrowUp":this.onArrowUpKey(e);break;case"ArrowLeft":this.onArrowLeftKey(e);break;case"ArrowRight":this.onArrowRightKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":this.onEnterKey(e);break;case"Escape":this.onEscapeKey(e);break;case"Tab":this.onTabKey(e);break;case"Backspace":this.onBackspaceKey(e);break}this.clicked=!1},onInput:function(e){var o=this;if(this.typeahead){this.searchTimeout&&clearTimeout(this.searchTimeout);var n=e.target.value;this.multiple||this.updateModel(e,n),n.length===0?(this.hide(),this.$emit("clear")):n.length>=this.minLength?(this.focusedOptionIndex=-1,this.searchTimeout=setTimeout(function(){o.search(e,n,"input")},this.delay)):this.hide()}},onChange:function(e){var o=this;if(this.forceSelection){var n=!1;if(this.visibleOptions&&!this.multiple){var s=this.multiple?this.$refs.focusInput.value:this.$refs.focusInput.$el.value,i=this.visibleOptions.find(function(b){return o.isOptionMatched(b,s||"")});i!==void 0&&(n=!0,!this.isSelected(i)&&this.onOptionSelect(e,i))}n||(this.multiple?this.$refs.focusInput.value="":this.$refs.focusInput.$el.value="",this.$emit("clear"),!this.multiple&&this.updateModel(e,null))}},onMultipleContainerFocus:function(){this.disabled||(this.focused=!0)},onMultipleContainerBlur:function(){this.focusedMultipleOptionIndex=-1,this.focused=!1},onMultipleContainerKeyDown:function(e){if(this.disabled){e.preventDefault();return}switch(e.code){case"ArrowLeft":this.onArrowLeftKeyOnMultiple(e);break;case"ArrowRight":this.onArrowRightKeyOnMultiple(e);break;case"Backspace":this.onBackspaceKeyOnMultiple(e);break}},onContainerClick:function(e){this.clicked=!0,!(this.disabled||this.searching||this.loading||this.isDropdownClicked(e))&&(!this.overlay||!this.overlay.contains(e.target))&&E(this.multiple?this.$refs.focusInput:this.$refs.focusInput.$el)},onDropdownClick:function(e){var o=void 0;if(this.overlayVisible)this.hide(!0);else{var n=this.multiple?this.$refs.focusInput:this.$refs.focusInput.$el;E(n),o=n.value,this.dropdownMode==="blank"?this.search(e,"","dropdown"):this.dropdownMode==="current"&&this.search(e,o,"dropdown")}this.$emit("dropdown-click",{originalEvent:e,query:o})},onOptionSelect:function(e,o){var n=arguments.length>2&&arguments[2]!==void 0?arguments[2]:!0,s=this.getOptionValue(o);this.multiple?(this.$refs.focusInput.value="",this.isSelected(o)||this.updateModel(e,[].concat(ae(this.d_value||[]),[s]))):this.updateModel(e,s),this.$emit("item-select",{originalEvent:e,value:o}),this.$emit("option-select",{originalEvent:e,value:o}),n&&this.hide(!0)},onOptionMouseMove:function(e,o){this.focusOnHover&&this.changeFocusedOptionIndex(e,o)},onOverlayClick:function(e){he.emit("overlay-click",{originalEvent:e,target:this.$el})},onOverlayKeyDown:function(e){switch(e.code){case"Escape":this.onEscapeKey(e);break}},onArrowDownKey:function(e){if(this.overlayVisible){var o=this.focusedOptionIndex!==-1?this.findNextOptionIndex(this.focusedOptionIndex):this.clicked?this.findFirstOptionIndex():this.findFirstFocusedOptionIndex();this.changeFocusedOptionIndex(e,o),e.preventDefault()}},onArrowUpKey:function(e){if(this.overlayVisible)if(e.altKey)this.focusedOptionIndex!==-1&&this.onOptionSelect(e,this.visibleOptions[this.focusedOptionIndex]),this.overlayVisible&&this.hide(),e.preventDefault();else{var o=this.focusedOptionIndex!==-1?this.findPrevOptionIndex(this.focusedOptionIndex):this.clicked?this.findLastOptionIndex():this.findLastFocusedOptionIndex();this.changeFocusedOptionIndex(e,o),e.preventDefault()}},onArrowLeftKey:function(e){var o=e.currentTarget;this.focusedOptionIndex=-1,this.multiple&&(me(o.value)&&this.$filled?(E(this.$refs.multiContainer),this.focusedMultipleOptionIndex=this.d_value.length):e.stopPropagation())},onArrowRightKey:function(e){this.focusedOptionIndex=-1,this.multiple&&e.stopPropagation()},onHomeKey:function(e){var o=e.currentTarget,n=o.value.length;o.setSelectionRange(0,e.shiftKey?n:0),this.focusedOptionIndex=-1,e.preventDefault()},onEndKey:function(e){var o=e.currentTarget,n=o.value.length;o.setSelectionRange(e.shiftKey?0:n,n),this.focusedOptionIndex=-1,e.preventDefault()},onPageUpKey:function(e){this.scrollInView(0),e.preventDefault()},onPageDownKey:function(e){this.scrollInView(this.visibleOptions.length-1),e.preventDefault()},onEnterKey:function(e){this.typeahead?this.overlayVisible?(this.focusedOptionIndex!==-1&&this.onOptionSelect(e,this.visibleOptions[this.focusedOptionIndex]),this.hide()):(this.focusedOptionIndex=-1,this.onArrowDownKey(e)):this.multiple&&(this.updateModel(e,[].concat(ae(this.d_value||[]),[e.target.value])),this.$refs.focusInput.value=""),e.preventDefault()},onEscapeKey:function(e){this.overlayVisible&&this.hide(!0),e.preventDefault()},onTabKey:function(e){this.focusedOptionIndex!==-1&&this.onOptionSelect(e,this.visibleOptions[this.focusedOptionIndex]),this.overlayVisible&&this.hide()},onBackspaceKey:function(e){if(this.multiple){if(N(this.d_value)&&!this.$refs.focusInput.value){var o=this.d_value[this.d_value.length-1],n=this.d_value.slice(0,-1);this.writeValue(n,e),this.$emit("item-unselect",{originalEvent:e,value:o}),this.$emit("option-unselect",{originalEvent:e,value:o})}e.stopPropagation()}},onArrowLeftKeyOnMultiple:function(){this.focusedMultipleOptionIndex=this.focusedMultipleOptionIndex<1?0:this.focusedMultipleOptionIndex-1},onArrowRightKeyOnMultiple:function(){this.focusedMultipleOptionIndex++,this.focusedMultipleOptionIndex>this.d_value.length-1&&(this.focusedMultipleOptionIndex=-1,E(this.$refs.focusInput))},onBackspaceKeyOnMultiple:function(e){this.focusedMultipleOptionIndex!==-1&&this.removeOption(e,this.focusedMultipleOptionIndex)},onOverlayEnter:function(e){X.set("overlay",e,this.$primevue.config.zIndex.overlay),be(e,{position:"absolute",top:"0",left:"0"}),this.alignOverlay()},onOverlayAfterEnter:function(){this.bindOutsideClickListener(),this.bindScrollListener(),this.bindResizeListener(),this.$emit("show")},onOverlayLeave:function(){this.unbindOutsideClickListener(),this.unbindScrollListener(),this.unbindResizeListener(),this.$emit("hide"),this.overlay=null},onOverlayAfterLeave:function(e){X.clear(e)},alignOverlay:function(){var e=this.multiple?this.$refs.multiContainer:this.$refs.focusInput.$el;this.appendTo==="self"?ve(this.overlay,e):(this.overlay.style.minWidth=ye(e)+"px",ge(this.overlay,e))},bindOutsideClickListener:function(){var e=this;this.outsideClickListener||(this.outsideClickListener=function(o){e.overlayVisible&&e.overlay&&e.isOutsideClicked(o)&&e.hide()},document.addEventListener("click",this.outsideClickListener))},unbindOutsideClickListener:function(){this.outsideClickListener&&(document.removeEventListener("click",this.outsideClickListener),this.outsideClickListener=null)},bindScrollListener:function(){var e=this;this.scrollHandler||(this.scrollHandler=new Oe(this.$refs.container,function(){e.overlayVisible&&e.hide()})),this.scrollHandler.bindScrollListener()},unbindScrollListener:function(){this.scrollHandler&&this.scrollHandler.unbindScrollListener()},bindResizeListener:function(){var e=this;this.resizeListener||(this.resizeListener=function(){e.overlayVisible&&!we()&&e.hide()},window.addEventListener("resize",this.resizeListener))},unbindResizeListener:function(){this.resizeListener&&(window.removeEventListener("resize",this.resizeListener),this.resizeListener=null)},isOutsideClicked:function(e){return!this.overlay.contains(e.target)&&!this.isInputClicked(e)&&!this.isDropdownClicked(e)},isInputClicked:function(e){return this.multiple?e.target===this.$refs.multiContainer||this.$refs.multiContainer.contains(e.target):e.target===this.$refs.focusInput.$el},isDropdownClicked:function(e){return this.$refs.dropdownButton?e.target===this.$refs.dropdownButton||this.$refs.dropdownButton.contains(e.target):!1},isOptionMatched:function(e,o){var n;return this.isValidOption(e)&&((n=this.getOptionLabel(e))===null||n===void 0?void 0:n.toLocaleLowerCase(this.searchLocale))===o.toLocaleLowerCase(this.searchLocale)},isValidOption:function(e){return N(e)&&!(this.isOptionDisabled(e)||this.isOptionGroup(e))},isValidSelectedOption:function(e){return this.isValidOption(e)&&this.isSelected(e)},isEquals:function(e,o){return Ie(e,o,this.equalityKey)},isSelected:function(e){var o=this,n=this.getOptionValue(e);return this.multiple?(this.d_value||[]).some(function(s){return o.isEquals(s,n)}):this.isEquals(this.d_value,this.getOptionValue(e))},findFirstOptionIndex:function(){var e=this;return this.visibleOptions.findIndex(function(o){return e.isValidOption(o)})},findLastOptionIndex:function(){var e=this;return ie(this.visibleOptions,function(o){return e.isValidOption(o)})},findNextOptionIndex:function(e){var o=this,n=e<this.visibleOptions.length-1?this.visibleOptions.slice(e+1).findIndex(function(s){return o.isValidOption(s)}):-1;return n>-1?n+e+1:e},findPrevOptionIndex:function(e){var o=this,n=e>0?ie(this.visibleOptions.slice(0,e),function(s){return o.isValidOption(s)}):-1;return n>-1?n:e},findSelectedOptionIndex:function(){var e=this;return this.$filled?this.visibleOptions.findIndex(function(o){return e.isValidSelectedOption(o)}):-1},findFirstFocusedOptionIndex:function(){var e=this.findSelectedOptionIndex();return e<0?this.findFirstOptionIndex():e},findLastFocusedOptionIndex:function(){var e=this.findSelectedOptionIndex();return e<0?this.findLastOptionIndex():e},search:function(e,o,n){o!=null&&(n==="input"&&o.trim().length===0||(this.searching=!0,this.$emit("complete",{originalEvent:e,query:o})))},removeOption:function(e,o){var n=this,s=this.d_value[o],i=this.d_value.filter(function(b,A){return A!==o}).map(function(b){return n.getOptionValue(b)});this.updateModel(e,i),this.$emit("item-unselect",{originalEvent:e,value:s}),this.$emit("option-unselect",{originalEvent:e,value:s}),this.dirty=!0,E(this.multiple?this.$refs.focusInput:this.$refs.focusInput.$el)},changeFocusedOptionIndex:function(e,o){this.focusedOptionIndex!==o&&(this.focusedOptionIndex=o,this.scrollInView(),this.selectOnFocus&&this.onOptionSelect(e,this.visibleOptions[o],!1))},scrollInView:function(){var e=this,o=arguments.length>0&&arguments[0]!==void 0?arguments[0]:-1;this.$nextTick(function(){var n=o!==-1?"".concat(e.id,"_").concat(o):e.focusedOptionId,s=ke(e.list,'li[id="'.concat(n,'"]'));s?s.scrollIntoView&&s.scrollIntoView({block:"nearest",inline:"start"}):e.virtualScrollerDisabled||e.virtualScroller&&e.virtualScroller.scrollToIndex(o!==-1?o:e.focusedOptionIndex)})},autoUpdateModel:function(){this.selectOnFocus&&this.autoOptionFocus&&!this.$filled&&(this.focusedOptionIndex=this.findFirstFocusedOptionIndex(),this.onOptionSelect(null,this.visibleOptions[this.focusedOptionIndex],!1))},updateModel:function(e,o){this.writeValue(o,e),this.$emit("change",{originalEvent:e,value:o})},flatOptions:function(e){var o=this;return(e||[]).reduce(function(n,s,i){n.push({optionGroup:s,group:!0,index:i});var b=o.getOptionGroupChildren(s);return b&&b.forEach(function(A){return n.push(A)}),n},[])},overlayRef:function(e){this.overlay=e},listRef:function(e,o){this.list=e,o&&o(e)},virtualScrollerRef:function(e){this.virtualScroller=e}},computed:{visibleOptions:function(){return this.optionGroupLabel?this.flatOptions(this.suggestions):this.suggestions||[]},inputValue:function(){if(this.$filled)if(ee(this.d_value)==="object"){var e=this.getOptionLabel(this.d_value);return e??this.d_value}else return this.d_value;else return""},hasSelectedOption:function(){return this.$filled},equalityKey:function(){return this.dataKey},searchResultMessageText:function(){return N(this.visibleOptions)&&this.overlayVisible?this.searchMessageText.replaceAll("{0}",this.visibleOptions.length):this.emptySearchMessageText},searchMessageText:function(){return this.searchMessage||this.$primevue.config.locale.searchMessage||""},emptySearchMessageText:function(){return this.emptySearchMessage||this.$primevue.config.locale.emptySearchMessage||""},selectionMessageText:function(){return this.selectionMessage||this.$primevue.config.locale.selectionMessage||""},emptySelectionMessageText:function(){return this.emptySelectionMessage||this.$primevue.config.locale.emptySelectionMessage||""},selectedMessageText:function(){return this.$filled?this.selectionMessageText.replaceAll("{0}",this.multiple?this.d_value.length:"1"):this.emptySelectionMessageText},listAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.listLabel:void 0},focusedOptionId:function(){return this.focusedOptionIndex!==-1?"".concat(this.id,"_").concat(this.focusedOptionIndex):null},focusedMultipleOptionId:function(){return this.focusedMultipleOptionIndex!==-1?"".concat(this.id,"_multiple_option_").concat(this.focusedMultipleOptionIndex):null},ariaSetSize:function(){var e=this;return this.visibleOptions.filter(function(o){return!e.isOptionGroup(o)}).length},virtualScrollerDisabled:function(){return!this.virtualScrollerOptions},panelId:function(){return this.id+"_panel"}},components:{InputText:K,VirtualScroller:Ce,Portal:Se,ChevronDownIcon:Le,SpinnerIcon:Me,Chip:Ue},directives:{ripple:xe}};function $(t){"@babel/helpers - typeof";return $=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},$(t)}function se(t,e){var o=Object.keys(t);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter(function(s){return Object.getOwnPropertyDescriptor(t,s).enumerable})),o.push.apply(o,n)}return o}function re(t){for(var e=1;e<arguments.length;e++){var o=arguments[e]!=null?arguments[e]:{};e%2?se(Object(o),!0).forEach(function(n){et(t,n,o[n])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(o)):se(Object(o)).forEach(function(n){Object.defineProperty(t,n,Object.getOwnPropertyDescriptor(o,n))})}return t}function et(t,e,o){return(e=tt(e))in t?Object.defineProperty(t,e,{value:o,enumerable:!0,configurable:!0,writable:!0}):t[e]=o,t}function tt(t){var e=ot(t,"string");return $(e)=="symbol"?e:e+""}function ot(t,e){if($(t)!="object"||!t)return t;var o=t[Symbol.toPrimitive];if(o!==void 0){var n=o.call(t,e||"default");if($(n)!="object")return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var nt=["aria-activedescendant"],it=["id","aria-label","aria-setsize","aria-posinset"],lt=["id","placeholder","tabindex","disabled","aria-label","aria-labelledby","aria-expanded","aria-controls","aria-activedescendant","aria-invalid"],at=["disabled","aria-expanded","aria-controls"],st=["id"],rt=["id","aria-label"],ut=["id"],ct=["id","aria-label","aria-selected","aria-disabled","aria-setsize","aria-posinset","onClick","onMousemove","data-p-selected","data-p-focus","data-p-disabled"];function dt(t,e,o,n,s,i){var b=j("InputText"),A=j("Chip"),q=j("SpinnerIcon"),W=j("VirtualScroller"),Z=j("Portal"),H=Ve("ripple");return d(),h("div",m({ref:"container",class:t.cx("root"),style:t.sx("root"),onClick:e[11]||(e[11]=function(){return i.onContainerClick&&i.onContainerClick.apply(i,arguments)})},t.ptmi("root")),[t.multiple?M("",!0):(d(),z(b,{key:0,ref:"focusInput",id:t.inputId,type:"text",name:t.$formName,class:G([t.cx("pcInputText"),t.inputClass]),style:Ke(t.inputStyle),value:i.inputValue,placeholder:t.placeholder,tabindex:t.disabled?-1:t.tabindex,fluid:t.$fluid,disabled:t.disabled,size:t.size,invalid:t.invalid,variant:t.variant,autocomplete:"off",role:"combobox","aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"aria-haspopup":"listbox","aria-autocomplete":"list","aria-expanded":s.overlayVisible,"aria-controls":i.panelId,"aria-activedescendant":s.focused?i.focusedOptionId:void 0,onFocus:i.onFocus,onBlur:i.onBlur,onKeydown:i.onKeyDown,onInput:i.onInput,onChange:i.onChange,unstyled:t.unstyled,pt:t.ptm("pcInputText")},null,8,["id","name","class","style","value","placeholder","tabindex","fluid","disabled","size","invalid","variant","aria-label","aria-labelledby","aria-expanded","aria-controls","aria-activedescendant","onFocus","onBlur","onKeydown","onInput","onChange","unstyled","pt"])),t.multiple?(d(),h("ul",m({key:1,ref:"multiContainer",class:t.cx("inputMultiple"),tabindex:"-1",role:"listbox","aria-orientation":"horizontal","aria-activedescendant":s.focused?i.focusedMultipleOptionId:void 0,onFocus:e[5]||(e[5]=function(){return i.onMultipleContainerFocus&&i.onMultipleContainerFocus.apply(i,arguments)}),onBlur:e[6]||(e[6]=function(){return i.onMultipleContainerBlur&&i.onMultipleContainerBlur.apply(i,arguments)}),onKeydown:e[7]||(e[7]=function(){return i.onMultipleContainerKeyDown&&i.onMultipleContainerKeyDown.apply(i,arguments)})},t.ptm("inputMultiple")),[(d(!0),h(x,null,D(t.d_value,function(v,y){return d(),h("li",m({key:"".concat(y,"_").concat(i.getOptionLabel(v)),id:s.id+"_multiple_option_"+y,class:t.cx("chipItem",{i:y}),role:"option","aria-label":i.getOptionLabel(v),"aria-selected":!0,"aria-setsize":t.d_value.length,"aria-posinset":y+1,ref_for:!0},t.ptm("chipItem")),[S(t.$slots,"chip",m({class:t.cx("pcChip"),value:v,index:y,removeCallback:function(O){return i.removeOption(O,y)},ref_for:!0},t.ptm("pcChip")),function(){return[c(A,{class:G(t.cx("pcChip")),label:i.getOptionLabel(v),removeIcon:t.chipIcon||t.removeTokenIcon,removable:"",unstyled:t.unstyled,onRemove:function(O){return i.removeOption(O,y)},pt:t.ptm("pcChip")},{removeicon:L(function(){return[S(t.$slots,t.$slots.chipicon?"chipicon":"removetokenicon",{class:G(t.cx("chipIcon")),index:y,removeCallback:function(O){return i.removeOption(O,y)}})]}),_:2},1032,["class","label","removeIcon","unstyled","onRemove","pt"])]})],16,it)}),128)),f("li",m({class:t.cx("inputChip"),role:"option"},t.ptm("inputChip")),[f("input",m({ref:"focusInput",id:t.inputId,type:"text",style:t.inputStyle,class:t.inputClass,placeholder:t.placeholder,tabindex:t.disabled?-1:t.tabindex,disabled:t.disabled,autocomplete:"off",role:"combobox","aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"aria-haspopup":"listbox","aria-autocomplete":"list","aria-expanded":s.overlayVisible,"aria-controls":s.id+"_list","aria-activedescendant":s.focused?i.focusedOptionId:void 0,"aria-invalid":t.invalid||void 0,onFocus:e[0]||(e[0]=function(){return i.onFocus&&i.onFocus.apply(i,arguments)}),onBlur:e[1]||(e[1]=function(){return i.onBlur&&i.onBlur.apply(i,arguments)}),onKeydown:e[2]||(e[2]=function(){return i.onKeyDown&&i.onKeyDown.apply(i,arguments)}),onInput:e[3]||(e[3]=function(){return i.onInput&&i.onInput.apply(i,arguments)}),onChange:e[4]||(e[4]=function(){return i.onChange&&i.onChange.apply(i,arguments)})},t.ptm("input")),null,16,lt)],16)],16,nt)):M("",!0),s.searching||t.loading?S(t.$slots,t.$slots.loader?"loader":"loadingicon",{key:2,class:G(t.cx("loader"))},function(){return[t.loader||t.loadingIcon?(d(),h("i",m({key:0,class:["pi-spin",t.cx("loader"),t.loader,t.loadingIcon],"aria-hidden":"true"},t.ptm("loader")),null,16)):(d(),z(q,m({key:1,class:t.cx("loader"),spin:"","aria-hidden":"true"},t.ptm("loader")),null,16,["class"]))]}):M("",!0),S(t.$slots,t.$slots.dropdown?"dropdown":"dropdownbutton",{toggleCallback:function(y){return i.onDropdownClick(y)}},function(){return[t.dropdown?(d(),h("button",m({key:0,ref:"dropdownButton",type:"button",class:[t.cx("dropdown"),t.dropdownClass],disabled:t.disabled,"aria-haspopup":"listbox","aria-expanded":s.overlayVisible,"aria-controls":i.panelId,onClick:e[8]||(e[8]=function(){return i.onDropdownClick&&i.onDropdownClick.apply(i,arguments)})},t.ptm("dropdown")),[S(t.$slots,"dropdownicon",{class:G(t.dropdownIcon)},function(){return[(d(),z(De(t.dropdownIcon?"span":"ChevronDownIcon"),m({class:t.dropdownIcon},t.ptm("dropdownIcon")),null,16,["class"]))]})],16,at)):M("",!0)]}),f("span",m({role:"status","aria-live":"polite",class:"p-hidden-accessible"},t.ptm("hiddenSearchResult"),{"data-p-hidden-accessible":!0}),T(i.searchResultMessageText),17),c(Z,{appendTo:t.appendTo},{default:L(function(){return[c(Te,m({name:"p-connected-overlay",onEnter:i.onOverlayEnter,onAfterEnter:i.onOverlayAfterEnter,onLeave:i.onOverlayLeave,onAfterLeave:i.onOverlayAfterLeave},t.ptm("transition")),{default:L(function(){return[s.overlayVisible?(d(),h("div",m({key:0,ref:i.overlayRef,id:i.panelId,class:[t.cx("overlay"),t.panelClass,t.overlayClass],style:re(re({},t.panelStyle),t.overlayStyle),onClick:e[9]||(e[9]=function(){return i.onOverlayClick&&i.onOverlayClick.apply(i,arguments)}),onKeydown:e[10]||(e[10]=function(){return i.onOverlayKeyDown&&i.onOverlayKeyDown.apply(i,arguments)})},t.ptm("overlay")),[S(t.$slots,"header",{value:t.d_value,suggestions:i.visibleOptions}),f("div",m({class:t.cx("listContainer"),style:{"max-height":i.virtualScrollerDisabled?t.scrollHeight:""}},t.ptm("listContainer")),[c(W,m({ref:i.virtualScrollerRef},t.virtualScrollerOptions,{style:{height:t.scrollHeight},items:i.visibleOptions,tabindex:-1,disabled:i.virtualScrollerDisabled,pt:t.ptm("virtualScroller")}),Ae({content:L(function(v){var y=v.styleClass,P=v.contentRef,O=v.items,k=v.getItemOptions,J=v.contentStyle,B=v.itemSize;return[f("ul",m({ref:function(w){return i.listRef(w,P)},id:s.id+"_list",class:[t.cx("list"),y],style:J,role:"listbox","aria-label":i.listAriaLabel},t.ptm("list")),[(d(!0),h(x,null,D(O,function(g,w){return d(),h(x,{key:i.getOptionRenderKey(g,i.getOptionIndex(w,k))},[i.isOptionGroup(g)?(d(),h("li",m({key:0,id:s.id+"_"+i.getOptionIndex(w,k),style:{height:B?B+"px":void 0},class:t.cx("optionGroup"),role:"option",ref_for:!0},t.ptm("optionGroup")),[S(t.$slots,"optiongroup",{option:g.optionGroup,index:i.getOptionIndex(w,k)},function(){return[Y(T(i.getOptionGroupLabel(g.optionGroup)),1)]})],16,ut)):Ee((d(),h("li",m({key:1,id:s.id+"_"+i.getOptionIndex(w,k),style:{height:B?B+"px":void 0},class:t.cx("option",{option:g,i:w,getItemOptions:k}),role:"option","aria-label":i.getOptionLabel(g),"aria-selected":i.isSelected(g),"aria-disabled":i.isOptionDisabled(g),"aria-setsize":i.ariaSetSize,"aria-posinset":i.getAriaPosInset(i.getOptionIndex(w,k)),onClick:function(R){return i.onOptionSelect(R,g)},onMousemove:function(R){return i.onOptionMouseMove(R,i.getOptionIndex(w,k))},"data-p-selected":i.isSelected(g),"data-p-focus":s.focusedOptionIndex===i.getOptionIndex(w,k),"data-p-disabled":i.isOptionDisabled(g),ref_for:!0},i.getPTOptions(g,k,w,"option")),[S(t.$slots,"option",{option:g,index:i.getOptionIndex(w,k)},function(){return[Y(T(i.getOptionLabel(g)),1)]})],16,ct)),[[H]])],64)}),128)),t.showEmptyMessage&&(!O||O&&O.length===0)?(d(),h("li",m({key:0,class:t.cx("emptyMessage"),role:"option"},t.ptm("emptyMessage")),[S(t.$slots,"empty",{},function(){return[Y(T(i.searchResultMessageText),1)]})],16)):M("",!0)],16,rt)]}),_:2},[t.$slots.loader?{name:"loader",fn:L(function(v){var y=v.options;return[S(t.$slots,"loader",{options:y})]}),key:"0"}:void 0]),1040,["style","items","disabled","pt"])],16),S(t.$slots,"footer",{value:t.d_value,suggestions:i.visibleOptions}),f("span",m({role:"status","aria-live":"polite",class:"p-hidden-accessible"},t.ptm("hiddenSelectedMessage"),{"data-p-hidden-accessible":!0}),T(i.selectedMessageText),17)],16,st)):M("",!0)]}),_:3},16,["onEnter","onAfterEnter","onLeave","onAfterLeave"])]}),_:3},8,["appendTo"])],16)}oe.render=dt;const pt={class:"clientes-container"},ft={class:"clientes-filtros"},ht={class:"clientes-card"},mt={class:"list-inline"},bt={class:"list-inline"},vt={class:"chip chip-usuario"},yt={class:"list-inline"},gt={class:"chip chip-plataforma"},Ot={class:"form-group"},wt={class:"form-group"},It={class:"form-group"},kt={class:"form-group"},Ct={class:"form-group"},St={class:"form-group"},Lt={class:"modal-actions"},Mt={__name:"Clientes",setup(t){const e=V([]),o=V(!1),n=V({id:null,nombre:"",telefonos:[""],correo:"",direccion:"",usuarios:[""],plataformas:[""]}),s=V(""),i=V(null),b=V(null),A=()=>{s.value="",i.value=null,b.value=null},q=_(()=>e.value.filter(a=>{const l=!s.value||a.nombre.toLowerCase().includes(s.value.toLowerCase()),r=!i.value||a.usuarios&&a.usuarios.includes(i.value),u=!b.value||a.plataformas&&a.plataformas.includes(b.value);return l&&r&&u})),W=_(()=>{const a=new Set;return e.value.forEach(l=>(l.usuarios||[]).forEach(r=>a.add(r))),Array.from(a).map(l=>({label:l,value:l}))}),Z=_(()=>{const a=new Set;return e.value.forEach(l=>(l.plataformas||[]).forEach(r=>a.add(r))),Array.from(a).map(l=>({label:l,value:l}))}),H=V([]),v=V([]),y=a=>{var r;const l=((r=a.query)==null?void 0:r.toLowerCase())||"";H.value=W.value.filter(u=>u.label.toLowerCase().includes(l))},P=a=>{var r;const l=((r=a.query)==null?void 0:r.toLowerCase())||"";v.value=Z.value.filter(u=>u.label.toLowerCase().includes(l))},O=async()=>{e.value=await je()};Be(O);const k=()=>{n.value={id:null,nombre:"",telefonos:[""],correo:"",direccion:"",usuarios:[""],plataformas:[""]},o.value=!0},J=()=>{o.value=!1},B=async()=>{n.value.nombre&&(n.value.telefonos=n.value.telefonos.filter(a=>a),n.value.usuarios=n.value.usuarios.filter(a=>a),n.value.plataformas=n.value.plataformas.filter(a=>a),n.value.id?await Ge(n.value.id,n.value):await $e(n.value),o.value=!1,await O())},g=a=>{var l,r,u;n.value={id:a.id,nombre:a.nombre,telefonos:(l=a.telefonos)!=null&&l.length?[...a.telefonos]:[""],correo:a.correo,direccion:a.direccion,usuarios:(r=a.usuarios)!=null&&r.length?[...a.usuarios]:[""],plataformas:(u=a.plataformas)!=null&&u.length?[...a.plataformas]:[""]},o.value=!0},w=async a=>{await He(a),await O()},Q=()=>n.value.telefonos.push(""),R=a=>n.value.telefonos.splice(a,1),ue=()=>n.value.usuarios.push(""),ce=a=>n.value.usuarios.splice(a,1),de=()=>n.value.plataformas.push(""),pe=a=>n.value.plataformas.splice(a,1);return le(i,a=>{typeof a=="object"&&a!==null&&(i.value=a.label)}),le(b,a=>{typeof a=="object"&&a!==null&&(b.value=a.label)}),(a,l)=>(d(),h("div",pt,[l[15]||(l[15]=f("h2",{class:"clientes-title"},"Clientes",-1)),f("div",ft,[c(p(K),{modelValue:s.value,"onUpdate:modelValue":l[0]||(l[0]=r=>s.value=r),placeholder:"Buscar por nombre...",class:"filtro-input",clearable:""},null,8,["modelValue"]),c(p(oe),{modelValue:i.value,"onUpdate:modelValue":l[1]||(l[1]=r=>i.value=r),suggestions:H.value,onComplete:y,optionLabel:"label",placeholder:"Filtrar por usuario",class:"filtro-autocomplete",dropdown:!0,forceSelection:"",onItemSelect:l[2]||(l[2]=r=>i.value=r.value.label)},null,8,["modelValue","suggestions"]),c(p(oe),{modelValue:b.value,"onUpdate:modelValue":l[3]||(l[3]=r=>b.value=r),suggestions:v.value,onComplete:P,optionLabel:"label",placeholder:"Filtrar por plataforma",class:"filtro-autocomplete",dropdown:!0,forceSelection:"",onItemSelect:l[4]||(l[4]=r=>b.value=r.value.label)},null,8,["modelValue","suggestions"]),c(p(C),{label:"Limpiar",icon:"pi pi-times",class:"p-button-secondary",onClick:A}),c(p(C),{label:"Agregar Cliente",icon:"pi pi-plus",onClick:k,class:"p-button-success"})]),f("div",ht,[c(p(ze),{value:q.value,stripedRows:"",responsiveLayout:"scroll",class:"clientes-table"},{default:L(()=>[c(p(F),{field:"nombre",header:"Nombre"}),c(p(F),{field:"telefono",header:"Teléfonos"},{body:L(r=>[f("ul",mt,[(d(!0),h(x,null,D(r.data.telefonos,(u,I)=>(d(),h("li",{key:I},T(u),1))),128))])]),_:1}),c(p(F),{field:"correo",header:"Correo"}),c(p(F),{field:"direccion",header:"Dirección"}),c(p(F),{header:"Usuarios"},{body:L(r=>[f("ul",bt,[(d(!0),h(x,null,D(r.data.usuarios,(u,I)=>(d(),h("li",{key:I},[f("span",vt,T(u),1)]))),128))])]),_:1}),c(p(F),{header:"Plataformas"},{body:L(r=>[f("ul",yt,[(d(!0),h(x,null,D(r.data.plataformas,(u,I)=>(d(),h("li",{key:I},[f("span",gt,T(u),1)]))),128))])]),_:1}),c(p(F),{header:"Acciones","body-class":"acciones-col"},{body:L(r=>[c(p(C),{icon:"pi pi-pencil",class:"p-button-rounded p-button-text p-button-info",onClick:u=>g(r.data)},null,8,["onClick"]),c(p(C),{icon:"pi pi-trash",class:"p-button-rounded p-button-text p-button-danger",onClick:u=>w(r.data.id)},null,8,["onClick"])]),_:1})]),_:1},8,["value"])]),c(p(Re),{visible:o.value,"onUpdate:visible":l[8]||(l[8]=r=>o.value=r),header:n.value.id?"Editar Cliente":"Nuevo Cliente",modal:!0,closable:!0,class:"clientes-dialog"},{default:L(()=>[f("div",Ot,[l[9]||(l[9]=f("label",{for:"nombre"},"Nombre:",-1)),c(p(K),{id:"nombre",modelValue:n.value.nombre,"onUpdate:modelValue":l[5]||(l[5]=r=>n.value.nombre=r),class:"w-full"},null,8,["modelValue"])]),f("div",wt,[l[10]||(l[10]=f("label",null,"Teléfonos:",-1)),(d(!0),h(x,null,D(n.value.telefonos,(r,u)=>(d(),h("div",{key:u,class:"input-row"},[c(p(K),{modelValue:n.value.telefonos[u],"onUpdate:modelValue":I=>n.value.telefonos[u]=I,class:"w-full"},null,8,["modelValue","onUpdate:modelValue"]),n.value.telefonos.length>1?(d(),z(p(C),{key:0,icon:"pi pi-minus",class:"p-button-text p-button-danger",onClick:I=>R(u)},null,8,["onClick"])):M("",!0)]))),128)),c(p(C),{icon:"pi pi-plus",class:"p-button-text",onClick:Q})]),f("div",It,[l[11]||(l[11]=f("label",{for:"correo"},"Correo:",-1)),c(p(K),{id:"correo",modelValue:n.value.correo,"onUpdate:modelValue":l[6]||(l[6]=r=>n.value.correo=r),class:"w-full"},null,8,["modelValue"])]),f("div",kt,[l[12]||(l[12]=f("label",{for:"direccion"},"Dirección:",-1)),c(p(K),{id:"direccion",modelValue:n.value.direccion,"onUpdate:modelValue":l[7]||(l[7]=r=>n.value.direccion=r),class:"w-full"},null,8,["modelValue"])]),f("div",Ct,[l[13]||(l[13]=f("label",null,"Usuarios:",-1)),(d(!0),h(x,null,D(n.value.usuarios,(r,u)=>(d(),h("div",{key:u,class:"input-row"},[c(p(K),{modelValue:n.value.usuarios[u],"onUpdate:modelValue":I=>n.value.usuarios[u]=I,class:"w-full"},null,8,["modelValue","onUpdate:modelValue"]),n.value.usuarios.length>1?(d(),z(p(C),{key:0,icon:"pi pi-minus",class:"p-button-text p-button-danger",onClick:I=>ce(u)},null,8,["onClick"])):M("",!0)]))),128)),c(p(C),{icon:"pi pi-plus",class:"p-button-text",onClick:ue})]),f("div",St,[l[14]||(l[14]=f("label",null,"Plataformas:",-1)),(d(!0),h(x,null,D(n.value.plataformas,(r,u)=>(d(),h("div",{key:u,class:"input-row"},[c(p(K),{modelValue:n.value.plataformas[u],"onUpdate:modelValue":I=>n.value.plataformas[u]=I,class:"w-full"},null,8,["modelValue","onUpdate:modelValue"]),n.value.plataformas.length>1?(d(),z(p(C),{key:0,icon:"pi pi-minus",class:"p-button-text p-button-danger",onClick:I=>pe(u)},null,8,["onClick"])):M("",!0)]))),128)),c(p(C),{icon:"pi pi-plus",class:"p-button-text",onClick:de})]),f("div",Lt,[c(p(C),{label:"Guardar",icon:"pi pi-save",onClick:B}),c(p(C),{label:"Cancelar",icon:"pi pi-times",class:"p-button-secondary",onClick:J})])]),_:1},8,["visible","header"])]))}},Dt=Pe(Mt,[["__scopeId","data-v-4101274d"]]);export{Dt as default};
