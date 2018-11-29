import discord
import urllib.request
import json
from discord.ext import commands


#Bot Information
bot = discord.Client()
botToken = "Put your token here."
places_input = ["show", "places"]

#Google Places Api Information
apiKey = "AIzaSyAu107Z8Uys2Fo9jTTS5VHcxkpLmAQgJR4"
jsonUrl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
jsonUrlDetails = "https://maps.googleapis.com/maps/api/place/details/json?"

#Bot online
@bot.event
async def on_ready():
    print("bot is ready to roll")

@bot.event
async def on_message(message):

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

async def on_message(message):
    """Main function"""
    for word in places_input:
        if word in message.content:
            await places(message)



bot.run(botToken)
