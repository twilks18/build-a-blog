import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                                                autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class PostIt(db.Model):
    title = db.StringProperty(required = True)
    posts = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



class MainHandler(Handler):
    def render_mainblog(self, title="", posts=""):
        posted = db.GqlQuery("SELECT * FROM PostIt ORDER BY created DESC LIMIT 5")

        self.render("mainblog.html", title=title, posts=posts,posted=posted)

    def get(self):
        self.render_mainblog()



class NewPosts(Handler):
    #copied from above
    def render_newpost(self, title="", posts="",error=""):


        self.render("newpost.html",title=title,posts=posts, error=error)

    def get(self):
        self.render_newpost()


    def post(self):
        title = self.request.get('title')
        post = self.request.get('posts')

        if title and post:

            p = PostIt(title=title, posts=post)
            p.put()

            #look up the id
            id = p.key().id()

            self.redirect("/blog/%s" % id)

        else:
            error='Please enter both a Title and Post'
            self.render_newpost(title, post, error)

class ViewPostHandler(webapp2.RequestHandler):

    def get(self,id):

        post_id = PostIt.get_by_id (int(id))

        postings = jinja_env.get_template("singleposts.html")
        posted = postings.render(post=post_id)

        self.response.out.write(posted)








app = webapp2.WSGIApplication([
    ('/blog', MainHandler),('/newposts', NewPosts),webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
