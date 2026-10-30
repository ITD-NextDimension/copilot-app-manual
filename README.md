# Copilot App 实跑手册 · Field Manual

用 GitHub Copilot App（GPT-6 Luna）实跑 [hol_ghc_app](https://github.com/kinfey/hol_ghc_app) 四个 Lab 的操作手册：每一步的提示词、App 截图、作品截图和独立验收结果。

| 语言 | 在线阅读 |
|---|---|
| 简体中文 | https://itd-nextdimension.github.io/copilot-app-manual/ |
| 繁體中文 | https://itd-nextdimension.github.io/copilot-app-manual/zh-TW/ |
| English | https://itd-nextdimension.github.io/copilot-app-manual/en/ |

截图中的个人账户信息与系统通知已做马赛克处理。

## 重新生成

三个页面由 `source/build.py` 生成：简体正文来自 `source/zh-CN.artifact.html`，繁体由 OpenCC（`opencc-js`，沿用上游课程的台湾术语表）转换，英文正文是 `source/body-en.html` 的人工翻译。

```bash
cd source
npm i --no-save opencc-js@1.0.5
python3 build.py
```

ITD · Next Dimension
