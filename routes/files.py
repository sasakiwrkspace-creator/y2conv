from flask import (
    render_template,
    send_from_directory,
    redirect,
    request,
    abort
)

import os


# ==========================================================
# 基本設定
# ==========================================================

# プロジェクトルート
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# downloads
DOWNLOAD_DIR = os.path.join(
    BASE_DIR,
    "downloads"
)


# 4桁番号
FILE_PASSWORD = "1234"


# ==========================================================
# パス安全確認
# ==========================================================

def safe_path(relative_path):
    """
    プロジェクトルート以下だけを操作可能にする。
    ../ などによるプロジェクト外へのアクセスを防止。
    """

    relative_path = (
        relative_path
        .replace("\\", "/")
        .strip()
    )

    # 先頭の / を除去
    relative_path = relative_path.lstrip("/")

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

        common = os.path.commonpath(
            [
                base_path,
                full_path
            ]
        )

    except ValueError:

        return None

    if common != base_path:

        return None

    return full_path


# ==========================================================
# ツリー作成
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

        # 名前順
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
                "name": name,
                "path": relative_file_path.replace(
                    os.sep,
                    "/"
                ),
                "is_dir": is_dir,
                "depth": depth
            }

            items.append(
                item
            )

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
# /files
# ==========================================================

def register_files(app):

    @app.route(
        "/files",
        methods=["GET", "POST"]
    )
    def list_files():

        # ==================================================
        # パス削除処理
        # ==================================================

        delete_message = None
        delete_error = None

        if request.method == "POST":

            action = request.form.get(
                "action",
                ""
            )

            # ==============================================
            # パス指定削除
            # ==============================================

            if action == "delete_path":

                password = request.form.get(
                    "password",
                    ""
                )

                target_path = request.form.get(
                    "target_path",
                    ""
                ).strip()

                if password != FILE_PASSWORD:

                    delete_error = (
                        "4桁番号が正しくありません。"
                    )

                elif not target_path:

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

                                import shutil

                                shutil.rmtree(
                                    full_path
                                )

                                delete_message = (
                                    f"フォルダを削除しました: "
                                    f"{target_path}"
                                )

                            else:

                                os.remove(
                                    full_path
                                )

                                delete_message = (
                                    f"ファイルを削除しました: "
                                    f"{target_path}"
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
        # ファイル構成ツリー
        # ==================================================

        tree = build_file_tree()

        # ==================================================
        # 表示
        # ==================================================

        return render_template(
            "files.html",
            files=files,
            tree=tree,
            delete_message=delete_message,
            delete_error=delete_error
        )


    # ======================================================
    # ダウンロード
    # ======================================================

    @app.route(
        "/download/<path:filename>"
    )
    def download_file(filename):

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

        filepath = safe_path(
            os.path.join(
                "downloads",
                filename
            )
        )

        # downloads外へのアクセス防止
        if filepath is None:

            abort(403)

        # ファイルが存在する場合だけ削除
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
