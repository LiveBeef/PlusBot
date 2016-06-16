import praw
from collections import deque
import re
import json
import os

#Set globals
r=praw.Reddit("/r/AutoModerator Contribution Bot")
sub = r.get_subreddit("AutoModerator")


class Bot():

    def __init__(self):

        #login
        r.login('PlusBot',os.environ.get('password'))

        #store up to 100 link/author pairs
        self.link_authors = deque([],maxlen=100)

        #get cache of authors and links awarded
        self.author_points = json.loads(r.get_wiki_page(sub,"plusbot").content_md)

    def run(self):
        self.scan_comments()

    def get_OP(self, link_id):

        #first check cache for if we already have this name
        for entry in self.link_authors:
            if entry[0]==link_id:
                return entry[1]
                break

        #then fetch and add it
        else:
            link = r.get_info(thing_id=link_id)
            author = link.author
            if author is None:
                self.link_authors.append((link_id,None))
                return None
            else:
                self.link_authors.append((link_id,author.name))
                return author.name

        

    def scan_comments(self):

        for comment in praw.helpers.comment_stream(r, "AutoModerator", limit=100, verbosity=0):

            #if comment isn't by OP then we're not interested
            op = self.get_OP(comment.link_id)
            if comment.author.name != op:
                continue

            #if comment doesn't start with a + character then we're not interested
            if not comment.body.startswith("+"):
                continue

            #if comment is top level then we're not interested
            if comment.parent_id == comment.link_id:
                continue

            #get parent comment author
            parent_comment = r.get_info(thing_id = comment.parent_id)

            #make sure user exists
            if parent_comment.author is None:
                continue

            #make sure they are different people
            if parent_comment.author.name == comment.author.name:
                continue

            #add user and link to authorpoints
            if parent_comment.author.name not in self.author_points:
                self.author_points[parent_comment.author.name]=[]

            self.author_points[parent_comment.author.name].append(comment.link_id)

            #get new score and flair text
            score = len(self.author_points[parent_comment.author.name])
            text = "+"+str(score)

            #fetch user flair
            flair = r.get_flair(sub,parent_comment.author)

            #if user has special flair, preserve it and the text. Otherwise set flair class by score.
            if "contributor" in flair['flair_css_class']:
                text = "Contributor "+text
            elif "regexninja" in flair['flair_css_class']:
                text = "Regex Ninja "+text
            elif "sorcerer" in flair['flair_css_class']:
                text = "Open Sorcerer "+text
            elif "user" in flair["flair_css_class"]:
                #certain unique flairs are passed on
                text = flair['flair_text']
            elif "plain" in flair["flair_css_class"]:
                text = flair['flair_text']
            else:
                #set flair class by score
                flair["flair_css_class"] = "score-t1"
                if score >=3:
                    flair["flair_css_class"] = "score-t2"
                if score >=10:
                    flair["flair_css_class"] = "score-t3"
                if score >=30:
                    flair["flair_css_class"] = "score-t4"

            #set new flair text and save to reddit
            flair['flair_text']=text
            r.set_flair_csv(sub,flair)

            #save new authorpoints to wiki
            reason = parent_comment.author.name+" "+comment.link_id+" "+text
            r.edit_wiki_page(sub,"plusbot",json.dumps(self.author_points),reason=reason)

            

            





if __name__=="__main__":
    bot=Bot()
    bot.run()
