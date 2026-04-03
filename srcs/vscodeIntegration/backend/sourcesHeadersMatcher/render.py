from pathlib import Path


def render_headers(rendered_headers):
    for rendered_header in rendered_headers:
        header_file = Path(rendered_header["path"])
        header_file.parent.mkdir(parents=True, exist_ok=True)
        header_file.write_text(rendered_header["string"], encoding="utf-8")
    return rendered_headers


def renderHeaders(rendered_headers):
    return render_headers(rendered_headers)
