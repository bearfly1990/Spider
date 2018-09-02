# Spider

自己爬虫的练手项目，还在学习中。

## Douban

目前爬的是 douban 前 250 名的电影名字和电影海报图片。

构造函数中的参数代表了要爬的页面数，默认 25 条一页。

```python
if __name__ == '__main__':
    spider_douban = SpiderDouban250(2)
    spider_douban.start_spider()
```

## 51job

目前解析的是`51job`的字符串搜索结果，把公司名包含`str_search`的条目都列出来，如果想搜索别的结果，就把`str_search`修改一下便可以了。

```python
if __name__ == '__main__':
    spider_51job = Spider51Job()
    spider_51job.str_search = '恒生电子'
    spider_51job.start_spider()
```
