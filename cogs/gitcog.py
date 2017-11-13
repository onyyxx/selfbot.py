import discord
from discord.ext import commands
import os
import json
import aiohttp
import traceback

class Git:
    '''Github Cog, facilitates viewing and creating issues'''
    def __init__(self, bot):
        self.bot = bot

    @property
    def githubtoken(self):
        '''
        Returns your token wherever it is

        Instructions to get this will be given soon. 
        This token can give any user complete access to the account.
        https://github.com/settings/tokens is where you make a token.
        '''
        with open('data/config.json') as f:
            config = json.load(f)
            return os.environ.get('GITHUBTOKEN') or config.get('GITHUBTOKEN')

    @commands.command()
    async def issue(self, ctx, repo, issueid):
        '''View an issue from Github!'''
        async with ctx.session.get(f"https://api.github.com/repos/{repo}/issues/{issueid}") as resp:
            if resp.status == 200 or resp.status == 201:
                issueinfo = await resp.json()
            else:
                return await ctx.send('ConnectionError: Github API Issue.')
        async with ctx.session.get(issueinfo['comments_url']) as resp:
            if resp.status == 200 or resp.status == 201:
                commentsinfo = await resp.json()
            else:
                return await ctx.send('ConnectionError: Github API Issue.')

        if issueinfo['state'] == 'closed': colour = 0xcb2431
        elif issueinfo['state'] == 'open': colour = 0x2cbe4e
        else: colour = 0xffffff
        try:
            issueinfo['pull_request']
        except KeyError:
            issuetype = 'Issue'
        else:
            issuetype = 'Pull Request'
        em = discord.Embed(title=issueinfo['title'] + ' (#' + str(issueinfo['number']) + ')', description=issueinfo['body'], url=issueinfo['html_url'], color=colour)
        em.set_author(name=issueinfo['user']['login'] + ' (' + issueinfo['author_association'].capitalize() + ')', icon_url=issueinfo['user']['avatar_url'])
        em.set_footer(text=issuetype + ' | ' + issueinfo['created_at'])
        for comment in commentsinfo:
            em.add_field(name=comment['user']['login'] + ' (' + comment['author_association'].capitalize() + ')', value=comment['body'], inline=False)
        await ctx.send(embed=em)
    
    @commands.command()
    async def makeissue(self, ctx, repo, title, *, body):
        '''Create an issue! `{}makeissue <title> | <body>`'''.format(ctx.prefix)
        async with ctx.session.post(f'https://api.github.com/repos/{repo}/issues', json={"title": title, "body": body}, headers={'Authorization': f'Bearer {self.githubtoken}'}) as resp:
            if resp.status == 200 or resp.status == 201:
                issueinfo = await resp.json()
            else:
                return await ctx.send('ConnectionError: Github API Issue.')

        em = discord.Embed(title=issueinfo['title'] + ' (#' + str(issueinfo['number']) + ')', description=issueinfo['body'], url=issueinfo['html_url'], color=0xcb2431)
        em.set_author(name=issueinfo['user']['login'] + ' (' + issueinfo['author_association'].capitalize() + ')', icon_url=issueinfo['user']['avatar_url'])
        em.set_footer(text='Issue | ' + issueinfo['created_at'])
        await ctx.send(embed=em)

    @commands.command()
    async def comment(self, ctx, repo, issueid:int, *, content):
        '''Comment on a Github Issue'''
        async with ctx.session.post(f'https://api.github.com/repos/{repo}/issues/{issueid}/comments', json={"body": content}, headers={'Authorization': f'Bearer {self.githubtoken}'}) as resp:
            if resp.status != 200 and resp.status != 201:
                return await ctx.send('ConnectionError: Github API Issue.')
        await ctx.send('Submitted comment to issue ' + str(issueid))

def setup(bot):
    bot.add_cog(Git(bot))
