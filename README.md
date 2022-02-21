<h1 style="text-align: center"><span style="color: #00a2e8">G</span>enshin <span style="color: #00a2e8">W</span>ish <span style="color: #00a2e8">K</span>it</h1>


原神祈愿卡池开发套件。

## 特性／Features

- [x] 获取祈愿历史记录，而无需验证或密码（仅需手动登陆原神PC客户端）。
- [x] 在数据处理上兼容原始格式、基本格式、[UIGF格式](https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat)，简单重写映射器即可支持更多自定义格式。
- [x] 导入缺失`id`的祈愿历史记录时会自动补全，支持拟合id及自定义高编码空间的id。
- [ ] 支持按卡池和按玩家两种方式处理及合并祈愿历史记录。
- [ ] 支持导出JSON文件以及多种格式的Excel文件。

## 开源协议／License

- 本项目：BSD 3-Clause
- [Django](https://github.com/django/django/tree/stable/3.2.x)：BSD 3-Clause
  - [`django.db.models.enums.ChoicesMeta`](https://github.com/django/django/blob/stable/3.2.x/django/db/models/enums.py) -> `gwk.typing.ChoicesMeta`
  - [`django.db.models.enums.Choices`](https://github.com/django/django/blob/stable/3.2.x/django/db/models/enums.py) -> `gwk.typing.Choices`


## 参考／References

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
            },
            ...
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
    "uigf_gacha_type": "000",
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

