@echo off
rem ============================================================
rem  Windows(コマンドプロンプト)用 ローカル実行ヘルパー
rem  日本の通常回線から実行して Imunify360 のボット遮断を回避します。
rem
rem  使い方(実行前に set で設定 -> run_local.bat):
rem    set NOS=1,2
rem    run_local.bat                      … 既定は dry-run(投稿しない)
rem
rem    set MODE=post
rem    set STATUS=draft
rem    set WRITE_MODE=upsert
rem    set NOS=1,2
rem    run_local.bat                      … No.1,2 を下書き投稿(既存は更新)
rem
rem  設定を消したいときは cmd を閉じて開き直すか、 set NOS= のように空で上書き。
rem ============================================================
setlocal
cd /d "%~dp0"

if "%MODE%"==""       set "MODE=dry-run"
if "%STATUS%"==""     set "STATUS=draft"
if "%WRITE_MODE%"==""  set "WRITE_MODE=create_only"
if "%LIMIT%"==""      set "LIMIT=0"

rem NOS / CATEGORY は空(=全件 / Excel列使用)を許可するので既定値は入れない
set "INPUT_FILE=data/wordpress-security-production.xlsx"
set "ARTICLES_DIR=projects/wordpress-security/articles"
set "IMAGES_DIR=projects/wordpress-security/eyecatches"
set "RESULTS_DIR=projects/wordpress-security/results"

set "DRY_RUN_FLAG="
if /I "%MODE%"=="dry-run" set "DRY_RUN_FLAG=--dry-run"

rem Maintenance modes:
rem   MODE=list   ... audit managed posts on the site (read-only)
rem   MODE=delete ... list then permanently delete after typing yes
rem   MODE=media  ... delete duplicate unused eyecatch images after typing yes
set "EXTRA_FLAGS="
if /I "%MODE%"=="list"   set "EXTRA_FLAGS=--list-managed"
if /I "%MODE%"=="delete" set "EXTRA_FLAGS=--delete-managed"
if /I "%MODE%"=="media"  set "EXTRA_FLAGS=--cleanup-media"

echo ==============================================
echo   MODE=%MODE%  STATUS=%STATUS%  WRITE_MODE=%WRITE_MODE%  NOS=%NOS%  LIMIT=%LIMIT%
echo ==============================================

rem --sheet は指定しない(先頭シート「制作管理表」が自動で使われる)
python wp_auto_post.py --input "%INPUT_FILE%" --articles-dir "%ARTICLES_DIR%" --images-dir "%IMAGES_DIR%" --post-status "%STATUS%" --write-mode "%WRITE_MODE%" --category "%CATEGORY%" --nos "%NOS%" --limit "%LIMIT%" --output-dir "%RESULTS_DIR%" %DRY_RUN_FLAG% %EXTRA_FLAGS%

endlocal
