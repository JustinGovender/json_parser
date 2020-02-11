import requests
import json
import html


URL_GOOGLE_TRANSLATE = 'https://www.googleapis.com/language/translate/v2'
URL_GOOGLE_DETECT = 'https://translation.googleapis.com/language/translate/v2/detect'
with open("google_api_key") as f:
    GOOGLE_API_KEY = f.readlines()


def google_detect(text_to_detect):
    query_params = {}
    query_params['key'] = GOOGLE_API_KEY
    query_params['q'] = text_to_detect
    google_result = None
    detected_lang = ''
    try:
        google_result = requests.post(URL_GOOGLE_DETECT, data=json.loads(json.dumps(query_params)))
    except Exception as e:
        print('can not get result from google with {}', e)

    if google_result:
        detected_lang = json.loads(google_result.text)['data']['detections'][0][0]['language']
        detected_lang = html.unescape(detected_lang)
    return detected_lang


def google_translate(text_to_translate, source_lang, target_lang):
    text_list = text_to_translate.split('\n')
    query_params = {'key': GOOGLE_API_KEY, 'source': source_lang, 'target': target_lang, 'q': text_list}
    google_result = None
    google_translated = dict.fromkeys(text_list, "")

    try:
        google_result = requests.post(URL_GOOGLE_TRANSLATE, data=json.loads(json.dumps(query_params)))
    except Exception as e:
        print('can not get result from google with {}', e)

    if google_result:
        del google_translated
        google_translated = dict(zip(text_list, [html.unescape(text['translatedText']) for text in json.loads(google_result.text)['data']['translations']]))

    return google_translated

if __name__=="__main__":
    google_translate('当你沮丧而烦恼时你需要帮助没事，没事闭上眼睛，想起我。\n很快我会在那里即使您最漆黑的夜晚也能照亮。\n李小龍, 本名李振藩，國際著名華人武打演員 、武術家 、導演、截拳道創始人。\n香港粵劇丑生李海泉之子，李小龙有两个姐姐、一个哥哥和一个弟弟。', 'zh', 'ko')