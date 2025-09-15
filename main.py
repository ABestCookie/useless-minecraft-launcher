import sys

if __name__ == "__main__":
    import sys

    args = sys.argv

    if "--help" in args:
        print("""
UMCL 啟動器 - 支援參數

--cui                啟用命令列模式啟動器
--version <版本>     搭配 --cui 使用，指定版本啟動
--help               顯示此說明

範例：
  python Tkui.py --cui
  python Tkui.py --cui --version 1.20.4
        """)
        sys.exit(0)

    if "--cui" in args:
        version_arg = None
        if "--version" in args:
            try:
                version_arg = args[args.index("--version") + 1]
            except IndexError:
                print("❌ 錯誤：缺少版本號，例如 --version 1.20.4")
                sys.exit(1)
        from app_mod.cui_main import launch_cui_mode
        launch_cui_mode(version_arg)
        
        sys.exit(0)

    # 預設進入 GUI 模式
    from app_mod.gui_main import main_app
    main_app()

