# Xiaozhi ESP32 Server Configuration Editor

@config_editor.py Thanks to [github.com/xinnan-tech/xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server) developers for open-sourcing the project that allows us to experience the local Xiaozhi service system.

## Project Introduction

The Xiaozhi ESP32 Server Configuration Editor is a graphical tool designed specifically for the xiaozhi-esp32-server project, aimed at simplifying the configuration file editing process. Through an intuitive interface, users can easily view and modify various configurations in the `data/.config.yaml` file without manually editing the YAML file.

![Xiaozhi ESP32 Server Configuration Editor](https://znhblog.com/static/img/bdfad1d57be1564e618faad4589eb2af.20250313211705.webp)

## Main Features

- **Graphical Interface**: Intuitive user interface making configuration editing simpler
- **Configuration File Loading and Saving**: Support for loading and saving YAML configuration files while preserving original formatting and comments
- **Multi-language Support**: Interface elements displayed in Chinese to enhance user experience
- **Modular Configuration**: Categorized display of various module configurations, including server settings, log settings, module selection, etc.
- **Automatic Update Detection**: Automatically checks for new versions at startup
- **First-time Startup Detection**: Automatically detects configuration files and directories at first startup, prompting users to create them if needed

## Detailed Functionality

### Configuration File Management
- Load Configuration File: Support for loading YAML configuration files from any location
- Save Configuration File: Save modified configurations while preserving original formatting and comments
- Reset Configuration: Reset configuration to the state when it was loaded

### Module Configuration
- **Server Settings**: Configure IP address, port, and authentication information
- **Log Settings**: Set log level, format, and storage location
- **Module Selection**: Select which VAD, ASR, LLM, TTS, and other modules to use
- **Prompt Editing**: Edit AI prompts to determine behavior and response style
- **Music Settings**: Configure music directory and related parameters
- **Other Settings**: Including exit commands, no-speech disconnect time, etc.

### Special Features
- **Token List Editing**: Edit token lists directly through YAML text for greater flexibility
- **Dynamic Module Selection**: Automatically identify available modules based on the configuration file
- **Apply Changes Button**: Apply all modifications at once for improved operational efficiency
- **Scrollable View**: Support for scrolling through long content to ensure all configuration items are visible

## Installation and Usage

### Download
Download the latest version of the executable file from the [Releases](https://github.com/jwhna1/xiaozhi-esp32-config-editor/releases) page.
I've shared "Xiaozhi ESP32 Server Editor.zip" on Quark Netdisk. Click the link to save it. Open the "Quark APP" to play videos online without downloading, enjoy original quality at 5x speed, and support TV casting.
Link: https://pan.quark.cn/s/ab4c9229eda7
Or get the latest version from:
**Blog**: [https://znhblog.com](https://znhblog.com)
**Bilibili**: [https://space.bilibili.com/298384872](https://space.bilibili.com/298384872)

### Running
1. Extract the downloaded file
2. Double-click to run `config_editor.exe` (Windows) or `config_editor` (Linux/macOS)
3. On first run, the program will check if the `data/.config.yaml` file exists
   - If it doesn't exist, it will prompt you to create it from `config.yaml` or create an empty file
4. Once loaded, you can begin editing the configuration

### Editing Configuration
1. Select the configuration item to edit from the left menu
2. Modify the configuration values in the editing area on the right
3. Click the "Apply Changes" button in the bottom right to apply modifications
4. When finished, click the "Save to File" button to save to the configuration file

## Development Information

### Technology Stack
- Python 3.x
- Tkinter (GUI library)
- ruamel.yaml (YAML processing library)

### Dependencies
If you want to run the source code or build the program yourself, you need to install the following Python libraries:

```bash
# requirements.txt
ruamel.yaml==0.17.21
PyYAML==6.0
pyinstaller==5.9.0  # only needed for building executable
```

Main dependency descriptions:
- **ruamel.yaml**: For processing YAML files, preserving comments and formatting
- **PyYAML**: For simple YAML processing
- **tkinter**: Python standard library for creating GUI interfaces (no separate installation required)

### Building Yourself
To build the executable:
1. Install the required dependencies
2. Use PyInstaller to build the executable:
   ```
   pyinstaller --onefile --windowed config_editor.py
   ```

## Frequently Asked Questions

**Q: Why did the format of the configuration file change after saving?**  
A: The latest version uses the ruamel.yaml library to save configurations, which can preserve original formatting and comments. If you still have issues, please update to the latest version.

**Q: How do I add new tokens?**  
A: Select "Server Settings" from the left menu, then edit the "Token List" section. You can add new token items directly in the YAML text box.

**Q: How do I change which modules are used?**  
A: Select "Module Selection" from the left menu, then select the module type you want to use from the dropdown menu.
    
As this is my first developed tool, there may be some shortcomings. Please be kind and understanding.

## Contact Information

- **Author**: Zeng Nenghun
- **Blog**: [https://znhblog.com](https://znhblog.com)
- **Bilibili**: [https://space.bilibili.com/298384872](https://space.bilibili.com/298384872)
- **QQ**: 7280051
- **Email**: jwhna1@gmail.com

If you have questions, you can join the WeChat group to communicate (request the WeChat group QR code via private message on Bilibili)

## Update Log

### v0.1.4
- Added version detection and update functionality
- Fixed token list editing issues
- Optimized user interface, added global apply button

### v0.1.3
- Added "About" dialog
- Added Chinese interface support
- Fixed multiple bugs

### v0.1.2
- Added configuration file loading functionality
- Optimized menu layout

### v0.1.1
- Added startup detection logic
- Fixed editor display issues

### v0.1.0
- Initial version release

## License

This project is open-source under the MIT license.

## Acknowledgments

Special thanks to the developers of the [github.com/xinnan-tech/xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server) project, whose open-source project allows us to experience the local Xiaozhi service system.

---

If you find this tool useful, please give the original project [xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server) a star ⭐! 