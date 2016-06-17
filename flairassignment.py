#This script assigns a flair class to all users with an un-classed flair. This is necessary because PlusBot freely overwrites un-flaired and un-classed users.

import praw
r=praw.Reddit('PlusBot flair class assignment')

r.login(input('username: '),input('password: '))
print('Log-in Successful')

subreddit = r.get_subreddit(input('subreddit: '))

print('retrieving flair list...')
try:
      flairlist = r.get_flair_list(subreddit)

except:
      print('something went wrong')
      raise ValueError('subreddit must be one where you have +flair mod permissions')

print('...done')
new_class = input('New CSS class (no spaces allowed):')

if " " in new_class:
    raise ValueError("new class cannot contain whitespace")      


new_flairs = []

print('Looking through flairs...')
for flair in flairlist:

    new_flair = flair
    
    if flair['flair_css_class']==None:
        new_flair['flair_css_class']=new_class
        new_flairs.append(new_flair)

print('...done')
print('Uploading new flair assignments...')
r.set_flair_csv(subreddit, new_flairs)
print('...done')
