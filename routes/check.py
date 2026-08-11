def get_ydl_base_options():
cookie_file = prepare_cookie_file()

```
options = {
    "cookiefile": cookie_file,
    "noplaylist": True,
    "quiet": False,
    "no_warnings": False,
    "verbose": True,
    "remote_components": {
        "ejs:github"
    }
}

deno_path = shutil.which("deno")

print("==========================================")
print("yt-dlp基本設定")
print("==========================================")
print("Cookie:", cookie_file)
print("Deno:", deno_path if deno_path else "見つかりません")
print("EJS remote component: ejs:github")
print("==========================================")

if deno_path:
    options["js_runtimes"] = {
        "deno": {
            "path": deno_path
        }
    }

return options
```
