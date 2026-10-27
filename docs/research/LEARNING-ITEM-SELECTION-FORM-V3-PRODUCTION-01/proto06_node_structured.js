// 設計検証用(本番コードではない): 既存フォームのFormLogic.buildStructured/buildTextを呼び、復元tool試作の期待値を得る。
// usage: node proto06_node_structured.js <form_logic.js> <data.json> <state.json>
const fs = require('fs');
const FL = require(require('path').resolve(process.argv[2]));
const d = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const st = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
process.stdout.write(JSON.stringify({ structured: FL.buildStructured(d, st, 'T0', { all_candidates: true }), old_text: FL.buildText(d, st),
  old_url: FL.buildChatGptUrl(d, st, 'T0'), old_copy_len: FL.buildCopyText(d, st, 'T0').length }));
