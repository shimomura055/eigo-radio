# -*- coding: utf-8 -*-
"""reversal_detector_v0: 反転型(否定・不在の誤り / 主体の取り違え)の決定論検出器。API不使用、Production未接続(測定専用)。
OPEN-233-REVERSAL-DETECT-HUMAN-ROUTE-TRIAL-01 委任_01。runner/checkerコードは編集しない独立モジュール。
流用: er052_output/open233_stage0_01/danger/danger_sentence_rules_v0.py(文分割・台帳parse・fact link・NEG語・主語抽出の枠)。

検出対象言語 = 台帳の言語(JA台帳: meta/hormuz/space_weapons/sewer -> JA R2文、EN台帳: ai_control -> EN文)。
  EN文×JA台帳の対応は概念辞書が要るため本版では扱わない(限界)。

(i)  neg_absence : 文に否定語があり、かつ台帳の「肯定の出来事fact」(POS_EVENTに一致)の語と重なる。
(ii) subj_class  : 文の主語名詞の役割クラス(human/ai/org/public)が、文が結び付くfact(一意リンクのみ)の主語クラスと異なる。
(iii)neg_subject : (i)かつ(ii)。
除外: 語り枠(I/you/we・問いかけ)の文、「not only」型の対比。
"""
import re
import sys
import os

sys.dont_write_bytecode = True
_DANGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'open233_stage0_01', 'danger')
sys.path.insert(0, os.path.abspath(_DANGER))
import danger_sentence_rules_v0 as D  # noqa: E402

VERSION = 'reversal_detector_v0'

# ---------------- 語り枠 ----------------
FRAME_EN = re.compile(r"\b(I|I'm|I’m|I’ve|I've|I’ll|I'll|you|your|you’re|you're|we|we’re|we're|our|us|my|let’s|let's)\b|\?\s*$")
FRAME_JA = re.compile(r'(私|わたし|僕|あなた|みなさん|皆さん|[?？]|でしょうか|ませんか|ましょう)')

# ---------------- 否定(対比型を除外) ----------------
NOT_ONLY_EN = re.compile(r'\bnot\s+(only|just|merely|simply)\b|\bno matter\b', re.I)
NOT_ONLY_JA = re.compile(r'(だけでなく|だけではなく|のみならず|だけじゃなく)')

# ---------------- 肯定の出来事(台帳factが「起きた」と述べる語) ----------------
POS_EVENT_EN = re.compile(r"\b(reach(?:ed|es)?|access(?:ed|es)?|leak(?:ed|s)?|exfiltrat\w*|publish\w*|upload\w*|download\w*|ran|run|announc\w*|post(?:ed)?|launch\w*|start(?:ed)?|began|stopp?ed|shut|disclos\w*|implement\w*|collect\w*|charg(?:e|ed|es)|roll(?:ed)?\s?back|report(?:ed)?|admit(?:ted)?|test(?:ed)?|found|identified|detected|exploit\w*|created|destroy\w*|deploy\w*|rose|fell|declin\w*|impos\w*|decided|stated|said|conduct\w*|completed|attempt\w*)\b", re.I)
POS_EVENT_JA = re.compile(r'(到達|アクセス|流出|持ち出|公開|アップロード|ダウンロード|実行|実施|発表|投稿|開始|始め|停止|テスト|徴収|課す|課し|ロールバック|報告|報じ|認め|発見|検出|確認|破壊|発射|配備|配置|上昇|下落|撤回|表明|説明|決定|採択|行っ|行い|開発|設置|導入|整備|廃止|選択|見直|展開|担当|かけ)')

# ---------------- 役割クラス辞書(rightmost一致=主辞) ----------------
_CLS_EN = {
    'human': r"humans?|person|people|staff|contractors?|workers?|employees?|engineers?|concierge|operators?|vice president|executives?|managers?|spokesperson|officials?|anyone|someone|nobody|no one|researchers?|maintainers?|secretary|president|experts?|counterpart",
    'ai': r"AI|models?|agents?|bots?|assistants?|Muse|Claude|GPT[\w\-\.]*|Mythos[\w ]*|chatbots?|LLM|algorithms?|systems?|software|programs?|packages?",
    'org': r"Meta|Anthropic|OpenAI|compan(?:y|ies)|government|administration|Pentagon|military|forces|agency|institute|AISI|Reuters|city|municipality|ministry|council|IMO|Russia|China|India|team|organizations?|Hugging Face|firms?|panel|group|United States|U\.S\.",
    'public': r"users?|customers?|public|citizens?|consumers?|residents?|households?|readers?|voters?|owners?",
}
_CLS_JA = {
    'human': r'人間|人|スタッフ|従業員|担当者|副社長|社員|社長|エンジニア|研究者|関係者|契約|コンシェルジュ|大統領|長官|職員|誰|だれ|専門家|作業員|氏',
    'ai': r'AI|人工知能|モデル|エージェント|Muse|ボット|アシスタント|システム|ソフトウェア|プログラム|パッケージ|Claude|GPT',
    'org': r'Meta|メタ|Anthropic|OpenAI|会社|企業|政府|当局|国防総省|統合軍|米軍|軍|機関|研究所|自治体|市|町|村|省|庁|チーム|組織|国連|国|ロシア|中国|インド|米国|米|宇宙軍|空軍|議会|理事会|裁判所',
    'public': r'利用者|ユーザー|顧客|消費者|市民|住民|国民|家庭|読者|世帯|公衆|相手',
}
_CLS_EN_RE = {k: re.compile(r'(?<![A-Za-z])(?:' + v + r')(?![A-Za-z])', re.I if k != 'ai' else 0) for k, v in _CLS_EN.items()}
_CLS_JA_RE = {k: re.compile(v) for k, v in _CLS_JA.items()}


def role_class(np_text, lang):
    """NP文字列の主辞(最も右で終わる一致、同位置なら長い一致)のクラス。無ければNone。"""
    res = _CLS_JA_RE if lang == 'ja' else _CLS_EN_RE
    best = None  # (end, length, cls)
    for cls, rx in res.items():
        for m in rx.finditer(np_text):
            cand = (m.end(), m.end() - m.start(), cls)
            if best is None or cand[:2] > best[:2]:
                best = cand
    return best[2] if best else None


# ---------------- 主語抽出 ----------------
_LEAD = D._LEAD


def subject_np(sent, lang):
    if lang == 'ja':
        s = _LEAD.sub('', sent.strip().lstrip('「『'))
        m = re.match(r'^(.{1,30}?)(は|が|も)', s)
        if not m:
            return None
        np_ = m.group(1)
        if '、' in np_:
            np_ = np_.split('、')[-1]
        return np_
    toks = re.findall(r"[A-Za-z][A-Za-z’'\-\.]*", sent)
    np_ = []
    for i, t in enumerate(toks):
        if i > 0 and D._VERBISH.match(t.lower()):
            break
        np_.append(t)
        if i >= 8:
            break
    if len(np_) >= 1 and np_[0] in ('But', 'And', 'So', 'Then', 'However', 'Nor', 'Yet', 'Still', 'Also') and len(np_) > 1:
        np_ = np_[1:]
    return ' '.join(np_) if np_ else None


def fact_subject_class(fact, lang):
    first = re.split(r'(?<=[。.])\s*', fact['claim'].strip())[0]
    return role_class(subject_np(first, lang) or '', lang)


# ---------------- 台帳: 肯定の出来事fact ----------------
def positive_facts(facts, lang):
    rx = POS_EVENT_JA if lang == 'ja' else POS_EVENT_EN
    return {fid: f for fid, f in facts.items() if rx.search(f['claim'])}


def _strip_neg(sent, lang):
    rx = D.NEG_JA if lang == 'ja' else D.NEG_EN
    return rx.sub(' ', sent)


def neg_overlap(sent, lang, facts):
    """否定文と、肯定の出来事factの語の重なり。戻り値: [(fid, 重なり量)]。"""
    s = _strip_neg(sent, lang)
    out = []
    pf = positive_facts(facts, lang)
    if lang == 'ja':
        sg = D.ja_bigrams(s)
        for fid, f in pf.items():
            fg = D.ja_bigrams(f['claim'] + ' ' + f['scope'])
            sh = len(sg & fg)
            if sh >= 5:
                out.append((fid, sh))
    else:
        st = D.en_tokens(s)
        for fid, f in pf.items():
            sh = len(st & D.en_tokens(f['all']))
            if sh >= 2:
                out.append((fid, sh))
    return sorted(out, key=lambda x: -x[1])


def detect(sent, lang, facts, ledger_txt, oracle_fid=None):
    """戻り値: dict(frame=bool, tags=[...], detail={...})。tags: neg_absence / subj_class / neg_subject。"""
    frame = bool((FRAME_JA if lang == 'ja' else FRAME_EN).search(sent))
    res = {'frame': frame, 'tags': [], 'detail': {}}
    if frame:
        return res
    negrx = D.NEG_JA if lang == 'ja' else D.NEG_EN
    m = negrx.search(sent)
    contrast = (NOT_ONLY_JA if lang == 'ja' else NOT_ONLY_EN).search(sent)
    has_neg = bool(m) and not contrast
    i_hit = []
    if has_neg:
        i_hit = neg_overlap(sent, lang, facts)
        if i_hit:
            res['detail']['neg_word'] = m.group(0)
            res['detail']['neg_facts'] = i_hit[:3]
    # (ii) 主体クラス
    ii = False
    snp = subject_np(sent, lang)
    scls = role_class(snp or '', lang) if snp else None
    if oracle_fid is not None:
        fids = [oracle_fid] if oracle_fid in facts else []
    else:
        fids = D.link_facts(sent, lang, facts, lax=False)
    res['detail']['subject_np'] = snp
    res['detail']['subject_class'] = scls
    res['detail']['linked'] = fids
    if scls and len(fids) == 1:
        fcls = fact_subject_class(facts[fids[0]], lang)
        res['detail']['fact_class'] = fcls
        if fcls and fcls != scls:
            ii = True
    if i_hit:
        res['tags'].append('neg_absence')
    if ii:
        res['tags'].append('subj_class')
    if i_hit and ii:
        res['tags'].append('neg_subject')
    return res
