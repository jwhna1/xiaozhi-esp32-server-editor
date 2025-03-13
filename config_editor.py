import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import copy
import ruamel.yaml
import yaml  # 添加PyYAML导入
import urllib.request
import json
import webbrowser
import threading

class ConfigEditor:
    # 定义版本号常量
    VERSION = "0.1.4"
    VERSION_CHECK_URL = "https://api.github.com/repos/your-username/xiaozhi-esp32-config-editor/releases/latest"
    DOWNLOAD_URL = "https://github.com/your-username/xiaozhi-esp32-config-editor/releases/latest"
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"小智ESP32服务端配置编辑器v{self.VERSION}  作者：曾能混 关注我的B站 https://space.bilibili.com/298384872")
        self.root.geometry("1000x700")
        
        # 配置文件路径
        self.config_path = os.path.join('data', '.config.yaml')
        self.config = None
        self.original_config = None
        self.yaml = ruamel.yaml.YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        
        # 检查配置文件和目录
        self.check_config_file()
        
        # 初始化翻译字典
        self.init_translations()
        
        # 加载配置
        self.load_config()
        
        # 创建UI
        self.create_ui()
        
        # 启动后台线程检查更新
        threading.Thread(target=self.check_for_updates_silent, daemon=True).start()
        
    def check_config_file(self):
        """检查配置文件和目录是否存在，如果不存在则提示创建"""
        # 检查data目录是否存在
        data_dir = os.path.dirname(self.config_path)
        if not os.path.exists(data_dir):
            if messagebox.askyesno("目录不存在", f"目录 {data_dir} 不存在，是否创建?", parent=self.root):
                try:
                    os.makedirs(data_dir)
                    print(f"已创建目录: {data_dir}")
                except Exception as e:
                    messagebox.showerror("错误", f"创建目录失败: {str(e)}", parent=self.root)
                    self.root.destroy()
                    sys.exit(0)
            else:
                messagebox.showinfo("退出", "应用程序将退出", parent=self.root)
                self.root.destroy()
                sys.exit(0)
        
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            # 检查是否存在config.yaml文件
            source_config = "config.yaml"
            if os.path.exists(source_config):
                if messagebox.askyesno("配置文件不存在", 
                                      f"配置文件 {self.config_path} 不存在，是否从 {source_config} 复制创建?", 
                                      parent=self.root):
                    try:
                        import shutil
                        shutil.copy2(source_config, self.config_path)
                        messagebox.showinfo("成功", f"已从 {source_config} 创建 {self.config_path}", parent=self.root)
                    except Exception as e:
                        messagebox.showerror("错误", f"复制配置文件失败: {str(e)}", parent=self.root)
                        if messagebox.askyesno("创建空文件", "是否创建空的配置文件?", parent=self.root):
                            try:
                                with open(self.config_path, 'w', encoding='utf-8') as f:
                                    self.yaml.dump({}, f)
                                messagebox.showinfo("成功", f"已创建空的配置文件 {self.config_path}", parent=self.root)
                            except Exception as e:
                                messagebox.showerror("错误", f"创建配置文件失败: {str(e)}", parent=self.root)
                                self.root.destroy()
                                sys.exit(0)
                        else:
                            messagebox.showinfo("退出", "应用程序将退出", parent=self.root)
                            self.root.destroy()
                            sys.exit(0)
                else:
                    if messagebox.askyesno("创建空文件", "是否创建空的配置文件?", parent=self.root):
                        try:
                            with open(self.config_path, 'w', encoding='utf-8') as f:
                                self.yaml.dump({}, f)
                            messagebox.showinfo("成功", f"已创建空的配置文件 {self.config_path}", parent=self.root)
                        except Exception as e:
                            messagebox.showerror("错误", f"创建配置文件失败: {str(e)}", parent=self.root)
                            self.root.destroy()
                            sys.exit(0)
                    else:
                        messagebox.showinfo("退出", "应用程序将退出", parent=self.root)
                        self.root.destroy()
                        sys.exit(0)
            else:
                # 如果没有源配置文件，询问是否创建空的配置文件
                if messagebox.askyesno("配置文件不存在", 
                                      f"配置文件 {self.config_path} 不存在，且未找到源文件 {source_config}，是否创建空的配置文件?", 
                                      parent=self.root):
                    try:
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            self.yaml.dump({}, f)
                        messagebox.showinfo("成功", f"已创建空的配置文件 {self.config_path}", parent=self.root)
                    except Exception as e:
                        messagebox.showerror("错误", f"创建配置文件失败: {str(e)}", parent=self.root)
                        self.root.destroy()
                        sys.exit(0)
                else:
                    messagebox.showinfo("退出", "应用程序将退出", parent=self.root)
                    self.root.destroy()
                    sys.exit(0)
    
    def init_translations(self):
        """初始化翻译字典"""
        self.translations = {
            # 主菜单项
            "server": "服务器设置",
            "log": "日志设置",
            "iot": "物联网设备",
            "xiaozhi": "小智设置",
            "selected_module": "模块选择",
            "prompt": "提示词",
            "ASR": "语音识别",
            "VAD": "语音活动检测",
            "LLM": "大语言模型",
            "TTS": "语音合成",
            "Memory": "记忆模块",
            "Intent": "意图识别",
            "music": "音乐设置",
            "module_test": "模块测试",
            "delete_audio": "删除音频",
            "close_connection_no_voice_time": "无语音断开时间",
            "CMD_exit": "退出命令",
            "manager": "管理器",
            "use_private_config": "使用私有配置",
            
            # 服务器设置
            "ip": "IP地址",
            "port": "端口",
            "auth": "认证设置",
            "enabled": "启用",
            "tokens": "令牌列表",
            "token": "令牌",
            "name": "名称",
            "allowed_devices": "允许设备",
            
            # 日志设置
            "log_format": "日志格式",
            "log_format_simple": "简单日志格式",
            "log_level": "日志级别",
            "log_dir": "日志目录",
            "log_file": "日志文件",
            "data_dir": "数据目录",
            
            # 物联网设备
            "Speaker": "扬声器",
            "volume": "音量",
            
            # 小智设置
            "type": "类型",
            "version": "版本",
            "transport": "传输方式",
            "audio_params": "音频参数",
            "format": "格式",
            "sample_rate": "采样率",
            "channels": "通道数",
            "frame_duration": "帧持续时间",
            
            # 音乐设置
            "music_dir": "音乐目录",
            "music_ext": "音乐文件扩展名",
            "refresh_time": "刷新时间",
            
            # 模块测试
            "test_sentences": "测试句子",
            
            # 按钮和通用文本
            "Save": "保存",
            "Reset": "重置",
            "Add": "添加",
            "Edit": "编辑",
            "Delete": "删除",
            "Update": "更新",
            "Cancel": "取消",
            "Confirm": "确认",
            "Value": "值",
            "Enable": "启用",
            "Disable": "禁用",
            "Success": "成功",
            "Error": "错误",
            "Warning": "警告",
            
            # 模型名称
            "SileroVAD": "Silero语音活动检测",
            "FunASR": "Fun语音识别",
            "DoubaoASR": "豆包语音识别",
            "OllamaLLM": "Ollama大语言模型",
            "GPT_SOVITS_V2": "GPT语音合成V2",
            "GPT_SOVITS_V3": "GPT语音合成V3",
            "mem_local_short": "本地短期记忆",
            "intent_llm": "LLM意图识别",
            "function_call": "函数调用意图识别",
            "nointent": "无意图识别",
            "nomem": "无记忆",
            "mem0ai": "Mem0AI记忆",
        }
    
    def translate(self, key):
        """翻译键名"""
        return self.translations.get(key, key)
    
    def load_config(self):
        """加载配置文件，保留原始格式和注释"""
        try:
            # 初始化ruamel.yaml
            self.yaml = ruamel.yaml.YAML()
            self.yaml.preserve_quotes = True
            self.yaml.indent(mapping=2, sequence=4, offset=2)
            
            # 使用ruamel.yaml加载配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = self.yaml.load(f)
            
            # 保存原始配置的副本
            self.original_config = copy.deepcopy(self.config)
            
            if self.config is None:
                self.config = {}
                self.original_config = {}
            
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败: {str(e)}", parent=self.root)
            if hasattr(self, 'config') and self.config is not None:
                # 已有配置，不做任何操作
                return
            else:
                # 首次加载失败，退出程序
                self.root.destroy()
                sys.exit(0)
    
    def save_config(self):
        """保存配置文件，保留原始格式和注释"""
        try:
            # 创建备份
            import shutil
            backup_path = f"{self.config_path}.bak"
            try:
                shutil.copy2(self.config_path, backup_path)
            except Exception as e:
                print(f"创建备份失败: {str(e)}")
            
            # 使用ruamel.yaml保存配置，保留原始格式和注释
            with open(self.config_path, 'r', encoding='utf-8') as f:
                yaml_content = self.yaml.load(f)
            
            # 更新修改的值
            self.update_yaml_values(yaml_content, self.config)
            
            # 保存回文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(yaml_content, f)
            
            messagebox.showinfo("成功", "配置已保存", parent=self.root)
            self.original_config = copy.deepcopy(self.config)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置文件失败: {str(e)}", parent=self.root)
            
            # 如果保存失败且存在备份，询问是否恢复
            if os.path.exists(backup_path):
                if messagebox.askyesno("恢复备份", "保存失败，是否从备份恢复?", parent=self.root):
                    try:
                        shutil.copy2(backup_path, self.config_path)
                        messagebox.showinfo("成功", "已从备份恢复", parent=self.root)
                    except Exception as restore_err:
                        messagebox.showerror("错误", f"恢复备份失败: {str(restore_err)}", parent=self.root)
    
    def update_yaml_values(self, target, source):
        """递归更新YAML值，保留注释和格式"""
        if isinstance(source, dict) and isinstance(target, dict):
            for key, value in source.items():
                if key in target:
                    if isinstance(value, (dict, list)) and isinstance(target[key], (dict, list)):
                        self.update_yaml_values(target[key], value)
                    else:
                        target[key] = value
                else:
                    target[key] = value
        elif isinstance(source, list) and isinstance(target, list):
            # 对于列表，我们需要完全替换，因为索引可能已经改变
            target.clear()
            target.extend(source)
    
    def create_ui(self):
        """创建用户界面 - 添加检查更新按钮"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建工具栏
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 添加加载配置文件按钮
        ttk.Button(toolbar, text="加载配置", command=self.load_config_file_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="保存到文件", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="重置", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        
        # 添加检查更新按钮
        ttk.Button(toolbar, text="检查更新", command=self.check_for_updates).pack(side=tk.LEFT, padx=5)
        
        # 添加关于按钮
        ttk.Button(toolbar, text="关于", command=self.show_about).pack(side=tk.RIGHT, padx=5)
        
        # 显示当前配置文件路径
        self.file_path_var = tk.StringVar(value=f"当前配置: {self.config_path}")
        ttk.Label(toolbar, textvariable=self.file_path_var).pack(side=tk.RIGHT, padx=20)
        
        # 创建分割窗口
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧菜单区域
        left_frame = ttk.Frame(paned, width=120)
        paned.add(left_frame, weight=1)
        
        # 创建树形菜单
        self.menu_tree = ttk.Treeview(left_frame, show="tree")
        self.menu_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.menu_tree.bind("<<TreeviewSelect>>", self.on_menu_select)
        
        # 设置菜单样式，使文字完全靠左对齐
        style = ttk.Style()
        style.configure("Treeview", indent=0)
        
        # 填充菜单
        self.populate_menu()
        
        # 右侧内容区域 - 使用Frame包含内容和按钮区域
        right_container = ttk.Frame(paned)
        paned.add(right_container, weight=4)
        
        # 创建内容区域（带滚动条）
        content_container = ttk.Frame(right_container)
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(content_container)
        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=self.canvas.yview)
        
        # 创建内容框架
        self.content_frame = ttk.Frame(self.canvas)
        
        # 配置Canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # 绑定事件，确保内容框架宽度与Canvas宽度一致
        def configure_canvas(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind('<Configure>', configure_canvas)
        
        # 绑定事件，确保Canvas滚动区域与内容框架大小一致
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.content_frame.bind('<Configure>', configure_scroll_region)
        
        # 放置Canvas和滚动条
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加底部按钮区域（固定在底部）
        self.bottom_frame = ttk.Frame(right_container)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        
        # 添加全局应用更改按钮（始终可用）
        self.apply_button = ttk.Button(
            self.bottom_frame, 
            text="应用更改", 
            command=self.apply_changes
        )
        self.apply_button.pack(side=tk.RIGHT, padx=5)
        
        # 初始化变更跟踪字典
        self.changes = {}
        
        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def populate_menu(self):
        """填充左侧菜单 - 动态从配置文件读取"""
        self.menu_tree.delete(*self.menu_tree.get_children())
        
        # 按照特定顺序显示主要配置项
        priority_keys = [
            "server", "log", "iot", "xiaozhi", "selected_module", "prompt",
            "delete_audio", "close_connection_no_voice_time", "CMD_exit",
            "music", "module_test", "manager", "use_private_config"
        ]
        
        # 首先添加优先级高的配置项
        for key in priority_keys:
            if key in self.config:
                display_name = self.translate(key)
                self.menu_tree.insert("", "end", text=display_name, values=(key,))
        
        # 然后添加其他配置项
        for key in self.config:
            if key not in priority_keys:
                display_name = self.translate(key)
                self.menu_tree.insert("", "end", text=display_name, values=(key,))
    
    def filter_menu(self, search_text):
        """根据搜索文本过滤菜单"""
        self.menu_tree.delete(*self.menu_tree.get_children())
        search_text = search_text.lower()
        
        for key in self.config:
            if search_text in key.lower():
                self.menu_tree.insert("", "end", text=key, values=(key,))
    
    def on_menu_select(self, event):
        """处理菜单选择事件 - 使用翻译，去掉标题框"""
        selected = self.menu_tree.selection()
        if not selected:
            return
        
        item = self.menu_tree.item(selected[0])
        key = item['values'][0]
        
        # 添加调试信息
        print(f"选择菜单项: {key}")
        print(f"配置类型: {type(self.config[key])}")
        if isinstance(self.config[key], dict):
            print(f"子项: {list(self.config[key].keys())}")
        
        # 清空内容区
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建编辑界面
        try:
            self.create_editor(key, self.config[key])
        except Exception as e:
            messagebox.showerror("错误", f"创建编辑界面失败: {str(e)}", parent=self.root)
            import traceback
            traceback.print_exc()
    
    def create_editor(self, key, value):
        """创建编辑界面，在内容框架中创建编辑器"""
        # 清空内容区
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 根据不同类型创建不同的编辑器
        if key == "prompt":
            self.create_prompt_editor(self.content_frame, key, value)
        elif key == "selected_module":
            self.create_module_selector(self.content_frame, key, value)
        elif isinstance(value, dict):
            self.create_dict_editor(self.content_frame, key, value)
        elif isinstance(value, list):
            self.create_list_editor(self.content_frame, key, value)
        elif isinstance(value, bool):
            self.create_bool_editor(self.content_frame, key, value)
        else:
            self.create_simple_editor(self.content_frame, key, value)
        
        # 重置滚动位置到顶部
        self.canvas.yview_moveto(0)
    
    def create_prompt_editor(self, parent, key, value):
        """创建提示词编辑器 - 使用全局保存按钮"""
        frame = ttk.LabelFrame(parent, text="编辑提示词")
        frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
        
        # 添加说明
        ttk.Label(
            frame, 
            text="提示词决定AI的行为和回复风格，请谨慎编辑",
            wraplength=700
        ).pack(anchor=tk.W, padx=10, pady=(5, 10))
        
        # 创建文本编辑器
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        text.insert(tk.END, value)
        
        # 添加文本变更事件
        def on_text_change(event=None):
            self.track_change(key, text.get(1.0, tk.END).strip())
        
        text.bind("<KeyRelease>", on_text_change)
        
        # 创建按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="重置", 
            command=lambda: text.delete(1.0, tk.END) or text.insert(tk.END, value)
        ).pack(side=tk.LEFT, padx=5)
    
    def create_module_selector(self, parent, key, value):
        """创建模块选择器界面 - 动态适应配置文件变化"""
        ttk.Label(
            parent, 
            text="选择要使用的各类模块",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, padx=10, pady=(5, 10))
        
        # 模块说明 - 从配置文件中提取注释
        module_descriptions = self.extract_module_descriptions()
        
        # 为每个模块创建选择器
        for module_type, current_value in value.items():
            # 创建模块框架
            module_frame = ttk.LabelFrame(parent, text=f"{self.translate(module_type)}")
            module_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
                
            # 添加模块描述
            if module_type in module_descriptions:
                ttk.Label(
                    module_frame, 
                    text=module_descriptions[module_type],
                    wraplength=700
                ).pack(anchor=tk.W, padx=10, pady=(5, 10))
            
            # 获取可用的选项
            options = self.get_available_options(module_type)
                
            # 创建选择框架
            select_frame = ttk.Frame(module_frame)
            select_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(select_frame, text="当前选择:").pack(side=tk.LEFT, padx=(0, 10))
            
            # 创建下拉菜单
            combo_var = tk.StringVar(value=current_value)
            
            # 如果当前值不在选项中，添加它
            if current_value not in options and current_value:
                options.append(current_value)
            
            # 如果没有选项，添加一个空选项
            if not options:
                options = [""]
            
            combo = ttk.Combobox(
                select_frame, 
                textvariable=combo_var,
                values=options,
                width=30,
                state="readonly"
            )
            combo.pack(side=tk.LEFT, padx=(0, 10))
            
            # 添加变更跟踪
            def on_combo_change(module=module_type, var=combo_var):
                self.track_nested_change(key, module, None, var.get())
            
            # 绑定下拉菜单变更事件
            combo.bind("<<ComboboxSelected>>", lambda event, m=module_type, v=combo_var: 
                      self.track_nested_change(key, m, None, v.get()))
    
    def create_dict_editor(self, parent, key, value):
        """创建字典编辑器 - 使用翻译"""
        ttk.Label(
            parent, 
            text=f"编辑 {self.translate(key)} 配置", 
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, padx=10, pady=(5, 10))
        
        # 为每个子项创建编辑框架
        for sub_key, sub_value in value.items():
            # 创建子项框架 - 使用翻译
            sub_frame = ttk.LabelFrame(parent, text=self.translate(sub_key))
            sub_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
            
            if isinstance(sub_value, dict):
                self.create_nested_dict_editor(sub_frame, key, sub_key, sub_value)
            elif isinstance(sub_value, list):
                self.create_nested_list_editor(sub_frame, key, sub_key, sub_value)
            elif isinstance(sub_value, bool):
                self.create_nested_bool_editor(sub_frame, key, sub_key, sub_value)
            else:
                self.create_nested_simple_editor(sub_frame, key, sub_key, sub_value)
    
    def create_nested_list_editor(self, parent, parent_key, key, value):
        """创建嵌套列表编辑器 - 为tokens列表提供文本编辑方式"""
        # 检查是否是tokens列表
        is_tokens_list = (key == "tokens")
        
        # 如果是tokens列表，使用文本编辑方式
        if is_tokens_list:
            # 创建框架
            text_frame = ttk.Frame(parent)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 提取真实数据（去除ruamel.yaml内部结构）
            clean_tokens = []
            for item in value:
                clean_token = {}
                if 'token' in item:
                    clean_token['token'] = str(item['token'])
                if 'name' in item:
                    clean_token['name'] = str(item['name'])
                if 'allowed_devices' in item:
                    clean_token['allowed_devices'] = [str(dev) for dev in item.get('allowed_devices', [])]
                clean_tokens.append(clean_token)
            
            # 转换为普通YAML文本
            import yaml
            yaml_text = yaml.dump(clean_tokens, default_flow_style=False)
            
            # 创建文本编辑器
            text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=10)
            text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text.insert(tk.END, yaml_text)
            
            # 添加说明
            ttk.Label(
                text_frame, 
                text="请按YAML格式编辑令牌列表，每个令牌项包含token和name字段",
                wraplength=700,
                foreground="gray"
            ).pack(anchor=tk.W, padx=5, pady=(5, 0))
            
            # 添加文本变更事件
            def on_text_change(event=None):
                try:
                    # 尝试解析YAML文本
                    new_value = yaml.safe_load(text.get(1.0, tk.END))
                    if new_value is None:
                        new_value = []
                    
                    # 验证格式
                    valid = True
                    for item in new_value:
                        if not isinstance(item, dict) or 'token' not in item or 'name' not in item:
                            valid = False
                            break
                    
                    if valid:
                        # 跟踪变更
                        self.track_nested_change(parent_key, key, None, new_value)
                        # 移除错误提示（如果有）
                        for widget in text_frame.winfo_children():
                            if hasattr(widget, 'error_label') and widget.error_label:
                                widget.error_label.destroy()
                                widget.error_label = None
                    else:
                        # 显示错误提示
                        if not hasattr(text, 'error_label') or not text.error_label:
                            text.error_label = ttk.Label(
                                text_frame, 
                                text="格式错误：每个项必须包含token和name字段",
                                foreground="red"
                            )
                            text.error_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
                except Exception as e:
                    # 显示错误提示
                    if not hasattr(text, 'error_label') or not text.error_label:
                        text.error_label = ttk.Label(
                            text_frame, 
                            text=f"YAML解析错误: {str(e)}",
                            foreground="red"
                        )
                        text.error_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
            
            text.bind("<KeyRelease>", on_text_change)
            
            # 添加重置按钮
            btn_frame = ttk.Frame(parent)
            btn_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Button(
                btn_frame, 
                text="重置", 
                command=lambda: text.delete(1.0, tk.END) or text.insert(tk.END, yaml.dump(clean_tokens, default_flow_style=False))
            ).pack(side=tk.LEFT, padx=5)
        else:
            # 创建列表框
            list_frame = ttk.Frame(parent)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 列表显示
            listbox = tk.Listbox(list_frame, height=6)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 滚动条
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.config(yscrollcommand=scrollbar.set)
            
            # 填充列表
            for item in value:
                listbox.insert(tk.END, str(item))
            
            # 编辑按钮
            btn_frame = ttk.Frame(parent)
            btn_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # 添加按钮 - 使用变更跟踪
            def add_item():
                dialog = tk.Toplevel(self.root)
                dialog.title("添加项")
                dialog.geometry("300x100")
                dialog.transient(self.root)
                dialog.grab_set()
                
                ttk.Label(dialog, text="输入新项:").pack(pady=(10, 5))
                
                var = tk.StringVar()
                entry = ttk.Entry(dialog, textvariable=var, width=40)
                entry.pack(pady=5)
                
                def add():
                    value = var.get()
                    if value:
                        # 获取当前列表的副本
                        current_list = []
                        parts = parent_key.split(".")
                        current = self.config
                        for part in parts:
                            current = current[part]
                        current_list = current[key].copy()
                        current_list.append(value)
                        
                        # 跟踪变更
                        self.track_nested_change(parent_key, key, None, current_list)
                        
                        # 更新UI
                        listbox.insert(tk.END, value)
                        dialog.destroy()
                
            ttk.Button(btn_frame, text="添加", command=add_item).pack(side=tk.LEFT, padx=5)
            
            # 编辑按钮 - 使用变更跟踪
            def edit_item():
                selected = listbox.curselection()
                if not selected:
                    messagebox.showwarning("警告", "请先选择一项", parent=self.root)
                    return
                
                index = selected[0]
                
                # 获取当前值
                parts = parent_key.split(".")
                current = self.config
                for part in parts:
                    current = current[part]
                old_value = current[key][index]
                
                dialog = tk.Toplevel(self.root)
                dialog.title("编辑项")
                dialog.geometry("300x100")
                dialog.transient(self.root)
                dialog.grab_set()
                
                ttk.Label(dialog, text="编辑项:").pack(pady=(10, 5))
                
                var = tk.StringVar(value=str(old_value))
                entry = ttk.Entry(dialog, textvariable=var, width=40)
                entry.pack(pady=5)
                
                def update():
                    value = var.get()
                    if value:
                        # 获取当前列表的副本
                        current_list = []
                        parts = parent_key.split(".")
                        current = self.config
                        for part in parts:
                            current = current[part]
                        current_list = current[key].copy()
                        current_list[index] = value
                        
                        # 跟踪变更
                        self.track_nested_change(parent_key, key, None, current_list)
                        
                        # 更新UI
                        listbox.delete(index)
                        listbox.insert(index, value)
                        dialog.destroy()
                
                ttk.Button(dialog, text="更新", command=update).pack(pady=5)
            
            ttk.Button(btn_frame, text="编辑", command=edit_item).pack(side=tk.LEFT, padx=5)
            
            # 删除按钮 - 使用变更跟踪
            def delete_item():
                selected = listbox.curselection()
                if not selected:
                    messagebox.showwarning("警告", "请先选择一项", parent=self.root)
                    return
                
                index = selected[0]
                if messagebox.askyesno("确认", "确定要删除所选项吗?", parent=self.root):
                    # 获取当前列表的副本
                    current_list = []
                    parts = parent_key.split(".")
                    current = self.config
                    for part in parts:
                        current = current[part]
                    current_list = current[key].copy()
                    del current_list[index]
                    
                    # 跟踪变更
                    self.track_nested_change(parent_key, key, None, current_list)
                    
                    # 更新UI
                    listbox.delete(index)
    
    def create_bool_editor(self, parent, key, value):
        """创建布尔值编辑器 - 移除保存按钮，添加变更跟踪"""
        frame = ttk.LabelFrame(parent, text=f"编辑 {key}")
        frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
        
        var = tk.BooleanVar(value=value)
        # 添加变更跟踪
        var.trace_add("write", lambda *args: self.track_change(key, var.get()))
        
        # 创建选择框架
        select_frame = ttk.Frame(frame)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(
            select_frame, 
            text="启用", 
            variable=var
        ).pack(side=tk.LEFT, padx=(0, 10))
    
    def create_simple_editor(self, parent, key, value):
        """创建简单值编辑器 - 移除保存按钮，添加变更跟踪"""
        frame = ttk.LabelFrame(parent, text=f"编辑 {key}")
        frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
        
        # 创建编辑框架
        edit_frame = ttk.Frame(frame)
        edit_frame.pack(fill=tk.X, padx=10, pady=10)
        
        var = tk.StringVar(value=str(value))
        # 添加变更跟踪
        var.trace_add("write", lambda *args: self.track_change(key, var.get(), type(value)))
        
        ttk.Label(edit_frame, text="值:").pack(side=tk.LEFT, padx=(0, 5))
        
        entry = ttk.Entry(edit_frame, textvariable=var, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    def create_nested_dict_editor(self, parent, parent_key, key, value):
        """创建嵌套字典编辑器 - 去掉多余的容器框架"""
        # 直接在父框架中创建子项，不使用额外的容器框架
        for sub_key, sub_value in value.items():
            # 创建子项框架
            sub_frame = ttk.LabelFrame(parent, text=sub_key)
            sub_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
            
            if isinstance(sub_value, dict):
                # 递归处理嵌套字典
                self.create_nested_dict_editor(sub_frame, f"{parent_key}.{key}", sub_key, sub_value)
            elif isinstance(sub_value, list):
                # 处理嵌套列表 - 修复这里，添加缺少的key参数
                self.create_nested_list_editor(sub_frame, f"{parent_key}.{key}", sub_key, sub_value)
            elif isinstance(sub_value, bool):
                # 处理嵌套布尔值
                var = tk.BooleanVar(value=sub_value)
                check_frame = ttk.Frame(sub_frame)
                check_frame.pack(fill=tk.X, padx=5, pady=5)
                
                ttk.Checkbutton(
                    check_frame, 
                    text="启用", 
                    variable=var
                ).pack(side=tk.LEFT, padx=(0, 10))
                
                ttk.Button(
                    check_frame, 
                    text="保存", 
                    command=lambda p=f"{parent_key}.{key}", k=sub_key, v=var: 
                        self.update_nested_value(p, k, None, v.get())
                ).pack(side=tk.LEFT)
            else:
                # 处理嵌套简单值
                self.create_nested_simple_editor(sub_frame, f"{parent_key}.{key}", sub_key, sub_value)
    
    def create_nested_bool_editor(self, parent, parent_key, key, value):
        """创建嵌套布尔值编辑器"""
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        var = tk.BooleanVar(value=value)
        
        ttk.Checkbutton(
            edit_frame, 
            text="启用", 
            variable=var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            edit_frame, 
            text="保存", 
            command=lambda p=parent_key, k=key, v=var: 
                self.update_nested_value(p, k, None, v.get())
        ).pack(side=tk.LEFT)
    
    def create_nested_simple_editor(self, parent, parent_key, key, value):
        """创建嵌套简单值编辑器 - 移除保存按钮，添加变更跟踪"""
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加说明标签
        if isinstance(value, str):
            if value.startswith("你的") or value.startswith("your"):
                ttk.Label(
                    edit_frame, 
                    text="请输入您的配置值",
                    foreground="gray"
                ).pack(anchor=tk.W, padx=5, pady=(0, 5))
            elif "#" in value:  # 如果值中包含注释
                comment = value.split("#", 1)[1].strip()
                ttk.Label(
                    edit_frame, 
                    text=comment,
                    foreground="gray"
                ).pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        var = tk.StringVar(value=str(value))
        # 添加变更跟踪
        var.trace_add("write", lambda *args: self.track_nested_change(parent_key, key, None, var.get(), type(value)))
        
        ttk.Label(edit_frame, text=f"{key}:").pack(side=tk.LEFT, padx=(0, 5))
        
        entry = ttk.Entry(edit_frame, textvariable=var, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    def update_value(self, key, value):
        """更新配置值"""
        self.config[key] = value
        messagebox.showinfo("成功", f"{key} 已更新", parent=self.root)
    
    def update_nested_value(self, parent_key, key, sub_key, value):
        """更新嵌套配置值"""
        try:
            if "." in parent_key:  # 处理多层嵌套
                parts = parent_key.split(".")
                current = self.config
                for part in parts:
                    current = current[part]
            
            if sub_key:
                current[key][sub_key] = value
            else:
                current[key] = value
        
            messagebox.showinfo("成功", f"{sub_key if sub_key else key} 已更新", parent=self.root)
        except Exception as e:
            messagebox.showerror("错误", f"更新配置失败: {str(e)}\n路径: {parent_key}.{key}" + 
                                (f".{sub_key}" if sub_key else ""), parent=self.root)
    
    def add_list_item(self, key, listbox):
        """添加列表项"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加项")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="输入新项:").pack(pady=(10, 5))
        
        var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=var, width=40)
        entry.pack(pady=5)
        
        def add():
            value = var.get()
            if value:
                self.config[key].append(value)
                listbox.insert(tk.END, value)
                dialog.destroy()
        
        ttk.Button(dialog, text="添加", command=add).pack(pady=5)
    
    def edit_list_item(self, key, listbox):
        """编辑列表项"""
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一项", parent=self.root)
            return
        
        index = selected[0]
        old_value = self.config[key][index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑项")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="编辑项:").pack(pady=(10, 5))
        
        var = tk.StringVar(value=str(old_value))
        entry = ttk.Entry(dialog, textvariable=var, width=40)
        entry.pack(pady=5)
        
        def update():
            value = var.get()
            if value:
                self.config[key][index] = value
                listbox.delete(index)
                listbox.insert(index, value)
                dialog.destroy()
        
        ttk.Button(dialog, text="更新", command=update).pack(pady=5)
    
    def delete_list_item(self, key, listbox):
        """删除列表项"""
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一项", parent=self.root)
            return
        
        index = selected[0]
        if messagebox.askyesno("确认", "确定要删除所选项吗?", parent=self.root):
            del self.config[key][index]
            listbox.delete(index)
    
    def convert_value(self, value_str, value_type):
        """转换值类型"""
        try:
            if value_type == int:
                return int(value_str)
            elif value_type == float:
                return float(value_str)
            elif value_type == bool:
                return value_str.lower() in ('true', 'yes', '1', 'y')
            else:
                return value_str
        except ValueError:
            return value_str
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置所有更改吗?", parent=self.root):
            self.config = copy.deepcopy(self.original_config)
            messagebox.showinfo("成功", "配置已重置", parent=self.root)
            self.populate_menu()

    def get_available_options(self, module_type):
        """获取指定模块类型的可用选项 - 动态从配置文件读取"""
        options = []
        
        # 尝试从配置文件中读取选项
        try:
            # 首先检查配置文件中是否存在该模块类型的配置
            if module_type in self.config:
                options = list(self.config[module_type].keys())
            
            # 如果是selected_module中的模块，检查对应的配置部分
            if module_type in ["VAD", "ASR", "LLM", "TTS", "Memory", "Intent"]:
                # 查找配置文件中对应的部分
                if module_type in self.config:
                    options = list(self.config[module_type].keys())
                
                # 如果没有找到或为空，使用默认值
                if not options:
                    if module_type == "Intent":
                        options = ["nointent", "intent_llm", "function_call"]
                    elif module_type == "Memory":
                        options = ["nomem", "mem0ai", "mem_local_short"]
                    elif module_type == "VAD":
                        options = ["SileroVAD"]
                    elif module_type == "ASR":
                        options = ["FunASR", "DoubaoASR"]
                    elif module_type == "LLM":
                        options = ["OllamaLLM"]  # 提供一个默认选项
                    elif module_type == "TTS":
                        options = ["EdgeTTS"]  # 提供一个默认选项
        except Exception as e:
            print(f"获取模块选项时出错: {str(e)}")
            # 出错时使用空列表
            options = []
        
        return options

    def update_module_selection(self, parent_key, module_type, selected_value):
        """更新模块选择"""
        self.config[parent_key][module_type] = selected_value
        messagebox.showinfo("成功", f"{module_type} 已更新为 {selected_value}", parent=self.root)

    def show_about(self):
        """显示关于对话框 - 添加检查更新按钮"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("600x400")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 创建标题
        title_frame = ttk.Frame(about_window)
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="小智ESP32服务端配置编辑器", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor=tk.W)
        
        version_frame = ttk.Frame(title_frame)
        version_frame.pack(anchor=tk.W, fill=tk.X, pady=(5, 0))
        
        version_label = ttk.Label(
            version_frame, 
            text=f"当前版本: v{self.VERSION}", 
            font=("Arial", 10)
        )
        version_label.pack(side=tk.LEFT)
        
        # 添加检查更新按钮
        ttk.Button(
            version_frame, 
            text="检查更新", 
            command=self.check_for_updates,
            width=10
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # 创建说明文本框
        text_frame = ttk.Frame(about_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        about_text = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            font=("Arial", 10),
            padx=10,
            pady=10,
            height=15
        )
        about_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=about_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        about_text.configure(yscrollcommand=scrollbar.set)
        
        # 设置文本内容
        about_content = f"""本配置器是基于github开源项目https://github.com/xinnan-tech/xiaozhi-esp32-server 
开发的UI配置工具更方便直观的修改服务端配置
如查程序不能在线更新也可到我的blog获取最新版本：http://znhblog.com
也可关注我的B站 https://space.bilibili.com/298384872

如果有问题可加微信群一起沟通（在B站私信索取微信群加群二维码）

这是一个用于编辑xiaozhi-esp32-server 配置文件的图形界面工具。
它允许您轻松查看和修改 `data/.config.yaml` 文件中的配置项，而无需手动编辑YAML文件。
联系方式：
QQ：7280051
邮箱：jwhna1@gmail.com

当前版本为v{self.VERSION}
"""
        
        about_text.insert(tk.END, about_content.format(self.VERSION))
        
        # 设置文本为只读，但可复制
        about_text.configure(state="disabled")
        
        # 添加关闭按钮
        button_frame = ttk.Frame(about_window)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(
            button_frame, 
            text="关闭", 
            command=about_window.destroy,
            width=10
        ).pack(side=tk.RIGHT)

    def load_config_file_dialog(self):
        """打开文件对话框选择配置文件"""
        from tkinter import filedialog
        
        # 打开文件对话框
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("YAML 文件", "*.yaml"), ("所有文件", "*.*")],
            initialdir=os.path.dirname(self.config_path),
            parent=self.root
        )
        
        if file_path:
            # 保存当前配置文件路径
            old_config_path = self.config_path
            
            try:
                # 更新配置文件路径
                self.config_path = file_path
                
                # 加载新的配置文件
                self.load_config()
                
                # 更新UI
                self.populate_menu()
                
                # 清空内容区
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
                
                # 更新文件路径显示
                self.file_path_var.set(f"当前配置: {self.config_path}")
                
                messagebox.showinfo("成功", f"已加载配置文件: {os.path.basename(file_path)}", parent=self.root)
            except Exception as e:
                # 加载失败，恢复原配置文件路径
                self.config_path = old_config_path
                messagebox.showerror("错误", f"加载配置文件失败: {str(e)}", parent=self.root)

    def extract_module_descriptions(self):
        """从配置文件中提取模块描述"""
        descriptions = {}
        
        # 默认描述，以防配置文件中没有
        default_descriptions = {
            "VAD": "语音活动检测模块，用于检测用户何时开始和结束说话",
            "ASR": "语音识别模块，将语音转换为文本",
            "LLM": "大语言模型模块，处理文本并生成回复",
            "TTS": "文本转语音模块，将AI回复转换为语音",
            "Memory": "记忆模块，使AI能够记住对话历史记录",
            "Intent": "意图识别模块，用于理解用户指令并执行对应操作"
        }
        
        try:
            # 尝试从原始YAML文件中读取注释
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析selected_module部分的注释
            if "selected_module:" in content:
                section = content.split("selected_module:")[1].split("\n\n")[0]
                lines = section.split("\n")
                
                current_module = None
                for line in lines:
                    line = line.strip()
                    if line.startswith("#"):
                        # 这是一个注释行
                        comment = line[1:].strip()
                        if current_module and current_module in ["VAD", "ASR", "LLM", "TTS", "Memory", "Intent"]:
                            if current_module in descriptions:
                                descriptions[current_module] += " " + comment
                            else:
                                descriptions[current_module] = comment
                    elif ":" in line and not line.startswith("#"):
                        # 这是一个模块定义行
                        parts = line.split(":", 1)
                        module = parts[0].strip()
                        if module in ["VAD", "ASR", "LLM", "TTS", "Memory", "Intent"]:
                            current_module = module
        except Exception as e:
            print(f"提取模块描述时出错: {str(e)}")
        
        # 使用默认描述填充缺失的描述
        for module, desc in default_descriptions.items():
            if module not in descriptions:
                descriptions[module] = desc
        
        return descriptions

    def apply_changes(self):
        """应用所有变更 - 处理嵌套变更"""
        try:
            # 应用变更
            for key, value in self.changes.items():
                if "." not in key:
                    # 简单变更
                    self.config[key] = value
                else:
                    # 嵌套变更
                    parts = key.split(".")
                    current = self.config
                    
                    # 导航到嵌套位置
                    for i in range(len(parts) - 1):
                        part = parts[i]
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    
                    # 设置值
                    current[parts[-1]] = value
            
            # 清空变更记录
            self.changes = {}
            
            messagebox.showinfo("成功", "所有更改已应用", parent=self.root)
            
            # 刷新当前编辑界面
            selected = self.menu_tree.selection()
            if selected:
                item = self.menu_tree.item(selected[0])
                key = item['values'][0]
                self.create_editor(key, self.config[key])
            
        except Exception as e:
            messagebox.showerror("错误", f"应用更改失败: {str(e)}", parent=self.root)
            import traceback
            traceback.print_exc()

    def track_change(self, key, value, value_type=None):
        """跟踪配置变更 - 不需要启用应用按钮"""
        if value_type:
            try:
                value = self.convert_value(value, value_type)
            except:
                pass
        
        # 记录变更
        self.changes[key] = value

    def track_nested_change(self, parent_key, key, sub_key, value, value_type=None):
        """跟踪嵌套配置变更 - 简化处理"""
        if value_type:
            try:
                value = self.convert_value(value, value_type)
            except:
                pass
        
        # 创建嵌套路径
        path = f"{parent_key}.{key}"
        if sub_key:
            path += f".{sub_key}"
        
        # 记录变更
        self.changes[path] = value
        
        print(f"跟踪变更: {path} = {value}")  # 调试信息

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 根据不同平台处理滚轮事件
        if event.num == 4 or event.num == 5:
            # Linux
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            else:
                self.canvas.yview_scroll(1, "units")
        else:
            # Windows / macOS
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def check_for_updates_silent(self):
        """静默检查更新，如果有新版本则显示通知"""
        try:
            latest_version = self.get_latest_version()
            if latest_version and self.is_newer_version(latest_version):
                # 在主线程中显示更新通知
                self.root.after(1000, lambda: self.show_update_notification(latest_version))
        except Exception as e:
            print(f"检查更新失败: {str(e)}")

    def check_for_updates(self):
        """检查更新并显示结果"""
        try:
            latest_version = self.get_latest_version()
            if latest_version:
                if self.is_newer_version(latest_version):
                    if messagebox.askyesno("发现新版本", 
                                          f"发现新版本 v{latest_version}，当前版本为 v{self.VERSION}。\n\n是否前往下载页面?", 
                                          parent=self.root):
                        webbrowser.open(self.DOWNLOAD_URL)
                else:
                    messagebox.showinfo("检查更新", f"当前已是最新版本 v{self.VERSION}。", parent=self.root)
            else:
                messagebox.showwarning("检查更新", "无法获取最新版本信息，请稍后再试。", parent=self.root)
        except Exception as e:
            messagebox.showerror("检查更新失败", f"检查更新失败: {str(e)}", parent=self.root)

    def get_latest_version(self):
        """从远程服务器获取最新版本号"""
        try:
            with urllib.request.urlopen(self.VERSION_CHECK_URL, timeout=5) as response:
                data = json.loads(response.read().decode())
                # 假设版本号格式为 "v0.1.3"，去掉前缀 "v"
                version = data.get("tag_name", "").lstrip("v")
                return version
        except Exception as e:
            print(f"获取最新版本失败: {str(e)}")
            return None

    def is_newer_version(self, latest_version):
        """比较版本号，检查是否有新版本"""
        try:
            current_parts = [int(x) for x in self.VERSION.split(".")]
            latest_parts = [int(x) for x in latest_version.split(".")]
            
            # 比较版本号
            for i in range(max(len(current_parts), len(latest_parts))):
                current = current_parts[i] if i < len(current_parts) else 0
                latest = latest_parts[i] if i < len(latest_parts) else 0
                
                if latest > current:
                    return True
                elif latest < current:
                    return False
            
            # 版本号完全相同
            return False
        except Exception as e:
            print(f"版本比较失败: {str(e)}")
            return False

    def show_update_notification(self, latest_version):
        """显示更新通知"""
        if messagebox.askyesno("发现新版本", 
                              f"发现新版本 v{latest_version}，当前版本为 v{self.VERSION}。\n\n是否前往下载页面?", 
                              parent=self.root):
            webbrowser.open(self.DOWNLOAD_URL)

    def create_list_editor(self, parent, key, value):
        """创建列表编辑器"""
        frame = ttk.LabelFrame(parent, text=f"编辑列表 {key}")
        frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
        
        # 创建列表框
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 列表显示
        listbox = tk.Listbox(list_frame, height=10)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        
        # 填充列表
        for item in value:
            listbox.insert(tk.END, str(item))
        
        # 编辑按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 添加按钮 - 使用变更跟踪
        def add_item():
            dialog = tk.Toplevel(self.root)
            dialog.title("添加项")
            dialog.geometry("300x100")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="输入新项:").pack(pady=(10, 5))
            
            var = tk.StringVar()
            entry = ttk.Entry(dialog, textvariable=var, width=40)
            entry.pack(pady=5)
            
            def add():
                value = var.get()
                if value:
                    # 获取当前列表的副本
                    current_list = self.config[key].copy()
                    current_list.append(value)
                    
                    # 跟踪变更
                    self.track_change(key, current_list)
                    
                    # 更新UI
                    listbox.insert(tk.END, value)
                    dialog.destroy()
            
        ttk.Button(btn_frame, text="添加", command=add_item).pack(side=tk.LEFT, padx=5)
        
        # 编辑按钮 - 使用变更跟踪
        def edit_item():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一项", parent=self.root)
                return
            
            index = selected[0]
            old_value = self.config[key][index]
            
            dialog = tk.Toplevel(self.root)
            dialog.title("编辑项")
            dialog.geometry("300x100")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="编辑项:").pack(pady=(10, 5))
            
            var = tk.StringVar(value=str(old_value))
            entry = ttk.Entry(dialog, textvariable=var, width=40)
            entry.pack(pady=5)
            
            def update():
                value = var.get()
                if value:
                    # 获取当前列表的副本
                    current_list = self.config[key].copy()
                    current_list[index] = value
                    
                    # 跟踪变更
                    self.track_change(key, current_list)
                    
                    # 更新UI
                    listbox.delete(index)
                    listbox.insert(index, value)
                    dialog.destroy()
            
        ttk.Button(btn_frame, text="编辑", command=edit_item).pack(side=tk.LEFT, padx=5)
        
        # 删除按钮 - 使用变更跟踪
        def delete_item():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一项", parent=self.root)
                return
            
            index = selected[0]
            if messagebox.askyesno("确认", "确定要删除所选项吗?", parent=self.root):
                # 获取当前列表的副本
                current_list = self.config[key].copy()
                del current_list[index]
                
                # 跟踪变更
                self.track_change(key, current_list)
                
                # 更新UI
                listbox.delete(index)
        
        ttk.Button(btn_frame, text="删除", command=delete_item).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
