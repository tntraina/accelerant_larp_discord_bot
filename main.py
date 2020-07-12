import discord
from discord.ext import commands
import random
from lark import Lark
import lark

accelerant_grammar = open("accelerant_ebnf.txt", "r").read()
accelerant = Lark(accelerant_grammar, start='call')

bot = commands.Bot(command_prefix='>')

class NPC:
    stats = dict()
    properties = []
    name = "Unnamed NPC"

    def __init__(self, name, vit=5, propertylist=[]):
        self.stats['Vitality'] = vit
        for p in propertylist:
            self.properties.append(p)
        self.name = name


npcs = []


@bot.event
async def on_ready():
    print("Ready? FIGHT!")


def eval_accelerant_call(call_text):
    str_area = "their target"
    str_target = "a standard attack"
    str_trait = "their main weapon"
    result = "It probably did something. I should implement this feature at some point."
    parse_tree = accelerant.parse(call_text)
    parsed_tuple = parse_tree.children
    parsed_data = dict()
    for d in parsed_tuple:
        print(d)
        if isinstance(d, lark.tree.Tree):
            d2 = d.children
            parsed_data[d.data] = d2
        elif isinstance(d, lark.lexer.Token):
            parsed_data[d.type] = d

    if 'area' in parsed_data.keys():
        print("AoE implicated")
        if parsed_data['area'] == "by my voice" or parsed_data['area'] == "in this place":
            str_area = "all the creatures around them"
        elif parsed_data['area'][0].type == "NAMED_TARGET":
            str_area = parsed_data['area'][0]
            result = f'But alas, there was no {str_area} to be found.'
            for mook in npcs:
                if mook.name == str_area:
                    result = "It probably did something. I should implement this feature at some point."
    if 'target' in parsed_data.keys():
        print("by-clause implicated")
        str_target = f'an anti-{parsed_data["target"][0]} attack'
    if 'cause' in parsed_data.keys():
        print("bane traits implicated")
        str_trait = parsed_data['cause'][0]
    if parsed_data['effect'][0].type == "STATUS":
        if parsed_data["effect"][0] == "death":
            str_effect = "kill"
        else:
            str_effect = parsed_data["effect"][0]
    elif isinstance(parsed_data['effect'], list):
        str_effect = f'do {parsed_data["effect"][0]} damage'
    print(parse_tree.pretty())
    return f'[[The character]] tried to {str_effect} {str_area} with {str_target} using {str_trait}.  ' + result

@bot.command()
async def spawn(ctx):
    print(ctx)
    list_of_npcs = ['slime', 'goblin', 'robot', 'soldier']
    random.shuffle(list_of_npcs)
    creature_name = list_of_npcs[0]
    npcs.append(NPC(name=creature_name[2:], propertylist=[creature_name[2:]]))
    status_update = f'{creature_name} appears!'
    await ctx.send(status_update)


@bot.command()
async def view(ctx, *args):
    if len(npcs) > 0:
        status_update = "You look around the battlefield and see "
        for n in npcs:
            status_update = status_update + n.name + ", "
        status_update = status_update[:-2]
    else:
        status_update = "The battlefield looks empty."
    await ctx.send(status_update)


@bot.command()
async def call(ctx, *args):
    attacker_name = ctx.message.author.display_name
    acc_call = ""
    for i in range(len(args)):
        acc_call = acc_call + str(args[i]) + " "
    acc_call = acc_call[:-1]
    print(acc_call)
    print(ctx)
    status_update = eval_accelerant_call(acc_call)
    status_update = status_update.replace("[[The character]]", attacker_name)
    await ctx.send(status_update)

token_data = open("secret_stuff.txt","r").read()
bot.run(token_date)
