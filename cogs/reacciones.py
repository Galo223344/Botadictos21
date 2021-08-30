import discord
import asyncio
import re
import json
from discord.ext import commands
from datetime import datetime, timedelta
from cogs.logs import logchannel
import random
from __main__ import admin_ids


# TODO: Comentar el codigo. Cambiar emojis por los del club de los 21


class Reactions(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    global giveaways
    giveaways = []
    global dict_gv
    dict_gv = {}

    with open('config.json', 'r') as f:
        configjson = json.load(f)
        global welcome_id
        welcome_id = int(configjson["welcome_id"])
        global welcome_channel_id
        welcome_channel_id = int(configjson["welcome_channel_id"])

    @commands.Cog.listener()
    async def on_ready(self):
        print ("Reacciones cog is ready")
        reaction_message = await self.bot.get_channel(welcome_channel_id).fetch_message(welcome_id)
        try:
            await reaction_message.add_reaction(emoji="<a:Thumbup:792171608323260416>")
        except:
            # print("fallo el poner la reaccion")
            pass
        # print(self.reaction_message)

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     pass
    #
    # @commands.Cog.listener()
    # async def on_reaction_remove(self, reaction, user):
    #     pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # print(payload)
        if payload.member.bot == True:
            return
        reaction_message = await self.bot.get_channel(welcome_channel_id).fetch_message(welcome_id)
        if payload.message_id == welcome_id:
            if str(payload.emoji) == "<a:Thumbup:792171608323260416>":
                role = discord.utils.get(payload.member.guild.roles, name="La People👤")
                await payload.member.add_roles(role)
                await reaction_message.remove_reaction(str(payload.emoji), payload.member)
                return
        for i in dict_gv:
            if i == payload.message_id:
                # print("Encontrado")
                if str(payload.emoji) == "<a:Tada:784983720226193428>":
                    # print("emoji correcto")
                    # print(i)
                    # print("impreso el valor de i")
                    if payload.member.id in dict_gv[i]:
                        # print("el usuario ya está ahí")
                        return
                    dict_gv[i].append(payload.member.id)
                    # print(dict_gv)

    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     print(payload)
    #     if payload.member.bot == True:
    #         print(bot)
    #         return
    #
    #     for i in dict_gv:
    #         print(i)
    #         if i in giveaways:
    #             print("encontrado remove")
    #             dict_gv[i].remove(payload.member.id)
    #             print(dict_gv)




    @commands.command(name="sorteo", aliases=["Sorteo","sort","Sort","gv","GV","giveaway","Giveaway"])
    async def giveaway(self, ctx, tiempo = None, cant_ganadores = None, nombre = None, *, desc = None):
        if ctx.author.id not in admin_ids:
            embed=discord.Embed(title="¡No tienes permisos para utilizar este comando!", description="Necesitas contar con el permiso `BOT_OPERATOR`", color=0xff0000)
            embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return

        from cogs.logs import gvchannel


        if tiempo == None or cant_ganadores == None or nombre == None or desc == None:
            
            embed=discord.Embed(title="¡Uso invalido!", description="", color=0xff0000)
            embed.add_field(name="Uso del comando:", value="`!sorteo Tiempo(1h/1d/1m) Ganadores(Cantidad de ganadores) Nombre(Nombre del sorteo) Descripción(Descripción del sorteo)`", inline=True)
            embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return

        cant_ganadores = int(cant_ganadores)

        tiempo = tiempo.replace(" ","")

        listtiempo = re.findall('\d+|\D+', tiempo)

        if 'm' in listtiempo:
            indexm = listtiempo.index("m") -1
            # print("encontrada m")
        else:
            indexm = None

        if 'h' in listtiempo:
            indexh = listtiempo.index("h") - 1
            # print("encontrada h")
        else:
            indexh = None

        if 'd' in listtiempo:
            indexd = listtiempo.index("d") - 1
            # print("encontrada d")
        else:
            indexd = None

        ##########

        if indexm  is not None:
            minutos = int(listtiempo[indexm])
        else:
            minutos = 0

        if indexh is not None:
            horas = int(listtiempo[indexh])
        else:
            horas = 0

        if indexd is not None:
            dias = int(listtiempo[indexd])
        else:
            dias = 0

        if minutos == 0 and horas == 0 and dias == 0:
            embed=discord.Embed(title="¡Tiempo invalido!", description="", color=0xff0000)
            embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return

        tiempofinal = datetime.now().replace(microsecond=0,second=0) + timedelta(minutes=minutos,hours=horas,days=dias)
        tiempo_formateado = tiempofinal.strftime("%d/%m/%Y %H:%M")

        minutos = minutos * 60
        horas = horas * 3600
        dias = dias * 86400


        tiempodormir = minutos + horas + dias

        tadaa = self.bot.get_emoji(784983720226193428)

        embed=discord.Embed(title=str(nombre), description=str(desc), color=0x2cdca3)
        embed.add_field(name="Cantidad de ganadores:", value=cant_ganadores, inline=False)
        embed.add_field(name="Creador por:", value=f"{ctx.message.author.mention}", inline=False)
        embed.set_footer(text=f"Finaliza el dia: {tiempo_formateado}, ¡reacciona con 🎉 para entrar!")

        channel=self.bot.get_channel(gvchannel)
        message = await channel.send("@everyone ¡Nuevo sorteo!", embed=embed)
        await message.add_reaction(emoji="<a:Tada:784983720226193428>")


        lchannel = self.bot.get_channel(logchannel)
        embed=discord.Embed(title="Nuevo sorteo", description=f"Creado por: {ctx.message.author.mention}", color=0xff6600)
        embed.add_field(name=str(nombre), value=str(desc), inline=False)
        embed.add_field(name="Cantidad de ganadores: ", value=cant_ganadores, inline=False)
        embed.set_footer(text=f"Finaliza el dia: {tiempo_formateado}.")
        embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await lchannel.send(embed=embed)


        global giveaways
        giveaways.append(message.id)
        global dict_gv
        dict_gv[message.id] = []

        # print(giveaways)
        # print(dict_gv)

        await asyncio.sleep(tiempodormir)

        if len(dict_gv[message.id]) == 0 or len(dict_gv[message.id]) < cant_ganadores:
            if len(dict_gv[message.id]) == 0:
                await ctx.send(f"\"{nombre}\": El sorteo finalizó sin ningun participante.")
                del dict_gv[message.id]
                lchannel = self.bot.get_channel(logchannel)
                embed=discord.Embed(title=f"El sorteo \"{nombre}\" finalizó incorrectamente", description="Razón: No hubo suficientes participantes.", color=0xff0000)

            else:
                await ctx.send(f"\"{nombre}\": No hubo suficientes participantes para la cantidad de premios disponibles. {ctx.message.author.mention}")
                del dict_gv[message.id]
                lchannel = self.bot.get_channel(logchannel)
                embed=discord.Embed(title=f"El sorteo \"{nombre}\" finalizó incorrectamente", description="Razón: No hubo suficientes participantes.", color=0xff6600)

            await lchannel.send(embed=embed)

            del dict_gv[message.id]

            return

        ganadores = []

        while len(ganadores) < cant_ganadores:
            eleccion = random.choice(dict_gv[message.id])
            if eleccion not in ganadores:
                if eleccion == None:
                    continue
                try:
                    eleccionn = ctx.guild.get_member(int(eleccion))
                    if eleccionn == None:
                        continue
                    ganadores.append(eleccion)
                except:
                    continue


        for i in ganadores:
            ganador = ctx.guild.get_member(int(i))
            embed=discord.Embed(title="¡Felicidades!", description=f"¡El usuario {ganador.mention} ha ganado el sorteo \"{nombre}\"!", color=0x008080)
            embed.add_field(name=f"En las proximas horas:", value=f"{ctx.message.author.mention} se va a comunicar contigo.", inline=True)
            await channel.send(embed=embed)
            embed=discord.Embed(title="¡Felicidades!", description="", color=0x008080)
            embed.add_field(name=f"🎉 ¡Acabas de ganar el sorteo \"{nombre}\"!", value="En las proximas horas, Gtadictos21 se va a comunicar con vos para entregarte el premio. 🎉", inline=True)
            await ganador.send(embed=embed)


        del dict_gv[message.id]

        lchannel = self.bot.get_channel(logchannel)
        embed=discord.Embed(title=f"El sorteo {nombre} finalizó correctamente.", description="¡Asegurense de contactar a los ganadores!", color=0x008080)
        await lchannel.send(embed=embed)

    @commands.command(name="resorteo")
    async def resorteo(self,ctx,m_id):
        if ctx.author.id not in admin_ids:
            embed=discord.Embed(title="¡No tienes permisos para utilizar este comando!", description="Necesitas contar con el permiso `BOT_OPERATOR`", color=0xff0000)
            embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return
        msg = await ctx.fetch_message(int(m_id))
        usuarios = []
        users = set()

        for reaction in msg.reactions:
            async for user in reaction.users():
                usuarios.append(user)

        print(usuarios)

        while True:
            eleccion = random.choice(usuarios)
            print(eleccion)
            eleccion = ctx.guild.get_member(int(eleccion.id))
            print(eleccion)


            if eleccion != None:
                if not eleccion.bot:
                    break


        embed=discord.Embed(title="Se ha realizado un resorteo:", description=f"El nuevo ganador es \"{eleccion.mention}\"", color=0x008080)
        await ctx.send(embed=embed)
        





    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     pass

    @commands.command(name="init")
    async def init(self,ctx):
        if ctx.author.id not in admin_ids:
            embed=discord.Embed(title="¡No tienes permisos para utilizar este comando!", description="Necesitas contar con el permiso `BOT_OPERATOR`", color=0xff0000)
            embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return
        embed=discord.Embed(title="", description=" ", color=0x00b7ff)
        embed.add_field(name="¡Hacé click en el emoji!", value="¡Hacé click en el emoji <a:Thumbup:792171608323260416> para poder acceder al servidor! ", inline=False)
        welcome_message = await ctx.send(embed=embed)
        await welcome_message.add_reaction(emoji="<a:Thumbup:792171608323260416>")

        global welcome_id
        welcome_id = welcome_message.id
        global welcome_channel_id
        welcome_channel_id = welcome_message.channel.id


        with open('config.json', 'r') as f:
            config = json.load(f)

        config["welcome_id"] = welcome_id
        config["welcome_channel_id"] = welcome_channel_id

        with open("config.json", "w") as outfile:
            json.dump(config, outfile)





def setup(bot):
    bot.add_cog(Reactions(bot))
