# GitHub 开源发布说明

仓库内容已经按公开项目整理。首次发布前只需完成所有者相关设置。

## 1. 最后检查

1. 在 `pyproject.toml` 中把 `OWNER` 替换为 GitHub 用户名或组织名。
2. 在 GitHub 创建名为 `cumcm-modeler-starter` 的空公开仓库，不要自动生成 README。
3. 如有项目维护邮箱，可在 Code of Conduct 和 Security Policy 中补充；没有也可继续使用 Security Advisories。
4. 运行本地检查：

   ```powershell
   .\scripts\check.ps1
   ```

## 2. 初始化并推送

```bash
git init -b main
git add .
git commit -m "feat: publish initial CUMCM modeler starter"
git remote add origin https://github.com/OWNER/cumcm-modeler-starter.git
git push -u origin main
```

如果安装了 GitHub CLI，也可以在仓库目录运行：

```bash
gh repo create cumcm-modeler-starter --public --source . --remote origin --push
```

执行前务必确认 GitHub 账号、组织和公开范围。

## 3. GitHub 设置

- Settings → General → 勾选 Issues；建议启用 Discussions。
- Settings → Pages → Source 选择 **GitHub Actions**。
- Settings → Security → 启用 Dependabot alerts 和 Private vulnerability reporting。
- Settings → Branches → 为 `main` 添加保护规则，要求 CI 通过后才能合并。
- About → Description：`CUMCM 算法导航、验证清单、训练路线与 Python 基线工具包`。
- Topics：`cumcm`、`mathematical-modeling`、`optimization`、`forecasting`、`python`、`education`。

## 4. 首个 Release

1. 确认 `CHANGELOG.md` 的 `0.1.0` 内容准确。
2. 创建标签：`git tag -a v0.1.0 -m "v0.1.0"`。
3. 推送标签：`git push origin v0.1.0`。
4. 在 GitHub Releases 中用 Changelog 内容创建 Release。
5. 使用 `docs/release-notes-v0.1.0.md` 作为首版发布说明，并上传源码压缩包和 wheel（若提供）。
6. 检查 Pages、CI、Issue 模板和下载链接。

## 5. 以后更新资料

- 规则更新必须给出官方链接和访问日期。
- 算法卡更新必须通过本地测试和仓库审计。
- 第三方内容只保存链接和元数据，不提交网页快照、课程视频或付费资料。
- 每次发布更新版本号、Changelog 和 CITATION 文件。
