from flask import (
    render_template,
    send_from_directory,
    redirect,
    request,
    abort
)

import os


# ==========================================================
# プロジェクトルート
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================================
# downloads
# ==========================================================

DOWNLOAD_DIR = os.path.join(
    BASE_DIR,
    "downloads"
)


# ==========================================================
# プロジェクトルート
#
# この配下だけファイル操作可能
# ==========================================================

PROJECT_ROOT = os.path.abspath(
    BASE_DIR
)


# ==========================================================
# 4桁番号
# ==========================================================

FILE_PASSWORD = "1234"


# ==========================================================
# 相対パス取得
# ==========================================================

def relative_path(path):

    return os.path.relpath(
        path,
        PROJECT_ROOT
    ).replace(
        os.sep,
        "/"
    )


# ==========================================================
# プロジェクト全体ツリー
#
# downloads は別表示するため除外
#
# .git
# .venv
# __pycache__
# も除外
# ==========================================================

def get_project_tree():

    tree = []

    if not os.path.exists(
        PROJECT_ROOT
    ):

        return tree


    for root, dirs, files in os.walk(
        PROJECT_ROOT
    ):

        # --------------------------------------------------
        # 表示しないディレクトリ
        # --------------------------------------------------

        dirs[:] = [
            d
            for d in dirs
            if d not in [
                ".git",
                ".venv",
                "__pycache__",
                "downloads"
            ]
        ]


        # --------------------------------------------------
        # 相対パス
        # --------------------------------------------------

        rel_root = relative_path(
            root
        )


        # --------------------------------------------------
        # ディレクトリ表示名
        # --------------------------------------------------

        if rel_root == ".":

            display_root = "y2conv"

        else:

            display_root = (
                "y2conv/"
                + rel_root
            )


        tree.append({
            "type": "directory",
            "path": display_root
        })


        # --------------------------------------------------
        # ファイル
        # --------------------------------------------------

        for filename in sorted(
            files
        ):

            full_path = os.path.join(
                root,
                filename
            )


            rel_path = relative_path(
                full_path
            )


            tree.append({
                "type": "file",
                "path":
                    "y2conv/"
                    + rel_path
            })


    return tree


# ==========================================================
# downloads一覧
# ==========================================================

def get_download_files():

    if not os.path.exists(
        DOWNLOAD_DIR
    ):

        return []


    files = []


    for filename in sorted(
        os.listdir(
            DOWNLOAD_DIR
        )
    ):

        filepath = os.path.join(
            DOWNLOAD_DIR,
            filename
        )


        if os.path.isfile(
            filepath
        ):

            files.append(
                filename
            )


    return files


# ==========================================================
# /tmp ツリー
#
# y2conv関連だけ表示
#
# 特に
#
# /tmp/y2conv_downloads
#
# の存在確認に使用
# ==========================================================

def get_tmp_tree():

    tree = []

    TMP_DIR = "/tmp"


    # ======================================================
    # /tmp/y2conv_downloads
    # ======================================================

    tmp_download_dir = os.path.join(
        TMP_DIR,
        "y2conv_downloads"
    )


    if os.path.exists(
        tmp_download_dir
    ):

        # --------------------------------------------------
        # フォルダ
        # --------------------------------------------------

        tree.append({
            "type": "directory",
            "path": "/tmp/y2conv_downloads"
        })


        # --------------------------------------------------
        # 中身
        # --------------------------------------------------

        for root, dirs, files in os.walk(
            tmp_download_dir
        ):

            # ----------------------------------------------
            # サブフォルダ
            # ----------------------------------------------

            for dirname in sorted(
                dirs
            ):

                full_path = os.path.join(
                    root,
                    dirname
                )


                tree.append({
                    "type": "directory",
                    "path":
                        full_path.replace(
                            os.sep,
                            "/"
                        )
                })


            # ----------------------------------------------
            # ファイル
            # ----------------------------------------------

            for filename in sorted(
                files
            ):

                full_path = os.path.join(
                    root,
                    filename
                )


                tree.append({
                    "type": "file",
                    "path":
                        full_path.replace(
                            os.sep,
                            "/"
                        )
                })


    else:

        # --------------------------------------------------
        # 存在しない場合
        # --------------------------------------------------

        tree.append({
            "type": "missing",
            "path":
                "/tmp/y2conv_downloads は存在しません"
        })


    # ======================================================
    # /tmp の y2conv関連ファイル
    #
    # 例:
    #
    # /tmp/y2conv_cookies_xxxxx.txt
    #
    # ======================================================

    tmp_files = []


    try:

        for name in os.listdir(
            TMP_DIR
        ):

            # --------------------------------------------------
            # y2conv_downloads は上ですでに確認済み
            # --------------------------------------------------

            if name == "y2conv_downloads":

                continue


            # --------------------------------------------------
            # y2conv関連だけ
            # --------------------------------------------------

            if (
                name.startswith(
                    "y2conv_"
                )
                or name.startswith(
                    "y2conv"
                )
            ):

                full_path = os.path.join(
                    TMP_DIR,
                    name
                )


                tmp_files.append(
                    full_path
                )


    except Exception as e:

        print(
            "TMP一覧取得失敗:",
            repr(e)
        )


    # ======================================================
    # y2conv関連一時ファイル表示
    # ======================================================

    for full_path in sorted(
        tmp_files
    ):

        if os.path.isdir(
            full_path
        ):

            tree.append({
                "type": "directory",
                "path":
                    full_path.replace(
                        os.sep,
                        "/"
                    )
            })

        else:

            tree.append({
                "type": "file",
                "path":
                    full_path.replace(
                        os.sep,
                        "/"
                    )
            })


    return tree


# ==========================================================
# プロジェクト配下の安全なパスを取得
# ==========================================================

def safe_project_path(
    requested_path
):

    if not requested_path:

        return None


    # ------------------------------------------------------
    # 前後空白除去
    # ------------------------------------------------------

    requested_path = (
        requested_path
        .strip()
        .replace(
            "\\",
            "/"
        )
    )


    if not requested_path:

        return None


    # ------------------------------------------------------
    # y2conv/ を取り除く
    #
    # 例:
    #
    # y2conv/routes/convert.py
    #
    # ↓
    #
    # routes/convert.py
    # ------------------------------------------------------

    if requested_path.startswith(
        "y2conv/"
    ):

        requested_path = (
            requested_path[
                len("y2conv/") :
            ]
        )


    # ------------------------------------------------------
    # y2conv/ だけの場合
    # ------------------------------------------------------

    if requested_path == "y2conv":

        requested_path = ""


    # ------------------------------------------------------
    # 絶対パス化
    # ------------------------------------------------------

    full_path = os.path.abspath(
        os.path.join(
            PROJECT_ROOT,
            requested_path
        )
    )


    # ------------------------------------------------------
    # PROJECT_ROOT外へのアクセス禁止
    #
    # ../
    # などによる脱出を防止
    # ------------------------------------------------------

    if (
        full_path != PROJECT_ROOT
        and not full_path.startswith(
            PROJECT_ROOT + os.sep
        )
    ):

        return None


    return full_path


# ==========================================================
# Flask登録
# ==========================================================

def register_files(app):


    # ======================================================
    # /files
    # ======================================================

    @app.route(
        "/files",
        methods=[
            "GET",
            "POST"
        ]
    )
    def list_files():


        # ==================================================
        # パスワード確認
        # ==================================================

        if request.method == "POST":


            password = request.form.get(
                "password",
                ""
            )


            if password == FILE_PASSWORD:


                # ------------------------------------------
                # downloads作成
                # ------------------------------------------

                os.makedirs(
                    DOWNLOAD_DIR,
                    exist_ok=True
                )


                # ------------------------------------------
                # downloads
                # ------------------------------------------

                download_files = (
                    get_download_files()
                )


                # ------------------------------------------
                # プロジェクトツリー
                # ------------------------------------------

                project_tree = (
                    get_project_tree()
                )


                # ------------------------------------------
                # TMPツリー
                # ------------------------------------------

                tmp_tree = (
                    get_tmp_tree()
                )


                # ------------------------------------------
                # 表示
                # ------------------------------------------

                return render_template(

                    "files.html",

                    files=download_files,

                    project_tree=project_tree,

                    tmp_tree=tmp_tree

                )


        # ==================================================
        # パスワード入力画面
        # ==================================================

        return """
        <!DOCTYPE html>

        <html lang="ja">

        <head>

        <meta charset="UTF-8">

        <title>File Check</title>

        </head>

        <body>

        <h3>
        ファイル管理
        </h3>

        <form method="post">

        <p>
        4桁番号を入力してください
        </p>

        <input
            type="password"
            name="password"
            maxlength="4"
            autofocus
        >

        <button
            type="submit"
        >
        確認
        </button>

        </form>

        </body>

        </html>
        """


    # ======================================================
    # ダウンロード
    # ======================================================

    @app.route(
        "/download/<path:filename>"
    )
    def download_file(
        filename
    ):

        return send_from_directory(

            DOWNLOAD_DIR,

            filename,

            as_attachment=True

        )


    # ======================================================
    # downloads 個別削除
    # ======================================================

    @app.route(
        "/delete/<path:filename>",
        methods=["POST"]
    )
    def delete_file(
        filename
    ):


        filepath = os.path.abspath(
            os.path.join(
                DOWNLOAD_DIR,
                filename
            )
        )


        # --------------------------------------------------
        # downloads外へのアクセス禁止
        # --------------------------------------------------

        if (
            filepath != DOWNLOAD_DIR
            and not filepath.startswith(
                DOWNLOAD_DIR + os.sep
            )
        ):

            abort(403)


        # --------------------------------------------------
        # ファイル削除
        # --------------------------------------------------

        if os.path.isfile(
            filepath
        ):

            os.remove(
                filepath
            )


        return redirect(
            "/files"
        )


    # ======================================================
    # y2conv配下 削除確認
    # ======================================================

    @app.route(
        "/delete-project",
        methods=["POST"]
    )
    def delete_project():


        requested_path = request.form.get(
            "path",
            ""
        )


        filepath = safe_project_path(
            requested_path
        )


        # --------------------------------------------------
        # 不正パス
        # --------------------------------------------------

        if not filepath:

            return """
            <!DOCTYPE html>

            <html lang="ja">

            <head>
            <meta charset="UTF-8">
            <title>削除エラー</title>
            </head>

            <body>

            <h3>
            削除できません
            </h3>

            <p>
            無効なファイルパスです。
            </p>

            <a href="/files">
            ファイル管理へ戻る
            </a>

            </body>

            </html>
            """


        # --------------------------------------------------
        # PROJECT_ROOT自体は禁止
        # --------------------------------------------------

        if filepath == PROJECT_ROOT:

            abort(403)


        # --------------------------------------------------
        # 存在確認
        # --------------------------------------------------

        if not os.path.exists(
            filepath
        ):

            return """
            <!DOCTYPE html>

            <html lang="ja">

            <head>
            <meta charset="UTF-8">
            <title>削除エラー</title>
            </head>

            <body>

            <h3>
            ファイルがありません
            </h3>

            <p>
            指定されたファイルまたはフォルダは
            存在しません。
            </p>

            <a href="/files">
            ファイル管理へ戻る
            </a>

            </body>

            </html>
            """


        # --------------------------------------------------
        # 表示用パス
        # --------------------------------------------------

        display_path = relative_path(
            filepath
        )


        # --------------------------------------------------
        # 確認画面
        # --------------------------------------------------

        return render_template(
            "delete_confirm.html",
            path=display_path
        )


    # ======================================================
    # y2conv配下 削除実行
    # ======================================================

    @app.route(
        "/delete-project-confirm",
        methods=["POST"]
    )
    def delete_project_confirm():


        requested_path = request.form.get(
            "path",
            ""
        )


        filepath = safe_project_path(
            requested_path
        )


        # --------------------------------------------------
        # 不正パス
        # --------------------------------------------------

        if not filepath:

            abort(400)


        # --------------------------------------------------
        # PROJECT_ROOTは禁止
        # --------------------------------------------------

        if filepath == PROJECT_ROOT:

            abort(403)


        # --------------------------------------------------
        # プロジェクト外は禁止
        # --------------------------------------------------

        if not (
            filepath.startswith(
                PROJECT_ROOT + os.sep
            )
        ):

            abort(403)


        # --------------------------------------------------
        # 削除
        # --------------------------------------------------

        try:

            if os.path.isdir(
                filepath
            ):

                import shutil

                shutil.rmtree(
                    filepath
                )

            elif os.path.isfile(
                filepath
            ):

                os.remove(
                    filepath
                )

        except Exception as e:

            print(
                "ファイル削除失敗:",
                repr(e)
            )


        return redirect(
            "/files"
        )
