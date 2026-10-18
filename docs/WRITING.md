# 写文章与发布（在线流程）

这套站点的目标：**任何设备、任何地点，打开浏览器就能写，写完即发布**，不需要本地 git、不需要 VS Code。

## TL;DR — 换一台新电脑的完整流程

1. 浏览器打开 <https://app.pagescms.org/>，GitHub 登录，选 `ColinCheungg.github.io` 仓库
2. 左侧 **Blog posts** → 点要写的文章的 **Edit**
3. 写正文 → **Date 填日期**（必填）→ 点 **Save**
4. 等 1–2 分钟，打开 <https://colincheungg.github.io/blog.html> 确认

没有第 5 步。不用 clone 仓库、不用装任何软件、不用敲 git 命令。

## 一、写作入口：Pages CMS

1. 手机或电脑浏览器打开 <https://app.pagescms.org/>
2. 用 GitHub 账号登录（`ColinCheungg`）
3. 首次使用时授权 Pages CMS 的 GitHub App 访问本仓库
4. 选择仓库 `ColinCheungg/ColinCheungg.github.io`
5. 左侧选 **Blog posts** → 点 **New** 新建，或点已有文章编辑

表单已经按 `blog/posts/*.md` 的 frontmatter 配好：

| 字段 | 说明 |
|---|---|
| Title | 文章标题 |
| Date | 发布/写作日期（**必填**，没有日期不会出现在列表里） |
| Summary | 可选，显示在标题下方的一句话摘要 |
| Draft | 勾选后永不显示在列表里 |
| Content | 正文，富文本编辑器，底层存 Markdown |

改完点 **Save**，Pages CMS 会直接向仓库 `main` 分支提交一次 commit。

> **新建文章（Add an entry）**：`blog/posts/` 下会生成一个 `.md` 文件。
> 文件名（slug）决定文章链接：建议用英文小写+连字符（如 `my-first-post`），
> URL 更短更好读；用中文文件名也能正常工作，只是链接会变成百分号编码。
> 唯一限制是不能含 `/` 或 `\`。

> 写作计划（那五篇占位）在 **Writing plan** 里改，对应 `blog/plan.json`。

## 二、发布是怎么生效的

```
你在 Pages CMS 保存
        ↓  直接 commit 到 main
GitHub Actions: deploy-pages.yml
        ↓  python3 scripts/build_index.py  →  blog/index.json
        ↓  rsync 组装 _site/（排除 .git / .github / scripts / docs）
        ↓  actions/deploy-pages
GitHub Pages（1–2 分钟）
```

索引是在**部署流水线内部**重新生成的，不会产生第二个 commit，因此不存在
「提交了但没重新部署」的问题。

`blog/index.json` 仍保留在仓库里作为**兜底**：万一 Actions 不可用，线上页面
依然有索引可读。它可能比最新的 `.md` 略旧，这是正常的——每次部署都会在工作区
重新生成并覆盖它，最终发布出去的永远是最新版本。

关键规则——一篇文章 **同时满足** 下面三点才会出现在博客列表里：

1. `date` 不为空
2. 正文有内容（去掉 HTML 注释后非空）
3. `draft` 不是 `true`

所以 `blog/posts/` 里放空骨架文件是安全的，它不会暴露出去。

**计划进度会自动更新**：当某篇文章的 slug 与 `blog/plan.json` 中的 slug 一致且已发布时，那条占位会自动消失，进度条自动 +20%。

## 三、本地预览

`blog.html` 用 `fetch` 读取 `blog/index.json`，直接用 `file://` 打开会被浏览器拦截，需要用 HTTP：

```bash
cd ColinCheungg.github.io
python3 -m http.server 8765
# 打开 http://127.0.0.1:8765/blog.html
```

改了文章后要重新生成索引：

```bash
python3 scripts/build_index.py
```

## 四、一次性设置：Pages 必须由 Actions 部署

整条链路依赖仓库设置正确。**只需设置一次**：

1. 打开 `Settings → Pages`
2. **Build and deployment → Source** 选择 **GitHub Actions**
   （不要选 "Deploy from a branch"）

设置后，`deploy-pages.yml` 每次 Push 到 `main` 都会自动构建并发布。
若 Source 仍是 "Deploy from a branch"，工作流会在 `Upload artifact` 步骤失败。

## 五、可选的加分项

- **发布前自动排版**：在 VS Code 里对文章运行 `/blog-formatting`，规则定义在
  `.github/skills/blog-formatting/SKILL.md`（标题层级、空行、代码块、frontmatter 规范化）。
  纯在线写作时这一步可跳过。

## 六、排查

| 现象 | 处理 |
|---|---|
| 文章保存了但列表没出现 | 检查 `date` 是否填了、正文是否为空、`draft` 是否为 true |
| 列表出现但点进去 404 | `blog/post.html?post=<slug>` 的 slug 必须与文件名完全一致 |
| 本地预览的列表比线上旧 | 手动to GitHub Pages` 是否失败 |
| Actions 报 `Upload artifact` 失败 | Pages Source 还不是 "GitHub Actions"，见第四节 |
| 本地打开 `blog.html` 提示加载失败 | 用 `python3 -m http.server` 起本地服务，不要双击文件 |
| 新克隆仓库后本地预览空白 | `blog/index.json` 是构建产物、不提交，先跑一次 `python3 scripts/build_index.py` |
