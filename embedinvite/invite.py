# Remove command logic originally from : https://github.com/mikeshardmind/SinbadCogs/tree/v3/messagebox

import discord
from redbot.core import commands, checks, Config

old_invite = None


class EmbedInvite(commands.Cog):
    """Personalize invite command with an embed and multiple options."""

    __author__ = "kennnyshiwa"

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot
        default = {
            "support": False,
            "support_serv": None,
            "description": "Thanks for choosing to invite {name} to your server",
            "setpermissions": "",
        }
        self.config = Config.get_conf(self, 376564057517457408, force_registration=True)
        self.config.register_global(**default)

    def cog_unload(self):
        global old_invite
        if old_invite:
            try:
                self.bot.remove_command("invite")
            except:
                pass
            self.bot.add_command(old_invite)

    @checks.is_owner()
    @commands.group()
    async def invitesettings(self, ctx):
        """Settings for embedinvite cog."""
        pass

    @invitesettings.command()
    async def description(self, ctx, *, text: str = ""):
        """
        Set the embed description.
        Leave blank for default description
        Default: "Thanks for choosing to invite {name} to your server"
        Use `{name}` in your message to display bot name.
        Enter ``None`` to disable the description
        """
        if text == "":
            await self.config.description.clear()
            return await ctx.send("Embed description set to default.")
        elif text == "None":
            await self.config.description.set("")
            return await ctx.send("Embed description disabled.")
        await self.config.description.set(text)
        await ctx.send(f"Embed description set to :\n`{text}`")

    @invitesettings.command()
    async def support(self, ctx, value: bool = None):
        """
        Choose if you want support field.
        Default: False
        """
        if value:
            await self.config.support.set(True)
            await ctx.send("Support field set to `True`.")
        else:
            await self.config.support.set(False)
            await ctx.send("Support field set to `False`.")

    @invitesettings.command()
    async def supportserv(self, ctx, supportserver):
        """
        Set a support server.
        Enter the invite link to your server.
        """
        await self.config.support_serv.set(supportserver)
        await ctx.send("Support server set.")

    @invitesettings.command()
    async def setpermissions(self, ctx, *, text: int = ""):
        """Set the default permissions value for your bot.
        Get the permissions value from https://discordapi.com/permissions.html
        If left blank, resets permissions value to none
        Enter ``None`` to disable the permissions value
        """
        if text == "":
            await self.config.setpermissions.clear()
            return await ctx.send("Permissions value reset")
        elif text == "None":
            await self.config.setpermission.set("")
            return await ctx.send("Permissions value disabled")
        await self.config.setpermissions.set(text)
        await ctx.send("Permissions set")

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def invite(self, ctx):
        """
        Send personalized invite for the bot.
        """
        permissions = await self.config.setpermissions()
        support_serv = await self.config.support_serv()
        support = await self.config.support()
        if support_serv is None and support is True:
            return await ctx.send("Bot Owner needs to set a support server!")
        embed = discord.Embed(
            description=(await self.config.description()).replace("{name}", self.bot.user.name),
            color=await ctx.embed_color(),
        )
        if discord.__version__[0] == "2":
            url = str(ctx.bot.user.avatar.replace(size=2048, static_format="webp"))
            if ctx.bot.user.avatar.is_animated() is False:
                url += "&quality=lossless"
        else:
            url = str(ctx.bot.user.avatar_url)
            if ctx.bot.user.is_avatar_animated() or requests.get(url).headers['content-type'] == "image/png":
                if ctx.bot.user.is_avatar_animated():
                    url = ctx.bot.user.avatar_url_as(format="gif", size=2048)
                if requests.get(url).headers['content-type'] == "image/png":
                    pass
            else:
                url += "&quality=lossless"
        embed.set_author(name=ctx.bot.user.name, icon_url=url)
        embed.set_thumbnail(url=url)
        embed.add_field(
            name="Bot Invite",
            value="https://discord.com/oauth2/authorize?client_id={}&scope=bot&permissions={}&scope=bot+applications.commands".format(
                self.bot.user.id, permissions
            ),
        )
        if support:
            embed.add_field(name="Support Server", value="{}".format(support_serv))
        embed.set_footer(text=f"{ctx.bot.user.display_name} made possible with the support of Red Discord Bot", icon_url="https://cdn.discordapp.com/icons/133049272517001216/a_aab012f3206eb514cac0432182e9e9ec.gif?size=512")
        await ctx.send(embed=embed)

async def setup(bot):
    invite = EmbedInvite(bot)
    global old_invite
    old_invite = bot.get_command("invite")
    if old_invite:
        bot.remove_command(old_invite.name)
    if discord.__version__[0] == "2":
        await bot.add_cog(invite)
    else:
        bot.add_cog(invite)