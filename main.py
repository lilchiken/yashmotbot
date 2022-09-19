import vk_api # для создания новых сервисов нужно будет создать новые классы с наследованием от пост а Posts будет только для вторички
import time
import os
import glob

session = vk_api.VkApi(token='...') # Здесь Ваш токен
vk= session.get_api()

class Post(): # Класс для инициализации запроса от вк ; zakrep = 0 - нет закрепа, 1 - есть закреп
    def init2(self):
        self.method_vk = session.method('wall.get', {'owner_id': self.group, 'count': 1 + self.zakrep})
        self.txt = self.method_vk['items'][self.zakrep]['text']
        self.id = self.method_vk['items'][self.zakrep]['id']
        self.url = f'https://vk.com/wall{self.group}_{self.id}'
        try:
            self.img_url = self.method_vk['items'][self.zakrep]['attachments'][0]['photo']['sizes'][-1]['url']
        except:
            self.img_url = 0

    def __init__(self, group_id, zakrep):
        self.group = group_id
        self.zakrep = zakrep
        self.init2()


class Posts(Post): # Класс для сохранения постов, перед сохранением обязательно нужно создать словарь методом get_dict!
    def get_dict(self):
        self.dict = {}

    def save_dict(self):
        self.dict[(self.group, self.id)] = [self.id, self.txt, self.img_url, self.url, 0, 0] # Последнии две переменные созданы для count likes
        path = os.path.expanduser('/Users/ilia/Documents/GitHub/yashmotbot/posts')
        file_name = os.path.join(path, f'{self.group}_{self.id}')
        if file_name not in sorted(glob.iglob(os.path.join('/Users/ilia/Documents/GitHub/yashmotbot/posts','*'))):
            with open (file_name, 'w') as file:
                file.write(str(self.dict))
                print('Новая запись') # if чтобы предотвратить перезапись
        else:
            print(self.dict)
        self.dict.clear()
        self.init2()

    def update(self):
        k = 100 # устанавливаем сколько файлов будет хранить директория posts
        self.get_dict()
        files_path = os.path.join('/Users/ilia/Documents/GitHub/yashmotbot/posts', '*')
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=False)
        if len(files) >= k:
            for i in range(len(files) - k):
                os.remove(os.path.join('/Users/ilia/Documents/GitHub/yashmotbot/posts', str(files[i])))
        self.save_dict()
        time.sleep(5)

farm = Posts(-114491444,1)
sicp = Posts(-180449771,1)
nike = Posts(-137481829,1)
rp = Posts(-92504944,1)
le = Posts(-123405556,1)
merch = Posts(-164624282,1)
box = Posts(-137681664,1)
menta = Posts(-202422190,1)


while True:
    farm.update()
    sicp.update()
    nike.update()
    rp.update()
    le.update()
    merch.update()
    box.update()
    menta.update()
    time.sleep(900)