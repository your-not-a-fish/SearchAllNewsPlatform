import time


class FilterDataDict(object):
    def __init__(self):
        self.limit_day = None
        self.limit_hours = None
        self.is_original = None
        self.media_type = None
        self.text_num = None
        self.img_num = None
        # self.num = None
        # self.forward_num = None
        # self.comments_num = None
        # self.like_num = None
        self.forbid_userID = None
        self.forbid_user = None

    def example_setting(self):
        self.limit_day = 1
        self.limit_hours = 24
        self.is_original = [0, 1]
        self.media_type = ['text', 'img', 'video']
        self.text_num = [30, 2000]
        self.img_num = [3, 20]

    def platform_setting(self):
        self.limit_hours = 24
        self.text_num = [30, 2000]
        self.img_num = [3, 20]

    def filter_by_day(self, data):
        """仅保留规定时间内的数据"""
        try:
            if self.limit_day and 'time_int' in data:
                timestamp = int(str(data['time_int'])[:10])
                time_difference = int(time.time()) - timestamp
                return time_difference <= self.limit_day * 24 * 3600
            return True
        except Exception:
            return True

    def filter_by_hours(self, data):
        try:
            if self.limit_hours and 'time_int' in data:
                timestamp = int(str(data['time_int'])[:10])
                time_difference = int(time.time()) - timestamp
                return time_difference <= self.limit_hours * 3600
            return True
        except Exception:
            return True


    def filter_by_original(self, data):
        try:
            if self.is_original and 'is_original' in data:
                if data['is_original'] not in self.is_original:
                    return False
            return True
        except Exception:
            return True

    def filter_by_media_type(self, data):
        try:
            if self.media_type and 'media_type' in data:
                if data['media_type'] not in self.media_type:
                    return False
            return True
        except Exception:
            return True

    def filter_by_text_num(self, data):
        try:
            if self.text_num and 'text' in data:
                if data['text']:
                    if self.text_num[0] <= len(data['text']) <= self.text_num[1]:
                        return True
                return False
            return True
        except Exception:
            return True

    def filter_by_img_num(self, data):
        try:
            if self.img_num and 'media_list' in data:
                if data['media_list']:
                    if self.img_num[0] <= len(data['media_list']) <= self.img_num[1]:
                        return True
                return False
            return True
        except Exception:
            return True

    def filter_data(self, data):
        """应用所有过滤条件到单个数据"""
        try:
            if not self.filter_by_day(data):
                return False
            if not self.filter_by_hours(data):
                return False
            if not self.filter_by_original(data):
                return False
            if not self.filter_by_media_type(data):
                return False
            if not self.filter_by_text_num(data):
                return False
            if not self.filter_by_img_num(data):
                return False
            return True
        except Exception:
            return True

    def filter_data_list(self, data_list):
        """过滤数据列表，只保留满足所有条件的数据"""
        try:
            filtered_list = []
            for data in data_list:
                if self.filter_data(data):
                    filtered_list.append(data)
            return filtered_list
        except Exception:
            return data_list
