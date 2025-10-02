# PowerShell version of frosti.update.sh
param(
    [string]$Language = ""
)

# --- Configuration ---
$UPSTREAM_REPO = "https://github.com/EveSunMaple/Frosti.git"
$TEMP_DIR = "frosti_temp_update"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$I18N_DIR = Join-Path $SCRIPT_DIR "src\i18n"

# --- Color Functions ---
function Write-Red($message) { Write-Host $message -ForegroundColor Red }
function Write-Green($message) { Write-Host $message -ForegroundColor Green }
function Write-Yellow($message) { Write-Host $message -ForegroundColor Yellow }
function Write-Blue($message) { Write-Host $message -ForegroundColor Blue }

# --- Language Setup ---
# Default to English
$lang = "en"

# Detect language from system settings
$systemLang = [System.Globalization.CultureInfo]::CurrentCulture.TwoLetterISOLanguageName
if ($systemLang -eq "zh") {
    $lang = "zh"
}

# Allow user to override language with a command-line argument
if ($Language -ne "") {
    $langFile = Join-Path $I18N_DIR "$Language.ps1"
    if (Test-Path $langFile) {
        $lang = $Language
    } else {
        Write-Yellow "Warning: Language '$Language' not found. Falling back to '$lang'."
    }
}

# Source the language file
$langFile = Join-Path $I18N_DIR "$lang.ps1"
if (Test-Path $langFile) {
    . $langFile
} else {
    Write-Red "Error: Language file '$langFile' not found. Exiting."
    exit 1
}

# --- Main Script ---
Write-Blue "========================================="
Write-Blue "      $MSG_HEADER_TITLE      "
Write-Blue "========================================="

Write-Yellow $MSG_WARNING_TITLE
Write-Host $MSG_WARNING_RECOMMENDATION
Write-Host $MSG_WARNING_IGNORE
Write-Host ""

do {
    $response = Read-Host $PROMPT_CONTINUE
} while ($response -eq "")

if ($response -notmatch "^[Yy]$") {
    Write-Host $MSG_CANCELLED
    exit 1
}

# Check Git status
$gitStatus = git status --porcelain 2>$null
if ($LASTEXITCODE -ne 0 -or $gitStatus) {
    Write-Red $ERR_GIT_DIRTY
    Write-Host $ERR_GIT_DIRTY_ADVICE
    exit 1
}
Write-Green $MSG_GIT_CLEAN

# Step 1: Clone repository
Write-Blue "`n$MSG_STEP1_CLONE"
if (Test-Path $TEMP_DIR) {
    Remove-Item -Recurse -Force $TEMP_DIR
}

git clone --depth 1 $UPSTREAM_REPO $TEMP_DIR
if ($LASTEXITCODE -ne 0) {
    Write-Red $ERR_STEP1_CLONE_FAILED
    exit 1
}
Write-Green $MSG_STEP1_CLONE_SUCCESS

# Step 2: Copy files using robocopy (Windows equivalent of rsync)
Write-Blue "`n$MSG_STEP2_RSYNC"

# Read .updateignore file if it exists
$excludePatterns = @()
$updateIgnoreFile = ".updateignore"
if (Test-Path $updateIgnoreFile) {
    $excludePatterns = Get-Content $updateIgnoreFile | Where-Object { $_ -and !$_.StartsWith("#") }
}

# Function to check if a path should be excluded
function ShouldExclude($path) {
    foreach ($pattern in $excludePatterns) {
        if ($path -like $pattern) {
            return $true
        }
    }
    return $false
}

# Copy files recursively while respecting .updateignore
function Copy-WithExclusion($source, $destination) {
    try {
        $sourceItems = Get-ChildItem -Path $source -Recurse -Force
        foreach ($item in $sourceItems) {
            $relativePath = $item.FullName.Substring($source.Length + 1)
            $destPath = Join-Path $destination $relativePath
            
            if (!(ShouldExclude $relativePath)) {
                if ($item.PSIsContainer) {
                    if (!(Test-Path $destPath)) {
                        New-Item -Path $destPath -ItemType Directory -Force | Out-Null
                    }
                } else {
                    $destDir = Split-Path $destPath -Parent
                    if (!(Test-Path $destDir)) {
                        New-Item -Path $destDir -ItemType Directory -Force | Out-Null
                    }
                    Copy-Item -Path $item.FullName -Destination $destPath -Force
                }
            }
        }
        return $true
    } catch {
        return $false
    }
}

$copyResult = Copy-WithExclusion $TEMP_DIR "."
if (!$copyResult) {
    Write-Red $ERR_STEP2_RSYNC_FAILED
    Remove-Item -Recurse -Force $TEMP_DIR
    exit 1
}
Write-Green $MSG_STEP2_RSYNC_SUCCESS

# Step 3: Delete obsolete files
Write-Blue "`n$MSG_STEP3_DELETE"
Write-Host $MSG_STEP3_DELETING_DRY_RUN

# Get list of files that exist locally but not in the source
$sourceFiles = Get-ChildItem -Path $TEMP_DIR -Recurse -File | ForEach-Object { $_.FullName.Substring($TEMP_DIR.Length + 1) }
$localFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { $_.FullName -notlike "*\$TEMP_DIR\*" } | ForEach-Object { $_.FullName.Substring((Get-Location).Path.Length + 1) }

foreach ($localFile in $localFiles) {
    if ($sourceFiles -notcontains $localFile -and !(ShouldExclude $localFile)) {
        if (Test-Path $localFile) {
            Write-Host "$MSG_STEP3_DELETING_FILE $localFile"
            Remove-Item -Path $localFile -Force
        }
    }
}

# Remove empty directories
$localDirs = Get-ChildItem -Path "." -Recurse -Directory | Where-Object { $_.FullName -notlike "*\$TEMP_DIR\*" } | Sort-Object FullName -Descending
foreach ($dir in $localDirs) {
    $relativePath = $dir.FullName.Substring((Get-Location).Path.Length + 1)
    if (!(ShouldExclude $relativePath)) {
        $items = Get-ChildItem -Path $dir.FullName -Force
        if ($items.Count -eq 0) {
            Write-Host "$MSG_STEP3_DELETING_EMPTY_DIR $relativePath"
            Remove-Item -Path $dir.FullName -Force
        } else {
            Write-Host "$MSG_STEP3_SKIPPING_NON_EMPTY_DIR $relativePath"
        }
    }
}

Write-Green $MSG_STEP3_DELETE_SUCCESS

# Step 4: Clean empty directories
Write-Blue "`n$MSG_STEP4_CLEAN_EMPTY"
$emptyDirs = Get-ChildItem -Path "." -Recurse -Directory | Where-Object { 
    $_.FullName -notlike "*\$TEMP_DIR\*" -and 
    (Get-ChildItem -Path $_.FullName -Force).Count -eq 0 
} | Sort-Object FullName -Descending

foreach ($emptyDir in $emptyDirs) {
    Remove-Item -Path $emptyDir.FullName -Force
}
Write-Green $MSG_STEP4_CLEAN_EMPTY_SUCCESS

# Step 5: Clean temporary files
Write-Blue "`n$MSG_STEP5_CLEAN_TEMP"
Remove-Item -Recurse -Force $TEMP_DIR
Write-Green $MSG_STEP5_CLEAN_TEMP_SUCCESS

# Step 6: Install dependencies with pnpm
Write-Blue "`n$MSG_STEP6_PNPM"
$pnpmExists = Get-Command pnpm -ErrorAction SilentlyContinue
if (!$pnpmExists) {
    Write-Yellow $WARN_PNPM_NOT_FOUND
    Write-Host $WARN_PNPM_GUIDE
} else {
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-Red $ERR_PNPM_INSTALL_FAILED
        exit 1
    }
    Write-Green $MSG_PNPM_INSTALL_SUCCESS
}

Write-Green "`n$MSG_FINAL_SUCCESS"
Write-Host $MSG_FINAL_ADVICE

exit 0
