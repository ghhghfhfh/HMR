import discord
from discord.ext import commands
import os
import logging
import sys
import asyncio
from dotenv import load_dotenv

# Отключаем сохранение логов в файл (только в консоль)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Только вывод в консоль, без файла
    ]
)
logger = logging.getLogger('discord_bot')

# ===== КОНФИГУРАЦИЯ ИНТЕНТОВ =====
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.voice_states = True  # Для отслеживания войсов
intents.invites = True       # Для отслеживания приглашений

# ===== СОЗДАНИЕ БОТА =====
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
    
    async def setup_hook(self):
        """Загрузка когов при запуске бота"""
        try:
            # Загружаем модули (без moderation)
            cogs_to_load = [
                'cogs.admin',
                'cogs.help',
                'cogs.Raid',
                'vk_tg_ds.voice_tracker',
                'vk_tg_ds.invite_tracker',
                'vk_tg_ds.link_system',
                'vk_tg_ds.role_watcher',
                'vk_tg_ds.bridge'
            ]
            
            for cog in cogs_to_load:
                try:
                    await self.load_extension(cog)
                    logger.info(f"✅ Загружен модуль: {cog}")
                except Exception as e:
                    logger.error(f"❌ Ошибка загрузки кога {cog}: {e}")
                
            logger.info("✅ Все коги успешно загружены")
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке когов: {e}")
    
    async def on_ready(self):
        """Событие при успешном подключении бота"""
        logger.info(f'✅ Бот успешно запущен как {self.user.name}')
        logger.info(f'🆔 ID бота: {self.user.id}')
        logger.info(f'👥 Подключен к {len(self.guilds)} серверам')
        
        # Выводим информацию о серверах
        for guild in self.guilds:
            logger.info(f'🏠 Сервер: {guild.name} (ID: {guild.id})')
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="за порядком | !help"
        )
        await self.change_presence(activity=activity)

# ===== ПОЛУЧЕНИЕ ТОКЕНА =====
def get_bot_token():
    """Получение токена с приоритетом на secret/token.env"""
    
    # Список путей для поиска токена
    env_paths = [
        'secret/token.env',
        '/home/container/secret/token.env',
        '.env',
        '/home/container/.env',
    ]
    
    # 1. Проверяем системные переменные
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if TOKEN:
        logger.info("✅ Токен найден в системных переменных окружения")
        return TOKEN.strip()
    
    # 2. Проверяем файлы
    for path in env_paths:
        try:
            if os.path.exists(path):
                logger.info(f"🔍 Проверяем файл: {path}")
                load_dotenv(path)
                TOKEN = os.getenv("DISCORD_BOT_TOKEN")
                if TOKEN:
                    logger.info(f"✅ Токен загружен из файла: {path}")
                    return TOKEN.strip()
                else:
                    logger.warning(f"⚠️ Файл {path} найден, но токен не обнаружен")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при чтении {path}: {e}")
    
    # 3. Токен не найден
    logger.critical("❌ ТОКЕН НЕ НАЙДЕН!")
    
    current_dir = os.getcwd()
    logger.info(f"📁 Текущая рабочая директория: {current_dir}")
    
    print("\n" + "="*60)
    print("❌ ТОКЕН НЕ НАЙДЕН!")
    print("="*60)
    print("\n📁 Текущая структура файлов:")
    
    try:
        root_files = os.listdir(current_dir)
        print(f"📋 Файлы в корне: {root_files}")
        
        secret_path = os.path.join(current_dir, 'secret')
        if os.path.exists(secret_path):
            secret_files = os.listdir(secret_path)
            print(f"📁 Файлы в secret/: {secret_files}")
        else:
            print("❌ Папка 'secret/' не найдена!")
            
        cogs_path = os.path.join(current_dir, 'cogs')
        if os.path.exists(cogs_path):
            cogs_files = os.listdir(cogs_path)
            print(f"📁 Файлы в cogs/: {cogs_files}")
        else:
            print("❌ Папка 'cogs/' не найдена!")
            
        vk_tg_ds_path = os.path.join(current_dir, 'vk_tg_ds')
        if os.path.exists(vk_tg_ds_path):
            vk_files = os.listdir(vk_tg_ds_path)
            print(f"📁 Файлы в vk_tg_ds/: {vk_files}")
        else:
            print("❌ Папка 'vk_tg_ds/' не найдена!")
            
    except Exception as e:
        print(f"❌ Ошибка при чтении структуры: {e}")
    
    print("\n🎯 РЕШЕНИЕ:")
    print("1. Создайте файл secret/token.env")
    print("2. Добавьте строку: DISCORD_BOT_TOKEN=ваш_токен")
    print("3. Перезапустите бота")
    print("="*60)
    
    sys.exit(1)

# ===== КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ БОТОМ =====
@commands.command(name='reload')
@commands.has_permissions(administrator=True)
async def reload_cog(ctx, cog: str):
    """Перезагружает указанный ког"""
    try:
        # Определяем в какой папке искать ког
        if cog.startswith('vk_tg_ds.'):
            await ctx.bot.reload_extension(cog)
        else:
            await ctx.bot.reload_extension(f'cogs.{cog}')
        await ctx.send(f'✅ Ког `{cog}` успешно перезагружен!')
        logger.info(f"🔄 Ког {cog} перезагружен по команде от {ctx.author}")
    except Exception as e:
        await ctx.send(f'❌ Ошибка перезагрузки кога `{cog}`: {e}')
        logger.error(f"Ошибка перезагрузки кога {cog}: {e}")

@commands.command(name='load')
@commands.has_permissions(administrator=True)
async def load_cog(ctx, cog: str):
    """Загружает указанный ког"""
    try:
        if cog.startswith('vk_tg_ds.'):
            await ctx.bot.load_extension(cog)
        else:
            await ctx.bot.load_extension(f'cogs.{cog}')
        await ctx.send(f'✅ Ког `{cog}` успешно загружен!')
        logger.info(f"📥 Ког {cog} загружен по команде от {ctx.author}")
    except Exception as e:
        await ctx.send(f'❌ Ошибка загрузки кога `{cog}`: {e}')
        logger.error(f"Ошибка загрузки кога {cog}: {e}")

@commands.command(name='unload')
@commands.has_permissions(administrator=True)
async def unload_cog(ctx, cog: str):
    """Выгружает указанный ког"""
    try:
        if cog.startswith('vk_tg_ds.'):
            await ctx.bot.unload_extension(cog)
        else:
            await ctx.bot.unload_extension(f'cogs.{cog}')
        await ctx.send(f'✅ Ког `{cog}` успешно выгружен!')
        logger.info(f"📤 Ког {cog} выгружен по команде от {ctx.author}")
    except Exception as e:
        await ctx.send(f'❌ Ошибка выгрузки кога `{cog}`: {e}')
        logger.error(f"Ошибка выгрузки кога {cog}: {e}")

@commands.command(name='modules')
@commands.has_permissions(administrator=True)
async def show_modules(ctx):
    """Показывает список загруженных модулей"""
    loaded_cogs = list(ctx.bot.cogs.keys())
    if loaded_cogs:
        embed = discord.Embed(
            title="📦 Загруженные модули",
            description="\n".join([f"• {cog}" for cog in loaded_cogs]),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Всего: {len(loaded_cogs)} модулей")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Нет загруженных модулей")

@commands.command(name='restart')
@commands.has_permissions(administrator=True)
async def restart_bot(ctx):
    """Перезапускает бота"""
    await ctx.send("🔄 Перезапуск бота...")
    logger.info(f"🔄 Перезапуск бота по команде от {ctx.author}")
    
    # Даем время на отправку сообщения
    await asyncio.sleep(2)
    
    # Перезапускаем
    os.execv(sys.executable, [sys.executable] + sys.argv)

@commands.command(name='reloadall')
@commands.has_permissions(administrator=True)
async def reload_all(ctx):
    """Перезагружает все модули"""
    await ctx.send("🔄 Перезагрузка всех модулей...")
    
    modules = [
        'cogs.admin',
        'cogs.help', 
        'cogs.Raid',
        'vk_tg_ds.voice_tracker',
        'vk_tg_ds.invite_tracker',
        'vk_tg_ds.link_system',
        'vk_tg_ds.role_watcher',
        'vk_tg_ds.bridge'
    ]
    
    success = 0
    for module in modules:
        try:
            await ctx.bot.reload_extension(module)
            success += 1
            logger.info(f"🔄 Перезагружен: {module}")
        except Exception as e:
            logger.error(f"❌ Ошибка {module}: {e}")
    
    await ctx.send(f"✅ Перезагружено {success}/{len(modules)} модулей")

# ===== ОБРАБОТКА ОШИБОК =====
@commands.Cog.listener()
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    logger.error(f"Ошибка в команде {ctx.command}: {error}")
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для выполнения этой команды!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ У бота недостаточно прав для выполнения этой команды!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Не хватает аргументов! Использование: `{ctx.command.qualified_name} {ctx.command.signature}`")
    else:
        await ctx.send(f"❌ Ошибка: {error}")

# ===== ЗАПУСК БОТА =====
async def main():
    """Основная функция запуска бота"""
    try:
        TOKEN = get_bot_token()
        bot = MyBot()
        
        # Добавляем команды управления
        bot.add_command(reload_cog)
        bot.add_command(load_cog)
        bot.add_command(unload_cog)
        bot.add_command(show_modules)
        bot.add_command(restart_bot)
        bot.add_command(reload_all)
        
        # Запускаем бота
        logger.info("🚀 Запуск бота...")
        await bot.start(TOKEN)
        
    except discord.LoginFailure:
        logger.critical("❌ Неверный токен бота! Проверьте токен в secret/token.env")
    except KeyboardInterrupt:
        logger.info("⏹️ Остановка бота")
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    print("="*50)
    print("🤖 Discord Бот запускается...")
    print("="*50)
    asyncio.run(main())