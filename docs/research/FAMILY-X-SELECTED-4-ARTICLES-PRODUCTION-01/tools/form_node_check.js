const FL=require('../../../../user_test/selection_form_v3/form_logic.js');const fs=require('fs');
// NUANCE-CORNER-ABOLITION-01(2026-10-30): ニュアンス解説は廃止。フォームデータ検査+人間可読コピー生成の確認のみ。
process.chdir(require('path').resolve(__dirname,'../../../..'));
const idx=JSON.parse(fs.readFileSync('user_test/selection_form_v3/data/articles.json','utf8'));
console.log('validateIndex errs:',JSON.stringify(FL.validateIndex(idx)));
let bad=0;
for(const a of idx.articles.filter(a=>/untidiness|ai_chat|waddle|jwst/.test(a.slug))){
  const d=JSON.parse(fs.readFileSync('user_test/selection_form_v3/'+a.data,'utf8'));
  if(d.nuance_spec||d.nuance||d.nuance_note_ja){bad++;console.log('FAIL(old nuance data)',a.slug,a.level);}
  const st=FL.newState();
  st.comment='';
  try{ const r=FL.buildReadable(d,st,{stem:a.slug+'__'+a.level+'__prod',file_sha256:'abcdef123456'}); if(!r||r.length<50) throw new Error('short'); if(/ニュアンス/.test(r.replace(/意味・ニュアンス・表現効果/g,''))) throw new Error('nuance text in readable'); if(!/AIF1-/.test(r)) throw new Error('not AIF1'); }catch(e){bad++;console.log('FAIL',a.slug,a.level,e.message)}
  console.log(a.slug,a.level,'phrases',(d.phrases||[]).length,'words',(d.words||[]).length,'grammar',(d.grammar||[]).length);
}
console.log('bad',bad);
