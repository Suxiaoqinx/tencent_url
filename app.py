from flask import Flask, request, jsonify ,Response
import requests
import time
import random
import json
import os
import base64

app = Flask(__name__)

cookie_str = ''

class QQMusic:
    def __init__(self):
        self.base_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg'
        self.guid = '10000'
        self.uin = '0'
        self.cookies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://y.qq.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        self.file_config = {
            'm4a': {'s': 'C400', 'e': '.m4a', 'bitrate': 'M4A'},
            '128': {'s': 'M500', 'e': '.mp3', 'bitrate': '128kbps'},
            '320': {'s': 'M800', 'e': '.mp3', 'bitrate': '320kbps'},
            'flac': {'s': 'F000', 'e': '.flac', 'bitrate': 'FLAC'},
            'ape': {'s': 'A000', 'e': '.ape', 'bitrate': 'ape'},
        }
        self.song_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg'
        self.lyric_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'

    def set_cookies(self, cookie_str):
        cookies = {}
        for cookie in cookie_str.split('; '):
            key, value = cookie.split('=', 1)
            cookies[key] = value
        self.cookies = cookies

    def ids(self, url):
        """
        从不同类型的 URL 中提取歌曲 ID，支持重定向和 /songDetail/ URL 形式
        """
        # 如果URL中包含 'c6.y.qq.com'，则发送请求获取重定向后的URL
        if 'c6.y.qq.com' in url:
            response = requests.get(url, allow_redirects=False)
            url = response.headers.get('Location')  # 获取重定向的URL

        # 检查重定向后的URL中是否包含 'y.qq.com'，并根据情况提取 id
        if 'y.qq.com' in url:
            # 处理 /songDetail/ 形式的 URL
            if '/songDetail/' in url:
                index = url.find('/songDetail/') + len('/songDetail/')
                song_id = url[index:].split('/')[0]  # 提取 '/songDetail/' 后面的部分
                return song_id
            
            # 如果是带 id= 参数的 URL，提取 id 参数
            if 'id=' in url:
                index = url.find('id=') + 3
                song_id = url[index:].split('&')[0]  # 提取 'id' 的值
                return song_id

        # 如果都不匹配，返回 None
        return None

    def get_music_url(self, songmid, file_type='flac'):
        """
        获取音乐播放URL
        """
        if file_type not in self.file_config:
            raise ValueError("Invalid file_type. Choose from 'm4a', '128', '320', 'flac', 'ape'")

        file_info = self.file_config[file_type]
        file = f"{file_info['s']}{songmid}{songmid}{file_info['e']}"

        req_data = {
            'req_1': {
                'module': 'vkey.GetVkeyServer',
                'method': 'CgiGetVkey',
                'param': {
                    'filename': [file],
                    'guid': self.guid,
                    'songmid': [songmid],
                    'songtype': [0],
                    'uin': self.uin,
                    'loginflag': 1,
                    'platform': '20',
                },
            },
            'loginUin': self.uin,
            'comm': {
                'uin': self.uin,
                'format': 'json',
                'ct': 24,
                'cv': 0,
            },
        }

        response = requests.post(self.base_url, json=req_data, cookies=self.cookies, headers=self.headers)
        data = response.json()
        purl = data['req_1']['data']['midurlinfo'][0]['purl']
        if purl == '':
            # VIP
            return None

        url = data['req_1']['data']['sip'][1] + purl
        prefix = purl[:4]
        bitrate = next((info['bitrate'] for key, info in self.file_config.items() if info['s'] == prefix), '')

        return {'url': url.replace("http://", "https://"), 'bitrate': bitrate}

    def get_music_song(self, mid, sid):
        """
        获取歌曲信息
        """
        if sid != 0:
            # 如果有 songid（sid），使用 songid 进行请求
            req_data = {
                'songid': sid,
                'platform': 'yqq',
                'format': 'json',
            }
        else:
            # 如果没有 songid，使用 songmid 进行请求
            req_data = {
                'songmid': mid,
                'platform': 'yqq',
                'format': 'json',
            }

        # 发送请求并解析返回的 JSON 数据
        response = requests.post(self.song_url, data=req_data, cookies=self.cookies, headers=self.headers)
        data = response.json()
        #return data
        # 确保数据结构存在，避免索引错误
        if 'data' in data and len(data['data']) > 0:
            song_info = data['data'][0]
            album_info = song_info.get('album', {})
            singers = song_info.get('singer', [])
            singer_names = ', '.join([singer.get('name', 'Unknown') for singer in singers])

            # 获取专辑封面图片 URL
            album_mid = album_info.get('mid')
            img_url = f'https://y.qq.com/music/photo_new/T002R800x800M000{album_mid}.jpg?max_age=2592000' if album_mid else 'https://axidiqolol53.objectstorage.ap-seoul-1.oci.customer-oci.com/n/axidiqolol53/b/lusic/o/resources/cover.jpg'

            # 返回处理后的歌曲信息
            return {
                'name': song_info.get('name', 'Unknown'),
                'album': album_info.get('name', 'Unknown'),
                'singer': singer_names,
                'pic': img_url,
                'mid': song_info.get('mid', mid),
                'id': song_info.get('id', sid)
            }
        else:
            return {'msg': '信息获取错误/歌曲不存在'}

    def get_music_lyric(self, mid):
        """
        获取歌曲歌词 - 旧版歌词接口
        """
        # 构造请求 URL
        url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        params = {
            '_': str(int(time.time())),  # 当前时间戳
            'format': 'json',
            'loginUin': ''.join(random.sample('1234567890', 10)),  # 随机生成的登录 UIN
            'songmid': mid  # 歌曲 MID
        }

        try:
            # 发送 GET 请求获取歌词数据
            response = requests.get(url, headers=self._headers, cookies=self.cookies, params=params)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            print(data)
            # 从返回的 JSON 数据中获取歌词
            lyric = data.get('lyric', '')
            if lyric:
                # 解码并返回歌词
                return base64.b64decode(lyric).decode('utf-8')
            else:
                return "未找到歌词"

        except requests.RequestException as e:
            return f"请求错误: {e}"
        except Exception as e:
            return f"解码错误: {e}"

    def get_music_lyric_new(self, songid):
        """从QQ音乐电脑客户端接口获取歌词

        参数:
            songID (str): 音乐id

        返回值:
            dict: 通过['lyric']和['trans']来获取base64后的歌词内容

            其中 lyric为原文歌词 trans为翻译歌词
        """
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        payload = {
            "music.musichallSong.PlayLyricInfo.GetPlayLyricInfo": {
                "module": "music.musichallSong.PlayLyricInfo",
                "method": "GetPlayLyricInfo",
                "param": {
                    "trans_t": 0,
                    "roma_t": 0,
                    "crypt": 0,  # 1 define to encrypt
                    "lrc_t": 0,
                    "interval": 208,
                    "trans": 1,
                    "ct": 6,
                    "singerName": "",
                    "type": 0,
                    "qrc_t": 0,
                    "cv": 80600,
                    "roma": 1,
                    "songID": songid,
                    "qrc": 0,  # 1 define base64 or compress Hex
                    "albumName": "",
                    "songName": "",
                },
            },
            "comm": {
                "wid": "",
                "tmeAppID": "qqmusic",
                "authst": "",
                "uid": "",
                "gray": "0",
                "OpenUDID": "",
                "ct": "6",
                "patch": "2",
                "psrf_qqopenid": "",
                "sid": "",
                "psrf_access_token_expiresAt": "",
                "cv": "80600",
                "gzip": "0",
                "qq": "",
                "nettype": "2",
                "psrf_qqunionid": "",
                "psrf_qqaccess_token": "",
                "tmeLoginType": "2",
            },
        }

        # 发送请求获取歌词
        try:
            res = requests.post(url, json=payload)  # 确保使用 POST 请求
            res.raise_for_status()  # 检查请求是否成功
            d = res.json()  # 解析返回的 JSON 数据
            
            # 提取歌词数据
            lyric_data = d["music.musichallSong.PlayLyricInfo.GetPlayLyricInfo"]["data"]
            # 处理歌词内容
            if 'lyric' in lyric_data and lyric_data['lyric']:
                # 解码歌词
                lyric = base64.b64decode(lyric_data['lyric']).decode('utf-8')
                tylyric = base64.b64decode(lyric_data['trans']).decode('utf-8')
            else:
                lyric = ''  # 没有歌词的情况下返回空字符串
                tylyric = ''  # 没有歌词的情况下返回空字符串
            return {'lyric': lyric,'tylyric': tylyric}  # 返回包含歌词的字典

        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return {'error': '无法获取歌词'}

@app.route('/song', methods=['GET'])
def get_song():
    song_url = request.args.get('url')
    if not song_url:
        return jsonify({"error": "url parameter is required"}), 400

    qqmusic = QQMusic()
    qqmusic.set_cookies(cookie_str)

    # 从传入的 URL 中提取 songmid 或 songid
    songmid = qqmusic.ids(song_url)

    # 文件类型处理
    file_types = ['flac', 'm4a', '128', '320', 'ape']
    results = {}

    try:
        # 如果 songmid 是数字，视为 songid (sid)
        sid = int(songmid)
        mid = 0
    except ValueError:
        # 否则视为 songmid (mid)
        sid = 0
        mid = songmid
    #return qqmusic.get_music_song(mid, sid)
    # 获取歌曲信息
    info = qqmusic.get_music_song(mid, sid)

    # 对于每种文件类型，获取对应的音乐 URL
    for file_type in file_types:
        result = qqmusic.get_music_url(info['mid'], file_type)
        if result:
            results[file_type] = result
        time.sleep(0.1)
    lyric =  qqmusic.get_music_lyric_new(info['id'])

    # 构造 JSON 输出
    output = {
        'song': info,
        'lyric': lyric,
        'music_urls': results,
    }
    json_data = json.dumps(output)
    return Response(json_data, content_type='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5122)
