# OPUS_REVIEW_COND_A_01: 固有名詞発音アラーム方針 Opus条件Aレビュー全文(逐語)

管理ID: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 / レビュー者: opus-consultant / 受領: Fable(委任_02の委任文付録として転記) / 保存: 委任_02(Sonnet、2026-10-22)。
Fableの採否は`docs/pm/OPUS_FINDINGS_LEDGER.md`のOF-PNAP-P-01〜15行を参照。反映先=`IMPLEMENTATION_DESIGN_01.md` §15。

---

結論: 条件付きで実装へ進んでよい。骨子は妥当で、既存Gateとも大筋で整合している。骨子とは、全ての救済層を通った後の`NG_BOTH/secondary_not_accepted`だけを入口にし、leafへはstatus OKとして返すため、HR Lock・queue・`approve_regenerate`を構造的に経由しないこと。flag×run scopeでFamily A/B/Cから切り離す点、語の脱落・数値・否定・KP・日本語をfail-closedにする点も妥当。ただし、受理の入口と固有名詞の判定根拠に「固有名詞の不一致だけ」を超えて緩和してしまう抜け道が3点、再利用経路にscope漏れと整合の不備が2点、TTS供給と完成報告の保証に穴が3点ある。

OF-PNAP-P-01 Major 入口条件が「Primaryが本当にNG」に限定されていない(er078:446-471,586-587; er006:1053-1066)。G1に`audit["p3_entry"]=="p3_primary_ng"`(かつdualなし)を追加。test: force_secondary×CMU-alt PASS×Secondary一般語差→不受理、primary_length_ng→不受理。

OF-PNAP-P-02 Major 文中大文字の根拠がTitle Caseで一般語を固有名詞扱い(er103:146-159、TOPIC_INTRO題名)。題名部分・連続大文字2語以上・コロン/引用符直後ではCMU収録語に大文字だけの根拠を認めない。test: 題名内一般語→不受理。

OF-PNAP-P-03 Major 両ASRが高頻度一般語に揃う場合(Muse→use系4件)は不受理。低頻度語への崩れ(kite/mellow/totem/mink)は承認の中心例として維持。類似度は綴り4文字以下で≥0.5、ASR語数≤原稿語数。校正再計測。

OF-PNAP-P-04 Info G3は許容。Secondaryだけの非固有名詞差に上限(≤2件、内容語2語以上の連続脱落は不受理)を推奨。脱落不受理は妥当。

OF-PNAP-P-05 Major (i)`rejudge_with_current_judge`は保存転写で必ずNG_BOTH→ALARM分岐で`evaluate_alarm_eligibility`再評価、`_j11_adopted_judgement`はALARM時Primary転写採用 (ii)Store共有でscope外からALARM音声が再利用され得る→scope外では再利用せず再生成 (iii)供給後PASS音声の再判定で元綴りと不一致→entryに`tts_input_text`と供給判断を保存し再判定に使用。

OF-PNAP-P-06 Major 供給置換のIGNORECASEで一般語(Nice/Muse/Gap)を書き換える→大文字小文字区別、小文字形が一般語なら大文字始まりのみ置換、test。

OF-PNAP-P-07 Major A階層自動供給のrespellingが検証済み引用と結び付いていない→人のtts_respelling、またはhintが引用のIPA/respellingと整合する場合のみ自動。ホストはラベル単位一致。Wikipediaは整合条件付きでA可。

OF-PNAP-P-08 Major 完成報告への掲載保証が手作業と例外握りつぶしに依存→機械生成報告へ埋め込み、ALARM数とreport件数一致検査、report不在時「集計失敗」明示(制作は止めない)、hookはfinally、Xは記事単位集約、継承recordは現runのlocation/segment。

OF-PNAP-P-09 Major(データ確認で解消) 初回受理の妥当性→slot2/3解消率を0円集計し`ALARM_ACCEPT_MIN_SLOT`をFableが決定。

OF-PNAP-P-10 Minor run scopeはcontext manager+finallyで解除。

OF-PNAP-P-11 Minor 供給の監査: 完成報告に「発音供給の適用一覧」、`compute_ledger_hits`の供給前text注記、Reicher→Rikerを`supply_map`へ。

OF-PNAP-P-12 Minor 設計書の行番号が古い(er019未commit差分、実際は1008/1407)。配線前確認。

OF-PNAP-P-13 Minor 境界外でHRに残る固有名詞のみ不一致の件数を区別表示。JA対象外を未解決事項に明記。

OF-PNAP-P-14 Info 旧ルール: HR投入経路は受け皿として必要、撤去0で妥当。OPEN-318/327/330/331/335は範囲縮小して継続。OPEN-371独立に同意。

OF-PNAP-P-15 Info test不足観点(P-01/02/03/05(i)〜(iii)/06、類似度0.40前後、scope解除、Z clip IDのFULL_STORY解決、Storeをまたぐ再利用、配布ファイル一覧に`audit/`非含有)。runtime見積約80円・翌JST日・7-7自律は妥当。供給の実発火証拠はA階層0件・Khaite B階層のままでは取れない(ユーザー承認操作)。量産単価は下がる方向、P-09で再試行を残す場合+約1円/件で再計算。

ユーザー判断・操作が本当に必要な事項: B階層(媒体由来)の承認操作は仕様上「人間」が行う。Khaite→Kate(出典Nylon、Stage 2で8/8有効)の承認登録がなければ運用開始時の供給効果は0件。Fableが承認候補一覧を作りユーザーに1回確認するのが適切。その他は承認範囲内の技術判断。
