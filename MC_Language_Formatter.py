import zipfile
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfile


format_list = 'formatlist.txt'
json_version = '1.16'
jar_version = '1.16.2'
end_line = '\xC2\xA7r",'   # \xC2\xA7 = §

home = os.environ['HOMEPATH']
current_directory = os.getcwd()
output_folder = 'output'
minecraft_loaction = home + '/AppData/Roaming/.minecraft/'
hash_location = minecraft_loaction + 'assets/objects'
json_version_dir = minecraft_loaction + 'assets/indexes/'
json_dir = json_version_dir + json_version + '.json'
jar_version_dir = minecraft_loaction + 'versions/'
jar_dir = jar_version_dir + jar_version + '/' + jar_version + '.jar'
en_us_json_dir = 'assets/minecraft/lang/en_us.json'
output_dir = current_directory + '/' + output_folder

json_version_list = [name for name in os.listdir(json_version_dir) if os.path.isfile(json_version_dir + name)]
jar_version_list = [name for name in os.listdir(jar_version_dir) if os.path.isdir(jar_version_dir + name)]

################################### Functions ###################################

def extract_en_us_json():
    json_version = opt_json.get()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(jar_dir, 'r') as zip_ref:
        zip_ref.extract(en_us_json_dir, output_dir + '/')
    
    if os.path.exists(output_dir + '/en_us.json'):
        os.remove(output_dir + '/en_us.json')
    os.rename(output_dir + '/' + en_us_json_dir, output_dir + '/en_us.json')
    os.removedirs(output_dir + '/' + en_us_json_dir[:-10])

    print('Extracted to /' + output_folder + '/' + en_us_json_dir)

def start():
    format_list = browse_box.get(1.0,"end-1c")
    json_version = opt_json.get()
    jar_version = opt_jar.get()
    
    print('Gathering hash directories...')

    # special case for en_us.json
    lang_code = ['en_us.json']
    lang_dir = [output_dir + '/' + en_us_json_dir]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(jar_dir, 'r') as zip_ref:
        zip_ref.extract(en_us_json_dir, output_dir + '/')

    # all other languages
    with open(json_dir, 'r') as f:
        json_contents = f.read()
    json_contents_splited = json_contents.split(',')

    for line in json_contents_splited:
        line = line.partition('minecraft/lang/')[2]
        if line != '':
            line = line.partition('": {"hash": "')
            lang_code.append(line[0])
            lang_hash = line[2][:-1]
            lang_dir.append(hash_location + '/' + lang_hash[0:2] + '/' + lang_hash)


    print('Formatting language files...')

    # generate list to help find all lines that have to get formated
    with open(format_list, 'r') as f:
        format_list_contents = f.read()
    format_list_contents_splited = format_list_contents.split('\n')

    find_to_format = []
    format = []
    for line in format_list_contents_splited:
        if '": ' in line:
            line = line.partition('": ')
            if (line[0][0] != '/') & (line[0][0] != '#'):   # ignore comments
                find_to_format.append(line[0] + line[1])
                format.append(line[2].partition('\xC2\xA7*'))


    # formatting language files
    for lang_loop in range(len(lang_code)):

        print('Formatting ' + lang_code[lang_loop])

        with open(lang_dir[lang_loop], 'r') as f:
            lang_dir_contents = f.read()
        lang_dir_contents_splited = lang_dir_contents.split('\n')

        # find all lines from current language that have to get changed
        current_lang = [s for s in lang_dir_contents_splited if any(xs in s for xs in find_to_format)]

        # apply format to all languages from format list
        apllied_format = ['{']
        for i in range(len(find_to_format)):
            line = [s for s in current_lang if find_to_format[i] in s]
            if line != []:      #TODO: Option: use en_us if language is not complete (for testing use gv_im.json 1.16.2/1.16)(Does MC use custom en_us or default?)
                line = line[0].partition('": ')
                if (format[i][0][-1] == '"') & (format[i][0].count('"') > 1):   # replace format
                    apllied_format.append( line[0] + line[1] + format[i][0][:-1] + end_line )
                else:                                                           # add format
                    apllied_format.append( line[0] + line[1] + format[i][0] + line[2][1:-2] + format[i][2] + end_line )
        # add { } and remove last ,
        apllied_format[-1] = apllied_format[-1][:-1]
        apllied_format.append('}')

        with open(output_folder + '/' + lang_code[lang_loop], 'w') as f:
            f.write('\n'.join(apllied_format))

    os.remove(output_dir + '/' + en_us_json_dir)
    os.removedirs(output_dir + '/' + en_us_json_dir[:-10])

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
opt_json = ttk.Combobox(innerFrame, value=json_version_list, state='readonly')
opt_json.current(0)
opt_json.grid(column=1, row=1, padx=pad_grid, pady=pad_grid, sticky="news")
extract_text = tk.StringVar()
extract_btn = ttk.Button(innerFrame, textvariable=extract_text, command=lambda:extract_en_us_json())
extract_text.set("Extract")
extract_btn.grid(column=2, row=1, padx=pad_grid, pady=pad_grid)


text = ttk.Label(innerFrame, text="Select version for all other languages:")
text.grid(column=0, row=2, padx=pad_grid, pady=pad_grid)
opt_jar = ttk.Combobox(innerFrame, value=jar_version_list, state='readonly')
opt_jar.current(0)
opt_jar.grid(column=1, row=2, padx=pad_grid, pady=pad_grid, sticky="news")


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
browse_btn = ttk.Button(innerFrame, width=3, textvariable=browse_text, command=lambda:browse_format_list())
browse_text.set("...")
browse_btn.grid(column=1, row=3, padx=pad_grid, pady=pad_grid, sticky='E')


start_text = tk.StringVar()
start_btn = ttk.Button(innerFrame, textvariable=start_text, command=lambda:start())
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


root.mainloop()