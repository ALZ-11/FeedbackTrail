
def point_updateI():
		global timeI, loading_dotsI, loadingButton_hiddenI
		if timeI <= 1000:
			if loadingButton_hiddenI.cget("text") != "loading...":
				loading_dotsI += "."
				timeI += 500
			else:
				loading_dotsI = "loading."
				timeI += 500
		else:
			point_updateII()
			return
		loadingButton_hiddenI.configure(text = loading_dotsI)        
		Traitement.after(500, point_updateI)

	loading_dotsI = "loading"
	loadingButton_hiddenI = Button(Traitement, text = loading_dotsI, font = "TkDefaultFont 24 bold", fg = "#F77C3F", bg = "#A1B2C3", command= point_updateI, bd = 0)
	timeI = 0

	loadingButton_hiddenI.place(relx = 0.5, rely = 0.5, anchor = CENTER)
	loadingButton_hiddenI.invoke()