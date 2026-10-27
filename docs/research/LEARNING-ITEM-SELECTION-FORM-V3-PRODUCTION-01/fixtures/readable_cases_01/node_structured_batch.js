// fixture生成/契約test用: 既存フォームのFormLogic.buildStructured(正本)を、複数のdata+stateに対して一括実行する。
// usage: node node_structured_batch.js <form_logic.js> <jobs.json>   jobs=[{data:<data json path>, state:{...}}]
// 出力: JSON配列。各要素は buildStructured の article/selection/comment/grammar_status/grammar_decision/kp_confirmed(復元payloadとの比較対象)。
const fs = require('fs');
const FL = require(require('path').resolve(process.argv[2]));
const jobs = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = jobs.map(function (j) {
  const d = JSON.parse(fs.readFileSync(j.data, 'utf8'));
  const s = FL.buildStructured(d, j.state, 'T0', {});
  return { article: s.article, selection: s.selection, comment: s.comment, grammar_status: s.grammar_status, grammar_decision: s.grammar_decision || null, kp_confirmed: s.kp_confirmed || null };
});
process.stdout.write(JSON.stringify(out));
