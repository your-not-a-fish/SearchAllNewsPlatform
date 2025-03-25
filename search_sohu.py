import time
import random
from DrissionPage import ChromiumOptions,Chromium
from filter import FilterDataDict
from storage import Storage



class SoHuSearch(object):
    def __init__(self, filter_options=None, storage_options=None):
        self.sleep_time = [1, 3]
        self.page_num = None
        self.search_list = []
        co = ChromiumOptions()
        co.use_system_user_path()
        self.browser  = Chromium(co)
        self.tab = self.browser.latest_tab
        if filter_options:
            self.filter = filter_options
        else:
            self.filter = FilterDataDict()
        if storage_options:
            self.storage = storage_options
        else:
            self.storage = Storage()

    def sleep_random_time(self):
        times = random.randint(self.sleep_time[0], self.sleep_time[1])
        for i in range(times):
            print('\r防封等待 {}/{}'.format(i+1, times), end='', flush=True)
            time.sleep(1)
        # print('\r ')

    def _parser_sohu_search_page_by_listen(self, keyword):
        url = f'https://search.sohu.com/?keyword={keyword}'
        self.tab.listen.start('&searchType=news&queryType=outside')
        self.tab.get(url)  # 访问网址，这行产生的数据包不监听
        pak = self.tab.listen.wait()
        datas = pak.response.body['data']['news']

        for d in datas:
            # print(d)
            data = {
                'platform': 'sough',
                'keyword': keyword,
                'userID': d['authorId'],
                'user': d['authorName'],
                'time_int': int(d['postTime']),
                'is_original': d.get('resourceType', 1),
                'url': d['url'],
                'mid': d['id'],
                'title': d['title'],
                'text': None,
                'media_type': 'video' if d['type'] == 4 else 'img',
                'media_list': d['imagesList'],
                    }
            self.search_list.append(data)
        self.tab.listen.stop()

    def _parse_article_page(self, url):
        self.tab.get(url)
        if len(self.tab.html) < 100:
            print('{}  页面内容为空!\n{}'.format(url, self.tab.html))
            return None
        content = self.tab.s_ele('@id=mp-editor')
        if content:
            return content.raw_text

    def search_news(self, keyword):
        self._parser_sohu_search_page_by_listen(keyword)
        self.tab.set.load_mode.eager()
        for i in range(len(self.search_list)):
            print('内容解析: {}/{} {}'.format(i+1, len(self.search_list), self.search_list[i].get('title', '')))
            text = self._parse_article_page(self.search_list[i]['url'])
            if text:
                self.search_list[i]['text'] = text
            # self.sleep_random_time()
        print('数据解析完成，共{}条数据'.format(len(self.search_list)))
        self.browser.quit()
        # self.storage.save_json_together(self.search_list, keyword)
        # self.storage.save_json_one_by_one(self.search_list, keyword)
        return self.search_list

    def search_and_storage(self, keyword):
        self.search_news(keyword)
        json_file = self.storage.save_json_together(self.search_list, keyword)
        return json_file


# s = SoHuSearch()
# s.search_news('长沙')

