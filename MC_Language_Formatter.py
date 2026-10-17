import json
import zipfile
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfile

# Global var
format_list = 'formatlist.txt'
json_version = '1.16'
jar_version = '1.16.2'
reset = '§r'   # \xC2\xA7 = §

appdata = os.environ.get('APPDATA', os.path.expanduser('~/AppData/Roaming'))
current_directory = os.getcwd()
output_folder = 'output'
en_us_json_dir = 'assets/minecraft/lang/en_us.json'
minecraft_loaction =    lambda: appdata + '/.minecraft/'
hash_location =         lambda: minecraft_loaction() + 'assets/objects'
json_version_dir =      lambda: minecraft_loaction() + 'assets/indexes/'
json_dir =              lambda: json_version_dir() + json_version + '.json'
jar_version_dir =       lambda: minecraft_loaction() + 'versions/'
jar_dir =               lambda: jar_version_dir() + jar_version + '/' + jar_version + '.jar'
output_dir =            lambda: current_directory + '/' + output_folder

def list_dir(path):
    return os.listdir(path) if os.path.isdir(path) else []

json_version_list = [name.replace('.json','') for name in list_dir(json_version_dir()) if os.path.isfile(json_version_dir() + name)]
jar_version_list = [name for name in list_dir(jar_version_dir()) if os.path.isdir(jar_version_dir() + name)]

################################### Functions ###################################

def extract_en_us_json():
    global jar_version

    jar_version = opt_jar.get()

    if not os.path.exists(output_dir()):
        os.makedirs(output_dir())

    with zipfile.ZipFile(jar_dir(), 'r') as zip_ref:
        en_us = zip_ref.read(en_us_json_dir)
    with open(output_dir() + '/en_us.json', 'wb') as f:
        f.write(en_us)

    print('Extracted to /' + output_folder + '/en_us.json')

def unescape(text):
    # format list values are written like JSON string contents (e.g. \" or \n)
    try:
        return json.loads('"' + text + '"')
    except ValueError:
        return text

def read_format_list(path):
    # returns {translation key: (text in front, text at back, replace)}
    rules = {}
    with open(path, 'r', encoding='utf8') as f:
        for line in f.read().splitlines():
            key, separator, rule = line.partition('": ')
            key = key.strip()
            rule = rule.lstrip()
            if not separator or key.startswith(('/', '#')) or not rule.startswith('"'):   # ignore comments
                continue
            rule = rule[1:]
            if '§*' not in rule and rule.endswith('"'):     # replace format
                rules[key[1:]] = (unescape(rule[:-1]), '', True)
            else:                                           # add format
                front, _, back = rule.partition('§*')       #\xC2\xA7 = §
                if back.endswith('"'):
                    back = back[:-1]
                rules[key[1:]] = (unescape(front), unescape(back), False)
    return rules

def start():
    global format_list
    global json_version
    global jar_version

    format_list = browse_box.get(1.0,"end-1c")
    json_version = opt_json.get()
    jar_version = opt_jar.get()

    print('Gathering hash directories...')

    # special case for en_us.json, it is only stored in the jar
    with zipfile.ZipFile(jar_dir(), 'r') as zip_ref:
        languages = {'en_us.json': json.loads(zip_ref.read(en_us_json_dir).decode('utf8'))}

    # all other languages
    with open(json_dir(), 'r', encoding='utf8') as f:
        objects = json.load(f)['objects']
    lang_hashes = {name.partition('minecraft/lang/')[2]: entry['hash']
                   for name, entry in objects.items() if name.startswith('minecraft/lang/')}

    print('Formatting language files...')

    rules = read_format_list(format_list)

    if not os.path.exists(output_dir()):
        os.makedirs(output_dir())

    for lang_code in ['en_us.json'] + list(lang_hashes):

        print('Formatting ' + lang_code)

        if lang_code in languages:
            lang = languages[lang_code]
        else:
            lang_hash = lang_hashes[lang_code]
            with open(hash_location() + '/' + lang_hash[0:2] + '/' + lang_hash, 'r', encoding='utf8') as f:
                lang = json.load(f)

        # apply format to all languages from format list
        applied_format = {}
        for key, (front, back, replace) in rules.items():
            if key in lang:      #TODO: Option: use en_us if language is not complete (for testing use gv_im.json 1.16.2/1.16)(Does MC use custom en_us or default?)
                text = front if replace else front + lang[key] + back
                applied_format[key] = text + reset

        with open(output_dir() + '/' + lang_code, 'w', encoding='utf8') as f:
            json.dump(applied_format, f, ensure_ascii=False, indent=2)

    print('Done! Files saved to /' + output_folder + '/')


################################### GUI ###################################
root = tk.Tk()
s = ttk.Style()
s.theme_use('vista')


root.title('Minecraft Language Formatter')
#root.iconbitmap("logo.ico")
root.geometry("1200x650")
innerFrame = tk.Frame(root, borderwidth=25)
innerFrame.pack(fill="both", expand=True)
innerFrame.rowconfigure(5, weight=1)
innerFrame.columnconfigure(1, weight=1)
pad_grid = 6


info =  'Minecraft Language Formatter\n'\
        'made by Moggla\n\n'\
        'This program lets you format all language files for Minecraft.\n\n'\
        'The format list must be formatted like in the example and should be in a text file.\n'\
        'Languages may not have all translations in it.\n'
text = ttk.Label(innerFrame, text=info, justify='center')
text.grid(columnspan=3, column=0, row=0, padx=pad_grid, pady=pad_grid)


text = ttk.Label(innerFrame, text="Select version for en_us:")
text.grid(column=0, row=1, padx=pad_grid, pady=pad_grid)
opt_jar = ttk.Combobox(innerFrame, value=jar_version_list, state='readonly')
if jar_version_list:
    opt_jar.current(0)
opt_jar.grid(column=1, row=1, padx=pad_grid, pady=pad_grid, sticky="news")
extract_text = tk.StringVar()
extract_btn = ttk.Button(innerFrame, textvariable=extract_text, command=extract_en_us_json)
extract_text.set("Extract")
extract_btn.grid(column=2, row=1, padx=pad_grid, pady=pad_grid)


text = ttk.Label(innerFrame, text="Select version for all other languages:")
text.grid(column=0, row=2, padx=pad_grid, pady=pad_grid)
opt_json = ttk.Combobox(innerFrame, value=json_version_list, state='readonly')
if json_version_list:
    opt_json.current(0)
opt_json.grid(column=1, row=2, padx=pad_grid, pady=pad_grid, sticky="news")


text = ttk.Label(innerFrame, text="Format list:")
text.grid(column=0, row=3, padx=pad_grid, pady=pad_grid)
browse_box = tk.Text(innerFrame, height=1, width=50, padx=5, pady=5, wrap='none', font=('TkDefaultFont', 10))
browse_box.insert(1.0, current_directory + '\\' + format_list)
browse_box.grid(column=1, row=3, padx=pad_grid, pady=pad_grid, sticky="news")
file_var = tk.StringVar(innerFrame)
file_var.set([])
def browse_format_list():
    filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
    )
    file = askopenfile(parent=innerFrame, mode='rb', title="Open a File", filetype=filetypes)
    if file:
        file_var.set(file.name)
        browse_box.delete('1.0',"end")
        browse_box.insert(1.0, file.name)
browse_text = tk.StringVar()
browse_btn = ttk.Button(innerFrame, width=3, textvariable=browse_text, command=browse_format_list)
browse_text.set("...")
browse_btn.grid(column=1, row=3, padx=pad_grid, pady=pad_grid, sticky='E')


start_text = tk.StringVar()
start_btn = ttk.Button(innerFrame, textvariable=start_text, command=start)
start_text.set("Start Formatting all Languages")
start_btn.grid(column=1, row=4, padx=pad_grid, pady=pad_grid)


text = ttk.Label(innerFrame, text="Console:")
text.grid(column=0, row=5, padx=pad_grid, pady=pad_grid)
console_box = tk.Text(innerFrame, height=10, width=50, padx=5, pady=5, font=('TkDefaultFont', 8))
console_box.grid(column=1, row=5, padx=pad_grid, pady=pad_grid, sticky="news")
def redirector(inputStr):
    console_box.update_idletasks()
    console_box.insert("end", inputStr)
    console_box.see("end")
sys.stdout.write = redirector
sys.stderr.write = redirector

if not jar_version_list or not json_version_list:
    extract_btn.state(['disabled'])
    start_btn.state(['disabled'])
    print('No Minecraft installation found in ' + minecraft_loaction() + '\n'
          'Start Minecraft Java Edition at least once, then restart this program.')


root.mainloop()