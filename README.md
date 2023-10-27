# DALL-E 3 HTTP

Here is the source code for a discord bot that requests image generations from DALL-E 3 via Microsoft Image Creator frontend via HTTP requests using your account cookie, it operates by reading a few files:
"cookies_U_owners.json" <--- the file which has your _U cookie pool
"credentials.txt" <--- the file which has your discord token

Then, it will listen for command ">dalle3 <prompt>" in a channel ID you specify. In test.py this channel ID is 123123123, you need to change this (right-click channel and copy ID). For image generation process, here are the sequential steps:

1) retrieve cookie from pool: choose random cookie from pool of cookies in cookies_U_owners.json file. It checks if cookie is blocked recently and not choose those one.

2) check token balance on this cookie, make a HTTP GET request and parse results for token balance.

3) if token balance == 0, then set "rt" header == "3" for non-token generation request. If have token balance > 0, set "rt" : "4" to use token (fast generation)

4) send POST request to URL which stimulates the image generation request. Parse this POST response for eventID.

4a) if not eventID in image generation initial POST, can be: acc issue, prompt blocked. So parse response content for causal and try to handle these cases, and failsafe for no eventID is to assume cookie bad and put 12h timeout on cookie.

5) extract eventID and IG values from initial POST response, then send GET request to different endpoint using these values injected appropriately to check status of URLs status page. The page gives blank content if pending or image URLs when done. ping this every 2s until result or timeout.

6) parse image IDs from successful GET ping, then append these IDs to base image hosting URL. These formatted URLs are available for public sharing or download (anyone can see the images if they have these IDs).

7) for this discord bot, it downloads and sends image data, but you could just handle URLs if you want

# Note: Account Cookie Required

To get your account cookie, login to your microsoft account and go to Bing Image Creator page. Right-click inspect, go to Storage tab, click into bing.com cookies, then find "_U" cookie, and copy value.
