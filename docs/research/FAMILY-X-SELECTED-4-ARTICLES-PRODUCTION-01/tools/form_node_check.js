const FL=require('../user_test/selection_form_v3/form_logic.js');const fs=require('fs');
const idx=JSON.parse(fs.readFileSync('user_test/selection_form_v3/data/articles.json','utf8'));
console.log('validateIndex errs:',JSON.stringify(FL.validateIndex(idx)));
let bad=0;
for(const a of idx.articles.filter(a=>/untidiness|ai_chat|waddle|jwst/.test(a.slug))){
  const d=JSON.parse(fs.readFileSync('user_test/selection_form_v3/'+a.data,'utf8'));
  for(const dec of ['adopt','reject']){
    const st=FL.newState();
    if(FL.nuanceOf(d)) FL.chooseNuance(st,dec,d);
    st.comment='';
    try{ const r=FL.buildReadable(d,st,{stem:a.slug+'__'+a.level+'__prod',file_sha256:'abcdef123456'}); if(!r||r.length<50) throw new Error('short'); }catch(e){bad++;console.log('FAIL',a.slug,a.level,dec,e.message)}
    if(!FL.nuanceOf(d)) break;
  }
  console.log(a.slug,a.level,'nuance:',!!FL.nuanceOf(d),'phrases',(d.phrases||[]).length,'words',(d.words||[]).length,'grammar',(d.grammar||[]).length);
}
console.log('bad',bad);
