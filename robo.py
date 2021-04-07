"""
Aksharkumar Patel
Alisher Komilov
CS4395.0W1
HW7 Chatbot Project
"""

#imports necessary
import sqlite3
import nltk
import string
from user import User
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import re
import random

#connection to the database
conn = sqlite3.connect('chatData.db')
c = conn.cursor()

#uncomment this for one time creation of a table if not created
#c.execute("""CREATE TABLE user(
#                name text,
#                age int,
#                likes text
#             );""")

#for testing process
#c.execute("INSERT INTO user VALUES ('Akshar', 23, 'NBA')")

#open the file with the knowledgebase
f = open('chat.txt', 'r', errors='ignore')
raw = f.read()
raw = raw.lower()  #lowercase
sent_tokens = nltk.sent_tokenize(raw)  #list of sentences tokens
word_tokens = nltk.word_tokenize(raw)  #list of words tokens

sent_tokens[:2]
word_tokens[:5]

lemmer = nltk.stem.WordNetLemmatizer()
stopwords = stopwords.words('english')
stemmer = SnowballStemmer("english")

#helper
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]


remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

#method to lematize the text 
def LemNormalize(text):
    lemmed_tokens = LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
    stems = [stemmer.stem(t) for t in lemmed_tokens if t not in stopwords]
    return stems


#list for greetings to be used by the bot
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]


#greetings method to return a greeting if user use it
def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

#imports for tfid and cosine similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


#response generating method
def response(user_response):
    print("Responding...")
    Bot_response = ''
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if (req_tfidf == 0):
        Bot_response = Bot_response + "Sorry! Not able to understand you!"
        return Bot_response
    else:
        Bot_response = Bot_response + sent_tokens[idx]
        return Bot_response

#database functions
def insert_user(u):
    with conn:
        c.execute("INSERT INTO user VALUES(:name, :age, :likes)", {'name':u.name, 'age':u.age, 'likes':u.likes})

def get_userLikes_by_name(name):
    c.execute("SELECT likes FROM user WHERE name=:name", {'name':name})
    return c.fetchone()

def get_user_by_name(name):
    c.execute("SELECT * FROM user WHERE name=:name", {'name':name})
    return c.fetchall()
    
def delete_user(name):
    with conn:
        c.execute("DELETE from user WHERE name= :name", {'name':name})

def update_user_likes(name, likes):
    with conn:
        c.execute("""UPDATE user SET likes= :likes
                    WHERE name= :name""",
                  {'name':name, 'likes': likes})

#method to add user to database if not there
def addUser():
    print("Enter User Name:")
    name = input().upper()
    
    print("Enter User Age:")
    age = input()

    u = User(name, age,'')
    insert_user(u)
    print("User Added!")

#finding user
def findUser():
    print("Enter your name: ")
    user_response = input().upper()
    name = get_user_by_name(user_response)
        #if user does not exist enter another name or add user
    if(name ==[]):
        print("User not found!")
        print("Enter N to create new user!")
        print("Enter R to enter another name!")
        resp = input().upper()
        if(resp =='R'):
            findUser()
        elif(resp =='N'):
            addUser()
        else:
            print("False Input!")
            findUser()
    else:
        print("Hi, ",user_response)       #if user exists ask what they need answered
        print("We talked about this last time: ")
        likes = get_userLikes_by_name(user_response)
        result = str(likes)
        sentence = nltk.word_tokenize(result)
        res = [word.lower() for word in sentence if re.match('^[a-zA-Z]+', word)] 
          
        r = [t for t in res if t not in stopwords]
        a = list(set(r))
        print(a[0])
        print(a)
        f = True
        while(f == True):
            print("Enter Y to know more about it, R to pick a random like, or N to continue.")
            user_in = input()
            if(user_in.upper() == 'Y'):
                print(response(a[0]))
                f = False
            elif(user_in.upper() == 'R'):
                print("Bot: ")
                choice = random.choice(a)
                sent_tokens.append(choice)
                print(response(choice))
                print("\n")
                f = False
            elif(user_in.upper() == 'N'):
                f = False
                return user_response
            else:
                print("Invalid Option!")
                
    return user_response

#start here         
flag = True
print("Bot: My name is Bot. Who am I talking to today? If you want to exit, type Bye!")
user = findUser()

#main communication and updating the likes in the database
while (flag == True):
    print("You: ")
    user_response = input()
    user_response = user_response.lower()
    #if bye then end the chat 
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
                likes = get_userLikes_by_name(user)
                update_user_likes(user.upper(), str(likes)+(user_response))   #for testing purpose
                sent_tokens.remove(user_response)
    else:
        flag = False
        print("Bot: Bye! Have a great day!")

conn.close()
