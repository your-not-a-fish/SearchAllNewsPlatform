import time
import random
import json
from DrissionPage import ChromiumOptions,Chromium
from filter import FilterDataDict
from storage import Storage


def standardization_data(data, keyword):
    # try:
        data_dict = {
            'platform': 'toutiao',
            'keyword': keyword,
            'userID': data['user_id'],
            'user': data['source'],
            'time_int': int(data['publish_time']),
            'is_original': 1,
            'url': 'https://toutiao.com/article/{}/'.format(data['id']),
            'mid': data['id'],
            'title': data['title'],
            'text': None,
            'media_type': 'img',
            'media_list': data['detail_image_list'] if 'detail_image_list' in data else None,
        }
        return data_dict
    # except:
    #     return None


class TouTiaoSearch(object):
    def __init__(self, filter_options=None, storage_options=None):
        self.sleep_time = [1, 3]
        self.page_num = 5
        self.print_info = True
        self.stop = False
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
        print('\r ')

    def _parse_search_page_by_jscript(self, url, keyword):
        self.tab.get(url)
        js_els = self.tab.s_eles('@tag():script')
        for j in js_els:
            if 'type' in j.attrs and 'data-for' in j.attrs :
                json_str = j.text
                if json_str[:9] == '{"rawData':
                    data = json.loads(json_str)
                    list_data = data['rawData']['data']
                    for f in list_data:
                        data = standardization_data(f, keyword)
                        if data:
                            if not self.filter.filter_by_day(data):
                                self.stop = True
                                print('时间超出，停止抓取')
                                break
                            if self.filter.filter_data(data):
                                self.search_list.append(data)
                        else:
                            print('数据解析异常')
                            print(f)
                    break

    def _parse_article_page(self, url):
        data = {'url': url}
        self.tab.get(url)

        if len(self.tab.html) < 100:
            print('{}  页面内容为空!\n{}'.format(data['url'], self.tab.html))
            data['error'] = '页面为空'
            return data
        if '验证码' in self.tab.html:
            print('{}  页面内容为空!\n{}'.format(data['url'], self.tab.html))
            data['error'] = '登录验证'
            return data
        content = self.tab.s_ele('@class=article-content')
        if content:
            ts = content.s_eles('@tag():p')
            text_list = [t.text for t in ts if t.text]
            data['text'] = ''.join(text_list).replace('\n', '')
            ele_img = content.s_eles('@tag():img')
            img_list = [m.attr('data-src') for m in ele_img if 'gif' not in m.attr('mime_type')]
            data['img_list'] = img_list
            data['comments_num'] = self.tab.ele('@id=comment-area').ele('@tag():span').text
            return data

    def search_news(self, keyword):
        # 获取搜索页的数据
        for i in range(self.page_num):
            print(f'页面:{i+1}')
            url = 'https://so.toutiao.com/search?dvpf=pc&source=search_subtab_switch&keyword={}&pd=information&action_type=search_subtab_switch&page_num={}&search_id=&from=news&cur_tab_title=news'.format(keyword, i)
            self._parse_search_page_by_jscript(url, keyword)
            next_page = self.tab.ele('@@class=text-ellipsis@@text()=下一页')
            if not next_page or self.stop:
                print('没有下一页了')
                break
            if i != self.page_num - 1:
                self.sleep_random_time()
        print('数据抓取完成，共{}条数据'.format(len(self.search_list)))
        self.tab.set.load_mode.eager()
        # 获取详情页的数据
        for i in range(len(self.search_list)):
            print('内容解析: {}/{} {}'.format(i+1, len(self.search_list), self.search_list[i].get('title', '')))
            # try:
            content = self._parse_article_page(self.search_list[i]['article_url'])
            if content and 'text' in content:
                self.search_list[i]['text'] = content['text']
                self.search_list[i]['media_list'] = content['img_list']
                if self.print_info:
                    print(self.search_list[i])
            # except:
            #     print(self.search_list[i])
        print('数据解析完成，共{}条数据'.format(len(self.search_list)))
        self.browser.quit()
        # self.storage.save_json_together(self.search_list, keyword)
        return self.search_list

    def search_and_storage(self, keyword):
        self.search_news(keyword)
        json_file = self.storage.save_json_together(self.search_list, keyword)
        return json_file

# t = TouTiaoSearch()
# t.page_num=1
# t.search_news('赵露思粉发挑染')
# t._parse_article_page('https://www.toutiao.com/article/7418044515522593289/?channel=&source=news')
