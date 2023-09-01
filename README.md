<h1 style="text-align: center">
  <span style="color: #00a2e8">G</span>enshin
  <span style="color: #00a2e8">W</span>ish
  <span style="color: #00a2e8">K</span>onverter
</h1>

原神祈愿记录转换器。

## 安装

- 使用 3.11 进行测试，但支持用 3.6 及以上版本的 Python 运行。
- 需要安装 click 来解析命令行、rich 来打印表格。

## 用法

使用 `python gwk.py --help` 获得完整说明。

## 参考

### page

`RawCollector.get_page()`方法内HTTP请求的响应。最外层包装为`GenshinResponse`类。

```JSON
{
    "retcode": 0,
    "message": "OK",
    "data": {
        "page": "0",
        "size": "20",
        "total": "0",
        "list": [
            {
                "uid": "玩家id",
                "gacha_type": "200",
                "item_id": "",
                "count": "1",
                "time": "yyyy-MM-dd HH:mm:ss",
                "name": "芭芭拉",
                "lang": "zh-cn",
                "item_type": "角色",
                "rank_type": "4",
                "id": "祈愿历史的ID，19位阿拉伯数字"
            }
        ],
        "region": "cn_gf01"
    }
}
```

### [UIGF.J](https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat#json-%E6%A0%BC%E5%BC%8F)格式

```JSON
{
    "gacha_type": "000",
    "item_id": "",
    "count": "1",
    "time": "yyyy-MM-dd HH:mm:ss",
    "name": "以理服人",
    "item_type": "武器",
    "rank_type": "3",
    "id": "1600099200004770203",
    "uigf_gacha_type": "000"
}
```

### auths

本地日志中的鉴权信息。

```JSON
{
    "authkey_ver": ["1"],
    "sign_type": ["2"],
    "auth_appid": ["webview_gacha"],
    "init_type": ["200"],
    "gacha_id": ["a0b0c0e0f00000000000000000000000000000"],
    "timestamp": ["1641300000"],
    "lang": ["zh-cn"],
    "device_type": ["pc"],
    "ext": [
        "{\"loc\":{\"x\":-333.5500075,\"y\":666.00000376,\"z\":-999.00000625},\"platform\":\"WinST\"}"
    ],
    "game_version": ["CNRELWin2.4.0_R5691054_S5715829_D5736476"],
    "plat_type": ["pc"],
    "region": ["cn_gf01"],
    "authkey": ["base64-encode string"],
    "game_biz": ["hk4e_cn"]
}
```
