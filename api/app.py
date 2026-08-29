from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
from collections import Counter
from io import BytesIO
from starlette.responses import JSONResponse
from fastapi.responses import FileResponse
import contextlib
import re
import os
from num2words import num2words
import wave
import onnxruntime as ort
# from googletrans import Translator
# from deep_translator import GoogleTranslator
import tempfile
import uuid
from starlette.background import BackgroundTask

model = YOLO("yolo11n.pt")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dick = {
    "twenty": "хорин",
    "thirty": "гучин",
    "forty": "дөчин",
    "fifty": "тавин",
    "sixty": "жаран",
    "seventy": "далан",
    "eighty": "наян",
    "ninety": "ерөн",
    "one": "нэг",
    "two":"хоёр",
    "three": "гурван",
    "four": "дөрвөн",
    "five": "таван",
    "six": "зургаан",
    "seven": "долоон",
    "eight": "найман",
    "nine": "есөн",
    "ten": "арван",
    "eleven": "арван нэгэн",
    "twelve": "арван хоёр",
    "thirteen": "арван гурван",
    "fourteen": "арван дөрвөн",
    "fifteen": "арван таван",
    "sixteen": "арван зургаан",
    "seventeen": "арван долоон",
    "eighteen": "арван найман",
    "nineteen": "арван есөн",
    "person": "хүн",
    "bicycle": "унадаг дугуй",
    "car": "машин",
    "motorcycle": "мотоцикл",
    "airplane": "онгоц",
    "bus": "автобус",
    "train": "галт тэрэг",
    "truck": "ачааны машин",
    "boat": "завь",
    "traffic light": "гэрлэн дохио",
    "fire hydrant": "гал унтраах усны цорго",
    "stop sign": "зогсох тэмдэг",
    "parking meter": "зогсоолын төлбөрийн аппарат",
    "bench": "сандал",
    "bird": "шувуу",
    "cat": "муур",
    "dog": "нохой",
    "horse": "морь",
    "sheep": "хонь",
    "cow": "үхэр",
    "elephant": "заан",
    "bear": "баавгай",
    "zebra": "тахь",
    "giraffe": "анааш",
    "backpack": "үүргэвч",
    "umbrella": "шүхэр",
    "handbag": "гар цүнх",
    "tie": "зангиа",
    "suitcase": "чемодан",
    "frisbee": "нисдэг таваг",
    "skis": "цанын хэрэгсэл",
    "snowboard": "сноуборд",
    "sports ball": "спортын бөмбөг",
    "kite": "цаасан шувуу",
    "baseball bat": "бэйсболын цохиур",
    "baseball glove": "бэйсболын бээлий",
    "skateboard": "скейтборд",
    "surfboard": "серфинг хийх самбар",
    "tennis racket": "теннисийн цохиур",
    "bottle": "усны сав",
    "wine glass": "дарсны хундага",
    "cup": "аяга",
    "fork": "сэрээ",
    "knife": "хутга",
    "spoon": "халбага",
    "bowl": "гүн аяга",
    "banana": "гадил",
    "apple": "алим",
    "sandwich": "сэндвич",
    "orange": "жүрж",
    "brocolli": "брокколи",
    "carrot": "лууван",
    # "hot dog": "хот-дог",
    "pizza": "пицца",
    "donut": "донат",
    "cake": "бялуу",
    "chair": "сандал",
    "couch": "буйдан",
    "potted plant": "савтай ургамал",
    "bed": "ор",
    "dining table": "хоолны ширээ",
    "toilet": "жорлон",
    "tv": "зурагт",
    "laptop": "зөөврийн компьютер",
    "mouse": "маус",
    "remote": "удирдлага",
    "keyboard": "гарын самбар",
    "cell phone": "гар утас",
    "microwave": "бичил долгионы зуух",
    "oven": "шарах шүүгээ",
    "toaster": "талх шарагч",
    "sink": "угаалтуур",
    "refrigerator": "хөргөгч",
    "book": "ном",
    "clock": "цаг",
    "vase": "ваар",
    "scissors": "хайч",
    "teddy bear": "бамбарууш",
    "hair drier": "үс хатаагч",
    "toothbrush": "шүдний сойз",
}

_pad = '_'
_punctuation = '!\'(),.:;? '
_special = '-'
# _letters = 'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЪЫЬЭЮЯабвгдеёжзийклмноөпрстуүфхцчшъыьэюя'
_letters = 'абвгдеёжзийклмноөпрстуүфхцчшъыьэюя'
_symbols = [_pad] + list(_special) + list(_punctuation) + list(_letters)
_symbol_to_id = {s: i for i, s in enumerate(_symbols)}
_whitespace_re = re.compile(r'\s+')
tts_session = {}
vocodeer_session = {}

# translator = Translator()
def _should_keep_symbol(s):
    # TODO: do i really need this?
    return s in _symbol_to_id and s != '_'


def _text_to_sequence(text):
    text = text.lower()
    text = re.sub(_whitespace_re, ' ', text)
    return [_symbol_to_id[s] for s in text if _should_keep_symbol(s)]


def _run_onnx(ort_session, input_vals):
    ort_inputs = {name.name: val for name, val in zip(ort_session.get_inputs(), input_vals)}
    ort_outs = ort_session.run(None, ort_inputs)
    return ort_outs[0]

def _save_wav(filename, samples, framerate=22050):
    with contextlib.closing(wave.open(filename, "wb")) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(samples.tobytes())

def getem(voice):
    if voice not in tts_session:
        tts_session[voice] = ort.InferenceSession(f'onnx_models/{voice}.onnx')
        vocodeer_session[voice] = ort.InferenceSession(f'onnx_models/{voice}_vocoder.onnx')
    return tts_session[voice], vocodeer_session[voice]

def synthesize(text, voice='female2', output='/tmp/output.wav'):
    text = text.lower().strip()

    if len(text) == 0:
        print("000")
        return

    if not any(c in _letters for c in text):
        print("monnone")
        return

    if text[-1] not in ['.', '?', '!']:
        text += '.'

    tts_onnx, vocoder_onnx = getem(voice)

    seq = _text_to_sequence(text)
    text_lengths = np.array([len(seq)], dtype=np.int64)
    seq = np.array([seq], dtype=np.int64)

    mel = _run_onnx(tts_onnx, [seq, text_lengths, np.array(1.0, dtype=np.float32)])
    audio = _run_onnx(vocoder_onnx, [mel])[0, 0, :]
    audio = (32767 * audio).astype(dtype=np.int16)

    _save_wav(output, audio)


@app.get("/")
def root():
    return {"message": "Hello, server is working"}

@app.post("/detect")
async def detect_this(file: UploadFile = File(...)):
#     vid_bytes =  await file.read()
#     vid = cv2.VideoCapture(BytesIO(vid_bytes))
#     detections = []
#     while vid.isOpened():
#         ret, frame = vid.read()
#         if not ret:
#             break
#         results = model(frame)
#         frame_detections = []
#         for result in results:
#             for box in result.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 cls_id = int(box.cls[0])
#                 conf = int(box.conf[0])
#                 frame_detections.append({
#                     "class": model.names[cls_id],
#                     "confidence": conf,
#                     "bbox": [x1, y1, x2, y2]
#                 })
#         detections.append(frame_detections)
#     return JSONResponse(content={"detections": detections})

    img_bytes = await file.read()
    detections = []
    nparr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = model(image)
    for result in results:
        for box in result.boxes:
            x1,y1,x2,y2 = map(int,box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = round(float(box.conf[0]), 2)
            detections.append({
                "class": model.names[cls_id],
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })
    return JSONResponse(content={"detections": detections})

@app.get("/voice")
# async def read_category_by_query(title: str):
#     role_to_return = None
#     for role in ENGINEER_ROLES:
#         if role.get('title').casefold() == title.casefold():
#             role_to_return = role
#     return role_to_return
async def aud(words: str):
    aud_to_return = None
    # aud_to_return = GoogleTranslator(source="auto", target="mn").translate(words)
    # aud_to_return = aud_to_return.text
    words = words.split()
    trans = []
    nums = []
    for word in words:
        if word.isdigit():
            nums.append(word)
            words.remove(word)

    for num, word in zip(nums, words):
    # print(num)
        num = num2words(num).replace("-", " ") 
        for k, v in dick.items():
            if word in k:
                trans.append(v)
            if " " in num and k in num:
                trans.append(v)
                print(num)
            elif " " not in num and num == k:
                trans.append(v)
    # print(trans[0])
    freq = Counter(trans)
    res = []
    for tran in trans:
        if freq[tran] > 0:
            res.append(tran)
            freq[tran] = 0

    aud_to_return = (" ".join(res))
    output = os.path.join(tempfile.gettempdir(), f"output{uuid.uuid4().hex}.wav")
    synthesize(aud_to_return, voice='female2', output=output)
    if not os.path.exists(output):
        return {"error": "synthesis failed"}
    return FileResponse(output, media_type="audio/wav", background=BackgroundTask(lambda: os.remove(output)))