import imghdr
import uuid
import requests
import re
import threading
import json
import chardet
from datetime import datetime, timedelta
import time


file_lock = threading.Lock()


def download_file(url, out_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        with open(out_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False


def load_json(file_path):
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'latin1', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                detected = chardet.detect(raw_data)
                actual_encoding = detected['encoding'] if detected['confidence'] > 0.7 else encoding
                decoded_data = raw_data.decode(actual_encoding)
                return json.loads(decoded_data)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        except FileNotFoundError:
            print(f"找不到文件: {file_path}")
        except Exception as e:
            print(f"加载文件时发生错误: {e}")
    raise Exception("无法使用任何已知编码打开文件")


def write_json(data, file_path):
    with file_lock:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def stand_name(string):
    # 去掉所有的特色符号，空格
    str1 = re.sub('\”|\*|\<|\n|\>|\?|\\|\||\/|\:|\"|\||', '', string)
    str2 = ''.join(str1.split())
    return str2


def uid_name():
    return ''.join(str(uuid.uuid4()).split('-'))


def get_suffix_by_url(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 检查请求是否成功
    # 使用imghdr来猜测图片格式
    img_format = imghdr.what(None, h=response.content)
    return img_format


def standardize_date(created_at):
    """标准化微博发布时间"""
    if "刚刚" in created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    elif "秒" in created_at:
        second = created_at[:created_at.find(u"秒")]
        second = timedelta(seconds=int(second))
        created_at = (datetime.now() - second).strftime("%Y-%m-%d %H:%M")
    elif "分钟" in created_at:
        minute = created_at[:created_at.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        created_at = (datetime.now() - minute).strftime("%Y-%m-%d %H:%M")
    elif "小时" in created_at:
        hour = created_at[:created_at.find(u"小时")]
        hour = timedelta(hours=int(hour))
        created_at = (datetime.now() - hour).strftime("%Y-%m-%d %H:%M")
    elif "今天" in created_at:
        today = datetime.now().strftime('%Y-%m-%d')
        created_at = today + ' ' + created_at[2:]
    elif '年' not in created_at:
        year = datetime.now().strftime("%Y")
        month = created_at[:2]
        day = created_at[3:5]
        times = created_at[6:]
        created_at = year + '-' + month + '-' + day + ' ' + times
    else:
        year = created_at[:4]
        month = created_at[5:7]
        day = created_at[8:10]
        times = created_at[11:]
        created_at = year + '-' + month + '-' + day + ' ' + times

    dt_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M")
    # 将 datetime 对象转换为 UTC 时间戳
    timestamp = int(time.mktime(dt_obj.timetuple()))
    return timestamp

