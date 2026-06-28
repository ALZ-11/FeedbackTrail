# placeholder funcs

def current_screen():
	global CurrentScreen 
	def next_screen_func():
		next_screen()
	try:
		NextScreen.destroy()
	except:
		pass
	try:
		PreviousScreen.destroy()
	except:
		pass
	CurrentScreen = Tk()
	CurrentScreen.geometry("1000x800")

	def func():
		pass