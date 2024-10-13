<?php
// 允许所有域的跨域请求
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Credentials: true");
//error_reporting(0);
header('Content-Type:application/json; charset=utf-8');
class QQMusic {
    private $base_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg';
    private $guid = '10000';
    private $uin = '0';
    private $cookies = [];
    private $headers = [
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    ];
    
    //歌曲文件类型

    //MASTER:   臻品母带2.0，24Bit 192kHz，size_new[0]
    //ATMOS_2:  臻品全景声2.0，16Bit 44.1kHz，size_new[1]
    //ATMOS_51: 臻品音质2.0，16Bit 44.1kHz，size_new[2]
    //FLAC:     flac 格式，16Bit 44.1kHz～24Bit 48kHz，size_flac
    //OGG_640:  ogg 格式，640kbps，size_new[5]
    //OGG_320:  ogg 格式，320kbps，size_new[3]
    //OGG_192:  ogg 格式，192kbps，size_192ogg
    //OGG_96:   ogg 格式，96kbps，size_96ogg
    //MP3_320:  mp3 格式，320kbps，size_320mp3
    //MP3_128:  mp3 格式，128kbps，size_128mp3
    //ACC_192:  m4a 格式，192kbps，size_192aac
    //ACC_96:   m4a 格式，96kbps，size_96aac
    //ACC_48:   m4a 格式，48kbps，size_48aac

    private $file_config = [
        '128' => ['s' => 'M500', 'e' => '.mp3', 'bitrate' => '128kbps'],
        '320' => ['s' => 'M800', 'e' => '.mp3', 'bitrate' => '320kbps'],
        'flac' => ['s' => 'F000', 'e' => '.flac', 'bitrate' => 'FLAC'],
        'master' => ['s' => 'AI00', 'e' => '.flac', 'bitrate' => 'Master'],
        'atmos_2' => ['s' => 'Q000', 'e' => '.flac', 'bitrate' => 'Atmos 2'],
        'atmos_51' => ['s' => 'Q001', 'e' => '.flac', 'bitrate' => 'Atmos 5.1'],
        'ogg_640' => ['s' => 'O801', 'e' => '.ogg', 'bitrate' => '640kbps'],
        'ogg_320' => ['s' => 'O800', 'e' => '.ogg', 'bitrate' => '320kbps'],
        'ogg_192' => ['s' => 'O600', 'e' => '.ogg', 'bitrate' => '192kbps'],
        'ogg_96' => ['s' => 'O400', 'e' => '.ogg', 'bitrate' => '96kbps'],
        'aac_192' => ['s' => 'C600', 'e' => '.m4a', 'bitrate' => '192kbps'],
        'aac_96' => ['s' => 'C400', 'e' => '.m4a', 'bitrate' => '96kbps'],
        'aac_48' => ['s' => 'C200', 'e' => '.m4a', 'bitrate' => '48kbps'],
    ];
    private $song_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg';
    private $lyric_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg';

    public function setCookies($cookie_str) {
        parse_str(str_replace('; ', '&', $cookie_str), $this->cookies);
    }

    public function ids($url) {
        if (strpos($url, 'c6.y.qq.com') !== false) {
            $ch = curl_init($url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            $response = curl_exec($ch);
            $redirect_url = curl_getinfo($ch, CURLINFO_REDIRECT_URL);
            if (!empty($this->cookies)) {
                curl_setopt($ch, CURLOPT_COOKIE, http_build_query($this->cookies, '', '; '));
            }
            curl_close($ch);
            $url = $redirect_url;
        }

        if (strpos($url, 'y.qq.com') !== false) {
            if (strpos($url, '/songDetail/') !== false) {
                preg_match('/\/songDetail\/([^\/\?]+)/', $url, $matches);
                return $matches[1] ?? '';
            }

            if (strpos($url, 'id=') !== false) {
                preg_match('/id=(\w+)/', $url, $matches);
                return $matches[1] ?? '';
            }
        }
        return null;
    }

    public function getMusicUrl($songmid, $file_type = 'flac') {
        if (!array_key_exists($file_type, $this->file_config)) {
            throw new Exception("Invalid file_type. Choose from 'm4a', '128', '320', 'flac', 'ape', 'dts'");
        }

        $file_info = $this->file_config[$file_type];
        $file = "{$file_info['s']}{$songmid}{$songmid}{$file_info['e']}";
        //exit($file);
        $req_data = [
            'req_1' => [
                'module' => 'vkey.GetVkeyServer',
                'method' => 'CgiGetVkey',
                'param' => [
                    'filename' => [$file],
                    'guid' => $this->guid,
                    'songmid' => [$songmid],
                    'songtype' => [0],
                    'uin' => $this->uin,
                    'loginflag' => 1,
                    'platform' => '20',
                ],
            ],
            'loginUin' => $this->uin,
            'comm' => [
                'uin' => $this->uin,
                'format' => 'json',
                'ct' => 24,
                'cv' => 0,
            ],
        ];

        $response = $this->curlRequest($this->base_url, json_encode($req_data));
        //exit($response);
        $data = json_decode($response, true);
        $purl = $data['req_1']['data']['midurlinfo'][0]['purl'] ?? '';

        if ($purl == '') {
            return null; // VIP or unavailable
        }

        $url = $data['req_1']['data']['sip'][1] . $purl;
        $prefix = substr($purl, 0, 4);
        $bitrate = array_search($prefix, array_column($this->file_config, 's'));

        return [
            'url' => str_replace("http://", "https://", $url),
            'bitrate' => $this->file_config[$file_type]['bitrate'] ?? ''
        ];
    }

    public function getMusicSong($mid, $sid) {
        $req_data = $sid !== 0 ? ['songid' => $sid, 'platform' => 'yqq', 'format' => 'json'] : ['songmid' => $mid, 'platform' => 'yqq', 'format' => 'json'];

        $response = $this->curlRequest($this->song_url, http_build_query($req_data));
        //exit($response);
        $data = json_decode($response, true);

        if (isset($data['data']) && count($data['data']) > 0) {
            $song_info = $data['data'][0];
            $album_info = $song_info['album'] ?? [];
            $singers = $song_info['singer'] ?? [];
            $singer_names = implode(', ', array_column($singers, 'name'));

            $album_mid = $album_info['mid'] ?? '';
            $img_url = $album_mid ? "https://y.qq.com/music/photo_new/T002R800x800M000{$album_mid}.jpg?max_age=2592000" : "https://example.com/default-cover.jpg";

            $minutes = floor($song_info['interval'] / 60);
            $seconds = $song_info['interval'] % 60;
            $duration_str = sprintf("%d:%02d", $minutes, $seconds);

            return [
                'name' => $song_info['name'] ?? 'Unknown',
                'album' => $album_info['name'] ?? 'Unknown',
                'singer' => $singer_names,
                'pic' => $img_url,
                'mid' => $song_info['mid'] ?? $mid,
                'id' => $song_info['id'] ?? $sid,
                'interval' => $duration_str
            ];
        } else {
            return ['msg' => '信息获取错误/歌曲不存在'];
        }
    }

    public function getMusicLyricNew($songid) {
        $payload = [
            "music.musichallSong.PlayLyricInfo.GetPlayLyricInfo" => [
                "module" => "music.musichallSong.PlayLyricInfo",
                "method" => "GetPlayLyricInfo",
                "param" => [
                    "trans_t" => 0,
                    "roma_t" => 0,
                    "crypt" => 0,
                    "lrc_t" => 0,
                    "interval" => 208,
                    "trans" => 1,
                    "ct" => 6,
                    "songID" => $songid,
                ],
            ],
            "comm" => [
                "ct" => "6",
                "cv" => "80600",
            ],
        ];

        try {
            $res = $this->curlRequest($this->base_url, json_encode($payload));
            $d = json_decode($res, true);
            $lyric_data = $d["music.musichallSong.PlayLyricInfo.GetPlayLyricInfo"]["data"];

            $lyric = !empty($lyric_data['lyric']) ? base64_decode($lyric_data['lyric']) : '';
            $tylyric = !empty($lyric_data['trans']) ? base64_decode($lyric_data['trans']) : '';
            return ['lyric' => $lyric, 'tylyric' => $tylyric];
        } catch (Exception $e) {
            return ['error' => '无法获取歌词'];
        }
    }

    private function curlRequest($url, $postFields = null) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $this->headers);
        if ($postFields) {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
        }
        if (!empty($this->cookies)) {
            curl_setopt($ch, CURLOPT_COOKIE, http_build_query($this->cookies, '', '; '));
        }
        $response = curl_exec($ch);
        curl_close($ch);
        return $response;
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $song_url = $_GET['url'] ?? null;
    //$level = [$_GET['level']] ?? null;
    if (!$song_url) {
        echo json_encode(["error" => "url & level parameter is required"]);
        http_response_code(400);
        exit;
    }

    $qqmusic = new QQMusic();
    $cookie_str = ''; // 设置你的cookie字符串
    $qqmusic->setCookies($cookie_str);
    // 从传入的 URL 中提取 songmid 或 songid
    $songmid = $qqmusic->ids($song_url);
    if (is_numeric($songmid)) {
        // 如果 songmid 是数字，视为 songid (sid)
        $sid = intval($songmid);
        $mid = 0;
    } else {
        // 否则视为 songmid (mid)
        $sid = 0;
        $mid = $songmid;
    }
    
    if ($songmid) {
        $music_info = $qqmusic->getMusicSong($mid, $sid);
        //$music_url = $qqmusic->getMusicUrl($music_info['mid'],$level);
        $music_lyric = $qqmusic->getMusicLyricNew($music_info['id']);
        // 文件类型处理
        $file_types = ['aac_48','aac_96','aac_192','ogg_96','ogg_192','ogg_320','ogg_640','atmos_51','atmos_2','master','flac','320','128'];;
        $results = [];  // 用于存储不同文件类型的结果

        foreach ($file_types as $file_type) {
            // 调用 getMusicUrl，传递正确的 $file_type
            $result = $qqmusic->getMusicUrl($music_info['mid'], $file_type);
    
            if ($result) {
                // 存储结果，同时保存 URL 和比特率
                $results[$file_type] = [
                    'url' => $result['url'], 
                    'bitrate' => $result['bitrate']
                ];
            }
        }
        $response = [
            'music_info' => $music_info,
            'music_url' => $results,
            'music_lyric' => $music_lyric,
        ];
        echo json_encode($response,480);
    } else {
        echo json_encode(["error" => "歌曲ID无效"]);
        http_response_code(400);
    }
}
?>