# OPUS_REVIEW_REQUEST_01(条件A: 新しい処理フロー設計の独立レビュー依頼、下書き)

対象: `WIRING_DESIGN_01.md` / `er019_family_x_std_comment3_z_method_01.py`(未配線)/ test。判断基準はユーザー仕様「Part 3冒頭を限定参照・結論/重要結果を先取りしない・割合を無条件に渡さない・Comment 1/2/4/Preview不変」。

論点:
1. 参照範囲制御の抜け: `CONCLUSION_MARKER_RE`/`RESULT_SENTENCE_RE`をすり抜けて結果・結論を含む文が渡る型(結果が語彙に乏しい叙述、"Researchers asked X, and Y happened"、否定形、引用内の結果)。逆に過剰遮断(7本中3本がfallback)が許容か。語彙が"two/three/ten/half"等の数詞や"thinks/means"を含む副作用。
2. 先取りlintの偽陰性/偽陽性: 日本語Commentが結果を言い換える場合(数値・英語語を含まない)は検出不能。`WITHHELD_TERM`は英語語がCommentに出る場合のみ。`JA_CONCLUSION_WORDS`の網羅性。漢数字の扱い(二〜九+助数詞のみ)。決定論のまま強化すべき点、あるいはLLM判定を入れないことの妥当性(コスト/再現性)。
3. retry/resume整合: lint違反→同一入力retry→Part1+Part2縮退→fail-closed(`COMMENT3_SPOILER_LINT_FAILED`、text=None)の流れ。失敗時に`a2_support_texts.json`へcomment_3=nullが残り下流(TTS/組立)が使う危険の遮断方法(専用marker+rc、KP stage前の停止)。保存済みa2_support_texts.json再利用時に旧方式の文面(旧X役割)が混在する場合の扱い(方式版の表示/検出が必要か。AI島Standardは再生成するので既存run側の混在は新規Prod run以外では発生しない想定)。
4. Regression: Comment 1/2/4/Previewのsha固定が実効的か(fake client経由)、Comment 3差替えで`results`キー/下流(`audit/a2_support_generation.json`、plan構築`:246`)に副作用がないか。
5. 役割文`COMMENT_2_ROLE`をComment 3に共用する設計(Comment 2と同じ役割文)のリスク: Comment 2とComment 3の文面が重複しやすい点はTrialで許容されたか(Trial COMPARISON_01.md参照)。
6. 旧`FAMILY_X_A2_COMMENT_3_ROLE`の撤去要否(既存testが参照)と、配線後に不要となる旧規則の整理。
