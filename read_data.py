import requests
import json
import media_objects as mo
from Key1 import USER_TOKEN

PAGE_ID = "229568753577594"

def getUser():
    
    url = f"https://graph.facebook.com/v19.0/me?fields=id,name&access_token={USER_TOKEN}"
    
    response = requests.request("GET", url)
    
    data = json.loads(response.text)

    return data

def getPages(user):
    url = f"https://graph.facebook.com/v19.0/{user.id}/accounts?access_token={USER_TOKEN}"
    response = requests.request("GET", url)
    data = json.loads(response.text)
    pages = data["data"]
    
    return pages

    
def getPostsFromPage(page):
    
    url = f"https://graph.facebook.com/v19.0/{page.id}/feed?access_token={page.token}"

    response = requests.request("GET", url)

    data = json.loads(response.text)

    posts = data['data']
    
    return posts
        

def getCommentsFromPost(page, post):
    
    url = f"https://graph.facebook.com/v19.0/{post.id}/comments?access_token={page.token}"

    response = requests.request("GET", url);

    data = json.loads(response.text)

    comment_data = data['data']

    return comment_data

def getReactions(page, object):

    url_love = f"https://graph.facebook.com/{object.id}?fields=reactions.type(LOVE).limit(0).summary(total_count)&access_token={page.token}"
    url_like = f"https://graph.facebook.com/{object.id}?fields=reactions.type(LIKE).limit(0).summary(total_count)&access_token={page.token}"
    url_wow = f"https://graph.facebook.com/{object.id}?fields=reactions.type(WOW).limit(0).summary(total_count)&access_token={page.token}"
    url_haha = f"https://graph.facebook.com/{object.id}?fields=reactions.type(HAHA).limit(0).summary(total_count)&access_token={page.token}"
    url_haha = f"https://graph.facebook.com/{object.id}?fields=reactions.type(SAD).limit(0).summary(total_count)&access_token={page.token}"
    url_angry = f"https://graph.facebook.com/{object.id}?fields=reactions.type(ANGRY).limit(0).summary(total_count)&access_token={page.token}"

    urls = [url_love, url_like, url_wow, url_haha, url_angry]
    reaction_dict = {"love": 0, "like": 0, "wow": 0, "haha": 0, "sad": 0, "angry": 0}

    for url in urls:
        response = requests.request("GET", url);
        data = json.loads(response.text)
        count = data['reactions']['summary']['total_count']

        if "LOVE" in url:
            reaction_dict["love"] = count
        elif "LIKE" in url:
            reaction_dict["like"] = count
        elif "WOW" in url:
            reaction_dict["wow"] = count
        elif "HAHA" in url:
            reaction_dict["haha"] = count
        elif "SAD" in url:
            reaction_dict["sad"] = count
        elif "ANGRY" in url:
            reaction_dict["angry"] = count
    
    return reaction_dict

def getPagePhoto(page):

    page_photo_url = f"https://graph.facebook.com/v19.0/{page.id}/photos?access_token={page.token}"  

    response = requests.request("GET", page_photo_url);

    page_photo_data = json.loads(response.text)
    photo_id = page_photo_data['data'][0]['id']

    photo_url = f"https://graph.facebook.com/v19.0/{photo_id}/picture?access_token={page.token}"
    response = requests.request("GET", photo_url);

    with open(page.photo_path, 'wb') as f:
        f.write(response.content)
    
    return response

def user_init():
    print("Initializing User...")
    user_data = getUser()
    user = mo.User(user_data['id'], user_data['name'], USER_TOKEN)
    user.pages = page_init(user)
    
    return user

def page_init(user):
    user_pages = getPages(user)
    pages = []
    for i in range(0, len(user_pages)):
        page = user_pages[i]
        pages.append(mo.Page(page['id'], page['name'], page['access_token']))
        page = pages[i]
        print("Initializing {}...".format(page.name))
        page.photo_path = f"./photos/photo{i}.jpg"
        page.posts = posts_init(page)
    
    return pages

def posts_init(page):
    page_posts = getPostsFromPage(page)
    posts = []
    for i in range(0, len(page_posts)):
        post = page_posts[i]
        try:
            posts.append(mo.Post(post['id'], post['message']))
        except KeyError:
            posts.append(None)
        if (posts[i]):
            post = posts[i]
            posts[i].reactions = getReactions(page, post)
            posts[i].comments = comments_init(page, post)
    
    return posts
    

def comments_init(page, post):
    post_comments = getCommentsFromPost(page, post)

    comments = []
    for i in range(0, len(post_comments)):
        comment = post_comments[i]
        comments.append(mo.Comment(comment['id'], comment['message']))
        comment = comments[i]
        comments[i].reactions = getReactions(page, comment)
    
    return comments