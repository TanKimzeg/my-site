import os
import sys
import subprocess
import shutil
from typing import Callable
import colorama
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

colorama.init(autoreset=True)

class Colors(Enum):
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    BLUE = colorama.Fore.BLUE
    YELLOW = colorama.Fore.YELLOW

class Messages:
    # --- Header ---
    msg_header_title: str

    # --- Warnings and Prompts ---
    msg_warning_title: str
    msg_warning_recommendation: str
    msg_warning_ignore: str
    prompt_continue: str
    msg_cancelled: str

    # --- Git Status ---
    err_git_dirty: str
    err_git_dirty_advice: str
    msg_git_clean: str

    # --- Final ---
    msg_step1_clone: str
    err_step1_clone_failed: str
    msg_step1_clone_success: str
    msg_step2_rsync: str
    err_step2_rsync_failed: str
    msg_step2_rsync_success: str
    msg_step3_delete: str
    msg_step3_deleting_dry_run: str
    msg_step3_deleting_empty_dir: str
    msg_step3_skipping_non_empty_dir: str
    msg_step3_deleting_file: str
    msg_step3_delete_success: str
    msg_step4_clean_empty: str
    msg_step4_clean_empty_success: str

    msg_step5_clean_temp: str
    msg_step5_clean_temp_success: str

    msg_step6_pnpm: str
    warn_pnpm_not_found: str
    warn_pnpm_guide: str
    err_pnpm_install_failed: str
    msg_pnpm_install_success: str

    # --- Final ---
    msg_final_success: str
    msg_final_advice: str
    
class ZhMSG(Messages):
    # --- Header ---
    msg_header_title = "Frosti 项目更新辅助脚本"

    # --- Warnings and Prompts ---
    msg_warning_title = "⚠️  警告: 此脚本将从官方仓库拉取最新文件并覆盖您的本地文件。"
    msg_warning_recommendation = "我们推荐您在更新前备份项目，或确保所有修改都已提交到 Git。"
    msg_warning_ignore = "此脚本会根据 `.updateignore` 文件来保护您的核心内容。"
    prompt_continue = "您是否理解风险并希望继续？(y/N): "
    msg_cancelled = "操作已取消。"

    # --- Git Status ---
    err_git_dirty = "❌ 错误: 您有未提交的本地修改。"
    err_git_dirty_advice = "为了安全起见，请先提交您的修改，然后再运行此脚本。"
    msg_git_clean = "✅ 本地Git状态干净，准备开始更新。"

    # --- Steps ---
    msg_step1_clone = "\n" + Colors.BLUE.value + "第一步: 正在从 GitHub 克隆最新的 Frosti 仓库..." 
    err_step1_clone_failed = "❌ 克隆失败，请检查您的网络连接或 Git 配置。"
    msg_step1_clone_success = "✅ 最新代码克隆成功！"
    msg_step2_rsync = "\n" + Colors.BLUE.value + "第二步: 正在安全地更新您的项目文件 (仅添加和覆盖)..."
    err_step2_rsync_failed = "❌ 文件更新失败。"
    msg_step2_rsync_success = "✅ 文件更新完成！"
    msg_step3_delete = "\n" + Colors.BLUE.value + "第三步: 正在智能删除官方已移除的文件 (不会影响您忽略的文件)..."
    msg_step3_deleting_dry_run = "正在进行干预式删除..."
    msg_step3_deleting_empty_dir = "删除空目录:"
    msg_step3_skipping_non_empty_dir = "跳过非空目录:"
    msg_step3_deleting_file = "删除文件:"
    msg_step3_delete_success = "✅ 已废弃文件清理完成。"
    msg_step4_clean_empty = "\n" + Colors.BLUE.value + "第四步: 正在清理所有残留的空文件夹..."
    msg_step4_clean_empty_success = "✅ 空文件夹清理完毕！"

    msg_step5_clean_temp = "\n" + Colors.BLUE.value + "第五步: 正在清理临时文件..."
    msg_step5_clean_temp_success = "✅ 清理完毕！"

    msg_step6_pnpm = "\n" + Colors.BLUE.value + "第六步: 正在使用 pnpm 安装/更新依赖..."
    warn_pnpm_not_found = "⚠️  警告: 未找到 pnpm 命令，请手动安装依赖。"
    warn_pnpm_guide = "您可以运行: npm install -g pnpm && pnpm install"
    err_pnpm_install_failed = "❌ 依赖安装失败，请手动运行 'pnpm install' 检查问题。"
    msg_pnpm_install_success = "✅ 依赖安装完成！"

    # --- Final ---
    msg_final_success = "\n" + Colors.GREEN.value + "🎉 更新流程全部完成！"
    msg_final_advice = "现在您可以启动项目，检查更新后的效果了。"

class EnMSG(Messages):
    # --- Header ---
    msg_header_title = "Frosti Project Update Assistant"

    # --- Warnings and Prompts ---
    msg_warning_title = "⚠️  Warning: This script will fetch the latest files from the official repository and overwrite your local files."
    msg_warning_recommendation = "We recommend backing up your project before updating, or ensuring all changes are committed to Git."
    msg_warning_ignore = "This script will protect your core content based on the `.updateignore` file."
    prompt_continue = "Do you understand the risks and wish to continue? (y/N): "
    msg_cancelled = "Operation cancelled."

    # --- Git Status ---
    err_git_dirty = "❌ Error: You have uncommitted local changes."
    err_git_dirty_advice = "For safety, please commit your changes before running this script."
    msg_git_clean = "✅ Local Git status is clean, ready to start the update."

    # --- Steps ---
    msg_step1_clone = "\n" + Colors.BLUE.value + "Step 1: Cloning the latest Frosti repository from GitHub..."
    err_step1_clone_failed = "❌ Clone failed. Please check your network connection or Git configuration."
    msg_step1_clone_success = "✅ Latest code cloned successfully!"

    msg_step2_rsync = "\n" + Colors.BLUE.value + "Step 2: Safely updating your project files (add and overwrite only)..."
    err_step2_rsync_failed = "❌ File update failed."
    msg_step2_rsync_success = "✅ File update complete!"

    msg_step3_delete = "\n" + Colors.BLUE.value + "Step 3: Intelligently deleting files removed from the official repo (won't affect your ignored files)..."
    msg_step3_deleting_dry_run = "Performing interactive deletion..."
    msg_step3_deleting_empty_dir = "Deleting empty directory:"
    msg_step3_skipping_non_empty_dir = "Skipping non-empty directory:"
    msg_step3_deleting_file = "Deleting file:"
    msg_step3_delete_success = "✅ Obsolete file cleanup complete."

    msg_step4_clean_empty = "\n" + Colors.BLUE.value + "Step 4: Cleaning up all remaining empty folders..."
    msg_step4_clean_empty_success = "✅ Empty folder cleanup complete!"

    msg_step5_clean_temp = "\n" + Colors.BLUE.value + "Step 5: Cleaning up temporary files..."
    msg_step5_clean_temp_success = "✅ Cleanup complete!"

    msg_step6_pnpm = "\n" + Colors.BLUE.value + "Step 6: Installing/updating dependencies with pnpm..."
    warn_pnpm_not_found = "⚠️  Warning: 'pnpm' command not found. Please install dependencies manually."
    warn_pnpm_guide = "You can run: npm install -g pnpm && pnpm install"
    err_pnpm_install_failed = "❌ Dependency installation failed. Please run 'pnpm install' manually to check for issues."
    msg_pnpm_install_success = "✅ Dependency installation complete!"

    # --- Final ---
    msg_final_success = "\n" + Colors.GREEN.value + "🎉 Update process fully completed!"
    msg_final_advice = "You can now start your project and check the updated results."


class MSG(Enum):
    ZH = ZhMSG()
    EN = EnMSG()

@dataclass
class Config:
    UPSTREAM_REPO = "https://github.com/EveSunMaple/Frosti.git"
    LANG = sys.argv[1].upper() if len(sys.argv) > 1 else "EN"
    ROOT = Path(__file__).parent.resolve()
    TEMP_DIR_NAME = "frosti_temp_update"
    TEMP_DIR = ROOT / TEMP_DIR_NAME
    IGNORE_FILE = ROOT / ".updateignore"
    MSG = MSG[LANG].value
    

def run(cmd: list[str], cwd: Path | None = None) -> int:
    p = subprocess.run(cmd, cwd=cwd)
    return p.returncode

def git_tree_clean() -> bool:
    res1 = run(["git", "diff", "--quiet"])
    res2 = run(["git", "diff", "--cached", "--quiet"])
    return res1 == 0 and res2 == 0

def load_ignore() -> Callable[[str], bool]:
    patterns: list[str] = []
    if Config.IGNORE_FILE.exists():
        patterns = Config.IGNORE_FILE.read_text(encoding="utf-8").splitlines()
    # default safe ignores（避免自删/误删）
    patterns += [
        ".git/",
        f"{Config.TEMP_DIR_NAME}/",
        Path(__file__).name,
    ]
    spec = None
    import fnmatch
    def is_ignored(rel_posix: str) -> bool:
        rp = rel_posix
        for pat in patterns:
            pat = pat.strip()
            if not pat or pat.startswith("#"):
                continue
            # directory pattern normalization
            if pat.endswith("/"):
                if rp == pat[:-1] or rp.startswith(pat):
                    return True
            if fnmatch.fnmatch(rp, pat):
                return True
        return False
    return is_ignored

def relpath(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()

def copy_from_temp(is_ignored: Callable[[str], bool]):
    for p in Config.TEMP_DIR.rglob("*"):
        rp = relpath(p, Config.TEMP_DIR)
        if not rp or is_ignored(rp):
            continue
        dst = Config.ROOT / rp
        if p.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)

def collect_paths(base: Path, is_ignored: Callable[[str], bool]) -> tuple[set[str], set[str]]:
    files, dirs = set(), set()
    for p in base.rglob("*"):
        if not p.exists():
            continue
        rp = relpath(p, base)
        if not rp or is_ignored(rp):
            continue
        if p.is_dir():
            dirs.add(rp)
        else:
            files.add(rp)
    return files, dirs

def delete_extras(is_ignored: Callable[[str], bool]):
    upstream_files, upstream_dirs = collect_paths(Config.TEMP_DIR, is_ignored)
    local_files, local_dirs = collect_paths(Config.ROOT, is_ignored)

    # files to delete: present locally but not in upstream
    files_to_delete = sorted(local_files - upstream_files)
    for rp in files_to_delete:
        try:
            (Config.ROOT / rp).unlink()
            print(Config.MSG.msg_step3_deleting_file, rp)
        except Exception:
            pass

    # dirs: delete only if empty after file deletion
    # sort by depth desc to try deeper first
    dirs_candidates = sorted(local_dirs - upstream_dirs, key=lambda s: s.count("/"), reverse=True)
    for rp in dirs_candidates:
        d = Config.ROOT / rp
        try:
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                print(Config.MSG.msg_step3_deleting_empty_dir, rp)
            else:
                print(Config.MSG.msg_step3_skipping_non_empty_dir, rp)
        except Exception:
            pass

def clean_empty_dirs():
    # Bottom-up removal of empty dirs
    for p in sorted([d for d in Config.ROOT.rglob("*") if d.is_dir()],
                    key=lambda x: x.as_posix().count("/"), reverse=True):
        try:
            if not any(p.iterdir()):
                p.rmdir()
        except Exception:
            pass

def main():
    print("=" * 40)
    msgs = Config.MSG
    print(msgs.msg_header_title)
    print("=" * 40)
    print(msgs.msg_warning_title)
    print(msgs.msg_warning_recommendation)
    print(msgs.msg_warning_ignore)

    ans = input(msgs.prompt_continue).strip().lower()
    if ans not in ('y', 'yes'):
        print(msgs.msg_cancelled)
        return 
    
    if not git_tree_clean():
        print(msgs.err_git_dirty)
        print(msgs.err_git_dirty_advice)
        return
    print(msgs.msg_git_clean)

    if Config.TEMP_DIR.exists():
        shutil.rmtree(Config.TEMP_DIR, ignore_errors=True)

    print(msgs.msg_step1_clone)
    if run(["git", "clone", "--depth", "1", Config.UPSTREAM_REPO, str(Config.TEMP_DIR)]) != 0:
        print(msgs.err_step1_clone_failed)
        return
    print(msgs.msg_step1_clone_success)

    print(msgs.msg_step2_rsync)
    is_ignored = load_ignore()
    try:
        copy_from_temp(is_ignored)
    except Exception:
        print(msgs.err_step2_rsync_failed)
        shutil.rmtree(Config.TEMP_DIR, ignore_errors=True)
        return
    print(msgs.msg_step2_rsync_success)

    print(msgs.msg_step3_delete)
    delete_extras(is_ignored)
    print(msgs.msg_step3_delete_success)

    print(msgs.msg_step4_clean_empty)
    clean_empty_dirs()
    print(msgs.msg_step4_clean_empty_success)

    print(msgs.msg_step5_clean_temp)
    # Windows 平台如遇权限问题，请使以管理员身份运行或手动删除临时文件夹
    shutil.rmtree(Config.TEMP_DIR, ignore_errors=True)
    print(msgs.msg_step5_clean_temp_success)

    print(msgs.msg_step6_pnpm)
    if shutil.which("pnpm"):
        rc = run(["cmd", "/c", "pnpm", "install"], cwd=Config.ROOT) if os.name == "nt" else run(["pnpm", "install"], cwd=Config.ROOT)
        if rc != 0:
            print(msgs.err_pnpm_install_failed)
            return
    else:
        print(msgs.warn_pnpm_not_found)
        print(msgs.warn_pnpm_guide)
        return
    print(msgs.msg_pnpm_install_success)

    print(msgs.msg_final_success)
    print(msgs.msg_final_advice)
    

if __name__ == "__main__":
    main()
