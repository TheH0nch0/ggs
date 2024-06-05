from flask import Flask, render_template, current_app
import requests
import logging

app = Flask(__name__)
app.config['DEBUG'] = True

def get_meme(attempts=5):
    urls = [
        "https://meme-api.com/gimme",
        "https://some-other-meme-api.com/random"
    ]

    for attempt in range(attempts):
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                app.logger.info(f"API Response from {url}: {data}")

                subreddit = data.get("subreddit", "unknown")
                meme_large = data.get("preview", [""])[-2] if url == "https://meme-api.com/gimme" else data.get("url")

                if meme_large:
                    return meme_large, subreddit

            except requests.Timeout:
                app.logger.error(f"Request timed out for {url}")
            except requests.RequestException as e:
                app.logger.error(f"Request failed for {url}: {e}")
            except (KeyError, IndexError) as e:
                app.logger.error(f"Error processing response from {url}: {e}")

    app.logger.warning("Reached maximum attempts for getting a meme")
    return None, None

@app.route("/")
def index():
    app.logger.info(f"Template folder: {current_app.template_folder}")
    meme_pic, subreddit = get_meme()
    if meme_pic and subreddit:
        return render_template("index.html", meme_pic=meme_pic, subreddit=subreddit)
    else:
        return render_template("error.html"), 500
    
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000)
