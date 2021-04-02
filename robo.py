import nltk
import numpy as np
import random
import string
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

f = open('chat.txt', 'r', errors='ignore')
raw = f.read()
raw = raw.lower()  # lowercase
sent_tokens = nltk.sent_tokenize(raw)  # list of sentences
word_tokens = nltk.word_tokenize(raw)  # list of words

sent_tokens[:2]
word_tokens[:5]

lemmer = nltk.stem.WordNetLemmatizer()
stopwords = stopwords.words('english')
stemmer = SnowballStemmer("english")

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]


remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)


def LemNormalize(text):
    lemmed_tokens = LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
    stems = [stemmer.stem(t) for t in lemmed_tokens if t not in stopwords]
    return stems



GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
USERS = ["akshar", "alisher"]

AKSHAR = ["Akshar"]
ALISHER = ["Alisher"]


# greetings check
def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def user(sentence):
    for word in sentence.split():
        if word.lower() == "akshar":
            return AKSHAR[0]
        elif word.lower() == "alisher":
            return ALISHER[0]


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Response generation
def response(user_response):
    Bot_response = ''
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if (req_tfidf == 0):
        Bot_response = Bot_response + "I am sorry! I don't understand you"
        return Bot_response
    else:
        Bot_response = Bot_response + sent_tokens[idx]
        return Bot_response


flag = True
print("Bot: My name is Bot. Who am I talking to today? If you want to exit, type Bye!")
u = 0
while (u == 0):
    user_response = input()
    if (user(user_response) == "Akshar"):
        u = 1
        print("Bot: Hi, " + user(user_response))
    elif (user(user_response) == "Alisher"):
        u = 2
        print("Bot: Hi, " + user(user_response))
    else:
        print("User not found!")
        print("Enter another name:")

while (flag == True):
    print("You: ")
    user_response = input()
    user_response = user_response.lower()
    if (user_response != 'bye'):
        if (user_response == 'thanks' or user_response == 'thank you'):
            flag = False
            print("Bot: You are welcome..")
        else:
            if (greeting(user_response) != None):
                print("Bot: " + greeting(user_response))
                print("What can I answer for you?")
            else:
                sent_tokens.append(user_response)
                word_tokens = word_tokens + nltk.word_tokenize(user_response)
                final_words = list(set(word_tokens))
                print("Bot: ", end="")
                print(response(user_response))
                sent_tokens.remove(user_response)
                if (u == 1):
                    AKSHAR.append(response(user_response))
                elif (u == 2):
                    ALISHER.append(response(user_response))
    else:
        flag = False
        print("Bot: Bye! take care..")