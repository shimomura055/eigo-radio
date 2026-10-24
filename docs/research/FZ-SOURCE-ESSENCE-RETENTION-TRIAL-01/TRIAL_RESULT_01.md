# TRIAL_RESULT_01: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02 結果(ユーザー原文§8の1〜10に対応する事実)

作成: 2026-10-25 / DEV/Trial専用・Production変更0。Status候補(Sonnet所見、判定はFable): **VALIDATED候補(Trial範囲、案A)**。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。Production採用・配線・『告げ口心臓』再生成・公開差替えは未実施・未承認。
ユーザー原文: `docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER.md`

1. **根本原因**(委任_01 ROOT_CAUSE_01.md + 委任_02で再現確認): R1/R2の固定文言`REVISE_USER_TMPL`の"in third person, "(`er062_family_z_writer_01.py:141`)。1a対照(同一入力r0.md、R1のみ)で現行文言は2/2サンプルで一人称44語→0語に反転(`1a/metrics_1a.json`)。寄与要因: key_roles描画"refer to this person by role... without a name"が一人称の語り手を外から呼ぶ指示として働く(Opus見落とし1、推定。案AのNarration行をKey people行より前に置いて解消)。過去Trial照合の訂正: er055 `NEUTRAL_CONVERSION_PLAN`(汎用文言の先例)あり(ROOT_CAUSE_01.md末尾に訂正記録)。
2. **上流設計上の問題**: source_essentialsに語り口の欄がなく、語り口を持つ唯一の場所conversion_planがR0にしか渡らない。守る対象の定義(スキーマ)に語り口がなかったため、伝達・確認の全経路が従った(ROOT_CAUSE_01 §3(5))。
3. **採用候補と適用工程**: 案A=Seed(`narration_voice`1欄、記入規則つき)→essentials→R0/R1/R2/Std全段のMust-keepにNarration行(Key people行より前)+REVISE固定句をMust-keep参照へ置換。追加LLM・Validator・retry 0。代替の最小案B'(汎用置換のみ、欄なし)は人称維持のみ。採用時の作業=`ADOPTION_NOTE_01.md`。
4. **『告げ口心臓』Advancedの改善結果**: 1b 2/2サンプルで一人称維持(一人称語42/43、三人称語23/24)、聞き手への呼びかけ維持(you 5/4、r0は4、現行r2は0)、essentials欠落0、Std人称一致、Adv音声Gate PASS(HR 0、273.8秒)。語りの質は1aで案A>汎用置換(Sonnet暫定平均6.0 vs 4.0)。事前基準未達は段落数のみ(17、基準19〜25)。`PHASE1_RESULT_01.md`、比較原稿=`COMPARISON_01.md`。
5. **横展開**: 賢者の贈り物・開いた窓・猿の手(各1サンプル)で人称不変(地の文の一人称語0)、語数・文長は完成版±25%内、essentials欠落0、結末保持。『賢者』の語り手介入は誘発されず。事前基準未達は猿の手の段落数(+8、完成版1点基準)のみ。`PHASE2_RESULT_01.md`、比較原稿=`COMPARISON_02.md`。
6. **面白さ・語り口・因果・心理・伏線回収への影響**: 現行r2で脱落していた心理(聞き手への呼びかけ、自己陶酔、恐怖を理解する内面)が回復。因果・出来事・結末は全案で維持。三人称作品ではNarration行が軽い文体傾向を与える程度で、冗長化・テンポ悪化は決定論上見られない。懸念: Std youが7(上限8)で呼びかけがやや多い、1a (iii)s2のyou=8。いずれも事前上限内。
7. **費用・所要時間・単価**: 実費108.81円/上限150円(`BUDGET_LOG_01.md`)、所要約18分(JST 07:59〜08:17、並列実行)。追加LLM呼出0・追加入力約+90 token/段。chain費用はProduction同作品との比較で系統的増加なし(−1.4〜+4.4円、reasoning token変動範囲)。量産単価70円/記事への影響は無視できる水準(サンプル少数)。
8. **Fable独立評価とStatus**: Fable評価待ち(本書は報告者=Sonnetの所見)。Status候補=VALIDATED候補(Trial範囲)。限界: 1a各2サンプル・1b 2サンプル・Phase 2各1サンプル、Sonnet読みは完全盲検でない、事前基準の段落数が未達(参照1点のみでノイズ帯未確定)、参照のsf_prodはPromptが異なるため幅の解釈に限界(Opus推奨の3点併記を実施)、盲検の最終判定はFable。
9. **ユーザー確認用**: 比較原稿=`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/COMPARISON_01.md`(告げ口心臓)、`COMPARISON_02.md`(横展開)。試聴URL=https://shimomura055.github.io/eigo-radio/user_test/fz_essence_trial_01/index.html(現行Adv[三人称]とTrial Adv[一人称]の比較。push後にpages deploy)。公開版 `user_test/family_z_tell_tale_heart_01/` は不変。
10. **SSOT/Git/残存Open Item**: OPEN-508 Status更新、DECISION_LOG 1件(下記commit)。残存: (a)Production採用判断(案A/案B'/不採用)=ユーザー、(b)『告げ口心臓』再生成・差替え=ユーザー判断候補J、(c)段落数ノイズの確認は必要になれば追加サンプル(任意、採用判断に必須ではない)。
