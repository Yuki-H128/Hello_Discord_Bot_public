import discord
from discord.ext import commands
from discord.ext import tasks
import random as rand
import pickle
from datetime import datetime

client = commands.Bot(command_prefix = '.')
dateFormatter = "%H:%M"

def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj,f)

def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data

@client.command(aliases=['登録'])
async def touroku(ctx, time, op :int = None):
    try:
        datetime.strptime(time, dateFormatter)
    except:
        await ctx.send('エラー')
        return
    name = ctx.message.author.id
    touroku = pickle_load('./touroku.pickle')
    okita = pickle_load('./okita.pickle')
    if op != None:
        try:
            touroku[name][op-1] = time
            okita[name] = False
            await ctx.send(f'{op}日後の起きる時間を変更しました。')
        except:
            await ctx.send(f'{op}日後は登録されていないので変更できません。')
    else:
        try:
            touroku[name].append(time)
        except:
            touroku[name] = [time]
        okita[name] = False
        await ctx.send(f'{len(touroku[name])}日後の起きる時間を設定しました。')
    pickle_dump(touroku, './touroku.pickle')
    pickle_dump(okita, 'okita.pickle')

#登録リセットコマンド
@client.command(aliases=['登録リセット'])
async def touroku_reset_command(ctx):
    name = ctx.message.author
    touroku = pickle_load('./touroku.pickle')
    touroku[name.id] = []
    pickle_dump(touroku, './touroku.pickle')
    await ctx.send('リセットしました')

@client.command(aliases=['確認'])
async def kakunin(ctx):
    name = ctx.message.author
    touroku = pickle_load('./touroku.pickle')
    try:
        for i in range(1,len(touroku[name.id])+1):
            await ctx.send(f'{i}日後：{touroku[name.id][i-1]}\n')
    except:pass
    if len(touroku[name.id])==0:   
        await ctx.send(f'{name.display_name}さんは登録されていません')

@client.command(aliases=['起きた'])
async def okita(ctx):
    name = ctx.message.author
    #role = ctx.guild.get_role(801231107861381170)
    role = discord.utils.get(ctx.message.guild.roles, name="寝坊")
    touroku = pickle_load('./touroku.pickle')
    okita = pickle_load('./okita.pickle')
    if okita[name.id] == True:
        yotei = datetime.strptime(touroku[name.id].pop(0), dateFormatter)
        now = datetime.strptime(f'{datetime.now().hour}:{datetime.now().minute}', dateFormatter)
        if yotei > now:
            await ctx.send(f'{name.display_name}さん！おはようございます！さすが～')
            await name.remove_roles(role)
        else:
            await ctx.send(f'{name.display_name}さんは「{yotei.hour:02}:{yotei.minute:02}」あれ？寝坊ですね。')
            await name.add_roles(role)
        okita[name.id] = False
    else:
        await ctx.send(f'{name.display_name}さん！今日も早く寝て、朝しっかりと起きましょう！おやすみ～')

    pickle_dump(touroku, './touroku.pickle')
    pickle_dump(okita, 'okita.pickle')
    

@client.command(aliases=['おみくじ'])
async def _5omikuji(ctx):
    omikuji = pickle_load('./omikuji.pickle')
    responses = ['大吉',
                 '中吉',
                 '吉',
                 '小吉',
                 '凶']
    name = ctx.message.author.display_name
    if name in omikuji:
        await ctx.send(f'{name}さん！今日の運勢は：{responses[-1]}\nHelloくんは何でもお見通しなのです。')
    else:
        omikuji.append(name)
        pickle_dump(omikuji, './omikuji.pickle')
        await ctx.send(f'{name}さん！今日の運勢は：{rand.choice(responses)}')

#おみくじリセット
def omikuji_reset():
    kara = []
    pickle_dump(kara, './omikuji.pickle')

#起きたリセット
def okita_reset():
    okita = pickle_load('./okita.pickle')
    for key in okita:
        okita[key] = True
    pickle_dump(okita, './okita.pickle')

@tasks.loop(seconds=60)
async def loop():
    now = datetime.now().strftime(dateFormatter)
    if now == '00:00':
        omikuji_reset()
        okita_reset()

'''
#おみくじリセットコマンド
@client.command(aliases=['おみくじリセット'])
@commands.has_permissions(administrator=True)
async def omikuji_reset_command(ctx):
    omikuji_reset()
    await ctx.send('リセットしました')
'''

#起きたリセットコマンド
@client.command(aliases=['起きたリセット'])
#@commands.has_permissions(administrator=True)
async def okita_reset_command(ctx):
    okita_reset()
    await ctx.send('リセットしました')


#メッセージ削除コマンド
@client.command(aliases=['削除'])
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount)

'''
#現在の時刻を表示
@client.command(aliases=['時刻'])
@commands.has_permissions(administrator=True)
async def jikoku_command(ctx):
    await ctx.send(f'{datetime.now()}')
'''

loop.start()

client.run('')
