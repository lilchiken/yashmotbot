import logging
import os
import glob
import random
import time
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Объект бота
#proxy_url = 'http://proxy.server:3128' необходим при деплое на сервер
bot = Bot(token="...", parse_mode="HTML") # Здесь Ваш токен
# Диспетчер для бота
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)


def queue_posts(): # отдает два списка: рандомный(0) и оригинальный(1)
    files_path = os.path.join('/Users/ilia/Documents/GitHub/yashmotbot/posts', '*')
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    posts_list = []
    origin_list = files.copy()
    def shufle():
        if len(origin_list) > len(posts_list):
            a = origin_list[random.randint(0,len(origin_list)-1)]
            if a not in posts_list:
                posts_list.append(a)
                shufle()
            else:
                shufle()
        else:
            pass
    shufle()
    return posts_list, origin_list

def update_queue(posts_list, origin_list):
    files_path = os.path.join('/Users/ilia/Documents/GitHub/yashmotbot/posts', '*')
    files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
    posts_list.clear()
    for post in files:
        if post not in origin_list:
            posts_list.append(post)
    if len(posts_list) != 0:
        for post in posts_list:
            origin_list.append(post)
    def shufle():
        if len(new_posts) > len(posts_list):
            a = new_posts[random.randint(0, len(new_posts)-1)]
            if a not in posts_list:
                posts_list.append(a)
            shufle()
        else:
            pass
    new_posts = posts_list.copy()
    if len(posts_list) != 0:
        posts_list.clear()
        shufle()
    return posts_list, origin_list

class UserState(StatesGroup):
    like = State()
    queue = State()
    num_post = State()
    original_queue = State()

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="/menu")
    keyboard.add(button_1)
    await set_userstates(state=state)
    await set_userstates2(state=state)
    await set_userstates3(state=state)
    await message.answer('Привет,\nЯШмот - мультисервисный бот связанный со шмотьем 😁\nВызови меню, чтобы узнать подробнее, что я могу.', reply_markup=keyboard)

@dp.message_handler(commands="menu")
async def cmd_menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="/shmot")
    keyboard.add(button_1)
    data = await state.get_data()
    if data['num_post'] == 999:
        await message.answer('Пока что имеется только один сервис <b>/shmot</b> 🥲\nОн вкидывает тебе шмотки с площадок необычного шмотья.\nВсе интуитивно понятно, быстрее попробуй ее.', reply_markup=keyboard)
        await state.update_data(num_post=0)
    else:
        await message.answer('Ну,\nдавай что-ли повторим?',reply_markup=keyboard)

@dp.message_handler(state=UserState.num_post)
async def set_userstates(state: FSMContext):
    await state.update_data(num_post = 999)

@dp.message_handler(state=UserState.queue)
async def set_userstates2(state: FSMContext):
    await state.update_data(queue = queue_posts()[0])

@dp.message_handler(state=UserState.original_queue)
async def set_userstates3(state: FSMContext):
    await state.update_data(original_queue = queue_posts()[1])

@dp.message_handler(commands="shmot")
async def cmd_shmot(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).row('❤️', '💔', '🥶')
    data = await state.get_data()
    time.sleep(0.8)
    print(data)
    try:
        with open(data['queue'][data['num_post']], 'r+') as f:
            s = f.read()
            s = eval(s)
            try:
                await bot.send_photo(message.chat.id, photo=list(s.values())[0][2])
            except:
                print('no photo')
            await message.answer(f'{list(s.values())[0][1]}\n<b>{list(s.values())[0][4]}</b> ❤\n<b>{list(s.values())[0][5]}</b> 💔', reply_markup=keyboard)
            await UserState.like.set()
    except FileNotFoundError:
        try:
            async def try_next():
                for x in range(1,101 - data['num_post']):
                    with open(data['queue'][data['num_post']+x], 'r+') as f:
                        if f.read():
                            await state.update_data(num_post=data['num_post'] + x)
                            await cmd_shmot(message=message, state=state)
                            break
            await try_next()
        except:
            await state.update_data(num_post = 999)
            await cmd_shmot(message=message, state=state)
    except IndexError:
        await state.update_data(queue = update_queue(data['queue'], data['original_queue']))
        data = await state.get_data()
        await state.update_data(original_queue = data['queue'][1])
        await state.update_data(queue = data['queue'][0])
        data = await state.get_data()
        if len(data['queue']) == 0:
            await message.answer('Новых постов нет, подождите')
            await cmd_menu(message=message, state=state)
        else:
            await message.answer('Новые посты:')
            await state.update_data(num_post=0)
            await cmd_shmot(message=message, state=state)

@dp.message_handler(state=UserState.like)
async def like_or_not(message: types.Message, state: FSMContext):
    await state.update_data(like = message.text)
    data = await state.get_data() # data['like']
    if data['like'] == '❤️':
        with open(data['queue'][data['num_post']], 'r') as f:
            s = f.read()
            s = eval(s)
            list(s.values())[0][4] += 1
        p = s.copy()
        with open(data['queue'][data['num_post']], 'w') as f:
            f.write(str(p))
            if str(data['num_post'])[-1] == '0' or str(data['num_post'])[-1] == '3' or str(data['num_post'])[-1] == '6':
                await message.answer(f'<a href="{list(p.values())[0][3]}">Крутой кардиган..или джинсы..😅\nИзвини, я пока не умею распозновать вещи по картинке,\nно при твоей поддержке я смогу этому научиться.\nЕсли ты понимаешь, о чем я 💰 😏</a>',parse_mode='HTML')
            elif str(data['num_post'])[-1] == '2' or str(data['num_post'])[-1] == '4' or str(data['num_post'])[-1] == '8':
                await message.answer(f'<a href="{list(p.values())[0][3]}">Круть, лови ссылку 😎\nНе забудь сказать продавцу, где ты нашел эту вещичку 😁</a>',parse_mode='HTML')
            else:
                await message.answer(f'<a href="{list(p.values())[0][3]}">Ух ты, тебе реально понравилось 👉👈\nБыло бы круто, если бы ты рассказал продавцу про мое существование ☺️</a>', parse_mode='HTML')
        await state.reset_state(with_data=False)
        await state.update_data(num_post=data['num_post'] + 1)
        await cmd_shmot(message = message, state = state)
    elif data['like'] == '💔':
        with open(data['queue'][data['num_post']], 'r') as f:
            s = f.read()
            s = eval(s)
            list(s.values())[0][5] += 1
        p = s.copy()
        with open(data['queue'][data['num_post']], 'w') as f:
            f.write(str(p))
        await state.reset_state(with_data=False)
        await state.update_data(num_post=data['num_post'] + 1)
        await cmd_shmot(message = message, state = state)
    elif data['like'] == '🥶':
        await state.reset_state(with_data=False)
        await cmd_menu(message= message, state= state)
    else:
        await message.answer('Я тебя не понял, давай еще раз.')
        await state.reset_state(with_data=False)
        await cmd_shmot(message=message, state=state)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)