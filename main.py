import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk
import re
from tkinter import messagebox
import threading
import time

class VideoMergerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("无损合并MP4视频")
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小
        window_width = 600
        window_height = 500
        
        # 计算窗口位置使其居中
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.file_paths = []
        self.setup_ui()
        
    def on_select(self, event):
        """处理选择事件"""
        # 当选择树形视图中的项目时触发
        selected_item = self.file_tree.selection()
        if selected_item:
            item = selected_item[0]
            values = self.file_tree.item(item, 'values')
            if values:
                # 可以在这里添加选择文件后的操作
                pass
    def on_click(self, event):
        """记录拖动开始的位置和选中的项目"""
        item = self.file_tree.identify_row(event.y)
        if item:
            # 确保只能拖动文件，不能拖动文件夹
            values = self.file_tree.item(item, 'values')
            if values and values[0].lower().endswith('.mp4'):
                self.drag_data['item'] = item
                self.drag_data['x'] = event.x
                self.drag_data['y'] = event.y
    def on_drag(self, event):
        """处理拖动过程"""
        if self.drag_data['item']:
            # 计算移动距离
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            
            # 获取当前鼠标位置对应的项目
            target_item = self.file_tree.identify_row(event.y)
            
            if target_item:
                # 高亮显示目标位置
                self.file_tree.selection_set(target_item)
    def on_drop(self, event):
        """处理拖放完成事件"""
        if not self.drag_data['item']:
            return
            
        # 获取目标位置的项目
        target_item = self.file_tree.identify_row(event.y)
        if not target_item or target_item == self.drag_data['item']:
            return
            
        # 获取源文件和目标位置的信息
        source_item = self.drag_data['item']
        source_values = self.file_tree.item(source_item, 'values')
        target_values = self.file_tree.item(target_item, 'values')
        
        # 确保目标也是一个文件而不是文件夹
        if not target_values or not target_values[0].lower().endswith('.mp4'):
            return
            
        # 更新文件路径列表中的顺序
        source_path = source_values[0]
        target_path = target_values[0]
        source_index = self.file_paths.index(source_path)
        target_index = self.file_paths.index(target_path)
        
        # 移动文件路径
        self.file_paths.pop(source_index)
        if target_index > source_index:
            target_index -= 1
        self.file_paths.insert(target_index, source_path)
        
        # 重新显示文件列表
        self.update_file_list()
        
        # 清除拖放数据
        self.drag_data['item'] = None
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 创建进度条
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', style='Horizontal.TProgressbar')
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        self.progress_bar['value'] = 0
        
        # 使用说明框架
        help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="5")
        help_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(5, 2))
        
        # 使用说明文本
        help_text = "使用步骤：\n"
        help_text += "1. 点击'导入文件夹'按钮，选择包含MP4视频的文件夹\n"
        help_text += "2. 在文件列表中，可以通过拖拽视频文件来调整合并顺序\n"
        help_text += "3. 点击'导出文件夹'按钮，选择合并后视频的保存位置\n"
        help_text += "4. 点击'开始合并'按钮，开始无损合并视频\n"
        help_text += "注意：合并后的视频将保持原有的文件夹结构，每个文件夹中的视频将被合并为一个文件"
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=780)
        help_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=2)
        
        # 文件列表框架
        list_frame = ttk.LabelFrame(main_frame, text="已选择的文件", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=(2, 5))
        
        # 创建树形视图
        self.file_tree = ttk.Treeview(list_frame, selectmode='browse', style='Custom.Treeview')
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置树形视图列
        self.file_tree['columns'] = ('fullpath')
        self.file_tree.column('#0', width=300)
        self.file_tree.column('fullpath', width=0, stretch=False)
        self.file_tree.heading('#0', text='文件结构')
        self.file_tree.heading('fullpath', text='完整路径')
        
        # 启用拖放功能
        self.file_tree.configure(selectmode='browse')
        self.file_tree.bind('<<TreeviewSelect>>', self.on_select)
        self.file_tree.bind('<Button-1>', self.on_click)
        self.file_tree.bind('<B1-Motion>', self.on_drag)
        self.file_tree.bind('<ButtonRelease-1>', self.on_drop)
        self.drag_data = {'item': None, 'x': 0, 'y': 0}
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        
        # 导入文件夹按钮
        self.import_button = ttk.Button(button_frame, text="导入文件夹", command=self.import_folder, style='Accent.TButton')
        self.import_button.grid(row=0, column=0, padx=5)
        
        # 导出文件夹按钮
        self.export_button = ttk.Button(button_frame, text="导出文件夹", command=self.export_folder)
        self.export_button.grid(row=0, column=1, padx=5)
        
        # 开始合并按钮
        self.merge_button = ttk.Button(button_frame, text="开始合并", command=self.merge_videos, style='Accent.TButton')
        self.merge_button.grid(row=0, column=2, padx=5)
        
        # 进度文本
        self.progress_var = tk.StringVar(value="准备就绪")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        
        # 版权信息
        copyright_text = "© 2025 一模型Ai (https://jmlovestore.com) - 不会开发软件吗 🙂 Ai会哦"
        copyright_label = ttk.Label(main_frame, text=copyright_text, font=("Microsoft YaHei UI", 8), foreground="#666666")
        copyright_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # 文件列表区域可扩展
        button_frame.columnconfigure((0, 1, 2), weight=1)
        
        # 设置自定义样式
        style = ttk.Style()
        style.configure('Custom.Treeview', rowheight=25)
        style.configure('Accent.TButton', font=('Microsoft YaHei UI', 9))
        style.configure('TLabel', font=('Microsoft YaHei UI', 9))
        style.configure('TLabelframe.Label', font=('Microsoft YaHei UI', 9, 'bold'))
    def natural_sort_key(self, s):
        """自然排序的关键函数，将字符串中的数字部分提取并按数值排序。"""
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
    
    def import_folder(self):
        folder_path = filedialog.askdirectory(title="选择需要导入的文件夹")
        if folder_path:
            self.input_folder = folder_path
            self.file_paths = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.mp4'):
                        self.file_paths.append(os.path.join(root, file))
            # 初始导入时按自然排序排列文件
            self.file_paths = sorted(self.file_paths, key=lambda x: self.natural_sort_key(os.path.basename(x)))
            self.update_file_list()
            
    def export_folder(self):
        if not hasattr(self, 'input_folder'):
            messagebox.showwarning("警告", "请先选择输入文件夹！")
            return
        folder_path = filedialog.askdirectory(title="选择导出文件夹")
        if folder_path:
            self.output_folder = folder_path
    
    def clear_files(self):
        self.file_paths = []
        self.file_tree.delete(*self.file_tree.get_children())
    
    def update_file_list(self):
        self.file_tree.delete(*self.file_tree.get_children())
        
        # 创建文件夹树形结构
        folders = {}
        main_folder_videos = []
        
        # 首先收集主文件夹中的视频和子文件夹中的视频
        for file_path in self.file_paths:
            relative_path = os.path.relpath(file_path, self.input_folder)
            parts = relative_path.split(os.sep)
            
            # 如果是主文件夹中的视频
            if len(parts) == 1:
                main_folder_videos.append(file_path)
                continue
            
            # 构建文件夹路径
            current_path = self.input_folder
            parent = ''
            
            # 添加文件夹节点
            for i, part in enumerate(parts[:-1]):
                current_path = os.path.join(current_path, part)
                folder_id = current_path
                
                if folder_id not in folders:
                    folders[folder_id] = True
                    # 添加完整路径到文件夹显示文本中
                    folder_display = f"{part} ({current_path})"
                    self.file_tree.insert(parent, 'end', folder_id, text=folder_display, values=(current_path,), open=True)
                parent = folder_id
            
            # 添加子文件夹中的文件节点
            file_name = parts[-1]
            self.file_tree.insert(parent, 'end', text=file_name, values=(file_path,))
        
        # 添加主文件夹中的视频到一个独立的虚拟目录下
        if main_folder_videos:
            # 创建一个虚拟的主文件夹节点
            main_folder_node_id = "main_folder_videos"
            main_folder_display = f"主文件夹视频 ({self.input_folder})"
            self.file_tree.insert('', 'end', main_folder_node_id, text=main_folder_display, values=(self.input_folder,), open=True)
            
            # 将主文件夹中的视频添加到这个节点下
            for video_path in main_folder_videos:
                file_name = os.path.basename(video_path)
                self.file_tree.insert(main_folder_node_id, 'end', text=file_name, values=(video_path,))
    def merge_videos(self):
        if not self.file_paths or not hasattr(self, 'output_folder'):
            messagebox.showwarning("警告", "请先选择输入和输出文件夹！")
            return
        
        # 禁用按钮，避免重复操作
        self.import_button.configure(state='disabled')
        self.export_button.configure(state='disabled')
        self.merge_button.configure(state='disabled')
        
        # 重置进度条
        self.progress_bar['value'] = 0
        
        def merge_thread():
            try:
                # 按文件夹分组视频
                folder_videos = {}
                for file_path in self.file_paths:
                    folder = os.path.dirname(file_path)
                    if folder not in folder_videos:
                        folder_videos[folder] = []
                    folder_videos[folder].append(file_path)
                
                total_folders = len(folder_videos)
                processed_folders = 0
                
                for folder, videos in folder_videos.items():
                    # 更新进度条
                    progress = int((processed_folders / total_folders) * 100)
                    self.progress_bar['value'] = progress
                    
                    # 创建对应的输出文件夹
                    relative_path = os.path.relpath(folder, self.input_folder)
                    output_folder = os.path.join(self.output_folder, relative_path)
                    os.makedirs(output_folder, exist_ok=True)
                    
                    # 定义输出文件名
                    output_file = os.path.join(output_folder, "merged.mp4")
                    txt_filename = os.path.join(output_folder, "文本.txt")
                    order_filename = os.path.join(output_folder, "合并顺序.txt")
                    
                    try:
                        # 创建文本文件
                        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                            for video_path in videos:
                                video_path = video_path.replace("\\", "/")
                                txt_file.write(f"file '{video_path}'\n")
                        
                        # 构建 ffmpeg 命令
                        ffmpeg_cmd = [
                            "ffmpeg",
                            "-f", "concat",
                            "-safe", "0",
                            "-i", txt_filename,
                            "-c", "copy",
                            output_file
                        ]
                        
                        self.progress_var.set(f"正在处理文件夹 {relative_path} ({processed_folders + 1}/{total_folders})")
                        
                        # 执行合并
                        subprocess.run(ffmpeg_cmd, check=True)
                        
                        # 生成合并顺序文件
                        with open(order_filename, 'w', encoding='utf-8') as order_file:
                            order_file.write("合并顺序如下：\n")
                            for idx, video_path in enumerate(videos, start=1):
                                order_file.write(f"{idx}. {os.path.basename(video_path)}\n")
                        
                        processed_folders += 1
                        
                    except subprocess.CalledProcessError as e:
                        self.progress_var.set(f"处理文件夹 {relative_path} 失败！")
                        messagebox.showerror("错误", f"合并失败！\n文件夹：{relative_path}\n错误信息：{e}")
                    finally:
                        # 清理临时文件
                        if os.path.exists(txt_filename):
                            os.remove(txt_filename)
                
                self.progress_var.set(f"处理完成！成功处理 {processed_folders}/{total_folders} 个文件夹")
                messagebox.showinfo("完成", f"视频合并完成！\n成功处理 {processed_folders}/{total_folders} 个文件夹\n输出目录：{self.output_folder}")
            finally:
                # 恢复按钮状态
                self.root.after(0, lambda: [
                    self.import_button.configure(state='normal'),
                    self.export_button.configure(state='normal'),
                    self.merge_button.configure(state='normal')
                ])
        
        # 启动处理线程
        threading.Thread(target=merge_thread, daemon=True).start()
    def run(self):
        self.root.mainloop()

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry("400x200")
        self.root.configure(bg='#f0f0f0')
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算窗口位置使其居中
        x = (screen_width - 400) // 2
        y = (screen_height - 200) // 2
        self.root.geometry(f"400x200+{x}+{y}")
        
        # 创建主框架并添加圆角和阴影效果
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建样式
        style = ttk.Style()
        style.configure('Splash.TLabel', font=('Microsoft YaHei UI', 10), foreground='#333333')
        style.configure('SplashTitle.TLabel', font=('Microsoft YaHei UI', 18, 'bold'), foreground='#1a73e8')
        style.configure('Splash.Horizontal.TProgressbar', background='#1a73e8', troughcolor='#e0e0e0', bordercolor='#e0e0e0')
        
        # 标题
        title_label = ttk.Label(main_frame, text="无损合并MP4视频", style='SplashTitle.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 进度条
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', variable=self.progress_var,
                                          style='Splash.Horizontal.TProgressbar', length=300)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 进度文本
        self.progress_text = ttk.Label(main_frame, text="正在加载... 0%", style='Splash.TLabel')
        self.progress_text.grid(row=2, column=0, pady=(0, 15))
        
        # 版权信息
        copyright_text = "© 2025 一模型Ai (https://jmlovestore.com)"
        copyright_label = ttk.Label(main_frame, text=copyright_text, font=("Microsoft YaHei UI", 8),
                                  foreground="#666666", style='Splash.TLabel')
        copyright_label.grid(row=3, column=0, pady=(10, 0))
        
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 添加窗口阴影效果
        self.root.wm_attributes('-alpha', 0.0)
        self.root.update()
        self.root.wm_attributes('-alpha', 1.0)
    
    def update_progress(self, value, text=None):
        self.progress_var.set(value)
        if text:
            self.progress_text.config(text=text)
        else:
            self.progress_text.config(text=f"正在加载... {value}%")
        self.root.update()
    
    def destroy(self):
        self.root.destroy()

def simulate_loading():
    splash = SplashScreen()
    total_steps = 100
    
    # 模拟加载过程
    loading_steps = [
        (0, "准备启动..."),
        (15, "正在初始化界面..."),
        (35, "正在加载依赖项..."),
        (55, "正在检查系统配置..."),
        (75, "正在准备资源文件..."),
        (90, "即将完成加载..."),
        (100, "加载完成")
    ]
    
    # 平滑动画效果
    for i, (target_progress, text) in enumerate(loading_steps):
        start_progress = loading_steps[i-1][0] if i > 0 else 0
        steps = target_progress - start_progress
        
        splash.update_progress(start_progress, text)
        
        # 平滑过渡到目标进度
        for step in range(steps):
            current_progress = start_progress + step + 1
            splash.update_progress(current_progress)
            time.sleep(0.02)  # 更短的延迟使动画更流畅
    
    time.sleep(0.3)  # 显示"加载完成"消息
    splash.destroy()
    
    # 启动主程序
    app = VideoMergerGUI()
    app.run()

if __name__ == "__main__":
    simulate_loading()
