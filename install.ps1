
param (
  [Switch] $uninstall = $false,
  [Switch] $help = $false
)

$browser = $args[0]
$custom_hkcu = $args[1]

# Hold registry path in HKEY_CURRENT_USER
$hkcu_dest = ""
# Json
$json_path = (pwd).toString()

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
  $pad = "    "
  Write-Output ""
  Write-Output "${pad}Installing script for ff2mpv"
  Write-Output "${pad}Command syntax: >.\install.ps1 [browser] [registry_path] [-uninstall] [-help]"
  Write-Output ""
  Write-Output ""
  Write-Output "${pad}Arguments:"
  Write-Output ""
  Write-Output "${pad}browser           The name of the browser to install"
  Write-Output "${pad}                  Valid options: firefox, chrome, chromium, edge, custom"
  Write-Output ""
  Write-Output "${pad}registry_path     The path in the registry for the NativeMessagingHost directory"
  Write-Output "${pad}                  Only needed if browser is `"custom`""
  Write-Output ""
  Write-Output ""
  Write-Output "${pad}Flags:"
  Write-Output ""
  Write-Output "${pad}-uninstall        Uninstall the registry key value for the given browser"
  Write-Output ""
  Write-Output "${pad}-help             Show this message"
  Write-Output ""
}

function select_browser () {
  switch ($browser) {
    "firefox" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Mozilla"
      $script:json_path = "$script:json_path\ff2mpv-windows.json"
    }
    "chrome" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Google\Chrome"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
    }
    "chromium" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Chromium"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
    }
    "edge" {
      $script:hkcu_dest = "Registry::HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge"
      $script:json_path = "$script:json_path\ff2mpv-windows-chrome.json"
    }
    "custom" {
      if (-not $custom_hkcu) {
        Write-Output "Please enter a path for HKEY_CURRENT_USER"
        $new_path = Read-Host -Prompt "> "
        $script:custom_hkcu = $new_path
        select_browser
      } else {
        $script:hkcu_dest = $custom_hkcu.replace("/", "\")
        $script:json_path = "$script:json_path\ff2mpv-windows-$($script:hkcu_dest.split("\")[-1]).json"
      }
    }
    "help" {
      help
      exit 0
    }
    "exit" {
      exit 0
    }
    default {
      Write-Output ""
      Write-Output "Invalid option. Please select a valid browser:"
      Write-Output "`"chrome`", `"firefox`", `"chromium`", `"edge`"`, or"
      Write-Output "`"custom`" and provide the path in the registry as a second argument"
      Write-Output "E.g. > `"custom`" `"Registry::HKEY_CURRENT_USER\SOFTWARE\Google\Chrome`" For Chrome"
      Write-Output ""
      Write-Output "Enter `"help`" to display more information or `"exit`" to quit."
      Write-Output ""
      $new_input = Read-Host -Prompt "> "
      $script:browser = $new_input.split()[0]
      $script:custom_hkcu = $new_input.split()[1]
      select_browser
    }
  }
}

function install () {
  select_browser
  $registry_dest = "$hkcu_dest\NativeMessagingHosts"

  # Test if the browser path entry exist 
  if (-not (Test-Path $hkcu_dest)) {
    Write-Output ""
    Write-Output "Please start your browser at least once to generate the required directories"
    exit 1
  }

  # Create NativeMessagingHosts if it doesn't exits
  if (-not (Test-Path $registry_dest)) {
    Write-Output ""
    Write-Output "Creating NativeMessagingHosts entry..."
    New-Item -Path $registry_dest
  }

  # Handle ff2mpv registry
  if (Test-Path "$registry_dest\ff2mpv") {
    $current = (Get-ItemProperty "$registry_dest\ff2mpv")."(default)" 
    if ($current -eq $json_path) {
      Write-Output ""
      Write-Output "Registry key already exists for browser `"$browser`""
    } else {
      Write-Output ""
      Write-Output "Registry key found with value:"
      Write-Output $current
      Write-Output "Overriding with: $json_path"
      New-Item -Path "$registry_dest\ff2mpv" -value $json_path -Force
    }
  } else {
    Write-Output ""
    Write-Output "Creating registry key in:"
    Write-Output "$registry_dest\ff2mpv"
    Write-Output "with value: $json_path"
    New-Item -Path "$registry_dest\ff2mpv" -value $json_path
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
    Write-Output "Python not found!"
    Write-Output "Please install python and add it to your path to continue..."
    exit 1
  }

  # Batch script update
  $bat = "@echo off
  call $python ff2mpv.py"
  $bat > "./ff2mpv.bat"

  # JSON manipulation if using chromium based browser
  if ($browser -ne "firefox") {
    Write-Output ""
    Write-Output "Creating JSON for $browser browser..."
    $json_file = Get-Content "./ff2mpv-windows.json" -raw | ConvertFrom-Json
    $json_file.PSObject.Properties.Remove('allowed_extensions')
    $tmp_list = New-Object System.Collections.ArrayList
    $_ = $tmp_list.add("chrome-extension://ephjcajbkgplkjmelpglennepbpmdpjg/")
    $json_file | Add-Member -MemberType NoteProperty -Name "allowed_origins" -value $tmp_list
    $json_file | ConvertTo-Json -depth 32 | Set-Content $json_path
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

  # Test if the browser path entry exist 
  if (Test-Path "$registry_dest\ff2mpv") {
    Write-Output ""
    Write-Output "Removing registry key..."
    Remove-Item "$registry_dest\ff2mpv"
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
