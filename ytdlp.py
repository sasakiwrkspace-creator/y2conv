# ==========================================================
# 安全なファイル名
# ==========================================================

def _safe_filename(title):

    if not title:
        title = "YouTube Video"

    title = str(title).strip()

    # Windows / Linux で問題になりやすい文字を置換
    invalid_chars = '<>:"/\\|?*'

    for char in invalid_chars:
        title = title.replace(char, "_")

    # 改行・タブなど
    title = title.replace("\n", " ")
    title = title.replace("\r", " ")
    title = title.replace("\t", " ")

    # 連続スペース
    title = " ".join(title.split())

    # 長すぎるファイル名を防止
    title = title[:180].rstrip()

    # 空になった場合
    if not title:
        title = "YouTube Video"

    return title
