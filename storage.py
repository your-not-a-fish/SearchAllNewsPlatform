import os
from datetime import datetime
import util


class Storage(object):
    def __init__(self):
        self.root = 'warehouse'
        self.material_folder = 'material'
        self.json_folder = 'json_out'
        self.csv_folder = 'csv'
        self.day_str = datetime.now().strftime("%Y_%m_%d")
        self.base_folder = None

    def download_data_file(self, data, keyword):
        """统一格式，可以避免素材重复下载"""
        if 'media_list' in data and len(data['media_list']):
            stand_keyword = util.stand_name(keyword)
            title = data.get('title', '')
            stand_title = util.stand_name(title)
            user = data.get('user', '')
            platform = data.get('platform', '')
            mid = data.get('mid', '')
            platform_user_mid = '{}_{}_{}'.format(platform, util.stand_name(user), mid)
            # 路径标准化
            out_material_folder = os.path.join(self.root, self.material_folder, stand_keyword, platform_user_mid)
            os.makedirs(out_material_folder, exist_ok=True)

            new_media_list = []
            media_list = data['media_list']
            for i in range(len(media_list)):
                # 获取url
                if type(media_list[i]) == str:
                    get_url = media_list[i]
                elif type(media_list[i]) == dict:
                    get_url = media_list[i].get('url', '')
                else:
                    get_url = ''
                # 判断类型
                if get_url:
                    url = 'https:' + get_url if get_url[:6] != 'https:' else get_url

                    media_type = data.get('media_type', 'img')
                    if media_type == 'img':
                        suffix = util.get_suffix_by_url(url)
                        file_path = os.path.join(out_material_folder,'{}_{}.{}'.format(i, stand_title, suffix))
                    else:
                        file_path = os.path.join(out_material_folder, '{}_{}.mp4'.format(i, stand_title))

                    if not os.path.exists(file_path):
                        os.makedirs(out_material_folder, exist_ok=True)
                        util.download_file(url, file_path)
                    new_media_list.append({
                        'url': url,
                        'file_path': file_path if os.path.exists(file_path) else None
                    })
                    data['media_list'] = new_media_list
        return data

    def save_json_one_by_one(self, data_list, keyword):
        """把所有的数据都下载下来，文档一个一个保存"""
        stand_keyword = util.stand_name(keyword)
        json_folder_one_by_one = os.path.join(self.root, self.json_folder, f'{self.day_str}_{stand_keyword}')
        out_json_file_list = []

        for i in range(len(data_list)):
            data = data_list[i]
            # 1.下载素材
            new_data = self.download_data_file(data, keyword)
            title = data.get('title', '')
            stand_title = util.stand_name(title)
            platform = data.get('platform', '')
            # 2.保存json
            os.makedirs(json_folder_one_by_one, exist_ok=True)
            out_json_file = os.path.join(json_folder_one_by_one, f'{i}_{platform}_{stand_title}.json')
            util.write_json(new_data, out_json_file)
            out_json_file_list.append(out_json_file)
            print('{}/{} {}  记录完成'.format(i+1, len(data_list), out_json_file))
        print('所有数据处理完成')

    def save_json_together(self, data_list, keyword):
        """把所有的数据都下载下来，文档一个一个保存"""
        stand_keyword = util.stand_name(keyword)
        out_folder = os.path.join(self.root, self.json_folder)
        os.makedirs(out_folder, exist_ok=True)
        json_together = os.path.join(out_folder, f'{stand_keyword}.json')
        new_data_list = []
        print(f'下载介质: {keyword}')

        for i in range(len(data_list)):
            platform = data_list[i].get('platform', '')
            title = data_list[i].get('title', '')
            print('\r{}/{} {} {}'.format(i+1, len(data_list), platform, title))
            data = data_list[i]
            new_data = self.download_data_file(data, keyword)
            new_data_list.append(new_data)

        util.write_json(new_data_list, json_together)
        print(f'{json_together}  记录完成')
        return json_together


