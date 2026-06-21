# Youtube-Video-Roulette
A simple piece of software that generates random YouTube videos for you. You can also see previous videos you've gotten from this program (PS : I made this project a few months ago, there might be small vunerabilities in this program)

Additional information :
Drive D is required to record videos you've gotten from this program (Without Drive D, the program would crash because there's no option to disable Video History in this program, will fix this in a second version)
Entirely written in Python (Pygame for UI)

How to setup :
On line 92, change the variable's value to your API key (in string value)

## How to get API key :
Open google cloud console and create a new project

Select your project and head to "APIs & Services" in Quick Access (bottom part of the page)

Once you opened the API Library, search for "Youtube Data API v3" then click on "Enable"

Head to "Credentials" page then click on "Create Credentials" then "API Key"

Copy and paste your API key into the variable in line 87
