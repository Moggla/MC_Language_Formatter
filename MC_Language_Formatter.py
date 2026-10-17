import json
import queue
import threading
import traceback
import zipfile
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfile

# Global var
format_list = 'formatlist.txt'
reset = '§r'   # \xC2\xA7 = §

appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
output_folder = 'output'
en_us_json_dir = 'assets/minecraft/lang/en_us.json'    # path inside the jar
minecraft_location =    appdata / '.minecraft'
hash_location =         minecraft_location / 'assets' / 'objects'
json_version_dir =      minecraft_location / 'assets' / 'indexes'
jar_version_dir =       minecraft_location / 'versions'
output_dir =            Path.cwd() / output_folder
json_dir =              lambda json_version: json_version_dir / (json_version + '.json')
jar_dir =               lambda jar_version: jar_version_dir / jar_version / (jar_version + '.jar')

json_version_list = [p.stem for p in json_version_dir.glob('*.json') if p.is_file()]
jar_version_list = [p.name for p in jar_version_dir.glob('*') if p.is_dir()]

################################### Functions ###################################

def extract_en_us_json():
    jar_version = opt_jar.get()

    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(jar_dir(jar_version), 'r') as zip_ref:
        (output_dir / 'en_us.json').write_bytes(zip_ref.read(en_us_json_dir))

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

def start(format_list_path, json_version, jar_version):
    print('Gathering hash directories...')

    # special case for en_us.json, it is only stored in the jar
    with zipfile.ZipFile(jar_dir(jar_version), 'r') as zip_ref:
        languages = {'en_us.json': json.loads(zip_ref.read(en_us_json_dir).decode('utf8'))}

    # all other languages
    with open(json_dir(json_version), 'r', encoding='utf8') as f:
        objects = json.load(f)['objects']
    lang_hashes = {name.partition('minecraft/lang/')[2]: entry['hash']
                   for name, entry in objects.items() if name.startswith('minecraft/lang/')}

    print('Formatting language files...')

    rules = read_format_list(format_list_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    for lang_code in ['en_us.json'] + list(lang_hashes):

        print('Formatting ' + lang_code)

        if lang_code in languages:
            lang = languages[lang_code]
        else:
            lang_hash = lang_hashes[lang_code]
            with open(hash_location / lang_hash[0:2] / lang_hash, 'r', encoding='utf8') as f:
                lang = json.load(f)

        # apply format to all languages from format list
        applied_format = {}
        for key, (front, back, replace) in rules.items():
            if key in lang:      #TODO: Option: use en_us if language is not complete (for testing use gv_im.json 1.16.2/1.16)(Does MC use custom en_us or default?)
                text = front if replace else front + lang[key] + back
                applied_format[key] = text + reset

        with open(output_dir / lang_code, 'w', encoding='utf8') as f:
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
browse_box.insert(1.0, str(Path.cwd() / format_list))
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


def start_in_background():
    # formatting runs in a separate thread so the window stays responsive
    args = (browse_box.get(1.0,"end-1c"), opt_json.get(), opt_jar.get())
    def work():
        try:
            start(*args)
        except Exception:
            traceback.print_exc()
        console_queue.put(None)     # tell the GUI that formatting is done
    extract_btn.state(['disabled'])
    start_btn.state(['disabled'])
    threading.Thread(target=work, daemon=True).start()
start_text = tk.StringVar()
start_btn = ttk.Button(innerFrame, textvariable=start_text, command=start_in_background)
start_text.set("Start Formatting all Languages")
start_btn.grid(column=1, row=4, padx=pad_grid, pady=pad_grid)


text = ttk.Label(innerFrame, text="Console:")
text.grid(column=0, row=5, padx=pad_grid, pady=pad_grid)
console_box = tk.Text(innerFrame, height=10, width=50, padx=5, pady=5, font=('TkDefaultFont', 8))
console_box.grid(column=1, row=5, padx=pad_grid, pady=pad_grid, sticky="news")
# tkinter widgets may only be used from the main thread, so prints are queued
console_queue = queue.Queue()
class Redirector:
    # replaces sys.stdout/stderr, which are None in a --windowed executable
    def write(self, inputStr):
        console_queue.put(inputStr)
    def flush(self):
        pass
def poll_console():
    while not console_queue.empty():
        inputStr = console_queue.get()
        if inputStr is None:
            extract_btn.state(['!disabled'])
            start_btn.state(['!disabled'])
        else:
            console_box.insert("end", inputStr)
            console_box.see("end")
    root.after(50, poll_console)
sys.stdout = sys.stderr = Redirector()
poll_console()

if not jar_version_list or not json_version_list:
    extract_btn.state(['disabled'])
    start_btn.state(['disabled'])
    print('No Minecraft installation found in ' + str(minecraft_location) + '\n'
          'Start Minecraft Java Edition at least once, then restart this program.')


root.mainloop()