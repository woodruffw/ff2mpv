
param (
  [Switch] $uninstall = $false,
  [Switch] $help = $false
)

$browser = $args[0]
$custom_hkcu = $args[1]

# Repository location
$repository_path = $PSScriptRoot
# Hold registry path in HKEY_CURRENT_USER
$hkcu_dest = ""
# Json
$json_path = $repository_path
# Edit json file for chromium
$use_chromium_json = $true
# Chrome Store Extension ID
$chrome_extension_id = "chrome-extension://ephjcajbkgplkjmelpglennepbpmdpjg/"
# List of browsers that this script support
$supported_browsers = @(
  'firefox',
  'librewolf',
  'chromium',
  'chrome',
  'edge',
  'brave',
  'custom-chromium',
  'custom-firefox'
)

function testCommand {
  Param ($command)
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = 'stop'
  try {
    if(Get-Command $command){return $true }
  } catch { return $false }
  finally { $ErrorActionPreference = $oldPreference }
}

function help {
  Write-Output "
    Installing script for ff2mpv
    Command syntax: > .\install.ps1 [browser] [registry_path] [-uninstall] [-help]


    Arguments:

    browser:          The name of the browser to install:
                       - $($supported_browsers -join "`n                       - ")

    registry_path:    The path in the registry for the NativeMessagingHost directory
                      Only needed if browser is `"custom-chromium`" or `"custom-firefox`"


    Flags:

    -uninstall        Uninstall the registry key value for the given browser

    -help             Show this message


    Usage:

    Install a supported browser (E.g. chromium):
    > .\install.ps1 chromium

    Install a custom browser (E.g. google chrome):
    > .\install.ps1 custom-chromium `"Registry::HKEY_CURRENT_USER\SOFTWARE\Google\Chrome`"

    Uninstall a supported browser (E.g. librewolf):
    > .\install.ps1 librewolf -uninstall

    Uninstall a custom browser (E.g. firefox):
    > .\install.ps1 custom-firefox `"Registry::HKEY_CURRENT_USER\SOFTWARE\Mozilla`" -uninstall

    Print help
    > .\install.ps1 -help
    "
}

function select_browser () {
  switch -Regex ($browser) {
    "^(firefox|librewolf)$" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Mozilla"
      $script:json_path = "$script:json_path\ff2mpv-windows.json"
      $script:use_chromium_json = $false
      break
    }
    "^chrome$" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Google\Chrome"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
      break
    }
    "^chromium$" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Chromium"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
      break
    }
    "^edge$" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
      break
    }
    "^brave$" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Google\Chrome"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
      break
    }
    "^custom-(chromium|firefox)$" {
      if (-not $custom_hkcu) {
        Write-Output "Please enter a path for HKEY_CURRENT_USER"
        $new_path = Read-Host -Prompt "> "
        $new_path = $new_path.Trim()
        if ($new_path -like 'exit*') {
          exit 0
        } elseif ($new_path -like 'help*') {
          help
          exit 0
        }
        $script:custom_hkcu = $new_path
        select_browser
        break
      } else {
        $script:hkcu_dest = $custom_hkcu.replace("/", "\")
        if (-not $script:hkcu_dest.StartsWith('Registry::','CurrentCultureIgnoreCase')) {
          $script:hkcu_dest = "Registry::$script:hkcu_dest"
        }
      }
    }
    "^custom-chromium$" {
      $script:json_path = "$script:json_path\ff2mpv-windows-$($script:hkcu_dest.split("\")[-1]).json"
      break
    }
    "^custom-firefox$" {
      $script:use_chromium_json = $false
      $script:json_path = "$script:json_path\ff2mpv-windows-$($script:hkcu_dest.split("\")[-1]).json"
      break
    }
    "^help$" {
      help
      exit 0
    }
    "^exit$" {
      exit 0
    }
    default {
      Write-Output ""
      Write-Output "Invalid option. Please select a valid browser:"
      $supported_browsers | % { Write-Output "> $_" }
      Write-Output ""
      Write-Output "E.g. To install for chromium:"
      Write-Output "> : `"chromium`""
      Write-Output ""
      Write-Output "For custom options provide the path in the registry as a second argument"
      Write-Output "E.g. If you want to custom install Google Chrome you can do:"
      Write-Output "> : `"custom-chromium`" `"Registry::HKEY_CURRENT_USER\SOFTWARE\Google\Chrome`""
      Write-Output ""
      Write-Output "Enter `"help`" to display more information or `"exit`" to quit."

      $new_input = Read-Host -Prompt "> "
      $new_input = $new_input.Trim()
      $brow, $hkcu = $new_input -split '\s+'

      $script:browser = $brow
      $script:custom_hkcu = $hkcu
      select_browser
    }
  }
}

function install () {
  select_browser
  $registry_dest = "$hkcu_dest\NativeMessagingHosts"
  $ff2mpv = "$registry_dest\ff2mpv"

  # Check if registry entry location for browser exists
  # The browser itself should create its own entry in registry but
  # some browsers default to search in the entries of some more popular browsers
  if (
    (($browser -eq 'librewolf') -or ($browser -eq 'brave')) -and -not (Test-Path "$hkcu_dest")
  ) {
    # LibreWolf: HKEY_CURRENT_USER\Software\LibreWolf.
    # But reads the entries for Mozilla Firefox and ignores the entries for LibreWolf.
    #
    # Brave: HKEY_CURRENT_USER\Software\BraveSoftware\Brave-Browser
    # But reads the entried for Google Chrome and ignores the entries for brave.
    Write-Output ""
    Write-Output "Creating `"$hkcu_dest`""
    Write-Output "entry in registry for $browser"
    # WARNING: The -Force will override the registry entry if exists.
    # Checking if the path exists (Test-Path) is very important to prevent that.
    New-Item -Path "$hkcu_dest" -Force
  }

  # Test if the browser path entry exist 
  if (-not (Test-Path $hkcu_dest)) {
    Write-Output ""
    Write-Output "Please start your browser at least once to generate the required registry entries"
    exit 1
  }

  # Create NativeMessagingHosts if it doesn't exits
  if (-not (Test-Path $registry_dest)) {
    Write-Output ""
    Write-Output "Creating NativeMessagingHosts entry..."
    New-Item -Path $registry_dest
  }

  # Handle ff2mpv registry
  if (Test-Path "$ff2mpv") {
    $current = (Get-ItemProperty "$ff2mpv")."(default)" 
    if ($current -eq "$json_path") {
      Write-Output ""
      Write-Output "Registry key already exists for browser `"$browser`""
    } else {
      Write-Output ""
      Write-Output "Registry key found with value:"
      Write-Output "$current"
      Write-Output "Overriding with: $json_path"
      New-Item -Path "$ff2mpv" -Value "$json_path" -Force
    }
  } else {
    Write-Output ""
    Write-Output "Creating registry key in:"
    Write-Output "$ff2mpv"
    Write-Output "with value: $json_path"
    New-Item -Path "$ff2mpv" -Value "$json_path"
  }

  # Detect Python Launcher
  $python = ""
  if (testCommand py) {
    Write-Output ""
    Write-Output "Found `"py`" launcher"
    $python = "py -3"
  } elseif (testCommand python3) {
    $python = "python3"
  } elseif (testCommand python) {
    $python = "python"
  } else {
    Write-Output ""
    Write-Output "Python not found!"
    Write-Output "Please install python and add it to your path to continue..."
    exit 1
  }

  # Batch script update
  $bat = "@echo off`ncall $python ff2mpv.py"
  [System.IO.File]::WriteAllLines("$repository_path\ff2mpv.bat", $bat)

  # JSON manipulation if using chromium based browser
  if ($use_chromium_json) {
    Write-Output ""
    Write-Output "Creating JSON for $browser browser..."
    $json_file = Get-Content "$repository_path\ff2mpv-windows.json" -Raw | ConvertFrom-Json
    $json_file.PSObject.Properties.Remove('allowed_extensions')
    $tmp_list = New-Object System.Collections.ArrayList
    $_ = $tmp_list.add($chrome_extension_id)
    $json_file | Add-Member -MemberType NoteProperty -Name "allowed_origins" -Value $tmp_list
    $json_file | ConvertTo-Json -Depth 32 | Set-Content "$json_path"
  } elseif ($browser -eq 'custom-firefox') {
    Write-Output ""
    Write-Output "Creating JSON for $browser browser..."
    Copy-Item "$repository_path\ff2mpv-windows.json" -Destination "$json_path"
  }

  # Show warning if mpv cannot be found in path
  if (-not (testCommand mpv)) {
    Write-Output ""
    Write-Output "**** WARNING: mpv was not found!!! ****"
    Write-Output "Make sure it is installed and in your path to use the extension!!!"
  }

  Write-Output ""
  Write-Output "DONE!"
}

function uninstall () {
  select_browser
  $registry_dest = "$hkcu_dest\NativeMessagingHosts"
  $ff2mpv = "$registry_dest\ff2mpv"

  # Test if the browser path entry exist 
  if (Test-Path "$ff2mpv") {
    Write-Output ""
    Write-Output "Removing registry key..."
    Remove-Item "$ff2mpv"
    Write-Output "Remove successful"
  } else {
    Write-Output ""
    Write-Output "Registry key for `"$browser`" not found."
  }
}

if ($help) {
  help
  exit 0
}

if ($uninstall) {
  uninstall
} else {
  install
}

exit 0
