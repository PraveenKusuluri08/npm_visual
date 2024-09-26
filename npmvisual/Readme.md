# Brainstorming and notes

Just jotting things down to help think about how I organize things.

This app is mostly functional. We should write as much as possible with pure virtual functions. 

Cache copies of package.json files are saved in the packages directory


# Production and Multithreading
Our application has some rather large db requests and web scraping capabilities. This means Multithreding will be important in the long run. 
Read this when we get a bit farther. We will probably want multithreading and wsgi may not be sufficient:
https://tonybaloney.github.io/posts/fine-tuning-wsgi-and-asgi-applications.html
switching to quart should be fast

we should use Gunicorn for now with a nginx proxy. Switch to asgi later. 

