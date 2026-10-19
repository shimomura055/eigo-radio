Opusレビュー_H(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01、条件C、read-only)

# 総合判定: GO_WITH_CHANGES

方向性は正しいです。②(「両ASR合意」条件の削除)の扱いと、③の中心(A2の6%減速後再検証が書換え後の文と照合されること)は、コードとtestで確認できました。ただし「PRODUCTION_WIRED」と判定するには、必須修正4点が足りません。
- M5: Rewrite後の発音候補の凍結で、時刻の区切りが崩れOF-179に違反し得る点。③が直接作った不具合ではありませんが、ユーザー指示§4の「後続音声検査」の範囲に入ります。
- Z再利用経路が単一参照点を通らない点。
- Human Review(HR)queueの行とLockのkeyで、原稿の文が食い違う点。
- CURRENT_SPECの記述が実装より広い点。

---

## 論点1 ③の一元化の完全性
**結論**: 減速後再検証(Family X A2・Z narrator・Z Dialogue・Voices A2)は、すべて単一参照点を通ります。retry・fallbackも周ごとに正しく決まります。ただし、Z(Family Z)のresume・再利用は単一参照点を通っていません。「全経路を一元化した」という記述は実態より広いです。

**根拠**:
- 減速後再検証: `er003_v1_n3_01_tts_generate.py:206`で置換しています。Ledger PhraseListの導出(L138)も、置換後の値を使っています。
- 外側ループ: `:376-391`で、周ごとの`result`から正解原稿を導き直します。LRが起きるのは内側で予算を使い切った後なので、LRの後に「元の原稿で取り直す」周は構造上ありません。
- LR後の再TTSの判定: `er003_v1_crosslevel_audio_02_common.py:409-415`。`rewritten_text`を正解原稿として統一judgeを通るので、減速後再検証と同じ文になります。
- 優先順位1位の`selection.selected.rewritten_segment`は、`retts_fn`へ実際に渡した文そのものです(`er020_tts_retry_local_rewrite_01.py:773`)。正規化の食い違いは見つかりませんでした。
- **漏れ**: Zの再利用(`er063_family_z_audio_01.py:730` `guard_entry(cached_entry)`)が受け取るのは`build_entry`のentry(`er063:932-990`)です。このentryは`local_rewrite_recovery`キーを持たず、`audio_text_deviation`しか持ちません。そのため`resolve_expected_text_after_local_rewrite`は元の原稿(Melos)を返します。
  - Family Xのentryは、実行結果のdictをそのまま保持しています。さらに`entry["text"]`がもともと書換え後の文なので、③の前から実質的に対応済みでした(`er019_family_x_validation_inheritance_01.py:248`)。
  - Zは`guard_entry`が保護差(値・否定)のときだけblockするので、今は実害がありません(「Melos→He」の差は保護差ではない)。ただし、Rewriteが保護語に触れた場合は、過剰blockによる再生成が起き得ます。
  - test `er020_lr_post_rewrite_expected_text_fzaq2_test_01.py:281-303`はX形のentryだけを使っており、Z形はカバーしていません。
- 「最終検証」(`finalize_a2_slowdown_final_ng`、`er003_v1_n3_01_tts_generate.py:306`)は、意図的に元の原稿を使っています(Lockのkey)。これ自体は妥当です。

**必須修正**:
- (1-a) `resolve_expected_text_after_local_rewrite`がZのentry形も扱えるようにする。方法は2案です。
  - Zのentryの`audio_text_deviation.audio_text_after`を、2次の出典として読む。
  - `build_entry`へ最小限のLR記録(status・rewritten_segment)を追加の形で保存する。
  
  あわせて、Z形entryの`guard_entry`/`rejudge` testを追加する。
- (1-b) CURRENT_SPEC L2818の「減速後再検証・retry・fallback・resume・最終検証を行う」を実態に合わせる。最終HR遷移とLockのkeyは元の原稿、resumeはLR記録のあるentryのみ、と明記する。

**任意改善**: なし。

## 論点2 M5(LR後の凍結とLedgerの時刻境界)
**結論**: 違反し得ます。ただし発生点は③ではなく、LR後の再TTSの判定です(M1配線以来、既に存在)。③はその凍結物を、減速後再検証でも使い続けるだけです(キャッシュのkeyが同じなので、新たな凍結は起きない)。それでも「Rewrite後の後続音声検査」で、承認済みのOF-179に違反し得るため、必須修正とします。

**根拠**:
- `er006_secondary_asr_01.py:198-211`: 凍結のkeyはcanonical_textで、`segment_started_at`は凍結した時点の現在時刻です。
- `:740`: LR後の再TTS(canonical=書換え後の文)で初めて凍結されるため、開始時刻はLRの時刻になります。
- 同じsegment内で、それより前にLedgerへ書き込む経路が実在します。`:997-1012`では、最終slot(3回目)がNGで、固有名詞らしき語だけの不一致の場合に`_resolve_unresolved_entity_for_review`を呼びます。これが`research_pronunciations`を実行し、`pronun_ledger.upsert`(`:339`)します。これはLRより前に起きます。
- その後、書換え後の文がその固有名詞を残している場合(問題span以外を書き換えた場合)、`_c2_candidates`の時刻条件(`er006_m1_multi_candidate_01.py:229`)をすり抜けます。結果、同じsegmentで調べたばかりの候補でM1が自動PASSし得ます。これはD-2'限定置換の「Tier3の調査結果の即時利用は自動PASSの根拠にしない」(`er006_secondary_asr_01.py:309-315`)にも反します。
- 注意: `segment_started_at=None`の場合、時刻フィルタは無効になり、より緩くなります(`_parse_ts(None)`→None)。「時刻が取れなければNone」という実装は安全側ではありません。

**必須修正(形)**:
- `_m1_frozen_for(canonical_text, *, anchor_text=None)`を追加し、次のように扱う。
  - anchor(元の原稿)が凍結済みなら、その`segment_started_at`を使って書換え後の文を凍結する。必要なら、その時点のsnapshotも保持して再利用する。
  - anchorが見つからない場合は、M1を不発(frozen=None)にして安全側に倒す。現在時刻やNoneでの凍結はしない。
- anchorの受け渡しは`attempt_ctx`(例: `m1_anchor_text`)で行い、次の4箇所に配線する。
  - crosslevelの`_retts_fn`(L415)
  - voice01のLR再TTS
  - news_tail_fixのLR再TTS
  - `apply_a2_slowdown_postprocess`(出典=`local_rewrite_text`の場合)
- 必要なtest:
  - (i) 元のsegment開始より後にupsertされたLedgerエントリは、LR再TTSでも減速後再検証でもM1候補から除外される。
  - (ii) 開始より前のエントリは、従来どおり候補になる。
  - (iii) anchorが無い場合はM1不発。
  - (iv) LRなしの経路は挙動が変わらない(byte-identical)。

**任意改善**: `_M1_FROZEN_CACHE`はプロセス内で消去されず、別segment・別runでも同じ文なら古い凍結を使い回します。結果がより厳しい側に倒れるだけなので無害ですが、一言記録しておくとよいです。

## 論点3 HR Lockのkeyを元の原稿のままにする設計
**結論**: Lockそのものは整合しています。ただし③によって、HR queueの行の`canonical_text`だけが書換え後の文になり、Lock・承認のkey(元の原稿)とずれました。ここは直すべきです。

**根拠**:
- 再実行の入口`check_before_generation`(`er011_human_review_lock_01.py:299-354`)は、毎回、呼出元の元の原稿で照合します。keyを元の原稿にしておくのは正しい設計です。
- 状態遷移:
  - LR後の再TTSがOKなら、内側の`guarded_generate`でRESOLVEDになる。
  - 減速後PASSなら、RESOLVEDのまま。
  - 減速後NGなら、`finalize_a2_slowdown_final_ng`の`record_outcome`(元の原稿、`attempts_log=[]`)でHUMAN_REVIEW_REQUIREDになる。二重計上はありません。
- `review_lock_state.json`はsegment_idをkeyにした単一エントリ(`:449`)なので、一意性に問題はありません。
- ずれの所在: 最終slotでの減速後NGは、`_post_slowdown_unified_judge`→`_log_human_review(detail)`(`er003_v1_n3_01_tts_generate.py:157-160`、`er006_secondary_asr_01.py:359-362`)を通ります。このqueue行の`canonical_text`は書換え後の文で、元の原稿は含まれません。
- 一方、承認の照合`_human_approved`(`er011:179-190`)は、元の原稿のshaで行います。担当者がqueueの文で`record_human_approval`(`er003_v1_n3_01_assemble.py:96`)を実行すると、shaが一致しません。永久に承認されず、Lockが解除されない状態になります(安全側ではあるが、運用上のblocker)。

**必須修正**: queue行へ`lock_canonical_text`(または`canonical_text_before_local_rewrite`)と`expected_text_source`を追加の形で記録する。`_post_slowdown_unified_judge`へ元の原稿を渡す。testを1件追加し、HR手順書の承認キーは元の原稿だと明記する。

**任意改善**: Zの`audio_text_deviation`はSTOPPEDのentryにも付きます(`er063:941`)。試聴担当が「音声は書換え後の文」と分かるよう、HR packageに表示するとよいです。

## 論点4 ②の反映
**結論**: 「通算3回を使い切った後でのみRewrite」と「Rewrite前の承認済み検証を省略しない」は、コードとtest(e)で固定されています。rollback経路は、既定がTrueのため無害です。記録で足ります。ただしCURRENT_SPECが、未実装の条件を発火条件として記述したままです。これは⑤と同じ型の乖離です。

**根拠**:
- LRの呼出は2箇所だけです。
  - `crosslevel:301-307`: 標準とfallbackを使い切った後。
  - `crosslevel:257-277`: `stop_retrying`の場合。
- cascadeが有効なら`stop_retrying`は常にFalseです(`er006_secondary_asr_01.py:743,973`、`_m1_accept:236`)。test `:268-277`で固定されています。
- rollback(`:716-727`)では`val.evaluate_attempt`由来のTrueが残ります。標準経路が早期に終わった場合、fallback予算は2になり、その1回目の後にLRへ入り得ます(通算2回)。ただしこのflagはコード定数で、既定はTrueです。
- 外側ループの2周目以降(fallback予算0)では、標準経路が尽きた時点でL301のLRに入ります。この場合も通算3回は満たしています。
- CURRENT_SPEC L2818は、「3NGにSecondary障害を含まない」を発火条件として挙げています。しかし実装はありません(Sonnet §1-b、OPEN-371/U4はユーザー判断待ち)。
- 他の条件(5 role・英語のみ・7 Gate・`LR_REWRITTEN`=PASS_WITH_WARNING・HR Lock不変)は緩められていません。L2808の基本フローとも矛盾しません。

**必須修正**: CURRENT_SPEC L2818で、「3NGにSecondary障害を含まない」に「未実装・OPEN-371(U4)ユーザー判断待ち」と注記する。`lr_used==0`は「構造的に満たす(明示判定なし)」と注記する。これはE-1(実コードとの行単位の照合)の是正です。⑤と同じ失敗(仕様書だけに存在する条件にPRODUCTION_WIREDが付く)を再発させないためです。

**任意改善**: rollback時の早期LRを、`OPEN_ITEMS`か仕様注記に「既知の逸脱(rollback時のみ)」として1行記録する。L257のLR呼出に「通算生成数が上限に達していること」のガードを足すのも可能です。ただしこれは挙動変更なので、Fableの判断になります。

## 論点5 品質上の帰結(Melos→Heの自動採用)
**結論**: 承認済みLR仕様の範囲内の帰結です。ユーザー指示原文(delegation_log §4 L67-71)は、まさに「Melos drank→He drank」を例に、書換え後の文を正解とするよう求めています。新たなユーザー判断は不要です。ただし、機械的な固有名詞保全Gateは存在しません。これは事実として報告に含めるべきです。

**根拠**:
- 7 GateはLLMによる5項目と局所性の2項目です(`er020_tts_retry_local_rewrite_01.py:525-546, 660-668`)。entity保全の機械チェックはありません(Grepで`entity|固有名詞|pronoun`は0件)。
- crosslevelのLR呼出(`crosslevel:430-432`)は`context_before_text/context_after_text`を渡していません。そのため、主人公名を代名詞にした書換えの指示対象が曖昧かどうかを、LLM Gateは前後文脈なしで判定しています。
- Family Xは、style profile Gateで`LOCAL_REWRITE_RECOVERY`をBLOCKします(人間承認が必須、`er019_family_x_style_profile_01.py:715-716`)。一方Zは、警告と試聴リストで自動採用します。この非対称は既存のものです。
- ①の修正次第では、part3_c1型のケースでLRそのものが発火しなくなります。

**必須修正**: なし。

**任意改善**: ユーザー報告に、「固有名詞→代名詞の書換えは、LLM Gate(文脈なし)のみで採用され、事後試聴で確認する」と1行添える。entity保全Gateや文脈の受け渡しを追加するのは新仕様なので、提案に留めること(§3「別の未承認条件を追加しない」に抵触し得るため、独断で実装しない)。

## 論点6 PRODUCTION_WIRED判定の充足
**結論**: 現時点では不足しています。条件付きで可です。

**根拠**:
- 経路の網羅は論点1、凍結の境界は論点2、queueとLockの整合は論点3を参照。
- Regression: 新規2件のfailは未commit差分の検出guardで、「commit後の再実行で解消」とされています。しかし報告§7の末尾に、その再実行結果の追記がありません(`ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md:70`で予告されているが未記載)。
- runtime evidence: 実際のrunのwavを使い、正式関数(実ffmpeg、減速後wavのsha一致、保存転写の再利用)で検証しています(`ITEM3_FORMAL_PATH_VERIFY_01.json`)。LRの発火は稀で、意図的に起こすには費用と誘導が必要です。そのためofflineの正式経路検証を証拠として採るのは妥当です。ただし、live runで`post_slowdown_expected_text_source=local_rewrite_text`がまだ観測されていないことは明記すべきです。
- actual model_id: 新しいモデル呼出は0です。LR時のmodel_idは既存の`luna_model_id`記録で賄えます。

## ユーザー判断が必要な事項
なし。論点5は既存の決定の範囲内です。entity保全Gateを追加するなら新仕様なのでユーザー判断が必要ですが、採るかどうかはFableが提案するかの判断です。「3NGにSecondary障害を含まない」(OPEN-371/U4)は、既に登録済みのユーザー判断待ちで、今回の新規事項ではありません。

## PRODUCTION_WIRED判定可否
次をすべて満たせば、条件付きで判定可能です。
1. 論点2のM5修正と、その4つのtest。
2. 論点1(1-a)のZ形entry対応とtest。
3. 論点3のHR queue行への元原稿・出典の記録とtest。
4. 論点4・論点1(1-b)のCURRENT_SPEC注記修正(未実装の条件の明記、一元化の対象範囲の正確化)。
5. commit後の全体suiteの再実行で、新規failが0であることを報告へ追記。
6. Statusの注記に「runtime evidence=offlineの正式経路(実wav)。LRのlive発火はまだ観測していない」と書く。

②については、コード側の残作業は条件4だけです。CURRENT_SPECの注記が直れば判定できます。

関連ファイル:
- C:\Users\tensh\eigo-radio\er003_v1_n3_01_tts_generate.py(L121-179, L182-274, L288-307, L370-410)
- C:\Users\tensh\eigo-radio\er003_v1_crosslevel_audio_02_common.py(L257-307, L362-368, L409-442)
- C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py(L198-211, L302-340, L346-382, L716-743, L997-1012)
- C:\Users\tensh\eigo-radio\er006_m1_multi_candidate_01.py(L229, L248-287)
- C:\Users\tensh\eigo-radio\er020_tts_retry_local_rewrite_01.py(L525-546, L660-668, L708-803)
- C:\Users\tensh\eigo-radio\er019_family_x_validation_inheritance_01.py(L233-254)
- C:\Users\tensh\eigo-radio\er078_reuse_value_guard_01.py(L32-71)
- C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py(L718-741, L932-990)
- C:\Users\tensh\eigo-radio\er011_human_review_lock_01.py(L179-190, L299-354, L357-471)
- C:\Users\tensh\eigo-radio\er020_lr_post_rewrite_expected_text_fzaq2_test_01.py
- C:\Users\tensh\eigo-radio\CURRENT_SPEC.md(L2818)