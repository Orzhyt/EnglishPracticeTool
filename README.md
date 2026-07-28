# English Practice Tool (EPT)

本地英语练习工具，涵盖**听力训练**和**口语练习**两大模块。

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| UI 框架 | PySide6 (Qt6) | 原生桌面 UI，专业美观 |
| 音频播放 | Qt Multimedia | 音频播放/录制，跨平台 |
| TTS 引擎 | CosyVoice3 | 阿里开源语音合成，支持零样本克隆 |
| 打包工具 | PyInstaller | 一键打包为 Windows exe |
| 语言 | Python 3.12+ | - |

## 项目结构

```
EnglishPracticeTool/
├── src/                        # 源代码
│   ├── main.py                 # 应用入口
│   ├── app.py                  # 主窗口（侧边栏 + 页面栈）
│   ├── styles.py               # 全局 QSS 样式
│   ├── pages/                  # 功能页面
│   │   ├── listening_page.py   # 听力练习页
│   │   └── speaking_page.py    # 口语练习页
│   ├── components/             # 可复用组件
│   │   └── nav_sidebar.py      # 左侧导航栏
│   └── utils/                  # 工具模块
│       ├── audio_utils.py      # 音频播放器封装
│       ├── md_parser.py        # 听力 MD 文件解析
│       ├── tts_generator.py    # TTS 音频生成
│       └── tts_worker.py       # TTS 后台线程
├── data/                       # 练习数据
│   └── listening/              # 听力 MD 文件
├── assets/                     # 静态资源
│   ├── app.ico                 # 应用图标
│   └── voices/                 # TTS 参考音频
├── models/                     # 模型权重（gitignore）
│   └── CosyVoice3-0.5B/       # CosyVoice3 模型文件
├── scripts/                    # 构建脚本
│   ├── app.spec                # PyInstaller 打包配置
│   └── build.bat               # 一键打包命令
├── third_party/                # 第三方仓库（gitignore）
│   └── CosyVoice/             # CosyVoice 源码
├── dist/                       # 打包产物（gitignore）
├── output/                     # 生成的音频（gitignore）
├── requirements.txt            # Python 依赖
├── pyproject.toml              # 项目元数据
└── README.md
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-repo/EnglishPracticeTool.git
cd EnglishPracticeTool
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> **注意**：默认会安装 CPU 版 PyTorch。如需 GPU 加速，请先单独安装 CUDA 版，并修改为适配的版本（如121）：

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 3. 配置 TTS（CosyVoice3）

听力练习的音频生成功能依赖 [CosyVoice3](https://github.com/FunAudioLLM/CosyVoice)，需要两步：

#### 3a. 克隆 CosyVoice 源码

```bash
git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git third_party/CosyVoice
```

#### 3b. 下载模型权重

使用 ModelScope 下载到 `models/CosyVoice3-0.5B/`：

```bash
modelscope download --model FunAudioLLM/Fun-CosyVoice3-0.5B-2512 --local_dir models/CosyVoice3-0.5B
```

### 3. 运行开发

```bash
cd src
python main.py
```

### 4. 打包 exe

```bash
scripts\build.bat
```

产物位于 `dist\EnglishPracticeTool\EnglishPracticeTool.exe`

## 架构说明

### 页面切换机制

主窗口 `MainWindow` 使用 `QStackedWidget` 管理多个页面，左侧 `NavSidebar` 发出 `page_changed(int)` 信号切换页面索引：

```
NavSidebar --[page_changed]--> MainWindow._switch_page() --> QStackedWidget.setCurrentIndex()
```

### 样式系统

全局 QSS 样式定义在 `src/styles.py`，通过 `setStyleSheet()` 注入主窗口，所有子组件自动继承。使用 `objectName` 选择器实现组件级样式隔离。支持浅色/深色主题切换。

### 音频工具

`AudioPlayer` 封装了 `QMediaPlayer` + `QAudioOutput`，提供统一的播放/停止/音量接口，供听力页和口语页调用。

### TTS 音频生成

听力页支持从 Markdown 文件生成音频：
1. `md_parser.py` 解析 MD 文件中的对话和题目
2. `tts_generator.py` 调用 CosyVoice3 合成语音，在对话和题目间插入静音间隔
3. `tts_worker.py` 在后台线程中执行生成，避免阻塞 UI

## 后续规划

- [ ] 听力页：听写输入、进度追踪
- [ ] 口语页：录音采集、语音识别（Whisper）、发音评分
- [ ] 数据持久化：SQLite 存储练习记录
- [ ] 设置页：音频源配置、难度选择
