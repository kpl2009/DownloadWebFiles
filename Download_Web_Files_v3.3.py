#Kendall Larson
#05-19-2015
#UPDATED: 10-28-2019
# - error correction attempt in download file FN
# - estimated time remaining
#Python v3.5+
#Download Web Files with GUI

#-------------------------------------------------< Notes >--------------------------------------------------------------------------------------------------------

# add persistence, open text file of dl links and keep track of whats been downloaded already so you can exit program and restart where it left off 
# add some sort of CRC or corruption check/mitigation
# make the program callable from command line with args and no gui
# convert code to use tkinter Place instead of pack									 

#-------------------------------------------------------< Modules >----------------------------------------------------------------------------------------------------------------

import sys
import os
import threading
import queue
import socket
import time
import datetime
import platform
import urllib.request
import urllib.parse
import urllib.error
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
#import ssl
#import hashlib
#import gzip
#import base64
#import binascii
#import zlib

#------------------------------------------------------< Functions >------------------------------------------------------------------------------------------------------------------

#def getMd5_FN(data):
#	if type(data).__name__ == 'str':
#		return hashlib.md5(data).hexdigest()
#	else:
#		return hashlib.md5(data)

#def credEntryDiag_FN():
#	credEntryDiag_UI = tk.Toplevel()
#	credEntryDiag_UI.title('Logon Credentials')
#	authFrame_UI = tk.Frame(credEntryDiag_UI, bg='#707070')
#	userLabel_UI = tk.Label(authFrame_UI, text='Username:', bg='#707070', fg='white')
#	passLabel_UI = tk.Label(authFrame_UI, text='Password:', bg='#707070', fg='white')
#	userEntry_UI = tk.Entry(authFrame_UI, width=20)
#	passEntry_UI = tk.Entry(authFrame_UI, width=20, show="*")
#	cancelBtn_UI = tk.Button(text='Cancel', command=credEntryDiag_UI.destroy())
#	authFrame_UI.pack(fill=tk.X, padx=240, pady=5)
#	userLabel_UI.pack(side=tk.LEFT, fill=tk.X)
#	userEntry_UI.pack(side=tk.LEFT, fill=tk.X, padx=5)
#	passLabel_UI.pack(side=tk.LEFT, fill=tk.X)
#	passEntry_UI.pack(side=tk.LEFT, fill=tk.X, padx=5)
#	pass_STR = passEntry_UI.get()

#def auth_FN(url_STR):
#	sslContext_OBJ = ssl.create_default_context()
#	httpsHandler_OBJ = urllib.request.HTTPSHandler(context=sslContext_OBJ)
#	authManager_OBJ = urllib.request.HTTPPasswordMgrWithDefaultRealm()
#	parse_LST = urllib.parse.urlparse(url_STR)
#	domain_STR = parse_LST[1]
#	domain_STR = r'https://{}/'.format(domain_STR)
#	authManager_OBJ.add_password(None, domain_STR, user_STR, pass_STR)
#	authHandler_OBJ = urllib.request.HTTPBasicAuthHandler(authManager_OBJ)
#	opener_OBJ = urllib.request.build_opener(httpsHandler_OBJ, authHandler_OBJ)
#	urllib.request.install_opener(opener_OBJ)

def threadAction_FN(action_FN):
	queue_SYS.put(action_FN)

def checkQueue_FN(mainWindow_UI):
	while True:
		try:
			task_SYS = queue_SYS.get(block=False)
		except:
			break
		else:
			mainWindow_UI.after_idle(task_SYS)
	mainWindow_UI.after(100, lambda: checkQueue_FN(mainWindow_UI))

def listCompare_FN(list1, list2):
	listDiff_LST = list(set(list1) - set(list2))
	return listDiff_LST

def pause_FN():
	global pauseState_BL
	pauseState_BL = True
	
def fileDiag_FN():
	global outDir_STR
	outDir_STR = tk.filedialog.askdirectory()
	if not outDir_STR:
		outDir_STR = cwd_STR
	fileInfoLbl_UI.configure(text='Current source file = {0} | Current output directory = {1}'.format(sourceDir_STR, outDir_STR))

def sourceFileDiag_FN():
	global sourceDir_STR
	global sourceFileSelected_BL
	sourceDir_STR = tk.filedialog.askopenfilename()
	if sourceDir_STR:
		sourceFileSelected_BL = True
	fileInfoLbl_UI.configure(text='Current source file = {0} | Current output directory = {1}'.format(sourceDir_STR, outDir_STR))

def sourceFileReader_FN(sourceFilePath_STR):
	global urlList_LST
	with open(sourceFilePath_STR, 'r') as sourceFile_FIL:
		for line_STR in sourceFile_FIL:
			try:
				urlList_LST.append(line_STR.rstrip())
			except() as err_sourceFileReaderFN:
				print(err_sourceFileReaderFN)
				continue

def sourceFileWriter_FN(newSourceFilePath_STR, listDiff_LST):
	with open(newSourceFilePath_STR, 'w') as newSourceFile_FIL:
		for url_STR in errors_LST:
			newSourceFile_FIL.write(url_STR)
	
def start_FN():
	global urlList_LST
	global errors_LST
	global newSourceFilePath_STR
	global dateTimeStartFN_STR
	threadAction_FN(lambda: startBtn_UI.config(text='Pause', command=pause_FN))
	dateTimeStartFN_STR = datetime.datetime.now().strftime("%m-%d-%y_%H-%M")
	failedDownloadsFile_STR = 'FailedDownloadLinks-{}'.format(dateTimeStartFN_STR) + r'.' + 'txt'
	newSourceFilePath_STR = os.path.join(outDir_STR, failedDownloadsFile_STR)
	if sourceFileSelected_BL == False:
		urlList_LST = list(urlTextbox_UI.get('1.0', tk.END).splitlines())
	else:
		sourceFilePath_STR = sourceDir_STR
		try:
			sourceFileReader_FN(sourceFilePath_STR)
		except() as sourceFileReaderErr_STR:
			print(sourceFileReaderErr_STR)
	try:
		threadAction_FN(lambda: urlTextbox_UI.delete('1.0', tk.END))
		threadAction_FN(lambda: urlTextbox_UI.configure(state='disabled'))
	except() as urlTextboxErr_STR:
		print(urlTextboxErr_STR)
	urlListCount_STR = str(len(urlList_LST))
	for item_INT, url_STR in enumerate(urlList_LST):
		index_INT = item_INT
		index_INT += 1
		index_STR = str(index_INT)
		indexGUI_STR = index_STR + r'.' + '0'
		indexEndGUI_STR = index_STR + r'.' + 'end'
		name_STR = namePrefix_STR + index_STR
		fileName_STR = os.path.join(outDir_STR, name_STR)
		for attempt in range(30):
			attempt_STR = str(attempt + 1)
			try:
				downloadFile_FN(fileName_STR, url_STR, index_INT, urlListCount_STR)
			except ValueError as valueErrorMsg_STR:
				print('value error occured during downloadFile_FN function call for download: {}'.format(url_STR))
				print('Retry #{0} for download: {1} in 5 seconds...'.format(attempt_STR, url_STR))
				time.sleep(5)
				continue
			except (urllib.error.URLError) as urlErrorMsg_STR:
				print('URL error occured during downloadFile_FN function call for download: {}'.format(url_STR))
				print('Retry #{0} for download: {1} in 5 seconds...'.format(attempt_STR, url_STR))
				time.sleep(5)
				continue
			except (IOError) as errorMsg_STR:
				print('IO error occured while downloading {}'.format(url_STR))
				print(errorMsg_STR)
				print('Retry #{0} for download: {1} in 5 seconds...'.format(attempt_STR, url_STR))
				time.sleep(5)
				continue
			except () as generalError_STR:
				print('An error occured during downloadFile_FN function call for download: {}'.format(url_STR))
				print(generalError_STR)
				print('Retry #{0} for download: {1} in 5 seconds...'.format(attempt_STR, url_STR))
				time.sleep(5)
				continue
			else:
				break
		else:
			print('Failed download for {}'.format(url_STR))
			errors_LST.append(url_STR)
			repString_STR = 'Download Failed : {}'.format(url_STR)
			try:
				threadAction_FN(lambda: urlTextbox_UI.configure(state='normal'))
				threadAction_FN(lambda: urlTextbox_UI.delete(indexGUI_STR, indexEndGUI_STR))
				threadAction_FN(lambda: urlTextbox_UI.insert(indexGUI_STR, repString_STR))
			except() as urlTextboxConfigErr_STR:
				print(urlTextboxConfigErr_STR)
	try:
		threadAction_FN(lambda: exitSequence_FN(urlListCount_STR, urlList_LST, urlListCp_LST))
	except() as exitSequenceErr_STR:
		print(exitSequenceErr_STR)
		sys.exit()

def progressBar_FN(fileSize_INT, fileDataSz_INT, fileSizeMb_STR, downloadStartTime_INT, fileSizeMb_INT):
	currentTime_INT = time.time()
	timeElapsed_INT = (currentTime_INT - downloadStartTime_INT)
	percent_INT = fileDataSz_INT * 100/fileSize_INT
	currentfileSizeMb_INT = round(fileDataSz_INT/1024/1024, 2)
	downloadSpeed_INT = round(currentfileSizeMb_INT/timeElapsed_INT, 2)
	downloadSpeed_STR = '{} MB/s'.format(str(downloadSpeed_INT))
	downloadProgress_STR = str(currentfileSizeMb_INT) + ' MB / {}'.format(fileSizeMb_STR)
	sizeRemaining_INT = (fileSizeMb_INT - currentfileSizeMb_INT)
	estTimeRemaining_INT = round(sizeRemaining_INT/downloadSpeed_INT)
	estTimeRemaining_STR = str(estTimeRemaining_INT)
	threadAction_FN(lambda: progressLbl_UI.configure(text='Download Speed: {0}  |  Progress: {1}  |  Est. Time Remaining {2} Seconds'.format(downloadSpeed_STR, downloadProgress_STR, estTimeRemaining_STR)))
	progressBar_UI['value'] = percent_INT
	progressBar_UI.step()

def getInfo_FN(url_STR, urlOpen_BIN):
	urlInfo_STR = urlOpen_BIN.info()
	try:
		urlInfoFileName_STR = urlInfo_STR.get_filename()
	except() as err_urlInfoFileName_STR:
		print(err_urlInfoFileName_STR)
		urlInfoFileName_STR = 'Placeholder'
	try:
		urlInfo_STR = urlInfo_STR.get_all
		fileSize_STR = urlInfo_STR('Content-Length')
	except() as err_urlInfo:
		print(err_urlInfo)
	if fileSize_STR is not None:
		fileSize_STR = fileSize_STR[0]
		fileSize_INT = int(fileSize_STR)
		fileSizeMb_INT = round(int(fileSize_STR)/1024/1024, 2)
		fileSizeMb_STR = '{} MB'.format(str(fileSizeMb_INT))
	else:
		fileSize_INT = 1
		fileSizeMb_STR = None
	if urlInfoFileName_STR is not None:
		urlInfoFileName_STR = urlInfoFileName_STR.strip()
	else:
		urlInfoFileName_STR = 'Placeholder'
	return {'urlInfoFileName_STR':urlInfoFileName_STR, 'fileSize_INT':fileSize_INT, 'fileSizeMb_STR':fileSizeMb_STR, 'fileSizeMb_INT':fileSizeMb_INT}

def downloadFile_FN(fileName_STR, url_STR, index_INT, urlListCount_STR):
	global urlListCp_LST
	global pauseState_BL
	ioSize_INT = 8192 #bytes
	socketTimeout_INT = 5 #seconds
	fileDataSz_INT = 0
	rwCount_INT = 0
	exceptCnt_INT = 0
	downloadCount_STR = str(index_INT)
	socket.setdefaulttimeout(socketTimeout_INT)
	with open(fileName_STR, 'wb') as outFile_FIL:
		urlOpen_BIN = urllib.request.urlopen(url_STR)
		try:
			fileInfo_DIC = getInfo_FN(url_STR, urlOpen_BIN)
			urlInfoFileName_STR = fileInfo_DIC['urlInfoFileName_STR']
			fileSize_INT = fileInfo_DIC['fileSize_INT']
			fileSizeMb_STR = fileInfo_DIC['fileSizeMb_STR']
			fileSizeMb_INT = fileInfo_DIC['fileSizeMb_INT']
		except() as InfoError_STR:
			print('unable to retrieve file metadata for {}'.format(url_STR))
			print(InfoError_STR)
			fileSize_INT = 1
			fileSizeMb_STR = None
			urlInfoFileName_STR = 'Placeholder'
		try:
			threadAction_FN(lambda: fileInfoLbl_UI.configure(text='Download = {0}/{1}  -  {2}'.format(downloadCount_STR, urlListCount_STR, urlInfoFileName_STR)))
		except() as fileInfoLblErr_STR:
			print(fileInfoLblErr_STR)
		downloadStartTime_INT = time.time()
		while True:
			if pauseState_BL == True:
					tk.messagebox.showinfo(message='Paused, press <OK> to continue')
					pauseState_BL = False
			else:
				try:
					fileData_BIN = urlOpen_BIN.read(ioSize_INT)
					if not fileData_BIN:
						break
					outFile_FIL.write(fileData_BIN)
					fileDataSz_INT += ioSize_INT
					rwCount_INT += 1
				except () as IOerror_STR:
					exceptCnt_INT += 1
					if (exceptCnt_INT < 30):
						print('Error: {0} Except Count {1}'.format(IOerror_STR, exceptCnt_INT))
						time.sleep(5)
						continue
					else:
						print('Download: {} failed'.format(url_STR))
						break
				if (rwCount_INT > 200):
					try:
						progressBar_FN(fileSize_INT, fileDataSz_INT, fileSizeMb_STR, downloadStartTime_INT, fileSizeMb_INT)
					except:
						continue
					rwCount_INT = 0
	if urlInfoFileName_STR is not None:
		newFileName_STR = os.path.join(outDir_STR, urlInfoFileName_STR)
		try:
			os.rename(fileName_STR, newFileName_STR)
		except:
			newnewFileName_STR = newFileName_STR + dateTimeStartFN_STR
			os.rename(fileName_STR, newnewFileName_STR)
		repString_STR = 'Download Finished : {}'.format(urlInfoFileName_STR) + '\n'
	else:
		repString_STR = 'Download Finished : {}'.format(url_STR)
	index_STR = downloadCount_STR + r'.' + '0'
	indexEnd_STR = downloadCount_STR + r'.' + 'end'
	urlListCp_LST.append(url_STR)
	try:
		threadAction_FN(lambda: urlTextbox_UI.configure(state='normal'))
		threadAction_FN(lambda: urlTextbox_UI.delete(index_STR, indexEnd_STR))
		threadAction_FN(lambda: urlTextbox_UI.insert(index_STR, repString_STR))
	except() as urlTextboxConfigErr_STR:
		print(urlTextboxConfigErr_STR)
	
def exitSequence_FN(urlListCount_STR, urlList_LST, urlListCp_LST):
	currentTime_STR = datetime.datetime.now()
	try:
		listDiff_LST = listCompare_FN(urlList_LST, urlListCp_LST)
		if not listDiff_LST:
			pass
		else:
			sourceFileWriter_FN(newSourceFilePath_STR, listDiff_LST)
	except() as listCompareErr_STR:
		print(listCompareErr_STR)
	exitWindow_UI = tk.Toplevel()
	exitWindow_UI.title('Downloads Finished')
	exitWindow_UI.geometry('600x600')
	exitWindow_UI.configure()
	errorsCount_UI = tk.Label(exitWindow_UI, text='Failed Downloads Count: {}'.format(len(errors_LST)))
	errorFrame_UI = tk.Frame(exitWindow_UI, height=300, bd=5)
	errorTextbox_UI = tk.Text(errorFrame_UI, bg='#1c1c1c', fg='white', font=(fontTbox_STR, 10), wrap=tk.NONE)
	exitBtnF_UI = tk.Button(exitWindow_UI, text='Exit', command=lambda: exitF_FN(exitWindow_UI))
	errorsCount_UI.pack()
	errorFrame_UI.pack()
	errorTextbox_UI.pack()
	exitBtnF_UI.pack()
	try:
		for index_INT, url_STR in enumerate(errors_LST):
			index_INT += 1
			index_STR = str(index_INT)
			threadAction_FN(lambda: errorTextbox_UI.configure(state='normal'))
			threadAction_FN(lambda: errorTextbox_UI.insert(index_STR, url_STR))
	except() as errorTextboxErr_STR:
		print(errorTextboxErr_STR)

def exit_FN():
	mainWindow_UI.quit()
	sys.exit()
	
def exitF_FN(exitWindow_UI):
	exitWindow_UI.quit()
	sys.exit()

#-------------------------------------------------------< Main >------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
	fontBtn_STR = 'TkDefaultFont'
	fontTbox_STR = 'TkDefaultFont'
	fontLbl_STR = 'TkDefaultFont'
	fSzTbox_INT = 35
	urlFrameHeight_INT = 705
	btnBrd_INT = 1
	try:
		platform_STR = platform.system()
		if platform_STR == 'Windows':
			fontBtn_STR = 'Segoe UI'
			fontTbox_STR = 'Segoe UI'
			fontLbl_STR = 'Segoe UI'
			fSzTbox_INT = 30 #31
			urlFrameHeight_INT = 700 #705
			btnBrd_INT = 2
	except() as err_platformTest:
		print(err_platformTest)
	cwd_STR = os.getcwd()
	outDir_STR = cwd_STR
	sourceDir_STR = None
	pauseState_BL = False
	sourceFileSelected_BL = False
	dateTimeStartFN_STR = None
	errors_LST = []
	namePrefix_STR = 'Temp'
	urlList_LST = []
	urlListCp_LST = []
	newSourceFilePath_STR = None
	queue_SYS = queue.Queue()
	thread_SYS = threading.Thread(target=start_FN)
	thread_SYS.setDaemon(True)
	
#--------------------------------------------------------< GUI >--------------------------------------------------------------------------------------------------------

	mainWindow_UI = tk.Tk()
	mainWindow_UI.title('Download Web Files')
	mainWindow_UI.geometry('1000x800')
	mainWindow_UI.configure(background='#969696')
	urlFrame_UI = tk.Frame(mainWindow_UI, height=urlFrameHeight_INT, bd=5)
	urlTextbox_UI = tk.Text(urlFrame_UI, height=fSzTbox_INT, bg='#1c1c1c', fg='white', insertbackground='white', font=(fontTbox_STR, 11), wrap=tk.NONE)
	urlScroll_UI = tk.Scrollbar(urlTextbox_UI)
	btnFrame_UI = tk.Frame(mainWindow_UI, bg='#969696')
	progressLbl_UI = tk.Label(urlFrame_UI, font=(fontLbl_STR, 10), text='')
	fileInfoLbl_UI = tk.Label(urlFrame_UI, font=(fontLbl_STR, 10), text='Current source file = {0}  |  Current output directory = {1}'.format(sourceDir_STR, outDir_STR))
	startBtn_UI = tk.Button(btnFrame_UI, relief=tk.RAISED, font=(fontBtn_STR, 10), height=1, bd=btnBrd_INT, width=5, text='Start', command=lambda: thread_SYS.start())
	exitBtn_UI = tk.Button(btnFrame_UI, relief=tk.RAISED, font=(fontBtn_STR, 10), height=1, bd=btnBrd_INT,  width=5, text='Exit', command=exit_FN)
	fileDiagBtn_UI = tk.Button(btnFrame_UI, relief=tk.RAISED, font=(fontBtn_STR, 10), height=1, bd=btnBrd_INT, width=5, text='Output Directory', command=fileDiag_FN)
	sourceFileDiag_UI = tk.Button(btnFrame_UI, relief=tk.RAISED, font=(fontBtn_STR, 10), height=1, bd=btnBrd_INT, width=5, text='Source File', command=sourceFileDiag_FN)
	progressBar_UI = ttk.Progressbar(urlFrame_UI)
	urlFrame_UI.pack(fill=tk.BOTH, padx=10, pady=20)
	urlFrame_UI.pack_propagate(False)
	urlTextbox_UI.pack(fill=tk.BOTH, pady=1)
	urlTextbox_UI.pack_propagate(False)
	urlScroll_UI.pack(fill=tk.Y, side=tk.RIGHT) 
	fileInfoLbl_UI.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
	progressBar_UI.pack(side=tk.TOP, fill=tk.X, padx=1, pady=2)
	progressLbl_UI.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
	btnFrame_UI.pack(fill=tk.X, padx=90)
	sourceFileDiag_UI.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=5)
	fileDiagBtn_UI.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=5)
	startBtn_UI.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=5)
	exitBtn_UI.pack(side=tk.LEFT, expand=1, fill=tk.X, padx=5, pady=5)
	urlScroll_UI.config(command=urlTextbox_UI.yview)
	urlTextbox_UI.config(yscrollcommand=urlScroll_UI.set)
	mainWindow_UI.after(100, lambda: checkQueue_FN(mainWindow_UI))
	mainWindow_UI.mainloop()