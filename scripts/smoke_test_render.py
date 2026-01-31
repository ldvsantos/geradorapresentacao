import os
import shutil
import subprocess
import sys
import tempfile


def copy_template(src: str, dst: str) -> None:
    ignore = shutil.ignore_patterns(
        ".quarto",
        "_site",
        "*.html",
        "*.pdf",
        "*.log",
    )
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)


def main() -> int:
    base_path = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(base_path, ".."))

    template_path = os.path.join(repo_root, "template")
    if not os.path.isdir(template_path):
        raise SystemExit(f"Template não encontrado: {template_path}")

    tmpdirname = tempfile.mkdtemp(prefix="gerador_apresentacao_smoke_")
    try:
        work_dir = os.path.join(tmpdirname, "projeto")
        copy_template(template_path, work_dir)

        qmd_path = os.path.join(work_dir, "apresentacao.qmd")
        with open(qmd_path, "w", encoding="utf-8") as f:
            f.write(
                """---
"""
                "title: \"Teste\"\n"
                "subtitle: \"Smoke Test\"\n"
                "institute: \"IFS\"\n"
                "date: today\n"
                "lang: pt-BR\n"
                "format:\n"
                "  revealjs:\n"
                "    theme: [simple, assets/ufs.scss]\n"
                "    css: assets/custom.css\n"
                "    slide-number: true\n"
                "---\n\n"
                "## Slide 1\n\n- ok\n"
            )

        env = os.environ.copy()
        env["QUARTO_PYTHON"] = sys.executable

        cmd = [
            "quarto",
            "render",
            "apresentacao.qmd",
            "--to",
            "revealjs",
            "--embed-resources",
            "--output-dir",
            ".",
        ]

        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            env=env,
        )

        out_html = os.path.join(work_dir, "apresentacao.html")
        print("exit=", result.returncode)
        print("html=", out_html)
        print("html_exists=", os.path.exists(out_html))
        if result.stdout:
            print("\nSTDOUT:\n", result.stdout[-2000:])
        if result.stderr:
            print("\nSTDERR:\n", result.stderr[-2000:])

        return 0 if result.returncode == 0 and os.path.exists(out_html) else 2

    finally:
        # Deixar o diretório temporário para inspeção se quiser (descomente para limpar)
        # shutil.rmtree(tmpdirname, ignore_errors=True)
        pass


if __name__ == "__main__":
    raise SystemExit(main())
