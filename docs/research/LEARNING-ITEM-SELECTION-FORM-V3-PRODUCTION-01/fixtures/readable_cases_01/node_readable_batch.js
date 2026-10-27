// 契約test用: フォームJSの FormLogic.buildReadable をfixture全ケースで実行し {case名: 出力} を返す(Pythonの参照実装とバイト一致を検査する)。
// usage: node node_readable_batch.js <form_logic.js> <fixtures dir>
const fs = require('fs'), crypto = require('crypto');
const FL = require(require('path').resolve(process.argv[2]));
const fx = process.argv[3];
const man = JSON.parse(fs.readFileSync(fx + '/manifest.json', 'utf8'));
const out = {};
man.cases.forEach(function (c) {
  const lf = Buffer.from(fs.readFileSync(fx + '/data/' + c.stem + '.json').toString('latin1').replace(/\r\n/g, '\n'), 'latin1');   // d6はLF正規化したバイト列(公開Pagesと同じ)
  const d = JSON.parse(lf.toString('utf8'));
  const st = JSON.parse(fs.readFileSync(fx + '/cases/' + c.name + '.state.json', 'utf8')).state;
  out[c.name] = FL.buildReadable(d, st, { stem: c.stem, file_sha256: crypto.createHash('sha256').update(lf).digest('hex') });
});
process.stdout.write(JSON.stringify(out));
