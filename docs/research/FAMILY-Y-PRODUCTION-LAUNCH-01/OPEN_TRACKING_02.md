# OPEN_TRACKING_02: Family Y Production立上げ — 未完了事項の追跡(委任_02A更新)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A / 2026-10-25。`OPEN_TRACKING_01.md`(OT-01〜OT-25)からの**更新と追加**のみを書く(OT-01〜25のうち下記以外は変更なし)。正本の追跡先は`OPEN_ITEMS.md`(OPEN-520/484/463)。分類は11-8(修正へ進む/ユーザー判断要/実害なし)。

## 1. OT-01〜25の更新

| ID | 更新内容 | 現Status(2026-10-25 02A) | 11-8分類 |
|---|---|---|---|
| OT-07 | Closing一般化の移植(Prompt 02 byte一致・schema・決定論検査・再生成1回・CONTRACT_STOP)・案B固定注入registry・Voice Gate/書換えを`er121_family_y_text_core_01.py`に実装(56 test PASS) | **テキストcoreのClosing/Gate lane実装済み**。Lead/紹介/Voice生成/注意書き/In One Line廃止はrunner/次委任 | 修正へ進む(継続) |
| OT-08 | 実在意見ベースVoice生成方式の採用範囲 | **解消**: ユーザー原文§7 L283-286に「記事構成・3 Voice生成」が必要な範囲として明記(台帳YL-C03を判断待ち→適用) | クローズ |
| OT-20 | Gate文言(`leak_tension_reverts_to_research`肯定側等)の扱い | 較正で状況が変化: ①M-1定義補完で過去FAIL5件中3件(案A初回・R1 gen_1・R2 SNS M1)は解消 ②R2宅配H2の`leak_discovery_syntax`(『見えてくる』)は3/3 FAILで残る=**G-2の根拠が強まった** ③`leak_tension_reverts_to_research`自体は定義が元から1行完結で変わらず判定器ばらつきの範囲。G-1提示時は『Y版は旧B原文のFAIL条件[survey/研究結果の紹介・数字比較が主たる内容ならFAIL]と括弧内観点を欠く=移植時の欠落の復元に近い』を添える(Opus確認事項3) | ユーザー判断要(D、立上げは止めない) |
| OT-21 | Chunk TTSのYへの扱い | **分類変更: 判断待ち→除外+OPEN記録**(台帳YL-B08、基準(ii)) | 実害なし |
| OT-22 | I-1〜I-4(run_gate運用・切り口付加・gate_history・固定本文は書換え禁止STOP) | **実装済み**(test固定)。I-1は『Prompt 02規則節+切り口+範囲保全guard』へ拡張(M-2) | 修正へ進む→完了(runtime evidenceはE-1/E-3で追加) |
| OT-23 | DEV専用機能の非移植 | `er121_family_y_text_core_01.py`について**test固定済み**(DEV非import、`SKIPPED_BUDGET`/`os.environ`/`argparse`/`__main__`無し)。runner/audio側は02B | 修正へ進む(02Bで完了) |
| OT-24 | Dangling Reference | 台帳を02へ置換(`spec_ledger_01.json`は履歴として残置)。`er121_family_y_calibration_01.py`は証跡用でProduction非参照 | 修正へ進む |

## 2. 新規追加

| ID | 区分 | 項目 | 適用対象 | 現Status | 残作業 | 解消条件 | 追跡先 | 11-8分類 |
|---|---|---|---|---|---|---|---|---|
| **OT-26** | **実装不具合(Opus M-1、02Aが実コードで確認)** | Phase 0の『不具合0件』は誤り。DEVのTension判定promptは『上記と同じ意味』の参照先(Voice用定義3項目)を含まない(`er110_family_y_persona_text_trial_01.py:376-381,405-414`)=判定器が3項目を定義なしで推測判定していた(移植ミス。旧B英語版は1promptで成立) | Y Closing Gate | **修正済み(Production版のみ。DEVは意図的に不変)**。較正済み(`GATE_CALIBRATION_01.md`) | なし(DEVを直さない理由=既存Trial成果物の再現性) | test固定済み(DEV差分=展開のみ) | OPEN-520 | 修正へ進む→完了 |
| **OT-27** | **ユーザー判断候補(D)** | **案B(ユーザー承認の固定Closing)がM-1後のTension判定promptで2/7 FAIL**(`leak_evidence_memorable`)。旧prompt 0/7。固定注入はFAIL=書換え禁止・再試行禁止でSTOP | Y(宅配) | Fable指示によりSTOP報告。案B関連の追加作業は停止 | Fable→ユーザー判断(案I:進める[推奨] / 案II:Gate文言変更 / 案III:判定再試行許可。`GATE_CALIBRATION_01.md` §3) | ユーザー判断 | OPEN-520/463 | **ユーザー判断要** |
| **OT-28** | 判断候補(Fable) | Lead+人物紹介のGate補助適用で、適用対象項目`leak_evidence_memorable`が3/4 FAIL(旧0/4)。同根(ナレーター文にVoice用定義が効く) | Y Lead/紹介 | 判断待ち | 適用対象外項目の範囲(補助適用の設定)をFableが決める。承認済みGate定義は変更しない | Fable判断 | OPEN-520 | 修正へ進む(Fable判断後) |
| **OT-29** | 発見(修正済み) | Closing局所書換えが指摘箇所以外の文まで書き換え、語りの出所(受取人→配達員)を変えた(初回evidence run)。範囲保全guardを追加し再run | Y Closing書換え | **修正済み・再runで保存確認**(`REWRITE_EVIDENCE_01.md`) | 運用実績で偽の`REWRITE_STOP`が多い場合のみFableが緩和を判断 | 実績 | OPEN-520 | 修正へ進む→完了 |
| **OT-30** | 台帳漏れ(Opus M-5) | Source Reference Contract/Yの引用文参照方式/gloss再整合/gloss人称Gate/gloss HR/RET/TTS予算wrapper/mock時ログ隔離/KP基本形化例外/routing key(台帳YL-A24〜A32, YL-C13) | Y | 台帳02に登録。配線は02B/後続 | 各行の残作業(特にYL-A28 gloss HRの有無確認) | 各行の完了証拠 | OPEN-484/520 | 修正へ進む |
| **OT-31** | Opus R-3の前提相違 | `er006`に『実model照合関数』は存在しない(`require_model`は呼出前の契約照合のみ)。呼出後のresponse.model照合は`er121.chat`に実装 | 共有 | 実装済み | 将来、共通化する場合はer006側の別案件 | — | OPEN-520 | 実害なし(報告事項) |
| **OT-32** | 未確認(R-6) | 原価低減: cached_tokens実測、flex/Batch可否 | Y | 未確認 | E-3実測で確認 | 実測 | BUDGET_PLAN_02 §5 | 実害なし |
| **OT-33** | 台帳運用(Opus R-5) | 正本=CURRENT_SPEC配線Status表に一本化。`spec_ledger_*.json`は立上げ作業表でY PRODUCTION_WIRED時に廃止。M-5漏れ行のCURRENT_SPEC配線表への転記 | Y/全体 | 台帳02完了。転記は02B/後続 | CURRENT_SPEC配線表のY列更新(実装・evidence後) | Y PRODUCTION_WIRED判定 | OPEN-520 | 修正へ進む |
| **OT-34** | 予算 | 立上げ総額が112〜160円(中央135円)に増加。個別Cap 150円は上限側で約10円超過し得る | Y | Fable判断 | Cap 170円への引上げ提案(7-7の範囲) | Fable判断 | BUDGET_PLAN_02 §2 | 修正へ進む(Fable判断) |

## 3. 完了条件の更新
OT-01〜07・22〜24が揃い、OT-12〜13の接続点が結線され、**OT-27(案B判断)**・OT-28が解消し、E-1〜E-5が完了した時点で`PRODUCTION_WIRED`の検討(判定はFable、ユーザー最終試聴PASSは別Status)。
