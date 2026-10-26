# VERIFY_02 公開検証(2026-10-27、push `357a131bf`)
- 公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/
- HTTP 200: `/`(13290B)、`form_logic.js`、`data/articles.json`、`data/` 配下の候補データ全9ファイル(猿の手Trial-02/replay、AI島a2/b1b、再配達a2/b1b、メロスa2、ダミー)。
- 公開URLに対するheadless Chrome(CDP)実DOM検証 `browser_check_02_public_output.txt`: **pass=19 fail=0**、Console error/exception 0。確認内容=全候補行の日本語訳+状態ラベル、Trial-02は「仮訳・未確定」/Production候補(メロス)は「正式訳」、AI理由の折りたたみ(call1は「AI理由なし」明示、call2/補完は理由表示)、開閉状態の保持、選定→送信URLのデコード文に区分|英語|日本語訳【状態】・コメント・AI理由節(確定内容と分離)、コピーJSON v2(全候補・AI理由は確定itemに混入しない)、ダミーの文法解説全文の送信、6000字超で切り詰めず全項目入りコピー誘導。
- ローカル版: `browser_check_02_local_output.txt` pass=19 fail=0(同一内容)。

## ユーザー実操作確認チェックリスト(更新。未検証の外部挙動のみ)
1. 候補の各行に日本語訳(ラベル付き)が表示される。Production候補(AI島・再配達・メロス)は「正式訳」、猿の手(試作/replay)は「仮訳・未確定」。
2. 「AI理由・確認用」を開くと、call2/補完の候補は理由が出る。最初の候補生成(call1)は「AI理由なし(仕様)」と出る。
3. ①②③のチェック(上限3/5/12)・文法枠・自由コメントが従来どおり動く。
4. **「ChatGPTへ送信」後、ChatGPT入力欄に反映されたテキストに** 区分|英語|日本語訳【状態】、自由コメント、【AI選定理由(確認用…)】節が入っている(本環境では未検証)。入っていない/送信文が長い場合は、選定結果がコピーされるので貼り付ける。
5. 「選定結果をコピー」で貼り付けたテキスト末尾のJSON(全候補・AI理由付き)が確認できる(clipboard成功は本環境で未検証)。
6. スマホ表示(日本語訳行・折りたたみの崩れがないか)。
