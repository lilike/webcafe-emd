# web.cafe 新词 EMD 雷达

积累式静态站：按**域名去重**，记录注册日、关键词、站点类型与热度。

- 在线页面：https://lilike.github.io/webcafe-emd/
- 数据：`data/sites.json`（域名主键）、`data/meta.json`
- 每日由「哥飞新词EMD雷达」例行合并 `hits_latest.json` 后推送

## 本地更新

```bash
python3 scripts/merge_sites.py
bash scripts/publish.sh
```

只读展示，不注册域名、不提交表单。
