#This script assigns a flair class to all users with an un-classed flair. This is necessary because PlusBot freely overwrites un-flaired and un-classed users.

import praw
r=praw.Reddit('PlusBot flair class assignment')

r.login(input('username: '),input('password: '))

subreddit = r.get_subreddit(input('subreddit: '))

#get flair list
flairlist = r.get_flair_list(subreddit, limit=None)

#this is important enough that it's worth protecting against a typo
new_class = input('New CSS class (no spaces allowed):')
if " " in new_class:
    raise ValueError("new class cannot contain whitespace")      


new_flairs = []

#iterate through flair list and look for users with un-classed flair
for flair in flairlist:

    new_flair = flair
    
    if flair['flair_css_class']==None:
        new_flair['flair_css_class']=new_class
        new_flairs.append(new_flair)

#Set new flairs
r.set_flair_csv(subreddit, new_flairs)

#Ensure that userflairs are enabled and displayed and that users can reset their flair to their points
r.add_flair_template(subreddit, text = "Score (comment anywhere)", css_class = "reset")

