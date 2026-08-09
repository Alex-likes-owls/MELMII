from fastapi import FastAPI
from fastapi.responses import FileResponse
import contextlib
import numpy as np
import re
import os
import wave
import onnxruntime as ort
# from googletrans import Translator
from deep_translator import GoogleTranslator

_pad = '_'
_punctuation = '!\'(),.:;? '
_special = '-'
# _letters = 'АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЪЫЬЭЮЯабвгдеёжзийклмноөпрстуүфхцчшъыьэюя'
_letters = 'абвгдеёжзийклмноөпрстуүфхцчшъыьэюя'
_symbols = [_pad] + list(_special) + list(_punctuation) + list(_letters)
_symbol_to_id = {s: i for i, s in enumerate(_symbols)}
_whitespace_re = re.compile(r'\s+')

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

    tts_onnx = ort.InferenceSession(f'onnx_models/{voice}.onnx')
    vocoder_onnx = ort.InferenceSession(f'onnx_models/{voice}_vocoder.onnx')
    seq = _text_to_sequence(text)
    text_lengths = np.array([len(seq)], dtype=np.int64)
    seq = np.array([seq], dtype=np.int64)

    mel = _run_onnx(tts_onnx, [seq, text_lengths, np.array(1.0, dtype=np.float32)])
    audio = _run_onnx(vocoder_onnx, [mel])[0, 0, :]
    audio = (32767 * audio).astype(dtype=np.int16)

    _save_wav(output, audio)
    # print(f"aud: {output}")

    # display(Audio(output, autoplay=True))

# Create FastAPI instance with custom docs
app = FastAPI(docs_url="/api/py/docs",
              openapi_url="/api/py/openapi.json",
              redoc_url="/api/py/redoc")


@app.get("/api/py/engineer-roles")
# async def read_category_by_query(title: str):
#     role_to_return = None
#     for role in ENGINEER_ROLES:
#         if role.get('title').casefold() == title.casefold():
#             role_to_return = role
#     return role_to_return
async def aud(words: str):
    aud_to_return = None
    aud_to_return = GoogleTranslator(source="auto", target="mn").translate(words)
    # aud_to_return = aud_to_return.text
    synthesize(aud_to_return, voice='female2', output='/tmp/output.wav')
    if not os.path.exists('/tmp/output.wav'):
        return {"error": "synthesis failed"}
    return FileResponse("/tmp/output.wav", media_type="audio/wav")
