from flask import (
    render_template,
    send_from_directory,
    redirect,
    request,
    abort,
    session
)

import os
import shutil

from paths import (
    BASE_DIR,
    DOWNLOAD_DIR
)


# ==========================================================
# 簡易パスワード
# ==========================================================

FILE_PASSWORD = "1234"


# ==========================================================
# files画面用セッションキー
# ==========================================================

FILES_SESSION_KEY = "files_authenticated"


# ==========================================================
# パス安全確認
# ==========================================================

def safe_path(relative_path):

    """
    BASE_DIR 以下だけを操作可能にする。

    ../ などを使って
    プロジェクト外へ出ることを防止する。
    """

    if not relative_path:

        return None

    relative_path = str(
        relative_path
    )

    relative_path = (
        relative_path
        .replace("\\", "/")
        .strip()
        .lstrip("/")
    )

    full_path = os.path.abspath(
        os.path.join(
            BASE_DIR,
            relative_path
        )
    )

    base_path = os.path.abspath(
        BASE_DIR
    )

    try:

        common_path = os.path.commonpath(
            [
                base_path,
                full_path
            ]
        )

    except ValueError:

        return None

    if common_path != base_path:

        return None

    return full_path


# ==========================================================
# ツリービュー作成
# ==========================================================

def build_file_tree():

    def scan_directory(
        directory,
        relative_path="",
        depth=0
    ):

        items = []

        try:

            names = os.listdir(
                directory
            )

        except Exception as e:

            print(
                "ディレクトリ読み込み失敗:",
                directory,
                repr(e)
            )

            return items

        # --------------------------------------------------
        # フォルダを先、ファイルを後
        # --------------------------------------------------

        names.sort(
            key=lambda name: (
                not os.path.isdir(
                    os.path.join(
                        directory,
                        name
                    )
                ),
                name.lower()
            )
        )

        for name in names:

            full_path = os.path.join(
                directory,
                name
            )

            relative_file_path = os.path.join(
                relative_path,
                name
            )

            try:

                is_dir = os.path.isdir(
                    full_path
                )

            except Exception:

                is_dir = False

            item = {

                "name":
                    name,

                "path":
                    relative_file_path.replace(
                        os.sep,
                        "/"
                    ),

                "is_dir":
                    is_dir,

                "depth":
                    depth

            }

            items.append(
                item
            )

            # --------------------------------------------------
            # フォルダの場合は中身も取得
            # --------------------------------------------------

            if is_dir:

                items.extend(
                    scan_directory(
                        full_path,
                        relative_file_path,
                        depth + 1
                    )
                )

        return items

    return scan_directory(
        BASE_DIR
    )


# ==========================================================
# files登録
# ==========================================================

def register_files(app):

    # ======================================================
    # セッション用Secret Key
    #
    # app.pyを変更しなくても動くように設定。
    #
    # 本格的な運用では環境変数
    # FILES_SECRET_KEY
    # を設定することを推奨。
    # ======================================================

    if not app.secret_key:

        app.secret_key = os.environ.get(
            "FILES_SECRET_KEY",
            "y2conv-files-secret-key"
        )

    # ======================================================
    # パス確認
    # ======================================================

    print("==========================================")
    print("files.py PATH設定")
    print("BASE_DIR:", BASE_DIR)
    print("DOWNLOAD_DIR:", DOWNLOAD_DIR)
    print(
        "DOWNLOAD_DIR exists:",
        os.path.isdir(DOWNLOAD_DIR)
    )
    print("==========================================")

    # ======================================================
    # /files
    # ======================================================

    @app.route(
        "/files",
        methods=["GET", "POST"]
    )
    def list_files():

        # ==================================================
        # 未認証
        # ==================================================

        if not session.get(
            FILES_SESSION_KEY,
            False
        ):

            error = None

            if request.method == "POST":

                password = request.form.get(
                    "password",
                    ""
                )

                if password == FILE_PASSWORD:

                    session[
                        FILES_SESSION_KEY
                    ] = True

                    return redirect(
                        "/files"
                    )

                else:

                    error = (
                        "4桁番号が正しくありません。"
                    )

            return render_template(
                "files.html",
                authenticated=False,
                error=error
            )

        # ==================================================
        # 認証済み
        # ==================================================

        delete_message = None
        delete_error = None

        # ==================================================
        # POST処理
        # ==================================================

        if request.method == "POST":

            action = request.form.get(
                "action",
                ""
            )

            # ==============================================
            # パス指定削除
            # ==============================================

            if action == "delete_path":

                target_path = request.form.get(
                    "target_path",
                    ""
                ).strip()

                if not target_path:

                    delete_error = (
                        "削除するファイルまたはフォルダを指定してください。"
                    )

                else:

                    full_path = safe_path(
                        target_path
                    )

                    if full_path is None:

                        delete_error = (
                            "プロジェクト外のファイルは削除できません。"
                        )

                    elif not os.path.exists(
                        full_path
                    ):

                        delete_error = (
                            "指定されたファイルまたはフォルダが存在しません。"
                        )

                    elif os.path.abspath(
                        full_path
                    ) == os.path.abspath(
                        BASE_DIR
                    ):

                        delete_error = (
                            "プロジェクトルート自体は削除できません。"
                        )

                    else:

                        try:

                            if os.path.isdir(
                                full_path
                            ):

                                shutil.rmtree(
                                    full_path
                                )

                                delete_message = (
                                    "フォルダを削除しました: "
                                    + target_path
                                )

                            else:

                                os.remove(
                                    full_path
                                )

                                delete_message = (
                                    "ファイルを削除しました: "
                                    + target_path
                                )

                        except Exception as e:

                            print(
                                "指定パス削除失敗:",
                                repr(e)
                            )

                            delete_error = (
                                "削除に失敗しました: "
                                + str(e)
                            )

        # ==================================================
        # downloads一覧
        # ==================================================

        files = []

        if os.path.exists(
            DOWNLOAD_DIR
        ):

            try:

                names = os.listdir(
                    DOWNLOAD_DIR
                )

                names.sort(
                    key=lambda x: x.lower()
                )

                for name in names:

                    full_path = os.path.join(
                        DOWNLOAD_DIR,
                        name
                    )

                    if os.path.isfile(
                        full_path
                    ):

                        files.append(
                            name
                        )

            except Exception as e:

                print(
                    "downloads読み込み失敗:",
                    repr(e)
                )

        # ==================================================
        # ツリー
        # ==================================================

        tree = build_file_tree()

        # ==================================================
        # 表示
        # ==================================================

        return render_template(
            "files.html",

            authenticated=True,

            files=files,

            tree=tree,

            delete_message=
                delete_message,

            delete_error=
                delete_error
        )

    # ======================================================
    # ログアウト
    # ======================================================

    @app.route(
        "/files/logout"
    )
    def files_logout():

        session.pop(
            FILES_SESSION_KEY,
            None
        )

        return redirect(
            "/files"
        )

    # ======================================================
    # ダウンロード
    # ======================================================

    @app.route(
        "/download/<path:filename>"
    )
    def download_file(filename):

        # ----------------------------------------------
        # files画面と同じ簡易認証
        # ----------------------------------------------

        if not session.get(
            FILES_SESSION_KEY,
            False
        ):

            return redirect(
                "/files"
            )

        # ----------------------------------------------
        # downloadsからのみ取得
        # ----------------------------------------------

        return send_from_directory(
            DOWNLOAD_DIR,
            filename,
            as_attachment=True
        )

    # ======================================================
    # downloads内ファイル削除
    # ======================================================

    @app.route(
        "/delete/<path:filename>",
        methods=["POST"]
    )
    def delete_file(filename):

        # ----------------------------------------------
        # files画面と同じ簡易認証
        # ----------------------------------------------

        if not session.get(
            FILES_SESSION_KEY,
            False
        ):

            return redirect(
                "/files"
            )

        # ----------------------------------------------
        # downloads以下に限定
        # ----------------------------------------------

        relative_path = os.path.join(
            "downloads",
            filename
        )

        filepath = safe_path(
            relative_path
        )

        if filepath is None:

            abort(403)

        # ----------------------------------------------
        # DOWNLOAD_DIRより外に出ていないか確認
        # ----------------------------------------------

        try:

            common_path = os.path.commonpath(
                [
                    os.path.abspath(
                        DOWNLOAD_DIR
                    ),
                    os.path.abspath(
                        filepath
                    )
                ]
            )

        except ValueError:

            abort(403)

        if common_path != os.path.abspath(
            DOWNLOAD_DIR
        ):

            abort(403)

        # ----------------------------------------------
        # ファイルのみ削除
        # ----------------------------------------------

        if os.path.isfile(
            filepath
        ):

            try:

                os.remove(
                    filepath
                )

            except Exception as e:

                print(
                    "downloadsファイル削除失敗:",
                    repr(e)
                )

        return redirect(
            "/files"
        )
