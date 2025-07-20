import fs from 'fs/promises';
import path from 'path';

export async function createComposerCommand(projectRoot = process.cwd()) {
  const claudeDir = path.join(projectRoot, '.claude');
  const commandsDir = path.join(claudeDir, 'commands');
  const composerFile = path.join(commandsDir, 'composer.md');

  // .claude/commands ディレクトリを作成
  await fs.mkdir(commandsDir, { recursive: true });

  // composer.md の内容 - Fixed template literal with proper escaping
  const composerContent = `"""
--- allowed-tools: [Read, Bash, Glob, TodoWrite, Edit] description: "Compose multiple agents and execute tasks" ---

# /composer - Project building with several agents

## Purpose
Build, compile, and package projects with comprehensive error handling and optimization by coordinating multiple Claude Code agents.

## Usage
\`\`\`bash
/composer <project_description>
\`\`\`

Example:
\`\`\`bash
/composer create memo app
/composer build todo application with database
\`\`\`

## Role
You are the Composer Agent. You function as a coordinating agent that distributes tasks, provides context, and defines roles for multiple Claude Code Agents.

## Overview
Execute the following steps to realize the project specified in \\$ARGUMENTS.

## Execution Steps

1. **Project Confirmation**
   - Clarify user requirements and confirm project overview

2. **Directory Preparation**
   - Create \`.composer-agents\` directory if it doesn't exist
   \`\`\`bash
   mkdir -p .composer-agents
   \`\`\`

3. **Check Existing Files**
   - Check existing requirement definition files using Read tool
   \`\`\`bash
   # Check existence and read existing files
   ls .composer-agents/
   \`\`\`

4. **Create/Check Requirements Definition**
   - Check existence of \`requirements.md\` (attempt to read with Read tool)
   - Create new if it doesn't exist, confirm content if it exists
   - Confirm content with user and proceed to next step after approval

5. **Create/Check Design Document**
   - Check existence of \`design.md\` (attempt to read with Read tool)
   - Create new if it doesn't exist, confirm content if it exists
   - Confirm content with user and proceed to next step after approval

6. **Create/Check Task Division**
   - Check existence of \`tasks.md\` (attempt to read with Read tool)
   - Create new if it doesn't exist, confirm content if it exists
   - Assign integer numbers to each task
   - Confirm content with user and proceed to next step after approval

7. **Launch Sub-agents**
   - Detect operating system and available terminal emulators
   - Launch multiple terminals according to the number of tasks in \`tasks.md\`
   - Automatically start Claude Code agents in each terminal

## Cross-Platform Terminal Detection

### Operating System Detection
\`\`\`bash
# Detect OS
if [[ "\\$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "\\$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "\\$OSTYPE" == "cygwin" ]] || [[ "\\$OSTYPE" == "msys" ]] || [[ "\\$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    OS="unknown"
fi
\`\`\`

### Terminal Emulator Detection and Launch

#### Linux
\`\`\`bash
launch_linux_terminal() {
    local title="\\$1"
    local command="\\$2"
    
    # Try terminals in order of preference
    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --tab --title="\\$title" -- bash -c "\\$command; exec bash"
    elif command -v konsole >/dev/null 2>&1; then
        konsole --new-tab --title "\\$title" -e bash -c "\\$command; exec bash"
    elif command -v xfce4-terminal >/dev/null 2>&1; then
        xfce4-terminal --tab --title="\\$title" -e "bash -c '\\$command; exec bash'"
    elif command -v mate-terminal >/dev/null 2>&1; then
        mate-terminal --tab --title="\\$title" -e "bash -c '\\$command; exec bash'"
    elif command -v terminator >/dev/null 2>&1; then
        terminator --new-tab --title="\\$title" -e "bash -c '\\$command; exec bash'"
    elif command -v xterm >/dev/null 2>&1; then
        xterm -T "\\$title" -e bash -c "\\$command; exec bash" &
    elif command -v urxvt >/dev/null 2>&1; then
        urxvt -title "\\$title" -e bash -c "\\$command; exec bash" &
    else
        echo "No suitable terminal emulator found for Linux"
        return 1
    fi
}
\`\`\`

#### macOS
\`\`\`bash
launch_macos_terminal() {
    local title="\\$1"
    local command="\\$2"
    
    # Try terminals in order of preference
    if command -v osascript >/dev/null 2>&1; then
        # Use AppleScript to open Terminal.app
        osascript -e "
        tell application \\"Terminal\\"
            do script \\"\\$command\\"
            set custom title of front window to \\"\\$title\\"
            activate
        end tell"
    elif command -v iterm >/dev/null 2>&1; then
        # iTerm2 support
        osascript -e "
        tell application \\"iTerm\\"
            create window with default profile
            tell current session of current window
                write text \\"\\$command\\"
                set name to \\"\\$title\\"
            end tell
        end tell"
    else
        echo "No suitable terminal emulator found for macOS"
        return 1
    fi
}
\`\`\`

#### Windows & WSL2
\`\`\`bash
detect_wsl_environment() {
    # Check if running inside WSL
    if [[ -f /proc/version ]] && grep -qi microsoft /proc/version; then
        if [[ -n "\\$WSL_DISTRO_NAME" ]]; then
            echo "wsl2"
        else
            echo "wsl1"
        fi
    elif [[ "\\$OSTYPE" == "cygwin" ]] || [[ "\\$OSTYPE" == "msys" ]]; then
        echo "cygwin"
    elif [[ -n "\\$WINDIR" ]]; then
        echo "native_windows"
    else
        echo "unknown"
    fi
}

launch_windows_terminal() {
    local title="\\$1"
    local command="\\$2"
    local win_env=\\$(detect_wsl_environment)
    
    case \\$win_env in
        "wsl2"|"wsl1")
            # Running inside WSL - use Windows Terminal or cmd.exe from WSL
            if command -v wt.exe >/dev/null 2>&1; then
                # Windows Terminal - simplified command without exec bash
                local escaped_command=\\$(printf '%s' "\\$command" | sed 's/"/\\\\"/g')
                # Try different approaches in order of preference
                if wt.exe new-tab --title "\\$title" -- wsl.exe -d "\\$WSL_DISTRO_NAME" bash -c "\\$escaped_command" 2>/dev/null; then
                    return 0
                elif wt.exe new-tab --title "\\$title" -- wsl.exe bash -c "\\$escaped_command" 2>/dev/null; then
                    return 0
                elif wt.exe new-tab --title "\\$title" bash -c "\\$escaped_command" 2>/dev/null; then
                    return 0
                else
                    return 1
                fi
            elif command -v cmd.exe >/dev/null 2>&1; then
                # Command Prompt - launch new WSL session without exec bash
                local escaped_command=\\$(printf '%s' "\\$command" | sed 's/"/\\\\"/g')
                cmd.exe /c start "WSL Task" cmd.exe /k "wsl.exe -d \\$WSL_DISTRO_NAME bash -c \\"\\$escaped_command\\""
            elif command -v powershell.exe >/dev/null 2>&1; then
                # PowerShell - launch new WSL session without exec bash
                local escaped_command=\\$(printf '%s' "\\$command" | sed "s/'/\\\\\\\\'/g" | sed 's/"/\\\\"/g')
                powershell.exe -Command "Start-Process -FilePath 'wsl.exe' -ArgumentList '-d','\\$WSL_DISTRO_NAME','bash','-c','\\$escaped_command' -WindowStyle Normal"
            else
                # Fallback: try native Linux terminal emulators within WSL
                launch_wsl_native_terminal "\\$title" "\\$command"
            fi
            ;;
        "cygwin")
            # Cygwin environment - without exec bash
            if command -v mintty >/dev/null 2>&1; then
                mintty -t "\\$title" -e bash -c "\\$command" &
            elif command -v cmd >/dev/null 2>&1; then
                cmd /c start "cmd" /k "bash -c '\\$command'"
            fi
            ;;
        "native_windows")
            # Native Windows (not in WSL) - without exec bash
            if command -v wt >/dev/null 2>&1; then
                local escaped_command=\\$(printf '%s' "\\$command" | sed 's/"/\\\\"/g')
                wt new-tab --title "\\$title" -- wsl.exe bash -c "\\$escaped_command"
            elif command -v cmd >/dev/null 2>&1; then
                local escaped_command=\\$(printf '%s' "\\$command" | sed 's/"/\\\\"/g')
                cmd /c start "cmd" /k "wsl.exe bash -c \\"\\$escaped_command\\""
            elif command -v powershell >/dev/null 2>&1; then
                local escaped_command=\\$(printf '%s' "\\$command" | sed "s/'/\\\\\\\\'/g" | sed 's/"/\\\\"/g')
                powershell -Command "Start-Process -FilePath 'wsl.exe' -ArgumentList 'bash','-c','\\$escaped_command' -WindowStyle Normal"
            fi
            ;;
        *)
            echo "Unknown Windows environment: \\$win_env"
            return 1
            ;;
    esac
}
\`\`\`

### Universal Terminal Launcher
\`\`\`bash
launch_terminal() {
    local title="\\$1"
    local command="\\$2"
    
    case \\$OS in
        "linux")
            launch_linux_terminal "\\$title" "\\$command"
            ;;
        "macos")
            launch_macos_terminal "\\$title" "\\$command"
            ;;
        "windows")
            launch_windows_terminal "\\$title" "\\$command"
            ;;
        *)
            echo "Unsupported operating system: \\$OS"
            echo "Falling back to sequential execution..."
            return 1
            ;;
    esac
}
\`\`\`

## Rules

- **File Operation Order**: Always read files with Read tool before using Edit/TodoWrite tools
- **Information Certainty**: When there are uncertain points or insufficient information, clearly state "There is not enough information to evaluate this reliably"
- **Evidence Documentation**: Always document evidence or sources when making judgments
- **Respect Existing Files**: If requirement definition files (\`requirements.md\`, \`design.md\`, \`tasks.md\`) already exist, utilize the existing ones
- **File Protection**: Do not rewrite requirement definition files unless explicitly instructed
- **Error Handling**: Maintain comprehensive error handling and reporting
- **Command Execution**: Use Bash for executing build commands
- **Communication**: Get user confirmation at each step and obtain approval before proceeding
- **Cross-Platform Support**: Automatically detect OS and available terminal emulators
- **Graceful Fallback**: If terminal launching fails, fall back to sequential task execution

## File Structure
\`\`\`
project-root/
├── .composer-agents/
│   ├── requirements.md  # Requirements definition
│   ├── design.md        # Design document
│   └── tasks.md         # Task division
└── [project files]
\`\`\`

"""`;

  // ファイルを作成
  await fs.writeFile(composerFile, composerContent, 'utf-8');
  
  console.log(`✅ composer.mdを作成しました: ${composerFile}`);
  return composerFile;
}