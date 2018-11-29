import discord, asyncio, random, requests, urllib.request, json, fuzzywuzzy, re
from discord.ext import commands
from discord.ext.commands import Bot
from googletrans import Translator, LANGUAGES
from chatterbot import ChatBot

#Defining Constants
bot = commands.Bot(command_prefix="!")
translator = Translator()
chatterbot = ChatBot("Koneko",
input_adapter = 'chatterbot.input.VariableInputTypeAdapter',
output_adapter ='chatterbot.output.OutputAdapter',
output_format="text",
database ='./Database.sqlite3')
TOKEN = "Add your token here."
translator_input = ["translate", "translator", "say"]
weather_input = ["weather"]
places_input = []
cat_input = ["cat", "cats", "neko", "kitten", "pussy"]
places_input = ["show", "places"]
directions_input = ["directions", "way", "path"]
dictionary_input = ["definition", "define"]
removal_list = ["," , "?", "!", ".", "to", "please", "in", " "]
function_list = []
#Weather
weather = "http://api.openweathermap.org/data/2.5/weather?appid=3df6497e52093d1235bb39591514913c&q="
googleMaps = 'AIzaSyAVOc0sbhcT5aSFmDshPka9f20dIy_TMNc'
#Places
apiKey = "AIzaSyAu107Z8Uys2Fo9jTTS5VHcxkpLmAQgJR4"
jsonUrl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
jsonUrlDetails = "https://maps.googleapis.com/maps/api/place/details/json?"
#Cat
cat_api_url = "https://api.thecatapi.com/v1/images/search?size=full&mime_types=jpg,png,gif&format=json&order=RANDOM&page=0&limit=1"
catfact_api_url = "https://cat-fact.herokuapp.com/facts"
#Dictionary
app_id ='7e4be9f6'
app_key ='fc87aebac9c9f6396cb8ec2922037763'
#Directions
key = 'AIzaSyAVOc0sbhcT5aSFmDshPka9f20dIy_TMNc'
TAG_RE = re.compile(r'<[^>]+>')
#### PROFANITY DECRYPTOR ####
m = open("encrypted_list.txt","r")
readEncrypted = m.read()
m.close()
splitEncrypted = readEncrypted.split("\n")
decrypted_list = []
decrypted_text = ""
for c in splitEncrypted:
    for c1 in c:       
        x = ord(c1)
        x = x - 1
        c2 = chr(x)
        decrypted_text = decrypted_text + c2
    decrypted_list.append(decrypted_text)
    decrypted_text = ""

#Defining Functions
@bot.event
async def on_ready():
    print("Online!")

async def translating(message):
    """Translates a specific part of the user input, indicated by "'". """
    if len(function_list) != 0:
        return
    user_input = message.content.lower()
    separate = user_input.split("'")
    if len(separate) == 3:
        sentence = separate[1]
        language = separate[2]
        for character in removal_list:
            language = language.replace(character, "")
            language = language.strip()
        for key in LANGUAGES: #a dictionary with all the languages the module supports (en:english, fr:french...)
            if LANGUAGES[key] == language:
                language = key
        result = translator.translate(sentence, dest=language, src="auto")
        await bot.send_message(message.channel, result.text)
        function_list.append("called")
        return True
    else:
        await bot.send_message(message.channel, "Specify what you want me to translate with a quotation :).")   
        await bot.send_message(message.channel, "Ex.: Can you translate 'how are you?' to french?")
        function_list.append("called")

async def chat(message):
    """Chatterbot module function"""
    response = chatterbot.get_response(message.content)
    response = str(response)
    wordsList = response.split(" ")
    for i in range(len(wordsList)):
        if wordsList[i] in decrypted_list:
            wordsList[i] = "%$@:!"
    response = " ".join(wordsList)  
    await bot.send_message(message.channel, response)

async def cat(message):
    """Outputs a cat fact along with a cat image"""
    if len(function_list) != 0:
        return
    data_list = requests.get(cat_api_url).json()
    data_dict = data_list[0]
    image = data_dict["url"]
    data_list = requests.get(catfact_api_url).json()["all"]
    data_dict = data_list[random.randint(0, len(data_list))]
    fact = data_dict["text"]
    await bot.send_message(message.channel, (fact + "\n" + image))
    function_list.append("called")
    return True

async def weatherer(message):
    if len(function_list) != 0:
        return
    user_input = message.content
    weather = "http://api.openweathermap.org/data/2.5/weather?appid=3df6497e52093d1235bb39591514913c&q="
    wordlist = user_input.split()
    city = wordlist[-1]
    for character in removal_list:
        if character in city:
            city = city.replace(character, "")
            city = city.strip()
    url = (weather)+(city)
    data = requests.get(url).json()
    weatherDesc = data["weather"][0]["main"]
    temperature = round(float(data["main"]["temp"] - (273.15)),1)
    weatherWriting = "The weather is "
    temperatureWriting = "The temperature is "
    await bot.send_message(message.channel, (str(weatherWriting) + (weatherDesc) + " in " + str(city)))
    await bot.send_message(message.channel, (str(temperatureWriting) + str(temperature) + "°C"))
    function_list.append("called")
    return True

async def places(message):
    if len(function_list) != 0:
        return
    #message from user
    message1 = message.content.lower()
    separated_list = message1.split()
    #we assume the last 3 words of setence is "place in location"
    location = separated_list[-3]
    type = separated_list[-1]
    #formats the words to be read in the url
    typeC = type.replace(" ", "+")
    locationC = location.replace(" ", "+")
    #creates the first url to get place id
    urlAdd1 = 'query={}+in+{}&key={}'.format(typeC,locationC,apiKey) #it's what we're going to add to json url
    url1 = jsonUrl + urlAdd1
    data1 = urllib.request.urlopen(url1).read().decode('utf-8')
    jsonDict = json.loads(data1) #Turns the json file into a dictionary that can be used
    #getting the place_id from jsonUrl
    placeIDList = []
    n = len(jsonDict["results"])
    for size in range(n):
        #sorts out the places_id
        placeID = jsonDict["results"][size]["place_id"]
        placeIDList.insert(-1, placeID)
    #grabs the place id, to form an url
    for pID in placeIDList:
        #second url
        urlAdd2 = 'placeid={}&fields=name,website,rating,opening_hours,formatted_address,formatted_phone_number&key={}'.format(pID,apiKey)
        url2 = jsonUrlDetails + urlAdd2
        data2 = urllib.request.urlopen(url2).read().decode('utf-8')
        jsonDict2 = json.loads(data2)
        results = jsonDict2["result"]
        if results == None:
            await bot.send_message(message.author, "Sorry, I couldn't find any results for your search!")
            function_list.append("called")
        else:
            #creating variables of all the info we need
            name = results.get("name")
            address = results.get("formatted_address")
            phone_number = results.get("formatted_phone_number")
            website = results.get("website")
            rating = results.get("rating")
            #getting if the restaurant is open or not
            openNow = jsonDict2['result']['opening_hours']['open_now']
            if openNow == True:
                openNow = "Yes"
            elif openNow == False:
                openNow = "No"
            else:
                pass
            openingHours = "\n".join(jsonDict2['result']['opening_hours']['weekday_text'])
            msg_results = "--------" + "\nName: " + str(name) + "\nAddress: " + str(address) \
            + "\nPhone Number: " + str(phone_number) + "\nWebsite: " + str(website) \
            + "\nRating: " + str(rating) +"\nIs it open? " + str(openNow) \
            + "\nOpening hours:\n" + str(openingHours)
            await bot.send_message(message.author, msg_results)
            function_list.append("called")
            return True

async def dictionary(message):
    if len(function_list) != 0:
        return
    word_id = message.content.split(" ")[-1]
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/en' + '/' + word_id.lower()
    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
    data = json.loads(r.text)
    definitions = ''.join(data["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"])
    try:
        etymo = ''.join(data["results"][0]["lexicalEntries"][0]["entries"][0]["etymologies"][0])
        await bot.send_message(message.channel, etymo)
    except:
        print("Word has no history")
    await bot.send_message(message.channel,"The definition is: "  + definitions)
    await bot.send_message(message.channel, (data["results"][0]["lexicalEntries"][0]["entries"][0]["grammaticalFeatures"][0]["text"]))
    function_list.append("called")


async def directionsreece(message):
    #we assume the format is - directions from (location) to (location)
    if len(function_list) != 0:
        return
    wordList = message.content.split(" ")
    fromindex = wordList.index("from")
    toindex = wordList.index("to")
    start = wordList[fromindex+1:toindex]
    start = ' '.join(start)
    end = wordList[(toindex+1):(len(wordList)+1)]
    end = ' '.join(end)
    directions  = 'https://maps.googleapis.com/maps/api/directions/json?origin='+start+'&destination='+end+'&key='
    url = directions+key
    data = requests.get(url).json()
    routes = data['routes'][0]
    travelInfo = routes['legs']
    steps = travelInfo[0]['steps']
    distance  = travelInfo[0]['distance']
    duration = travelInfo[0]['duration']
    distance1 = distance['text']
    duration1 = duration['text']
    for i in range(len(steps)):
        followme = (steps[i]['html_instructions'])
        followme = TAG_RE.sub('',followme)
        await bot.send_message(message.channel, "Directions: " + followme)
    await bot.send_message(message.channel, "The distance is: " + distance1)
    await bot.send_message(message.channel, "The duration is: +" + duration1)
    function_list.append("called")


@bot.event#(pass_context=True)
async def on_message(message):
    """Main function"""
    #Prevents the chatbot from taking its own messages as input.
    if message.author.bot is True:
        return
    for word in message.content.split(" ") : 
        if word in decrypted_list:
            await bot.send_message(message.channel, "Whoopsie daisy, you shouldn't say such profanities. Have a cat instead ! ")
            await cat(message)
            return
    for word in translator_input:
        if word in message.content:
            await translating(message)
    for word in cat_input:
        if word in message.content:
            await cat(message)
    for word in weather_input:
        if word in message.content:
            await weatherer(message)
    for word in places_input:
        if word in message.content:
            await places(message)
    for word in directions_input:
        if word in message.content:
            await directionsreece(message)
    for word in dictionary_input:
        if word in message.content:
            await dictionary(message)
    if len(function_list) == 0:
        await chat(message)
    else:
        function_list.remove("called")


bot.run(TOKEN) #Change the ^variable^ to your token