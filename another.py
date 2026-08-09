from collections import Counter
from num2words import num2words
dic = {
    "one": "нэг",
    "two":"хоёр",
    "three": "гурав",
    "four": "дөрөв",
    "twenty": "хорь",
    "eleven": "арван нэг",
    "teddy bear": "бамбарууш",
    "hair drier": "үс хатаагч",
    "toothbrush": "шүдний сойз",
    "cell phone": "гар утас",
    "person": "хүн",
}
words = "21 person 4 teddy bear"
trans = []
words = words.split()
nums = []
for word in words:
    if word.isdigit():
        nums.append(word)
        words.remove(word)
        
print(words, nums)
n2w = []
for num in nums:
    num = num2words(num).replace("-", " ")
    n2w.append(num)

n2w = " ".join(n2w).split()
print(n2w)

for num, word in zip(n2w, words):
    for k, v in dic.items():
        if num == k or word in k:
            trans.append(v)

freq = Counter(trans)
res = []
for tran in trans:
    if freq[tran] > 0:
        res.append(tran)
        freq[tran] = 0

print(res)
print(" ".join(res))


#One I used with cardinal:
# for k, v in dic.items():
#     if k in words:
#         print(v)
# trans = []
# words = words.split()
# for word in words:
#     for k, v in dic.items():
#         if word in k:
#             trans.append(v)
# print(trans[0])
# freq = Counter(trans)
# res = []
# print(freq["нэг"])
# for tran in trans:
#     if freq[tran] > 0:
#         res.append(tran)
#         freq[tran] = 0

# print(res)
# print(" ".join(res))
