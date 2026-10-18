# 写文章与发布（在线流程）

这套站点的目标：**任何设备、任何地点，打开浏览器就能写，写完即发布**，不需要本地 git、不需要 VS Code。

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

> 写作计划（那五篇占位）在 **Writing plan** 里改，对应 `blog/plan.json`。

## 二、发布是怎么生效的

```
你在 Pages CMS 保存
        ↓  直接 commit 到 main
GitHub Actions: blog-index.yml
        ↓  运行 scripts/build_index.py
blog/index.json 重新生成（已发布列表 + 计划进度）
        ↓
GitHub Pages 部署（1–2 分钟）
```

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

## 四、可选的加分项

- **发布前自动排版**：在 VS Code 里对文章运行 `/blog-formatting`，规则定义在 `.github/skills/blog-formatting/SKILL.md`（标题层级、空行、代码块、frontmatter 规范化）。纯在线写作时这一步可跳过。
- **让 Pages 立刻重新部署**：默认工作流用 `GITHUB_TOKEN` 推送索引，GitHub 不会因此再次触发 Pages 构建。若发现线上索引没更新，在仓库
  **Settings → Secrets and variables → Actions** 添加 `BLOG_INDEX_TOKEN`（fine-grained PAT，权限 `contents: write`），工作流会自动改用它，之后每次都会正常触发部署。

## 五、排查

| 现象 | 处理 |
|---|---|
| 文章保存了但列表没出现 | 检查 `date` 是否填了、正文是否为空、`draft` 是否为 true |
| 列表出现但点进去 404 | `blog/post.html?post=<slug>` 的 slug 必须与文件名完全一致 |
| 线上列表没更新 | 等 1–2 分钟；仍未更新则看 Actions 里 `Rebuild blog index` 是否失败 |
| 本地打开 `blog.html` 提示加载失败 | 用 `python3 -m http.server` 起本地服务，不要双击文件 |
