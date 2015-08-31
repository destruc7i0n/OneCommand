from oneCommand import gen_stack, parse_commands

from Tkinter import *
import os, pyperclip
from tkFileDialog import askopenfilename
lastpath = os.path.join(os.path.expanduser("~"), "Documents")

class CustomText(Text):
	def __init__(self, *args, **kwargs):
		Text.__init__(self, *args, **kwargs)

	def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):

		start = self.index(start)
		end = self.index(end)
		self.mark_set("matchStart", start)
		self.mark_set("matchEnd", start)
		self.mark_set("searchLimit", end)

		count = IntVar()
		while True:
			index = self.search(pattern, "matchEnd","searchLimit",
								count=count, regexp=regexp)
			if index == "": break
			self.mark_set("matchStart", index)
			self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.tag_add(tag, "matchStart", "matchEnd")



def show(txt):
	wdw = Toplevel()
	l = Label(wdw,text=txt)
	Button(wdw, text="Ok", command=wdw.destroy,width=10).pack(side=BOTTOM)
	l.pack()
	l.focus_set()
	wdw.transient(root)
	wdw.grab_set()
	root.wait_window(wdw)
	#print 'done!'

def showInstructions():
	return show("""Prepend your command with `#` to comment it out.\nPrepend your command with `DEFINE:` to make it a variable definition.\nExample: `DEFINE:world hello` and `say $world` would say `hello`.\nPrepend your command with `INIT:` to make it only run when the structure is deployed.\nPrepend your command with `COND:` to make it a conditional command.""")

def high(*args):
	e1.highlight_pattern("^#.*$","grey",regexp=True)
	e1.highlight_pattern("\$\w+","light_blue",regexp=True)
	e1.highlight_pattern("^\s*COND:","light_red",regexp=True)
	e1.highlight_pattern("^\s*INIT:","light_green",regexp=True)
	#e1.highlight_pattern("^\s*DEFINE:\s*\w+","light_blue",regexp=True)
	e1.highlight_pattern("^\s*DEFINE:","blue",regexp=True)

def loadFile():
	global lastpath
	path = askopenfilename(title="Select file...", initialdir=lastpath, filetypes=[('All Files', '.*')])
	lastpath = os.path.dirname(path)
	if len(path) != 0:
		with open(path) as f:
			content = f.read()
			if len(e1.get("0.0",END)) != 1:
				e1.delete("1.0",END)
			e1.insert("1.0",content)
			high()
	else:
		show("No file selected.")

def copyIt():
	pyperclip.copy(out.get("1.0", END))

def lezDoThis():
	commands = []
	commands = e1.get('1.0', END).splitlines()
	if len(commands) == 0:
		show("No commands")
	mode = ""
	mode = v.get()
	if mode == "":
		show("Cannot get mode")
	init_commands, clock_commands = parse_commands(commands)
	final_command = gen_stack(init_commands, clock_commands, mode, False)
	out.configure(state=NORMAL)
	out.delete(1.0, END)
	if len(final_command) <= 32500 and final_command:
		out.insert(END, final_command)
		leng.set(str(len(final_command))+" characters")
	elif not final_command:
		show("No command generated")
		leng.set("0 characters")
	else:
		show("Command too large ({length} > 32500)".format(length=str(len(final_command))))
	out.configure(state=DISABLED)

if __name__ == "__main__":
	root = Tk()
	root.resizable(width=FALSE, height=FALSE)
	root.wm_title("1.9 Command Compiler - By TheDestruc7i0n and Wire Segal")
	img = PhotoImage(file="cmd.gif")
	root.tk.call("wm", "iconphoto", root._w, img)

	l1 = Label(root,text="Input:",font = "Helvetica 14 bold").grid(row=0,column=0,pady=2,padx=5,sticky=W)
	openfile = Button(root,text="Open File",width=10,command = loadFile).grid(row=0,column=0,pady=2,padx=5,sticky=E)

	e1 = CustomText(width = 70, height=30,wrap=NONE)

	e1.grid(row=1,column=0,pady=5,padx=5)
	e1.tag_configure("grey",foreground="#606060")
	e1.tag_configure("light_red",foreground="#FF5555")
	e1.tag_configure("light_green",foreground="#55FF55")
	e1.tag_configure("blue",foreground="#0000AA")
	e1.tag_configure("light_blue",foreground="#5555ff")
	e1.bind("<KeyRelease>", high)

	l2 = Label(root,text="""TheDestruc7i0n and Wire Segal's 1.9 One Command Generator\nPlease report any bugs at the GitHub repo: https://github.com/destruc7i0n/OneCommand/issues""").grid(row=1,column=1,rowspan=1,sticky=W+E+N)

	showinfo = Button(root,text="Show Instructions",width=30,command=showInstructions).place(relx=0.67, rely=0.2, anchor=W)

	v = StringVar()
	v.set("i")
	rb1 = Radiobutton(root, text="Manual", variable=v,value="m",height=2,width=5, bd=4).place(relx=0.7, rely=0.3, anchor=W)
	rb2 = Radiobutton(root, text="Instant", variable=v,value="i",height=2,width=5, bd=4).place(relx=0.8, rely=0.3, anchor=W)

	gen = Button(root,text="Generate",width=33,height=3,command=lezDoThis).place(relx=0.53, rely=0.52, anchor=W)#.grid(row=1,column=1,pady=2,padx=5,sticky=E)
	copyit = Button(root,text="Copy",width=33,height=3,command=copyIt).place(relx=0.77, rely=0.52, anchor=W)

	leng = StringVar()
	leng.set("0 characters")
	ccount = Label(root, textvariable=leng).place(relx=0.73, rely=0.43, anchor=W)


	out = Text(width = 60, height=13,padx=10)
	out.configure(state=NORMAL)
	out.configure(state=DISABLED)
	out.place(relx=0.53, rely=0.79, anchor=W)

	mainloop()