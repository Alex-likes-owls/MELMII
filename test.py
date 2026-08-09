from collections import Counter
from num2words import num2words
dic = {
    "twenty": "хорь",
    "one": "нэг",
    "two":"хоёр",
    "three": "гурав",
    "four": "дөрөв",
    "fourteen": "арван дөрөв",
    "eleven": "арван нэг",
    "teddy bear": "бамбарууш",
    "hair drier": "үс хатаагч",
    "toothbrush": "шүдний сойз",
    "cell phone": "гар утас",
    "person": "хүн",
}
words = "21 person 14 teddy bear"
trans = []
words = words.split()
nums = []
for word in words:
    if word.isdigit():
        nums.append(word)
        words.remove(word)
        
# print(words, nums)
# n2w = []
# for num in nums:
#     num = num2words(num).replace("-", " ")
#     n2w.append(num)

# for num, word in zip(nums, words):
#     num = num2words(num).replace("-", " ")
#     print(num)
#     for k, v in dic.items():
#         if num == k or word in k:
#             trans.append(v)
for num, word in zip(nums, words):
    # print(num)
    num = num2words(num).replace("-", " ") 
    for k, v in dic.items():
        if word in k:
            trans.append(v)
        if " " in num and k in num:
            trans.append(v)
            print(num)
        elif " " not in num and num == k:
            trans.append(v)

# print(trans)

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
