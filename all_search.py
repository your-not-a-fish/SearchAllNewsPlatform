from search_sohu import SoHuSearch
from search_toutiao import TouTiaoSearch
from search_weibo import WeiBoSearch
from DrissionPage import ChromiumOptions,Chromium
from filter import FilterDataDict
from storage import Storage


class SearchNews(object):

    def __init__(self, filter_options=None, storage_options=None):
        """
        初始化搜索器
        :param filter_options: 过滤选项
        :param storage_options: 存储选项
        :param sleep_time: 搜索间隔时间范围 [min, max]，默认 [1, 3]
        :param page_num: 每个平台搜索的页数，默认 5
        :param print_info: 是否打印详细信息，默认 True
        """
        # 设置默认参数
        self.sleep_time = [5, 15]
        self.page_num = 5
        self.print_info = True
        
        if filter_options:
            self.filter = filter_options
        else:
            self.filter = FilterDataDict()
        if storage_options:
            self.storage = storage_options
        else:
            self.storage = Storage()


    def search_news(self, keyword):
        """
        统一搜索接口
        :param keyword: 搜索关键词
        :param platforms: 要搜索的平台列表，如 ['weibo', 'sohu', 'toutiao']，默认为None表示搜索所有平台
        :return: 所有平台的搜索结果列表
        """
        all_results = []

        weibo = WeiBoSearch()
        weibo.page_num = self.page_num
        weibo.sleep_time = self.sleep_time
        weibo.print_info = self.print_info
        data_list1 = weibo.search_news(keyword)

        sohu = SoHuSearch()
        sohu.sleep_time = self.sleep_time
        sohu.print_info = self.print_info
        data_list2 = sohu.search_news(keyword)

        toutiao = TouTiaoSearch()
        toutiao.page_num = self.page_num
        toutiao.sleep_time = self.sleep_time
        toutiao.print_info = self.print_info
        data_list3 = toutiao.search_news(keyword)

        for data in data_list1:
            all_results.append(data)
        for data in data_list2:
            all_results.append(data)
        for data in data_list3:
            all_results.append(data)
        return all_results

    def search_and_storage(self, keyword):
        """
        搜索并保存结果
        :param keyword: 搜索关键词
        :param platforms: 要搜索的平台列表
        :return: 保存的文件路径
        """
        results = self.search_news(keyword)
        json_file = self.storage.save_json_together(results, keyword)
        return json_file



# news = SearchNews()
# news.page_num = 1
# news.search_and_storage('赵丽颖')






