Hello, this a instagram user scraper usin https://gramsnap.com/en/, and using its Api to asynchronusly gather intagram user information. 

**Use case**

The gathered information can be use for user engagement analisis, emailing or messagings prospects, and business market analisis. 


***Why not use selenium?***

On previous versions using selenium, it would take way too long for gathering the user information, nevermind the the many lines of code to automate the interaction with the website.

The information displayed on the site was very limited. However while using the api, I was able to see much more information such as email, phone number, business category, location and much more.

**Future**

If you vited the website and made a query, they also give an option to download images, reels and stories. There is an API for them, I just haven't found an use for my particular project. I will eventually implement this in code, for further user analisis.

**Notes**

You will need to have a list of intagram usernames, I used Bardeen to quickly automate this process, but eventually I will add this to the project as well. 

When making requests, I found effective to add a wait 5 seconds betweeen requests, as any faster than that would overwhelm the server. (Feel free to test for your self)

By default I only parse certain informaton I'm interested in, but you're welcome to inspect the api response and gather other infomration you see fit to your project.

I build this project with my up to date knoledge of python and webscraping skills. I'm open to any improvements that could be made to the scraper.

Feel free to message me about any questions you may have!.
