# 快速安装指南

## 安装步骤

### 1. 安装依赖

```bash
pip install Pillow
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 安装插件

将整个 `Chinitsu-Ready-Hand-Training` 文件夹复制到 AstrBot 的插件目录中。

AstrBot 插件目录通常位于：
- `AstrBot/data/plugins/` 或
- `~/.astrbot/plugins/`

### 3. 重启 AstrBot

重启 AstrBot 后，插件会自动加载。

### 4. 验证安装

在任意支持的平台（QQ、Telegram 等）的群聊中发送：

```
/清一色
```

如果 BOT 回复并发送了麻将牌图片，说明插件安装成功！

## 验证脚本

在安装前，你可以运行验证脚本检查环境：

```bash
python verify_plugin.py
```

该脚本会检查：
- Pillow 是否已安装
- 麻将牌资源是否完整
- 麻将逻辑是否正常
- 图片生成是否正常
- 答案解析是否正常

## 目录结构

确保你的目录结构如下：

```
AstrBot/
└── data/
    └── plugins/
        └── Chinitsu-Ready-Hand-Training/
            ├── main.py
            ├── metadata.yaml
            ├── requirements.txt
            ├── README.md
            ├── USAGE.md
            └── Regular/
                ├── Front.png
                ├── Man1.png ~ Man9.png
                ├── Sou1.png ~ Sou9.png
                └── Pin1.png ~ Pin9.png
```

## 常见问题

### Q: 提示 "Pillow not found"

**A:** 运行 `pip install Pillow` 安装 Pillow 库。

### Q: 提示 "资源文件缺失"

**A:** 确保 `Regular` 文件夹中包含所有必需的图片文件（Front.png, Man1-9.png, Sou1-9.png, Pin1-9.png）。

### Q: 插件未加载

**A:** 
1. 检查文件夹名称是否正确
2. 检查 AstrBot 日志中是否有错误信息
3. 确认 AstrBot 版本 >= v4.5.0

### Q: 图片无法显示

**A:** 
1. 确保 Regular 文件夹中的图片完整
2. 检查图片文件权限
3. 查看 AstrBot 日志中的错误信息

## 卸载

1. 停止 AstrBot
2. 删除 `Chinitsu-Ready-Hand-Training` 文件夹
3. 重启 AstrBot

## 获取帮助

如果遇到问题，请：
1. 查看 [USAGE.md](USAGE.md) 了解详细使用方法
2. 查看 [DEVELOPMENT.md](DEVELOPMENT.md) 了解技术细节
3. 在 GitHub 上提交 Issue

---

**祝你使用愉快！🀄️**
