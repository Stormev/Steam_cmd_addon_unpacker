import os
import shutil

text_about = "Программа предназначена для распоковки скачанных аддонов через steam cmds в рабочу папку с модами.\n" \
             "Введите help для инструкции\n" \
             "Введите exit для выхода\n"

text_help = "Чтобы запустить распаковщик введите SteamModUnpacker Input Output *prefix " \
            "*separate_descriptor " \
            "*descriptor_name *descriptor_format \n" \
            "Аргументы помеченные звездочкой необязательны" \
            "Input - Папка откуда программа будет брать аддоны\n" \
            "Output - Куда программа будет распаковывать\n" \
            "prefix - Префик папки (чтобы можно было отличить от других)\n" \
            "separate_descriptor - Отделять дескриптор аддона из его родной папки в папку распаковки\n" \
            "descriptor_name -  Задаёт стандартное имя дескриптора\n" \
            "descriptor_format - Задаёт стандартный формат дескриптора\n"


# Модуль
class SteamModUnpacker:
    def __init__(self, f_in, f_out, prefix="auto_", separate_descriptor=True,
                 descriptor_name='descriptor', descriptor_format='.mod'):
        # Распаковать из директории
        self.folder_input = f_in
        # Директория куда будет распакованно
        self.folder_output = f_out
        # Префик папки (чтобы можно было отличить от других)
        self.prefix = prefix
        # Отделять дескриптор аддона из его родной папки в папку распаковки
        self.separate_descriptor = separate_descriptor

        # Стандартное имя дескриптора
        self.descriptor_name = descriptor_name
        # Стандартный формат (.mod)
        self.descriptor_format = descriptor_format

    # Проверяем наличие запретных знаков в имени аддона
    def check_correct_name_file(self, w):
        bad_sym = ['!', '@', '#', '$', '%', '^', '&', ':', '>', '<', '}', '{', "/"]
        w_list = list(w)
        for sym_indx in range(len(w_list)):
            if w[sym_indx] in bad_sym:
                w_list[sym_indx] = '_'
        return ''.join(w_list)

    # Функция распаковщик
    def unpack(self):
        print('Начало распаковки --------------------')

        # Список результата распаковки
        not_loaded = []
        already_exist = []
        success = []

        # Проверка наличие путей
        if os.path.exists(self.folder_input) and os.path.exists(self.folder_output) and self.prefix:
            max_range = len(os.listdir(self.folder_input))
            descriptor_name = f"{self.descriptor_name}{self.descriptor_format}"

            # Проходится по списку изначальных аддонов
            for folder_name, indx in zip(os.listdir(self.folder_input), range(max_range)):
                print(f'В процессе: {folder_name}', f"{round((indx+1)/max_range*100)}%")
                mod_path = f"{self.folder_input}/{folder_name}"
                descriptor = f"{self.folder_input}/{folder_name}/{descriptor_name}"

                if not os.path.exists(descriptor):
                    not_loaded.append(f"({'DescriptorNotFound'}, {folder_name}, {mod_path})")
                    continue

                # Поиск названия мода
                mod_name = None
                with open(descriptor, "r", encoding='utf-8') as f:
                    meta = list(map(lambda x: x.rstrip('\n'), f.readlines()))
                    for val in range(len(meta)):
                        if "name=" in meta[val]:
                            mod_name = meta[val][5:].strip('"').replace(' ', '_')

                if not mod_name:
                    not_loaded.append(f"({'NotFoundName'}, {folder_name}, {mod_path})")
                    continue

                # создание директории куда копировать распакованный мод
                mod_name_tocopy = self.check_correct_name_file(self.prefix + mod_name)
                mod_dir_tocopy = f"{self.folder_output}/{mod_name_tocopy}"
                descriptor_name_tocopy = f"descriptor_{mod_name_tocopy}.mod"
                if self.separate_descriptor:
                    descriptor_dir_tocopy = f"{self.folder_output}/{descriptor_name_tocopy}"
                else:
                    descriptor_dir_tocopy = f"{mod_dir_tocopy}/{descriptor_name}"

                # Функция перезаписи дескриптора где перезаписывается path либо добавляется
                def override_descriptor(descriptor_path):
                    override_id = None
                    text_data = None
                    with open(descriptor_path, "r", encoding="utf-8") as f:
                        text_data = f.readlines()
                        meta = list(map(lambda x: x.rstrip('\n'), text_data))

                        for string, indx_meta in zip(meta, range(len(meta))):
                            if 'path=' in string:
                                override_id = indx_meta

                    if not override_id:
                        with open(descriptor_path, "a", encoding="utf-8", newline='\n') as f:
                            f.write(f'\npath="{mod_dir_tocopy}"')
                    else:
                        with open(descriptor_path, "w", encoding="utf-8", newline='\n') as f:
                            print(f'Перезапись файла {descriptor_path}')
                            text_data[override_id] = f'path="{mod_dir_tocopy}"\n'
                            f.writelines(text_data)

                if os.path.exists(mod_dir_tocopy):
                    already_exist.append(f"({mod_name}, {folder_name}, {mod_path})")

                    if not os.path.exists(descriptor_dir_tocopy) and self.separate_descriptor:
                        shutil.copy(descriptor, descriptor_dir_tocopy)
                        override_descriptor(descriptor_dir_tocopy)
                    continue

                # Копирование
                shutil.copytree(mod_path, mod_dir_tocopy)
                if self.separate_descriptor:
                    shutil.copy(descriptor, descriptor_dir_tocopy)

                # Перезапись
                override_descriptor(descriptor_dir_tocopy)

                success.append(f"({mod_name}, {folder_name}, {mod_path})")

        print('Распаковка окончена ------------------')
        print(f'>> Успешно: {",".join(success) or "None"}\n')
        print(f'>> Незагруженно: {", ".join(not_loaded) or "None"}\n')
        print(f'>> Уже существуют: {", ".join(already_exist) or "None"}\n')


if __name__ == "__main__":
    print(text_about)
    # Консоль
    while True:
        message = input()

        if message == 'help':
            print(text_help)

        elif message == 'exit':
            break

        elif message[:16] == 'SteamModUnpacker':
            # Сплитер (почему не метод split - тк в названии некоторых папок есть пробелы
            # и требуется разделить их на объекты)
            data = []
            world = ''
            world_flag = False
            message_cut = message[17:]
            for sym, indx in zip(message_cut, range(len(message_cut))):
                if sym == '"' or sym == "'":
                    world_flag = not world_flag
                if sym == ' ' and not world_flag:
                    data.append(world.strip('"').strip("'"))
                    world = ''
                else:
                    world += sym
                if indx >= len(message_cut) - len(data):
                    data.append(world.strip('"').strip("'"))

            print(data)
            if len(data) < 2:
                print('Укажите папки загрузки и выгрузки')
                continue
            #'D:/Games/SteamMods/steamapps/workshop/content/281990'
            #'C:/Users/User/Documents/Paradox Interactive/Stellaris/mod'
            try:
                obj = SteamModUnpacker(data[0], data[1], *data[2:])
                obj.unpack()
            except Exception as err:
                print('Ошибка\n', err)

        elif message == 'debug':
            obj = SteamModUnpacker('D:/Games/SteamMods/steamapps/workshop/content/281990',
                                   'C:/Users/User/Documents/Paradox Interactive/Stellaris/mod')
            obj.unpack()

        else:
            print('Неизвестная команда')
            print(message)
