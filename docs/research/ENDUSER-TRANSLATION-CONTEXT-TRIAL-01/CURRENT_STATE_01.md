# CURRENT_STATE_01(ENDUSER-TRANSLATION-CONTEXT-TRIAL-01 委任_01 Phase 1(a)、2026-10-31)

調査基準: origin/main d84cff09c(メインツリーの`er135_enduser_translate_01.py`は未追跡の古い版で現行ではない。以下は全て origin/main の worktree で確認)。コード変更0・Production出力変更0。

## 1. 生成訳の経路(file:line)
- 入口: runner(X=`er019_family_x_listening_page_01.py:262`、Z=`er026_family_z_fiction_production_runner_01.py:2784`、Y=`er121_family_y_runner_01.py:1388`) → `er135_enduser_page_01.py:1822 hook_run`(`translate_llm=AUTO_TRANSLATE_LLM` :1823、実体 :1747) → `:1401 make_translator(tcd, llm)` :828 → `:1006 generate_missing_translations` :839。
- 対象part: `GENERATE_KINDS`(:820=`ASSET_TRANSLATION_KINDS`[rev01-h]=preview/story/comment/oneline)のうち、承認済み訳が無く英語本文のpart(`:839-`)。= X: Std In One Line、Adv Preview/Comment/In One Line。Y: Adv Preview/Comment/In One Line。Z: Std・Adv の story・Preview・Comment・In One Line。X/Y の story と Std の Preview/Comment は承認済み訳があり生成しない。
- 公開済み10記事の生成訳の実数(`ev03/pool_all_generated_03.json`): **61 part・310文**(X 35part/150文、Y 6/11、Z 20/149[story 210文はZ])。承認済み訳あり573文、訳なし256文。
- 訳生成: `er135_enduser_translate_01.py:491 translate_part(part_id, sentences, level, family, cache_dir, llm)`。段落(para)単位でfail-closed。1partにつき translate 1 call(+再試行)、対訳照合(verify)1 call。
- 使用モデル: `MODEL = routing.SUPPORT_MODEL` = **gpt-6-luna**(:29、`er006_model_routing_contract_01.py:50`)。応答modelが違えば`ModelContractError`でSTOP(`DefaultLLM` :399、fallbackしない)。単価(`er009_..._cost.py`): input 16円/1Mtoken、cached input 1.6円、output 80円/1Mtoken。**reasoning modelでoutput(思考token含む)が費用の大半**(probe: 翻訳output 192〜1269token)。

## 2. Promptと現在渡している文脈
- Prompt本文: `TRANSLATE_HEAD`(:38、訳し方[意味正確・情報の追加省略禁止・数字/固有名保持・文脈は訳さない])+文脈欄+`# 訳す英文`(番号付き)+出力形式JSON。Promptに用語集・記事タイトル・他partの情報を入れる欄は無い。
- **文脈欄 `TRANSLATE_CONTEXT_LABEL`(:49)=「同じパートの他の文」**。組立 `:521 context = [s for s in sents if s["sid"] not in tset]`、`:321 build_translate_prompt` が `- 英文` を列挙。ここで`tset`=訳対象(pending)の文。新規生成では**part内の全段落がpendingなので文脈は空**(Comment 4=1段落3文が全て対象→空。probe A で確認: translate input 431 token)。文脈が入るのは「同一partの一部の段落だけがキャッシュhit/再試行の場合」だけ。
- 他part・記事タイトル(topic_en)・Full Storyの英文・承認済み訳は一切渡らない。→ 「直前partの語義」(Comment 4の`working things left out`)も、Z story内の代名詞の指示対象(`its exact sound`=妹の笑い声)も、partを跨ぐ訳語統一(city=都/街/町)も、Production経路では保証されない。
- 各partは独立した1回の呼出であり、同じ語を別partで同じ訳にする機構は無い(キャッシュは文群の英語shaが鍵のみ)。

## 3. verify(対訳照合、:56 VERIFY_HEAD)の検査内容
- 入力=「英文と訳」の番号付き対訳のみ(**文脈なし**)。判定誤り=意味の反転・数値・固有名・情報の欠落/追加。「言い回しの自然さ・文体の好みだけを理由にしない」。語義の選び方(多義語)を明示的に検査する項目は無い。
- 決定論検査: `structure_check`(:291 check_ja流用+文結合疑い)・`check_numbers`(:259)。
- **実測(probe、ev04_probe)**: 現行A(文脈なし)の訳「省かれたもの」はverifyを**通る**(誤訳がすり抜ける。OPEN-634の再現)。直前part文脈を足した方式Bでは翻訳が1回目で正しく「出しっぱなしの物」と訳されたのに、verifyが「left outは省かれた・取り残された」と**不合格にし**(文脈を見ていないため)、再翻訳で悪化(「外に出してある物」)→再度不合格→fail-closed(英語のみ表示)になった。= **文脈を足すだけでは、文脈を見ないverifyが正しい訳を落とす**。方式採用にはverifyへの文脈入力の要否検討が必須。

## 4. retry / fallback / regeneration / resume
- translate: `MAX_TRANSLATE_ATTEMPTS=2`(:33、件数/ID不一致・構造/数値NGのretry)。verify: `MAX_VERIFY_ATTEMPTS=2`(:34、応答不正のretry)。対訳照合NG段落は**指摘付きで1回だけ再翻訳→再照合**(`MAX_VERIFY_ROUNDS=2` :35、:513ループ、指摘=`RETRY_NOTE_*` :314-)。上限厳守。NGが残る段落は訳None→partは英語のみ表示(fail-closed、部分jaなし)。
- fallbackモデルなし(`ModelContractError`でSTOP)。
- resume/再実行: キャッシュ`ja_generated.json`(`<run>/enduser_sync_cache/`)。**鍵=段落の英語文群sha256(NFKC・空白正規化)のみ**(`para_key` :120)。Prompt sha・model・文脈は鍵に含めない(:9コメント M5)。命中時は保存訳を決定論検査し直して再利用(`_cached_para` :449)、成功のみ保存(失敗は非キャッシュ :592)、当該partに無い旧entryは保存時に除去(:606)。
- 含意: (1) **鍵に文脈が入っていない**ため、文脈方式を変えても既存キャッシュは命中し続け、新方式は新規生成分にしか効かない(逆に旧訳が残る=本委任②のComment 4で発生)。(2) 方式採用時は文脈をキャッシュ鍵(または方式ID)に含めるかの設計が必要で、含めれば公開済み記事の再produceでキャッシュmiss→再生成(API費用・訳の変動)が起きるため移行方針が要る。(3) 現行の誤訳は、キャッシュを消して再生成すれば**確率的に再発**する(probe A: 初回に続き2回目の独立生成でも「省かれたもの」。2/2)。

## 5. キャッシュ構造
- `ja_generated.json` = `{schema:"enduser_ja_generated_v1", entries:{<para_key>:{part_id, level, family, sids, ja[], ja_source:"generated", model, prompt_sha256, generated_at}}}`(`save_generated` :438)。End User生成時に`ja`・`ja_align`(1文=1群、`build_ja_fields` :468)としてarticle.jsonへ展開される。公開dirの`article.json`はキャッシュの再利用物(`build_info.generated_translation`にen/ja shaを記録、陳腐化検査あり)。
- 旧訳キャッシュ是正(②): `CLOSEOUT_CACHE_01.md`参照。
