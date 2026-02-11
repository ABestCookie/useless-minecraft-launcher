#Install-Module -Name BurntToast -Force -Scope CurrentUser
Import-Module BurntToast



# 取得圖示的完整路徑
$logoPath = Join-Path (Get-Location) "art/java.ico"

# 建立通知
New-BurntToastNotification `
    -Text "UMCL 通知", "測試" `
    -AppLogo $logoPath `
    -Sound Default