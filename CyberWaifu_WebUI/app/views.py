from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

system_prompt = ''

def start(request):
    pass

def load_memory(request):
    pass

def get_voice(request):
    value = request.GET.get('value') # 1：汉语，2：日语
    voices = []
    model_info = None
    try:
        # django 相对路径使用的是 manage.py
        with open("../model/config.json", "r", encoding="utf-8") as f:
            model_info = json.load(f)
            lst = list(model_info.values())
            for item in lst:
                if (value == '1' and item['language'] == "Chinese")\
                    or (value == '2' and item['language'] == "Japanese"):
                    voices.append(item['name_zh'] + '(' + item['describe'] + ')')
    except Exception as e:
        voices = ["加载声线失败"]
        print(e)
    return JsonResponse(voices, safe=False)

def test(request):
    return render(request, 'test.html')

# Create your views here.
def index(request):
    char_list = []
    try:
        # django 相对路径使用的是 manage.py
        with open("../characters/config.json", "r", encoding="utf-8") as f:
            char_json = json.load(f)
            char_list = list(char_json.keys())
    except Exception as e:
        char_list = ["加载人设失败"]
        print(e)

    print("加载人设：", end='')
    print(char_list)

    voices = []
    model_info = None
    try:
        # django 相对路径使用的是 manage.py
        with open("../model/config.json", "r", encoding="utf-8") as f:
            model_info = json.load(f)
            voices = list(model_info.values())
    except Exception as e:
        voices = ["加载声线失败"]
        print(e)

    return render(request, 'index.html', {'characters': char_list, 'voices': voices})