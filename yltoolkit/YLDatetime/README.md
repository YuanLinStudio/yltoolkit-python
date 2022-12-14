# 时间格式 `YLDatetime`

`YLDatetime` 基于 python 自带模块 `datetime` 和 `zoneinfo` 编写，主要为若干个便捷函数。

## 时区支持

`YLDatetime` 主要支持 3 个时区，分别是 UTC (世界标准时)，CST (中国标准时间, UTC + 08:00) 和本地时间 (由用户设置的所在地区决定)。

## 获取当前时间

使用 `YLDatetime.now(standard: TimeStandard = TimeStandard.UTC)` 来获取当前时间。默认时间格式为 UTC。若要设置为其他格式，传入 `standard` 参数即可。 `TimeStandard` 是时间标准的一个枚举，其内容即三个支持的时区对象 (`UTC`, `CST`, `LOCAL`)。

## 从字典 / JSON 载入日期

使用 `YLDatetime.load_date(*, from_json: dict)` 来初始化一个日期对象。支持的方法有以下三种：

### 1. 指定日期

传入的字典用 `exactly` 键，可调用 `datetime.date()` 方法初始化一个日期。若该键对应的值是 `"today"`，则会调用 `YLDatetime.now().date()` 来获取当前日期；若该键对应的值是一个字典，应包括 1 个键：

- `date`: 指定的日期。该键对应的值是一个字典，该字典将被解包并作为参数输入至 `datetime.date` 方法。

示例：

> 今天

``` json
{
    "exactly": "today"
}
```

> 2022 年 1 月 1 日

``` json
{
    "exactly": {
        "date": {
            "year": 2022,
            "month": 1,
            "day": 1
        }
    }
}
```

### 2. 相对一个日期（参考日期）一段时间间隔的另一个日期

传入的字典用 `relevant` 键，其对应的值为一个字典，包括 3 个键：

- `from`: 参考日期，格式与传入 `YLDatetime.load_date(*, from_json: dict)` 的参数相同。运行时将递归调用 `YLDatetime.load_date` 来获取参考日期。
  
- `method`: 将参考日期向前推（更早的时间）或向后退（更晚的时间），分别使用 `"minus"` 和 `"add"`。
  
- `timedelta`: 相对的时间间隔。该键对应的值是一个字典，该字典将被解包并作为参数输入至 `datetime.timedelta` 方法。
  解析后的 `timedelta` 对象应该是一个正的时间间隔，也就是说类似于 `days = -1` 的结果不应该被接受，而是使用 `"method": "minus"` 来获取一个比参考日期早的日期。

示例：

> 明天

``` json
{
    "relevant": {
        "from": {
            "exactly": "today"
        },
        "method": "add",
        "timedelta": {
            "days": 1
        }
    }
}
```

> 上周的明天

``` json
{
    "relevant": {
        "from": {
            "exactly": "today"
        },
        "method": "add",
        "timedelta": {
            "weeks": 1,
            "days": -1
            // 此处 `days` 可为 -1，因为 `timedelta` 方法进行解析时 `weeks` 参数也会被转换为 `days`，因此最终的 `days` 是 7 - 1 = 6，是满足规则的
        }
    }
}
```

### 3. 相对一个日期（参考日期），替换某个日期成分的另一个日期

传入的字典用 `replacing` 键，其对应的值为一个字典，包括 2 个键：

- `from`: 参考日期，格式与传入 `YLDatetime.load_date(*, from_json: dict)` 的参数相同。运行时将递归调用 `YLDatetime.load_date` 来获取参考日期。
  
- `replace`: 需要修改的日期成分。该键对应的值是一个字典，该字典将被解包并作为参数输入至 `datetime.date.replace` 方法。

示例：

> 本月 1 日

``` json
{
    "replacing": {
        "from": {
            "exactly": "today"
        },
        "replace": {
            "day": 1
        }
    }
}
```

> 今年 5 月 3 日

``` json
{
    "replacing": {
        "from": {
            "exactly": "today"
        },
        "replace": {
            "month": 5,
            "day": 3
        }
    }
}
```

传入 `YLDatetime.load_date` 的字典键仅能在上述 3 种中选择一个 (if-else 关系)。若出现多个键，将按照 `"exactly" > "relevant" > "replacing"` 的顺序选择靠前的一个。

## 日期时间的代码规则

程序内部的所有处理日期 / 时间的代码应当使用 UTC 时间，以保证时间处理不因为时区不一致 / 冬夏季时间变换 (DST) 而出现错误。

输入输出时应根据需要使用 UTC / CST 或本地时间。
