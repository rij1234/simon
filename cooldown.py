from discord.ext import commands
import discord

class CustomCooldown:
    def __init__(self, rate: int, per: float, bucket: commands.BucketType):
        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)

    def __call__(self, ctx: commands.Context):
            if ctx.author.id == ctx.bot.owner_id:
                return True
            bucket = self.default_mapping.get_bucket(ctx.message)
            retry_after = bucket.update_rate_limit()
            if retry_after:
                raise commands.CommandOnCooldown(bucket, retry_after)
            return True
