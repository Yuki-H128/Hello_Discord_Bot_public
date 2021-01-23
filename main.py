#モジュールのインクルード
from module import my_pickle as mp #自作pickleモジュール
import discord #discordモジュール
from discord.ext import commands #commandsモジュール
from discord.ext import tasks #tasksモジュール
from datetime import datetime #日付、時刻モジュール

bot = commands.Bot(command_prefix = '.') #コマンドの最初の文字
dateFormatter = "%H:%M" #datetimeで使うフォーマット

#起きる時間を登録するコマンド
@bot.command(aliases = ['設定'])
async def set(ctx, time, option:int = None):
    #データフォーマットにあっているか確認する
    try: time = datetime.strptime(time, dateFormatter)
    except: await ctx.send('error'); return
    #ユーザーを取得する
    name = ctx.message.author
    #ファイルのロード
    time_dic = mp.pickle_load('time_dic')
    check_dic = mp.pickle_load('check_dic')
    #ユーザーのtime_listを取得する
    try: time_list = time_dic[name.id]
    except: time_list = []
    #オプションが指定されていないときの処理
    if option == None:
        time_list.append(time)
        num = len(time_list)
    #オプションが指定されたときの処理
    else:
        try:
            time_list[option - 1] = time
            num = option
        except: await ctx.send('error'); return
    #time_listをtime_dic[name.id]に代入する
    time_dic[name.id] = time_list
    #time_dirをtime_dir.pickleに書き込む
    mp.pickle_dump(time_dic, 'time_dic')
    check_dic[name.id] = False; mp.pickle_dump(check_dic, 'check_dic')
    await ctx.send(f'{name.display_name}さんの{num}日後の起きる時間を設定しました！')
    return

@bot.command(aliases = ['確認'])
async def check(ctx):
    #ユーザーを取得
    name = ctx.message.author
    #ファイルのロード
    time_dic = mp.pickle_load('time_dic')
    #ユーザーのtime_listを取得する
    try: time_list = time_dic[name.id]
    except: time_list = []
    #リストが空のときの処理
    if len(time_list) == 0: await ctx.send(f'{name.display_name}さんは登録されていません...'); return
    #リストに要素がある場合
    await ctx.send(f'{name.display_name}さんの予定を表示します！')
    #リストに要素がある場合
    i = 0
    for time in time_list:
        await ctx.send(f'{i + 1}日後 {time.hour:02}:{time.minute:02}')
        i += 1

@bot.command(aliases = ['起きた'])
async def get_up(ctx):
    #ユーザー、ロールを取得
    name = ctx.message.author; role = discord.utils.get(ctx.message.guild.roles, name="寝坊")
    #ファイルのロード
    time_dic = mp.pickle_load('time_dic')
    check_dic = mp.pickle_load('check_dic')
    #ユーザーのtime_list,checkを取得する
    try: time_list = time_dic[name.id]
    except: time_list = []
    try: check = check_dic[name.id]
    except: check = True
    #リストが空のときの処理
    if len(time_list) == 0: await ctx.send(f'{name.display_name}さんは登録されていません...'); return
    #checkがFalseのときの処理
    if check == False: await ctx.send(f'{name.display_name}さん！明日も早く起きましょう！'); return
    #checkがTrue,リストに要素があるとき
    now = datetime.strptime(f'{datetime.now().hour}:{datetime.now().minute}', dateFormatter); time = time_list.pop(0)
    if now <= time: await ctx.send(f'{name.display_name}さん！おはようございます！さすが～'); await name.remove_roles(role)
    else: await ctx.send(f'{name.display_name}さん！{time.hour:02}:{time.minute:02}...寝坊ですね（●｀ε´●）'); await name.add_roles(role)
    #データを書き込む
    time_dic[name.id] = time_list; mp.pickle_dump(time_dic, 'time_dic')
    check_dic[name.id] = False; mp.pickle_dump(check_dic, 'check_dic')

#空の辞書をファイルに上書きする関数
def reset_check():
    check_dic = {}; mp.pickle_dump(check_dic, 'check_dic')

#空の辞書をファイルに上書きする関数を起動するコマンド
@bot.command(aliases = ['チェックリセットコマンド'])
async def reset_check_command(ctx):
    reset_check()

#00:00に起動する関数
@tasks.loop(seconds=60)
async def loop():
    now = datetime.now().strftime(dateFormatter)
    if now == '03:00': reset_check()

#ループ処理開始
loop.start()

bot.run('ODAwODU2MjIxMTcwNDAxMzQx.YAYNeg.auADwBQcJawqaEmiIpsfSUUGmjM')