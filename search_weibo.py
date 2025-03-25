import time
import random
from DrissionPage import ChromiumOptions, Chromium, SessionPage
from filter import FilterDataDict
from storage import Storage
import util
import re


def get_user_id_from_href(url):
    """从href中解析出用户ID"""
    match = re.search(r'/(\d+)(?:\?|$)', url)
    user_id = match.group(1) if match else None
    return int(user_id)


def parse_weibo_search_page(feed_list, keyword):
    """解析出整个页面的数据"""
    page_content = []
    for feed in feed_list:
        if 'url_show' not in feed.attrs:  # 排除广告
            data = {'platform': 'weibo', 'keyword': keyword, 'mid': int(feed.attr('mid')), 'title': ''}

            info = feed.ele('@class=name').attrs
            data['userID'] = get_user_id_from_href(info['href'])
            data['user'] = info['nick-name']
            time_text = feed.ele('@class=from').eles('@tag():a')[0].text
            data['time_int'] = util.standardize_date(time_text)
            data['text'] = feed.ele('@node-type=feed_list_content').raw_text.replace('\u200b', '').strip()
            source_info = feed.ele('@node-type=feed_list_forwardContent')
            data['is_original'] = 0 if source_info else 1
            # 介质
            media = feed.ele('@node-type=feed_list_media_prev')
            if media:
                video_type = media.child().attr('node-type')
                if video_type == 'fl_pic_list':
                    gif = media.ele('@tag()=video')
                    if gif:
                        data['media_type'] = 'video'
                        data['media_list'] = [gif.attr('src')]
                    else:
                        data['media_type'] = 'img'
                        media_info = media.s_eles('@tag():img')
                        data['media_list'] = [img.attr('src').replace('sinaimg.cn/thumb150/', 'sinaimg.cn/mw690/') for img in media_info]
                elif video_type == 'feed_list_media_disp':
                    data['media_type'] = 'video'
                    video_info = str(media.ele('@tag()=video-player').attrs)
                    index = video_info.find("""src:'//f.video""")
                    end_index = video_info.find(""",video'""")
                    video_src = video_info[index + 5: end_index + 6]
                    data['media_list'] = [video_src]
                else:
                    print('!!!')

            see_infos = feed.ele('@class=card-act').s_eles('@tag():a')
            see_list = [int(see_infos[i].text) if see_infos[i].text.isdigit() else 0 for i in range(3)]
            data['forward_num'] = see_list[0]
            data['comments_num'] = see_list[1]
            data['likes_num'] = see_list[2]
            page_content.append(data)
    return page_content


class WeiBoSearch(object):
    def __init__(self, filter_options=None, storage_options=None):
        self.sleep_time = [15, 30]
        self.page_num = 5
        self.print_info = True
        self.cookies = None
        self.page = None
        self.config_file = 'config.json'
        self.search_list = []
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

    def load_cookies(self):
        co = ChromiumOptions()
        co.use_system_user_path()
        browser = Chromium(co)
        tab = browser.latest_tab
        tab.set.load_mode.eager()
        tab.get('https://weibo.com/')
        for i in range(120):
            station = tab.ele('@class=LoginCard_text_3BtVI', timeout=3)
            if station:
                print(F'\r{i}/120 微博搜索需要登入账号，请手动登入账号', end='', flush=True)
                time.sleep(3)
            elif i == 119:
                raise Exception('浏览器未登录微博')
            else:
                self.login = True
                print('登录成功', end='')
                break
        print(tab.cookies())
        self.cookies = tab.cookies()
        self.page = SessionPage()
        self.page.set.cookies(self.cookies)
        browser.quit()
        print('cookies 加载成功')

    def get_for_url_list(self, url_list, key_word):
        for i in range(len(url_list)):
            print(f'页面: {i+1}/{self.page_num}')
            self.page.get(url_list[i])
            feed_list = self.page.s_eles('@action-type=feed_list_item')
            data_list = parse_weibo_search_page(feed_list, key_word)
            if len(data_list) == 0:
                break
            for data in data_list:
                if self.filter.filter_by_hours(data):
                    self.search_list.append(data)
                    if self.print_info:
                        print(data)
            if i != len(url_list) - 1:
                self.sleep_random_time()
        return self.search_list

    def search_news(self, keyword):
        """直接搜索"""
        self.load_cookies()
        url_list = [f'https://s.weibo.com/weibo?q={keyword}&page_num={i+1}' for i in range(self.page_num)]
        self.get_for_url_list(url_list, keyword)
        print('数据解析完成，共{}条数据'.format(len(self.search_list)))
        # filter_data_list = self.filter.filter_data_list(self.search_list)
        # self.storage.save_json_together(filter_data_list, keyword)
        return self.search_list

    def search_and_storage(self, keyword):
        self.search_news(keyword)
        json_file = self.storage.save_json_together(self.search_list, keyword)
        return json_file

    def search_news_by_scheme(self, scheme_dict):
        """热点获取"""
        self.load_cookies()
        url_list = ['https://s.weibo.com{}&page_num={}'.format(scheme_dict['search_url'], i+1) for i in range(self.page_num)]
        self.get_for_url_list(url_list, key_word=scheme_dict['word_scheme'])
        filter_data_list = self.filter.filter_data_list(self.search_list)
        # self.storage.save_json_together(filter_data_list, keyword)
        return filter_data_list


w = WeiBoSearch()
w.page_num = 2
w.search_news('赵丽颖')

