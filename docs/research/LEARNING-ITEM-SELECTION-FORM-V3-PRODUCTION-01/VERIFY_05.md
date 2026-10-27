# VERIFY_05(委任_05、2026-10-27、API 0・JPY0)

- 公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/ (commit 9a1b08a1b。Pages反映確認: form_logic.jsに新文言、index.html HTTP 200)
- headless Chrome(公開URL、実DOM) `browser_check_05.mjs`: pass=30 fail=0(`browser_check_05_public_output.txt`。ローカルも同30/0: `browser_check_05_local_output.txt`)。
- 全11記事枠で「理由欄(details.why)が存在する候補=reason_jaが非空の候補」と完全一致(猿の手DEV 4/11理由あり、猿の手補完evidence 0/8、ダミー 0/12、7+5 evidence 8記事は全候補理由あり)。理由ありは理由本文が逐語表示。理由なし記事で`AI理由なし`/`（なし）`が画面に出ない。Console error/exception 0。選択上限(①<=3/①+②<=5/①+②+③<=12)は不変(uk_train Advanced 12件)。
- 注: 理由なし記事の送信はURL長超過でコピー誘導(null)のため、送信文面の「AI理由なし」非出現は単体test(node)で担保。
