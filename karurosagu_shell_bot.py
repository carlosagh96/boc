#!/usr/bin/python3

################################################################################
# MF Shell
################################################################################

import aiohttp
import aiofiles
import asyncio
import base64
import configparser
import cryptg
import datetime
import json
import logging
import multivolumefile
import os
import py7zr
import shutil
import sys
import random
import re
import time
import traceback
import urllib.parse
import yarl

from aiohttp import web
# from atds3 import get_token
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from errors import *
from fake_useragent import UserAgent
from functools import partial
from mega_api_modded import Mega
# from mega_api_modded import get_mega_folder
from pathlib import Path
from py7zr import *
from re import match
# from s3_sign_down import get_signed_url
from telethon import TelegramClient, events, functions, types, errors, Button
from youtubesearchpython import Playlist
from yt_dlp import YoutubeDL
from zipfile import ZipFile, ZIP_STORED

################################################################################
# Bot Credentials and environment variables
################################################################################

_ev_api_id=os.getenv('API_ID')
_ev_api_hash=os.getenv('API_HASH')
_ev_bot_token=os.getenv('BOT_TOKEN')
_ev_website_url=os.getenv('WEBSITE',"http://127.0.0.1/")
#_web_host=socket.getfqdn()
#_ev_website_url="https://"+_web_host
_ev_port=os.getenv("PORT","8080")
_ev_channel=os.getenv('CHANNEL',"-1001517958931")

# TODO: Change VIP system to group dependant (ChatID)
# vip_group=os.getenv('VIP_GROUP',None)

_extra_signature="\n<p>Bot programado y hospedado por <a href=https://t.me/CarlosAGH>カルロサグ</a>."
_extra_disclosure="\n<p>El bot está en constante desarrollo. No responderé preguntas sobre la programación ni el hospedaje del bot. Antes de aclarar dudas sobre cómo operar el bot, tenga en cuenta que todo lo que debe saber está en la guía y en la ayuda completa, para algo se escribió todo eso, asi que debe leer primero antes de preguntar."

_ev_bot_token_debug=os.getenv('BOT_TOKEN_DEBUG')

try:
	debugging=eval(os.getenv('DEBUGGING',"False"))
except:
	debugging=False

if debugging:
	_ev_bot_token=_ev_bot_token_debug

try:
	assert _ev_api_id
	assert _ev_api_hash
	assert _ev_bot_token
	assert _ev_bot_token_debug

except:
	local=True

else:
	local=False
	startup=True

if local:
	try:
		from credentials import load_my_credentials
		_ev_api_id,_ev_api_hash,_ev_bot_token=load_my_credentials()
		_ev_bot_token_debug=_ev_bot_token

	except:
		startup=False

	else:
		startup=True

if not startup:
	print("EXCUSE ME WHAT THE FUCK")
	exit()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(msg)s',level=logging.INFO)
bot=TelegramClient("the",_ev_api_id,_ev_api_hash).start(bot_token=_ev_bot_token)

################################################################################
# Constants/Global variables
################################################################################

# Paths and appname

_app_cwd=Path(".")
_app_cwd_abs=_app_cwd.resolve()
_fse_root=Path("shared")
_tickets_path=Path("tickets")
_path_ffmpeg=Path("ffmpeg")

# Admin files on bash
_bash_out="admin_bash_out"
_bash_err="admin_bash_err"

# Some HTML Colors
_cgray1="#33393B"
_cgray2="#515658"
_cc=[_cgray1,_cgray2]

# For the human-readable units
_kilobyte=1024
_megabyte=_kilobyte*_kilobyte
_megabyte_fe=1398200
_gigabyte=_megabyte*_kilobyte

# Transfer jobs and limits for each user
transfer_jobs=0

# Simultanious Network Transfer Limit
_sntl=2

# Selection types
_stype_s="SIMPLE"
_stype_r="RANGE"
_stype_f="FREE"

# Queue for controlled jobs
_gq_sub=[]
_gq_cpu=[]
_gq_req=[]
_gq_ffs=[]

# aiohttp Socket read time-out
_tout=aiohttp.ClientTimeout(sock_read=30)

# FFmpeg web workers
_ffmpeg_workers=["https://web-carlosagh96.cloud.okteto.net/"]

# Supported websites
def addwsite(bank,ws):
	bank.append(ws)
	return ws

# For mere mortals

_wget_support=[]

_ws_androeed=addwsite(_wget_support,"androeed.ru")
_ws_apkaward=addwsite(_wget_support,"apkaward.com")
_ws_mf=addwsite(_wget_support,"mediafire.com")
_ws_sf=addwsite(_wget_support,"solidfiles.com")
_ws_tokyvideo=addwsite(_wget_support,"tokyvideo.com")
_ws_vimm=addwsite(_wget_support,"vimm.net")
_ws_zippy=addwsite(_wget_support,"zippyshare.com")

_cdl_support=[]

_ws_freeco=addwsite(_cdl_support,"freecomiconline.me")
_ws_hvmanga=addwsite(_cdl_support,"heavenmanga.com")
_ws_lectortmo=addwsite(_cdl_support,"lectortmo.com")
_ws_leermanga=addwsite(_cdl_support,"leermanga.net")
_ws_mtemplo=addwsite(_cdl_support,"manga-templo.com")
_ws_mangafox=addwsite(_cdl_support,"mangafoxfull.com")
_ws_mreadercc=addwsite(_cdl_support,"mangareader.cc")
_ws_mreadertv=addwsite(_cdl_support,"mangareader.tv")
_ws_mangasin=addwsite(_cdl_support,"mangas.in")
_ws_tmonline=addwsite(_cdl_support,"tumangaonline.site")
_ws_xoxocm=addwsite(_cdl_support,"xoxocomics.com")

# For the VIPs

_wget_support_vip=[]
_cdl_support_vip=[]

_ws_subscene=addwsite(_wget_support_vip,"subscene.com")
_ws_tusubtitulo=addwsite(_wget_support_vip,"tusubtitulo.com")
_ws_osubt1=addwsite(_wget_support_vip,"opensubtitles.org")
_ws_yifysubs=addwsite(_wget_support_vip,"yifysubtitles.org")

_ws_chochox=addwsite(_cdl_support_vip,"chochox.com")
_ws_ehentai=addwsite(_cdl_support_vip,"e-hentai.org")
_ws_hentaifox=addwsite(_cdl_support_vip,"hentaifox.com")
_ws_imhentai=addwsite(_cdl_support_vip,"imhentai.xxx")
_ws_nhentai=addwsite(_cdl_support_vip,"nhentai.net")
_ws_tmohentai=addwsite(_cdl_support_vip,"tmohentai.com")
_ws_vmporno=addwsite(_cdl_support_vip,"vermangasporno.com")

# Checks if the url belongs to a supported website, returns None if not supported, returns the supported website in case of being supported
def supported_website(host_list,url):
	yurl=yarl.URL(url)
	yurl_host=yurl.host
	host_selected=None
	for host in host_list:
		if host in yurl_host:
			host_selected=host

	return host_selected

######################
# Messages and strings
######################

# SAY MY NAME!!!
_the_name_of_the_bot="The Mother Fucking Shell 🌚👨🏿‍💻🤠"

# Error messages
_msg_error_fsize="El tamaño del archivo no concuerda"
_msg_error_skel="Error: "
_msg_error_url="La URL no es válida"
_msg_error_this="Excepción no registrada: "
_msg_error_404="Estado 404: Recurso no encontrado"
_msg_error_exists="Un recurso con el mismo nombre ya existe"
_msg_error_wargs="Cantidad de argumentos incorrecta"
_msg_error_nonfile="La ubicación dada no es un archivo"
_msg_error_nondir="La ubicación dada no existe o no es un directorio"
_msg_error_unknown="La unicación dada no es ni un archivo ni un directorio"
_msg_error_empty="No se encontraron elementos válidos en el directorio seleccionado"
_msg_error_iarg="Argumento no válido"
_msg_error_notfound="Elemento no encontrado"
_msg_error_archiver="No puedes hacer más de un trabajo de archivado simultáneo"
_msg_error_tquota="No se permiten más de "+str(_sntl)+" transferencias simultáneas de red por usuario"
_msg_error_few="No tiene sentido: hay menos de 2 archivos"

_acc_uptobox={"carlitoselcubanito@gmail.com":["Viernesnegr0","3e89856643fae194b1908728aa912d908xtx4"]}

###############
# URL "Actions"
###############

# website URL "actions"
_url_actions=["mkm3u","txtdl","txtdl-idm"]

# mkm3u related
_avsuffixes=["aac",".avi",".flac",".flv",".m4a",".m4v",".mka",".mkv",".mp3",".mp4",".mpeg",".mpg",".ogg",".rm",".rmvb",".wav",".webm",".wma",".wmv"]

############################
# HTML,CSS,JS Pieces of code
############################

# The DOCTYPE HTML thing seems to f*** up some things that work OK without it
#_piece_html_start_="<!DOCTYPE html>\n<html>\n<meta content='text/html;charset=utf-8'>"
_piece_html_start="<html>\n<head>\n"
_piece_html_title="<title>Servidor de archivos</title>"
_piece_html_end="\n</body>\n</html>"
_piece_css_default="\nbody{background-color:#25292b;color:white;}\na{padding:8;background-color:transparent;font-weight:bold;}\na:link{color:#00BFFF;text-decoration:none;}\na:hover{text-decoration:underline;}\na:active{color:white;}\na:visited {color:#4682B4;text-decoration:none;}\ntd{font-size:150%;}"

_piece_html_body_iview=" style='text-align:center;' onload='USize()' onresize='USize()'"
#_piece_js_iview="function USize(){let f=32;let w=window.innerWidth;let h=window.innerHeight;let wt=w-f;let ht=h-f;let hc=24;let hi=ht-hc;document.getElementById('mc').style.width=wt;document.getElementById('mc').style.height=ht;document.getElementById('ic').style.width=wt;document.getElementById('ic').style.height=hi;}"

_img_style_iview_w="width:100%;"
_img_style_iview_h="height:100%;"

#_css_iview={_iview_args[0]:_img_style_iview_w,_iview_args[1]:_img_style_iview_h}

################################################################################
# ATDS3 Gathered Tokens Private Pool
################################################################################

# Token storage. Dict Sintax: key = Core Token; Value = anyof(used, busy, snyc)
# agtpp_pool={}

# List of used-up tokens
# agtpp_trash=[]

# AGTTP Service Status
#_agtpp_wait="WAITING"
#_agtpp_trig="TRIGGER"
#_agtpp_work="WORKING"
# agtpp_working=False

# AGTTP token status
#_token_used="USED_UP_TOKEN"
#_token_busy="BUSY_TOKEN"
#_token_snyc="STATUS_NOT_YET_CONFIRMED"

# Functions used by this service

# Fetch token with SNYC from the AGTPP
#async def agtpp_fetch():
#	global agtpp_pool
#	global agtpp_working
#
#	if not agtpp_working:
#		agtpp_working=True
#
#	try:
#		while len(agtpp_pool)==0:
#			await asyncio.sleep(1)
#
#		if len(agtpp_pool)>0:
#			found_snyc=False
#			chosen=""
#			while len(chosen)==0:
#				for k in agtpp_pool:
#					if found_snyc:
#						break
#
#					else:
#						status=agtpp_pool.get(k)
#						if _token_snyc in status:
#							chosen=str(k)
#							agtpp_pool.update({chosen:_token_busy})
#							print("Retrieved Token with SNYC:",k)
#
#				if len(chosen)==0:
#					print("Tokens available are either busy or wasted, still waiting...")
#					await asyncio.sleep(1)
#
#			return chosen
#
#	except Exception as e:
#		return None

# Grabs tokens from ATDS3. Each time it works destroys tokens marked as used up and populates the pool with new tokens
#async def agtpp_service():
#	global agtpp_pool
#	global agtpp_trash
#	global agtpp_ssset
#	global agtpp_working
#	tfetch_max=100+len(_viplist)*10
#	if tfetch_max==0:
#		print("THERE ARE NO VIP USERS, CANCELLING AGTPP")
#		return
#
#	else:
#		print("Initiated AGTPP Service loop")
#
#	while True:
#		await asyncio.sleep(1)
#		if agtpp_working:
#			if len(agtpp_pool)>0:
#				tmp_rem_used=[]
#				for tkn in agtpp_pool:
#					val=agtpp_pool.get(tkn)
#					if val==_token_used:
#						tmp_rem_used=tmp_rem_used+[tkn]
#
#				if len(tmp_rem_used)>0:
#					for rem in tmp_rem_used:
#						agtpp_pool.pop(rem)
#						agtpp_trash=agtpp_trash+[ctoken]
#
#			tfetch=tfetch_max-len(agtpp)
#			while tfetch>0:
#				# ctoken=await get_token()
#				ctoken=await asyncio.wait_for(get_token(),timeout=5)
#				if ctoken:
#					f=False
#					if not ctoken in agtpp.keys():
#						f=True
#
#					if ctoken in agtpp_trash:
#						f=True
#
#					if not f:
#						agtpp.update({ctoken:_token_snyc})
#						tfetch=tfetch-1
#
#				else:
#					tfetch=tfetch-1
#
#			agtpp_working=False

################################################################################
# Archiver and unarchiver stuff
################################################################################

# PY7ZR FILTERS

_copy_filter=[{'id': FILTER_COPY}]
_copy_filter_ext=[{'id': FILTER_COPY},{'id': FILTER_CRYPTO_AES256_SHA256}]

# IMPORTANT FOR EXTRACTING 7Z WITH SHUTIL

shutil.register_unpack_format('7zip',['.7z'],unpack_7zarchive)

# Archiver job types

_7z=".7z"
_gzip=".gz"
_tar=".tar"
_zip=".zip"

# Unarchiver detections

_single="single"
_zip_multi3="zip_multi3"
_zip_multi4="zip_multi4"
_7z_single="7z_single"
_7z_multi3="7z_multi3"
_7z_multi4="7z_multi4"
_gz_multi3="gz_multi3"
_xz_multi3="xz_multi3"

################################################################################
# Bot commands system
################################################################################

# Helpers

_ch_num="Número"
_ch_rng="Rango"
_ch_nums="Números"
_ch_nor=_ch_num+" ó "+_ch_rng
_ch_name="Nombre"
_ch_opt=" (Opcional)"
_ch_dep=" (Depende del caso)"

# Categories

# Skel:
# cmdlist_cat={"/command1:["This command does this thing","Argument 1","Argument 2"],"/command2:["This command has no args"]}

_command_pattern=re.compile(r"^/[a-z]*")

# TODO: finish redacting the /ytdls command

_clist_fs={"/ls":1,"/cd":1,"/back":0,"/mkdir":1,"/mv":2,"/rm":1,"/info":0,"/mediainfo":1,"/bren":3,"/seven":3,"/crypt":2,"/ext":2}
_clist_nw={"/auto":0,"/download":1,"/upload":1,"/ua":1,"/wget":1,"/gddl":1,"/megacreds":2,"/megadl":1,"/ytdl":1,"/que":2,"/cancel":1,"/brake":1,"/share":0}
_clist_help={"/about":0,"/help":0,"/start":0,"/ok":0}
#_clist_vip={"/esubs":["Scrapper de subtítulos de Erai-Raws. Dale una URL del sitio de subtítulos de EraiRaws y te devuelve URLs de archivos según el idioma","URL de una serie","Idioma (spa ó all)"],"/cdl":["Descargador de manga/comic porno. Descarga y empaqueta en CBZ.\nSitios actualmente soportados:\nchochox.com\ne-hentai.org\nhentaifox.com\nimhentai.xxx\nnhentai.net\ntmohentai.com\nvermangasporno.com","URL de galería"],"/vipinfo":["Muestra la lista de usuarios que son VIP"]}
_clist_vip={"/esubs":2,"/cdl":1,"/vipinfo":0}
# _clist_vip={_c_cdl:["Descargador de manga/comic porno. Descarga y empaqueta en CBZ.\nSitios actualmente soportados:\nchochox.com\ne-hentai.org\nhentaifox.com\nimhentai.xxx\nnhentai.net\ntmohentai.com\nvermangasporno.com","URL de galería"],"/ktodus":["Envía señal de cancelación al descargador de toDus."],_c_tdl:["Descargador de toDus (Reporten errores por favor). Se usa respondiendo a un TXT del lado de Telegram"],"/tt":["Asigna un token de forma fija. Si se usa respondiendo a un mensaje, el contenido se asume como token. Si se usa como mensaje normal, el argumento debe ser el token.\nEl token es en su forma completa, o sea: \"Bearer blablabla...\").","Token de toDus."+_ch_dep],"/vipinfo":["Muestra la lista de usuarios que son VIP"]}
# _clist_vip={"/ktodus":["Envía señal de cancelación al descargador de toDus."],"/pool":["Activa/Desactiva el soporte del pool de tokens de ATDS3. Desactivado de forma predeterminada. Solo se usan tokens del pool, el token declarado de forma manual no se tiene en cuenta ni se comparte con la piscina."],"/tdl":["Descargador de toDus (Reporten errores por favor). Se usa respondiendo a un TXT del lado de Telegram"],"/tt":["Asigna un token de forma fija. Solo se tiene en cuenta en caso de tener desactivado el soporte de ATDS3. Si se usa respondiendo a un mensaje, el contenido se asume como token. Si se usa como mensaje normal, el argumento debe ser el token.\nEl token es en su forma completa, o sea: \"Bearer blablabla...\").","Token de toDus."+_ch_dep],"/vipinfo":["Muestra la lista de usuarios que son VIP"]}
_clist_dev={"/test":0,"/peek":1,"/fix":3,"/bash":1,"/notes":0,"/devmode":0,"/devpost":1}

_devmode=debugging
_devmode_label="No se puede usar este bot ahora mismo, pruebe más tarde"

# Command system: Mix all categories

cmdlist_all={}

# cmdlist_all.update(cmdlist_category)

cmdlist_all.update(_clist_fs)
cmdlist_all.update(_clist_nw)
cmdlist_all.update(_clist_help)
cmdlist_all.update(_clist_vip)
cmdlist_all.update(_clist_dev)

################################################################################
# User Session system
################################################################################

# Session dict

_sessions={}

# Session Data Identifier (used for indexing session data)

_sdid=0

def sdidi():
	global _sdid
	_sdid=_sdid+1
	return _sdid

_sd_time=0
_sd_cwd=sdidi()
_sd_netwquota=sdidi()
_sd_ua=sdidi()
_sd_saved=sdidi()

_sd_hproc=sdidi()
_sd_hview=sdidi()

_sd_exec_mv=sdidi()
_sd_exec_rm=sdidi()

_sd_que=sdidi()

_sd_rec=sdidi()

#_sd_que_urls=sdidi()
#_sd_que_mega=sdidi()
#_sd_que_tg_down=sdidi()
#_sd_que_tg_up=sdidi()

_sd_fkey=sdidi()
_sd_autodl=sdidi()
_sd_mega_session=sdidi()

_sd_shared=sdidi()
_sd_shared_name=sdidi()

# _sd_todus_dl=sdidi()
#_sd_todus_token=sdidi()
#_sd_todus_atds3=sdidi()
#_sd_todus_token_last=sdidi()

# Session share names(for masking the UID)

_uid_masks={"bot":0,"canal":0,"grupo":0,"jane-doe":0,"john-doe":0,"usuario":0}

# Hard-coded User lists. VIP users and Banned users
# TODO: Find a way to add the bot owner and API credentials owner automatically to the VIP list, manually putting the person in charge of this monster is sloppy as fuck

print("\nSearching and loading for the hard-coded user lists...\n")

_viplist=[]
if os.path.exists("hcul_vip.nfo"):
	vipfile=open("hcul_vip.nfo","r")
	viplist_raw=vipfile.readlines()
	if len(viplist_raw)>0:
		print("VIP Users:\n{")
		for line in viplist_raw:
			tmp=line.strip()
			_viplist=_viplist+[tmp]
			print("\t"+tmp)

		print("}\n")

	else:
		print("No VIP Users\n")

	del viplist_raw
	vipfile.close()

else:
	print("VIP users list hcul_vip.nfo is missing\n")

# Banned Users list

_banlist=[]
if os.path.exists("hcul_ban.nfo"):
	banfile=("hcul_ban.nfo","r")
	banlist_raw=banfile.readlines()
	if len(banlist_raw)>0:
		print("Banned Users:\n{")
		for line in banlist_raw:
			tmp=line.strip()
			_banlist=_banlist+[tmp]
			print("\t"+tmp)

		print("}\n")

	else:
		print("No Banned Users\n")

	del banlist_raw
	banfile.close()

else:
	print("Banned users list hcul_ban.nfo is missing")

################################################################################
# Functions
################################################################################

# Makes a comic book archive out of a directory
def mkcbz(path_dir):
	basedir=Path(path_dir).name
	try:
		images=list(Path(path_dir).glob("*"))
		if path_dir.endswith("/"):
			path_dir=path_dir[:-1]

		with ZipFile(path_dir+".cbz","w",ZIP_STORED) as z:
			for image_path in images:
				image_name=Path(image_path).name
				z.write(image_path,basedir+"/"+image_name)
	except Exception as e:
		return [False,str(e)]

	else:
		return [True]

# Creates a ticket
def mkticket(extra_thing="",aspath=True):
	if aspath:
		dirname="tickets/"

	else:
		dirname=""

	if len(extra_thing)>0:
		extra_thing=extra_thing+"-"

	return dirname+extra_thing+str(time.strftime("%Y-%m-%d-%H-%M-%S"))

# Human-readable units. Returns a string
def hr_units(inbytes):
	if inbytes>_kilobyte:
		if inbytes>_megabyte:
			if inbytes>_gigabyte:
				fsize=str(round(inbytes/_gigabyte,2))+" GB"

			else:
				fsize=str(round(inbytes/_megabyte,2))+" MB"

		else:
			fsize=str(round(inbytes/_kilobyte,2))+" KB"

	else:
		fsize=str((inbytes))+" B"

	return fsize

# Nicely padded numbers

def paddednumb(dlen,numb,spc="0",dlen_as_figs=False):
	numb_str=str(numb)

	if dlen_as_figs:
		lim_str=dlen
	else:
		lim_str=len(str(dlen))

	thy_str=numb_str
	ldiff=lim_str-len(numb_str)
	while ldiff>0:
		thy_str=spc+thy_str
		ldiff=ldiff-1

	return thy_str

# Fix a path string
def path_gitgud(path_shitty):
	path_proc=Path(path_shitty)
	path_almost_gud=path_proc.as_posix()
	path_gud=path_almost_gud.replace("//","/")
	print("Fixed shitty path",path_shitty,"→",path_gud)

	return path_gud

# Gets a serverside path if exists and if it's relative to the fse_root
def get_serverside_path(gpath):
	absolute=gpath.resolve()

	try:
		assert absolute.exists()
		# assert absolute.is_relative_to(_fse_root_path_real)
		assert absolute.is_relative_to(_app_cwd_abs)

	except Exception as e:
		return None

	else:
		if absolute==_app_cwd_abs:
			absolute=_fse_root_path_real

		return absolute

# Turns a given URL into an HTML-ready snippet. href, and shit included
def url_in_html(u):
	return "<a href='"+u+"'>[ LINK ]</a> <code>"+u+"</code>"

# HTML error printout
def html_error_page(status,explanation):
	if len(explanation)>0:
		explanation="\n<p>"+explanation

	return _piece_html_start+_piece_html_title+"\n<style>"+_piece_css_default+";</style>\n</head>\n<p><h2>Error "+str(status)+"</h2>\n<p>"+explanation+"\n<p>\n<p><a href=/>Volver a la página inicial</a>"

# Checks wether a file list in "list_target" match any registered suffixes in "list_filter". Returns a new list with the matches
def list_filter_suffix(list_given,list_filter):
	list_filtered=[]
	for fse in list_given:
		if fse.suffix in list_filter:
			list_filtered=list_filtered+[fse]

	return list_filtered

################################################################################
# Directories
################################################################################

_fse_root_path=_app_cwd.joinpath(_fse_root)

_fse_root_path_real=_fse_root_path.resolve()

if not _fse_root_path_real.exists():
	_fse_root_path.mkdir()

if not _path_ffmpeg.exists():
	_path_ffmpeg.mkdir()

# Create the tickets directory
if not _tickets_path.exists():
	_tickets_path.mkdir()

################################################################################
# Reception
################################################################################

#class Reception:
#	def __init__(self):
#		self.working=False
#
#	async def cooldown():
#		while True:
#			

################################################################################
# Queues
################################################################################

# Base Queue class

class QueueBase:
	# Assign name to the queue
	def __init__(self,n=""):
		self.name=n
		self.queue=[]
		self.attrib={"cancel":False,"brake":False,"working":False}

	def reset(self):
		self.queue.clear()
		self.attrib.update({"cancel":False,"brake":False,"working":False})

	# Gets size of the queue, Returns int
	def get_size(self,debug=False):
		if debug:
			print("len(self.queue) =",len(self.queue))
		return len(self.queue)

	# Gets a value of the queue from given index, Returns None if not found
	def get_value(self,i=0):
		try:
			value=self.queue[i]
		except:
			value=None

		return value

	# Checks existance of a value in the queue. Returns bool
	def check_value(self,v):
		if len(self.queue)==0:
			return False

		if v in self.queue:
			return True
		else:
			return False

	# Adds a value to a queue. Returns a bool
	def add_value(self,v):
		#if v in self.queue:
		#	return False
		#else:
		#	self.queue=self.queue+[v]
		#	return True
		self.queue.append(v)

	# Deletes a value from a queue by index. Returns a bool
	def del_index(self,i=0):
		try:
			self.queue.pop(i)
		except:
			print("error while deleting element",i)
			return True
		else:
			print("element",i,"deleted!")
			return False

	# Deletes values from a queue in a range. Returns list of deleted values and the offset
	def del_index_range(self,range_args):
		olist,offset=get_select_range(self.queue,range_args,qpatch=True,get_offset_index=True)
		if len(olist)>0:
			for val in olist:
				if self.queue.index(val)>0:
					self.queue.remove(val)

		return olist,offset

	# Get chunked (telegram related)
	def get_chunked(self,vlist=None,title=None,offset=0):
		print("name =",self.name)

		if not title:
			msg="<p>"+self.name+"\n<p>"

		else:
			msg="<p>"+title+"\n<p>"

		if not vlist:
			vlist=self.queue
			title=self.name

			if self.attrib["brake"]:
				msg=msg+"(F)\n<p>"
			else:
				msg=msg+"(L)\n<p>"

		p=[]
		if len(vlist)>0:
			index=offset
			i=0
			max_index=len(vlist)-1
			for val in vlist:
				snum="<code>"+paddednumb(max_index,index,spc=" ")+"</code> "
				add=self.show_value(val,prefix=snum)
				if not add:
					add="\n<p>"+snum+"..."

				i=i+1

				if i==len(vlist):
					p=p+[msg+add]

				else:
					if len(msg+add)>4000:
						p=p+[msg]
						msg=add
					else:
						msg=msg+add

				index=index+1

		else:
			msg=msg+"..."

		return p

# Each queue shows values for displaying according to a specific format

# URLs: [URL string, Dir Pathlib obj]
class QueueForURLs(QueueBase):
	def show_value(self,v,prefix=""):
		try:
			string="\n<p>"+prefix+"[ <a href='"+v[0]+"'>LINK</a> ] [ <code>"+v[0]+"</code> ] [ Salida: <code>"+get_path_show(v[1])+"</code> ]"
			if len(v)==3:
				string=string+" ["+str(v[2])+"]"

		except:
			string=None

		return string

	def check_value_spc(self,v):
		e=False
		if len(self.queue)>0:
			for val in self.queue:
				if v[0]==val[0]:
					e=True
					break

		return e

# Telegram Event Objects (Downloads, usually): [Telegram Object, Suggested name, Dir Pathlib obj]
class QueueForTGE(QueueBase):
	def show_value(self,v,prefix=""):
		try:
			ev=v[0]
			sug=v[1]
			out=v[2]
			print("v =",v)
			print("ev.file.name =",ev.file.name)

			if ev.file.name:
				fname="Nombre: <code>"+ev.file.name+"</code>"

			else:
				if sug:
					fname="Nombre: <code>"+sug+"</code>"

				else:
					fname="Id: "+str(ev.id)

			string="\n<p>"+prefix+" [ Salida: <code>"+get_path_show(out)+"</code> ] [ <code>"+fname+"</code> ] [ "+hr_units(ev.file.size)+" ]"

		except Exception as e:
			print("error at QueueForTGE.show_value() →",e)
			string=None

		return string

	def check_value_spc(self,v):
		e=False
		aev,apt=v
		for val in self.queue:
			qev=val[0]
			if aev.file.name and qev.file.name:
				if aev.file.name==qev.file.name:
					qpt=val[1]
					if apt==qpt:
						e=True

					if apt.joinpath(aev.file.name).exists():
						e=True

		return e

# Files: Pathlib objects
class QueueForFiles(QueueBase):
	def show_value(self,v,prefix=""):
		try:
			fz=os.path.getsize(str(v))
			result="\n<p>"+prefix+" [ <code>"+get_path_show(v)+"</code> ] [ "+hr_units(fz)+" ]"
		except:
			result=None
		return result

# Queue brake checker
async def queue_brake_checker(q,e):
	b=q.attrib["brake"]
	if b:
		await e.reply("La cola está frenada")
		while True:
			b=q.attrib["brake"]
			if b:
				await asyncio.sleep(1)
			else:
				break

################################################################################
# Newsletter for the website
################################################################################

# Leave messages in the website, they die 24 hours after being posted (something else gets it done)

class AdminPublicMessage:

	# Each post is a list: [title,content]
	def __init__(self,the_post):
		self.time_arrival=datetime.datetime.now()
		self.data=the_post

	# Gets the post title + the message inside. The returned message is HTML parsed btw
	def get_data(self):
		title=self.data[0]
		text_raw=self.data[1]
		text_html="<p>"+text_raw.replace("\n","\n<p>")
		return [title,text_html]

	# Get 'age' of the post in seconds, do some math for this shit
	def get_age(self):
		current_time=datetime.datetime.now()
		datediff=current_time-self.time_arrival
		return datediff.seconds

	# The 'newdata' arg is a 2 index list, 0 is the title, and 1 is the content, if an index has 0 length, the index is ignored
	def edition(self,newdata):
		new_title=newdata[0]
		new_text=newdata[1]
		if len(new_title)>0:
			self.data[0]=new_title

		if len(new_text)>0:
			self.data[1]=new_text

# The place where all posts are stored
admin_public_messages=[]

# Add a new post
def admin_post_add(post_title,post_message):
	global admin_public_messages
	post_object=AdminPublicMessage([post_title,post_message])
	admin_public_messages=[post_object]+admin_public_messages

# Delete an existing post
def admin_post_del(index):
	global admin_public_messages
	post_object=admin_public_messages[index]
	admin_public_messages.pop(index)
	del post_object

# Checks and deletes old messages

async def admin_posts_supervisor():
	global admin_public_messages
	while True:
		posts=len(admin_public_messages)
		if posts>0:
			last_post=admin_public_messages[posts-1]
			age_in_seconds=last_post.get_age()
			if age_in_seconds/3600>24:
				admin_post_del(posts-1)

		await asyncio.sleep(60)

################################################################################
# Fake User Agent for the downloaders
################################################################################

# Up-to-date user agents

_ua_utd=["Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50"]

# If the connection required by the module fails, not to worry, this thing also has a hardcoded user agents list :)

_ua_dict={"c":"Chrome","f":"Firefox","o":"Opera","s":"Safari","r":"Aleatorio"}

def get_user_agent(uareq="r"):

	hcuagents=["Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0","Mozilla/5.0 (X11; Linux i686; rv:68.0) Gecko/20100101 Firefox/68.0","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 Firefox/79.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"]

	try:
		ua=UserAgent()

		if uareq=="c":
			give_uagent=ua.chrome

		elif uareq=="f":
			give_uagent=ua.firefox

		elif uareq=="o":
			give_uagent=ua.opera

		elif uareq=="s":
			give_uagent=ua.safari

		elif uareq=="r":
			give_uagent=ua.random

		else:
			raise Exception("Falling back to random UA")

	except:
		give_uagent=random.choice(hcuagents)

	return give_uagent

################################################################################
# Lower Level functions
################################################################################

# VERY IMPORTANT FOR THE BOT EVENT HANDLER
def tg_cmd_chk(text):
	cmdp_findall=_command_pattern.findall(text)
	try:
		assert text.find("\n")==-1
		assert text.find("\t")==-1
		assert len(cmdp_findall)==1

	except:
		return False

	else:
		return True

# Free selector argument parser
def get_args_free(raw_crap):
	result=[]
	try:
		assert "," in raw_crap
		if raw_crap.startswith(",") or raw_crap.endswith(","):
			raise Exception("LOL")

	except:
		return None

	raw_split=raw_crap.split(",")
	try:
		assert len(raw_split)>1
		for e in raw_split:
			es=e.strip()
			eint=int(es)
			assert eint>-1
			if eint in result:
				raise Exception("LOL")

			result.append(eint)

	except:
		return None
	else:
		print("free select",result)
		return result

# Range selector argument parser
def get_args_range(raw_crap):
	rev=False
	try:
		argparts=raw_crap.split("-")
		assert len(argparts)==2
		ro=int(argparts[0])
		rargs=[ro]
		araw=argparts[1]
		tlen=len(araw)

		if araw[tlen-1]=="r":
			rev=True
			rl=int(araw[:-1])

		else:
			rl=int(araw)

	except Exception as e:
		print("Range syntax error. RawCrap =",raw_crap,"Error =",e)
		return None

	else:
		return [ro,rl,rev]

# Get selected elements from a free selection
def get_select_free(inlist,free_args):
	outlist=[]
	x=0
	x_max=len(inlist)
	while x<x_max:
		y=0
		loopit=True
		while loopit:
			if len(free_args)>0:
				if free_args[0]==y:
					element=inlist[y]
					print("\t+",y,)
					outlist.append(element)
					free_args.pop(0)
					loopit=False

			if len(free_args)==0:
				loopit=False

			y=y+1

		x=x+1
		if len(free_args)==0:
			break

	return outlist

# Get selected elements from a ranged selection
def get_select_range(inlist,range_args,qpatch=False,get_offset_index=False):
	r_start,r_len,rev=range_args
	if not rev:
		offset=r_start

		# Queue protection patch
		if qpatch:
			if offset==0:
				offset=offset+1

		if r_len>0:
			outlist=inlist[offset:r_start+r_len]

		else:
			outlist=inlist[offset:]

	else:
		if r_len>0:
			offset=r_start+1-r_len

			# Queue protection patch
			if qpatch:
				if offset==0:
					offset=offset+1

			outlist=inlist[offset:r_start+1]

		else:

			# Queue protection patch
			if qpatch:
				offset=1
			else:
				offset=0

			outlist=inlist[offset:r_start+1]

	if not get_offset_index:
		return outlist

	else:
		return outlist,offset

################################################################################
# Lower level file system functions
################################################################################

# Get a display path for sending in a message, etc...
def get_path_show(thepath,relto=None):
	if not relto:
		lp=list(thepath.parents)
		lp.reverse()
		if len(lp)>1:
			rdir=lp[1]
			rel=thepath.relative_to(rdir)
			showpath=Path("/").joinpath(rel)
			return str(showpath)

		else:
			return "/"

	else:
		rel=thepath.relative_to(relto)
		showpath=Path("/").joinpath(rel)
		return str(showpath)

# Get directory contents
async def aio_get_dircont(gpath,fsetype=2,get_pop=False):
	ls_raw=list(gpath.glob("*"))
	ls_raw.sort()
	ls_clean=[]
	if get_pop:
		d=0
		f=0

	if fsetype==2:
		get_dirs=True
		get_files=True

	elif fsetype==1:
		get_dirs=True
		get_files=False

	elif fsetype==0:
		get_dirs=False
		get_files=True

	if get_dirs:
		for fse in ls_raw:
			if fse.is_dir():
				ls_clean=ls_clean+[fse]
				if get_pop:
					d=d+1

	if get_files:
		for fse in ls_raw:
			if fse.is_file():
				ls_clean=ls_clean+[fse]
				if get_pop:
					f=f+1

	if get_pop:
		if fsetype==0:
			return ls_clean,f

		if fsetype==1:
			   return ls_clean,d

		if fsetype==2:
			   return ls_clean,d,f


	else:
		return ls_clean

################################################################################
# Higher level file system functions
################################################################################

# async version: returns a path
async def aio_get_fsepath(cpath,element,fsetype=2):
	#cpath=Path(rootdir).joinpath(currdir)
	if element>-1:
		if cpath.exists():
			ls_path=await aio_get_dircont(cpath)
			if element<len(ls_path):
				fse=ls_path[element]
				if fsetype==2:
					return fse

				else:
					if fsetype==0:
						if fse.is_file():
							return fse

						else:
							return None

					if fsetype==1:
						if fse.is_dir():
							return fse

						else:
							return None

			else:
				return None

	else:
		plist=list(cpath.parents)
		plist.reverse()
		if abs(element)<len(plist):
			return plist[element]

		else:
			return None

# File system element selector by range. Returns list of pathlib objects. Arguments are a pathlib path and range parameters (get 'em from range arg parser)
async def aio_get_dircont_ranged(tgtpath,range_params):
	outlist=[]
	tmpdirlist=await aio_get_dircont(tgtpath)

	if len(tmpdirlist)>0:
		outlist=get_select_range(tmpdirlist,range_params)

	return outlist

# File system element free selector. Returns freely selected elements
async def aio_get_dircont_free(tgtpath,free_params):
	outlist=[]
	tmpdirlist=await aio_get_dircont(tgtpath)

	if len(tmpdirlist)>0:
		outlist=get_select_free(tmpdirlist,free_params)

	return outlist

# Directory contents listing, used in /back, /cd and /ls. Arg is relative to "root/", the output is an array

# ASYNC VERSION OF PREVIUS FUNCTION: displays LS output directly as telegram messages
async def aio_display_ls(chatobj,replyto,currdir,tgtdir,the_title="",crange=[]):
	# chatobj = corresponding chat
	# replyto = Event message to reply
	# uid = user ID
	# currdir = current directory
	# tgtdir = target directory
	# crange = given range args, (as a result from the range parser)
	if len(crange)>0:
		dirlist=await aio_get_dircont_ranged(tgtdir,crange)

	else:
		dirlist=await aio_get_dircont(tgtdir)

	index_max=len(dirlist)

	print("FSEs")
	for f in dirlist:
		print(f)

	if tgtdir==currdir:
		if len(the_title)==0:
			the_title="Observando directorio actual"

		footer="\n<p>\n<p>/ls Ver\n<p>/back Subir un nivel"

	else:
		if len(the_title)==0:
			the_title="Observando otro directorio"

		footer=""

	space=" "
	eol="\n"
	none="\n<p>..."
	lschunk="<p>"+the_title+eol+"<p>"+eol+"<p><code>"+get_path_show(tgtdir)+"</code>\n<p>"
	lsdump=[]

	if index_max==0:
		lschunk=lschunk+none
		lsdump=[lschunk+footer]

	if index_max>0:
		space=" "
		if len(crange)==0:
			fsei=0

		else:
			if not crange[2]:
				fsei=crange[0]

			else:
				if crange[1]>0:
					fsei=crange[0]+1-crange[1]

				else:
					fsei=0

		lnamemax=0
		for fse in dirlist:
			fsename=fse.name
			if len(fsename)>lnamemax:
				lnamemax=len(fsename)

		index=0

		last_fsei=index_max-1

		for fse in dirlist:

			thename=fse.name

			if fse.is_dir():
				index_type="📂"
				filesize="-"

			else:
				index_type="📄"
				filesize_raw=os.path.getsize(str(fse))
				filesize=hr_units(filesize_raw)

			#extraspace=""
			#midx=index_max-1
			#if midx>9:
			#	mlen=len(str(midx))
			#	ilen=len(str(fsei))
			#	aespace=mlen-ilen
			#	if aespace>0:
			#		i=0
			#		while i<aespace:
			#			extraspace=extraspace+space
			#			i=i+1

			endspace=""
			cnamelen=len(thename)
			aespace=lnamemax-cnamelen
			if aespace>0:
				i=0
				while i<aespace:
					endspace=endspace+space
					i=i+1

			lschunk_add=eol+"<p><code>"+paddednumb(last_fsei,fsei,spc=space)+space+index_type+space+thename+endspace+space+"["+filesize+"]</code>"

			index=index+1
			fsei=fsei+1

			if index==index_max:
				if len(lsdump)>0:
					lschunk=none+lschunk

				lsdump=lsdump+[lschunk+lschunk_add+footer]

			else:
				if len(lschunk+lschunk_add)>4000:
					if len(lsdump)>0:
						lschunk=none+lschunk

					lsdump=lsdump+[lschunk]
					lschunk=lschunk_add

				else:
					lschunk=lschunk+lschunk_add

	lsout=None

	for mchunk in lsdump:
		try:
			if not lsout:
				lsout=await replyto.reply(mchunk,parse_mode="html")

			else:
				lsout=await lsout.reply(mchunk,parse_mode="html")

		except Exception as e:
			print("tg msg error at aio_display_ls()",e)

		await asyncio.sleep(0.1)

################################################################################
# Filters and conditions. By returning True, they mean that they "passed"
################################################################################

# When giving new names to files and directories

def check_correct_fse_name(namae):
	try:
		assert namae.startswith(".")
		assert namae.endswith(".")
		assert "/" in namae
		assert "\\" in namae
		assert "*" in namae

	except:
		chkres=True

	else:
		chkres=False

	return chkres

# Check wether it is an URL the given string, very simple shit
def check_url(test_url):
	it_is=False

	if test_url.startswith("http://"):
		it_is=True

	if test_url.startswith("https://"):
		it_is=True

	return it_is

################################################################################
# Youtube
################################################################################

_ytdlf_vres=["360p","720p","1080p"]
_ytdlf_other=["exa"]
_ytdlf=_ytdlf_vres+_ytdlf_other


# Returns real video URL, in case of being a playlist without index or something else, it returns shit
def youtube_determ(url):
	yurl=yarl.URL(url)
	jv=False
	result=None
	wutt=False

	if "youtube.com" in yurl.host:

		if yurl.path.startswith("/playlist"):
			print("playlist")

		elif yurl.path.startswith("/watch"):

			if yurl.query.get("v") and yurl.query.get("list") and yurl.query.get("index"):
				jv=True

			elif yurl.query.get("v") and yurl.query.get("list") and (not yurl.query.get("index")):
				print("playlist")

			elif yurl.query.get("v") and not yurl.query.get("list"):
				jv=True

			elif not (yurl.query.get("v") or yurl.query.get("list")):
				wutt=True

			else:
				wutt=True

		else:
			wutt=True

		if jv:
			print("video")
			result="https://youtu.be/"+yurl.query.get("v")

	print("result =",result,"; wutt =",wutt)
	return result,wutt

def youtube_getter(url,specs=None):
	selected=-1
	msg=""

	try:
		if not specs:
			specs="720p"

		with YoutubeDL({"noplaylist":"true"}) as yyy:
			info=yyy.extract_info(url,download=False)

	except Exception as e:
		msg=str(e)
		return msg

	else:
		if "exa" in specs:
			i=len(info["formats"])-1
			while i>-1:
				#print("FORMAT",i,info["formats"][i])
				#print("\tformat_note",info["formats"][i]["format_note"])
				#print("\text",info["formats"][i]["ext"])
				#print("\tacodec",info["formats"][i]["acodec"])
				#print("\taudio_ext",info["formats"][i]["audio_ext"])
				cformat=info["formats"][i]
				if cformat["resolution"]=="audio only" and (cformat["ext"]=="m4a" or cformat["acodec"].startswith("mp4")):
					selected=i

				if selected>-1:
					i=-1

				else:
					i=i-1

		else:
			# Try and get a good quality video in a classic MP4
			format_notes=["144p","240p"]
			for res in _ytdlf_vres:
				format_notes.append(res)
				if res==specs:
					break

			format_notes.reverse()

			print("format_notes =",format_notes)

			for format_note in format_notes:
				#print("current format_note",format_note)

				if selected<0:
					i=len(info["formats"])-1

				while i>-1:
					#print("FORMAT",i,info["formats"][i])
					#print("\tformat_note",info["formats"][i]["format_note"])
					#print("\text",info["formats"][i]["ext"])
					#print("\tacodec",info["formats"][i]["acodec"])
					#print("\taudio_ext",info["formats"][i]["audio_ext"])

					# cformat=info["formats"][i]

					if info["formats"][i]["format_note"].startswith(format_note):
						if info["formats"][i]["ext"]=="mp4":
							if info["formats"][i]["acodec"].startswith("mp4"):
								selected=i
								print("SELECTED FORMAT",info["formats"][selected])

					i=i-1

	if selected>-1:
		return info["title"],info["formats"][selected]

	else:
		return None

# Youtube playlist gatherer (HOT AND HEAVY)
def youtube_getter_from_pl(url,outdir):
	msg_log=""
	msg_err=""
	urls=[]
	plinfo=[]
	try:
		playlist=Playlist(url)
		print("\nplaylist.info =",playlist.info)
		plinfo.append(playlist.info["info"]["title"])
		plinfo.append(playlist.info["info"]["id"])

	except Exception as e:
		msg_log="\n<p>Mientras se obtenía la lista de reproducción:\n<p><code>"+str(e)+"</code>"

	if len(msg_log)==0:
		try:
			while playlist.hasMoreVideos:
				playlist.getNextVideos()

		except Exception as e:
			msg_log="\n<p>Mientras se obtenían más enlaces:\n<p><code>"+str(e)+"</code>"

		for video in playlist.videos:
			try:
				vid=video["id"]
				vurl="https://youtu.be/"+vid
				urls.append(vurl)

			except Exception as e:
				msg_err=msg_err+"URL:"+vurl+";Error:"+str(e)+"\n"

	if len(msg_log)==0 and len(msg_err)>0:
		msg_log=="\n<p>Hubo errores al recuperar URLs"

	elif len(msg_log)==0 and len(msg_err)==0:
		msg_log=="OK"

	return msg_log,msg_err,plinfo,urls

#def youtube_getter_from_pl(url,outdir):
#
#	fatal=False
#	added=0
#	msg=""
#	msg_bigger=""
#
#	try:
#		playlist=Playlist(url)
#
#	except Exception as e:
#		msg="Mientras se obtenía la lista de reproducción:\n<code>"+str(e)+"<code>"
#		fatal=True
#
#	if not fatal:
#		try:
#			while playlist.hasMoreVideos:
#				playlist.getNextVideos()
#
#		except Exception as e:
#			if len(msg)>0:
#				msg=msg+"\n"
#
#			msg=msg+"<p>Mientras se agarraban más vídeos:\n<p><code>"+str(e)+"</code>"
#
#		for video in playlist.videos:
#			try:
#				vid=video["id"]
#				vurl="https://youtu.be/"+vid
#				value=[vurl,outdir,specs]
#				exists=que.check_value_spc(value)
#				if not exists:
#					que.add_value(value)
#
#			except Exception as e:
#				msg_bigger=msg_bigger+"URL:"+vurl+";Error:"+str(e)+"\n"
#
#			else:
#				added=added+1
#
#	return fatal,added,msg,msg_bigger

################################################################################
# MEGA
################################################################################

# MEGA Login
def mega_login(mega_object,username,password):

	try:
		if username and password:
			if len(username)>0 and len(password)>0:
				mega_object.login(username,password)

		else:
			mega_object.login()

	except Exception as e:
		print(e)

	else:
		print("OK")

# MEGA Downloader function
def mega_downloader(currdir,url,mega_object,filedata):

	filepath_show="???"
	retmsg=""
	exc=""

	try:
		print("getting url_info...")

		url_info_raw=mega_object.get_public_url_info(url)

		total_size=url_info_raw.get("size")
		filename=url_info_raw.get("name")
		print("total_size =",total_size)
		print("filename =",filename)

	except Exception as e:
		exc=str(e)
		retmsg="Al recoger datos del archivo: <code>"+exc+"</code>"

	else:
		downdir=str(currdir)
		filepath=currdir.joinpath(filename)
		filedata.update({"conf":True,"fpath":filepath,"tsize":total_size})

	if len(retmsg)==0:

		try:
			cancel_this=filedata.get("cancel")
			if cancel_this:
				raise Exception("Cancelado")

			if filepath.exists():
				raise Exception(_msg_error_exists)

			mega_object.download_url(url,downdir,data_link=filedata)

		except Exception as e:
			exc=str(e)
			retmsg="Proceso de descarga: <code>"+exc+"</code>"
		else:
			exc=""

		if "referenced before assignment" in exc:
			filedata.update({"kick":True})
			if filepath.exists():
				filepath.unlink()

	return retmsg

# New MEGA downloader: a MEGA object per URL
def mega_downloader_new(currdir,url,filedata,mega_user,mega_pass):

	filepath_show="???"
	retmsg=""
	exc=""

	mega_object=Mega()

	try:
		if mega_user and mega_pass:
			if len(mega_user)>0 and len(mega_pass)>0:
				mega_object.login(mega_user,mega_pass)
		else:
			mega_object.login()

	except Exception as e:
		exc=str(e)
		retmsg="Inicio de sesión: <code>"+exc+"</code>"

	else:
		print("OK")

	if len(retmsg)==0:
		try:
			print("getting url_info...")

			url_info_raw=mega_object.get_public_url_info(url)

			total_size=url_info_raw.get("size")
			filename=url_info_raw.get("name")
			print("total_size =",total_size)
			print("filename =",filename)

		except Exception as e:
			exc=str(e)
			retmsg="Al recoger datos del archivo: <code>"+exc+"</code>"

		else:
			downdir=str(currdir)
			filepath=currdir.joinpath(filename)
			filedata.update({"conf":True,"fpath":filepath,"tsize":total_size})

	if len(retmsg)==0:

		try:
			cancel_this=filedata.get("cancel")
			if cancel_this:
				raise Exception("Cancelado")

			if filepath.exists():
				raise Exception(_msg_error_exists)

			mega_object.download_url(url,downdir,data_link=filedata)

		except Exception as e:
			exc=str(e)
			retmsg="Proceso de descarga: <code>"+exc+"</code>"
		else:
			exc=""

		# Stupid error...
		if "referenced before assignment" in exc:
			filedata.update({"kick":True})
			if filepath.exists():
				filepath.unlink()

	del mega_object

	return retmsg

################################################################################
# Other functions
################################################################################

# 7Z Splitter
def sevenzipper(fdpath,psize,pwd):
	# splitter_data = {"the_user_id":0,"event_id":0,"csize":0,"tsize":0}
	output=""
	path_basedir=fdpath.parent

	if fdpath.is_dir():
		archive_name=fdpath.name+".7z"

	else:
		stembased=fdpath.stem+".7z"
		if stembased==fdpath.name:
			archive_name=fdpath.name+".7z"

		else:
			archive_name=stembased

	archive_path=path_basedir.joinpath(archive_name)

	if pwd:
		the_filter=_copy_filter_ext

	else:
		the_filter=_copy_filter

	try:
		if psize==0:
			if archive_path.exists():
				raise Exception("El archivo ya existe")

			with py7zr.SevenZipFile(str(archive_path),'w',filters=the_filter,password=pwd) as archive:
				if pwd:
					archive.set_encrypted_header(mode=True)

				archive.writeall(fdpath,fdpath.name)

		else:
			with multivolumefile.open(str(archive_path),'wb', psize*_megabyte) as target_archive:
				with py7zr.SevenZipFile(target_archive,'w',filters=the_filter,password=pwd) as archive:
					if pwd:
						archive.set_encrypted_header(mode=True)

					archive.writeall(fdpath,fdpath.name)

			vol=0
			while True:
				vol=vol+1
				osfx="."+paddednumb(9999,vol)
				ofse=path_basedir.joinpath(archive_name+osfx)
				if not ofse.exists():
					break

			if vol<1000:
				vol=0
				while True:
					vol=vol+1
					osfx="."+paddednumb(9999,vol)
					ofse=path_basedir.joinpath(archive_name+osfx)
					nsfx="."+paddednumb(999,vol)
					nfse=path_basedir.joinpath(archive_name+nsfx)
					if ofse.exists():
						ofse.rename(nfse)

					else:
						break

	except Exception as e:
		f="sevenzipper-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
		traceback.print_exc(file=open(f,"w"))
		output=str(e)

	return output

# Archive maker V2 (DISCHARGED)
def archiver(fdpath,atype=_tar,psize=1):
	bdpath=fdpath.parent
	aname=fdpath.name+atype
	apath_str=str(fdpath)+atype
	fdpath_str=str(fdpath)
	output=""
	try:
		if atype==_tar:
			raise Exception("DESHABILITADO POR RIESGO DE MEMORIA")
			#rel=fdpath.relative_to(bdpath)
			#with tarfile.open(apath_str,"w") as tar:
			#	tar.add(fdpath_str,arcname=str(rel))

		elif atype==_zip:
			raise Exception("DESHABILITADO POR RIESGO DE MEMORIA")
			#fse_list=list(fdpath.rglob("*"))
			#with ZipFile(fdpath_str,"w") as z:
			#	for fse in fse_list:
			#		fse_rel=fse.relative_to(bdpath)
			#		z.write(str(fse),arcname=str(fse_rel))

		elif atype==_7z:
			with multivolumefile.open(apath_str,'wb', psize*_megabyte) as target_archive:
				with py7zr.SevenZipFile(target_archive,'w',filters=_copy_filter) as archive:
					archive.writeall(fdpath,aname)

			rgx=r""+aname+".[0-9]*"
			afiles=list(bdpath.glob(rgx))

			# workaround for the multivolumefiles 4 figures thing...

			if len(afiles)<1000:
				for fse in afiles:
					osfx=fse.suffix
					nsfx=osfx[2:0]
					fse_nn=bdpath.joinpath(aname+nsfx)
					fse.rename(fse_nn)

		else:
			raise Exception("Formato no soportado. Avise al programador urgentemente")

	except Exception as e:
		output=str(e)

	return output

# Archive unpacker
def unpacker(tfile,outdir):
	m=""
	#infile_str=str(tfile[0])
	infile_str=str(tfile)

	print("tfile =",tfile)
	print("outdir =",outdir)

	# unzip
	# $ unzip tfile -d outdir
	try:
		if infile_str.endswith(".7z.001"):
			infile_7z=infile_str[:-4]
			with multivolumefile.open(infile_7z, mode="rb",password=None) as target_archive:
				with py7zr.SevenZipFile(target_archive,"rb") as archive:
					archive.extractall(str(outdir))

		elif infile_str.endswith(".7z"):
			with py7zr.SevenZipFile(infile_str,"r") as archive:
				archive.extractall(str(outdir))

		else:
			# shutil.unpack_archive(extractme,ticket)
			shutil.unpack_archive(infile_str,outdir)

	except Exception as e:
		m=str(e)

	return m

# KFSCrypt in a function. Returns key contents when making a key (default). Returns error log when encrypting/decrypting

_kfscrypt_mkey="MAKEKEY"
_kfscrypt_encr="ENCRYPT"
_kfscrypt_decr="DECRYPT"

def kfscrypt(uid,arg=_kfscrypt_mkey,cdir=None,inkey="",filepaths=[],data_link=None):

	if _kfscrypt_mkey in arg:
		outkey=Fernet.generate_key()
		return outkey

	if len(inkey)>0 and len(filepaths)>0:
		if (_kfscrypt_encr in arg) or (_kfscrypt_decr in arg):
			wutt=False
			msglog=[]
			try:
				key=Fernet(inkey)

			except Exception as e:
				wutt=True
				msglog=["<p>#Error al leer la clave\n<p>\t<code>"+str(e)+"</code>"]

			if not wutt:

				ticket=mkticket(uid,aspath=False)

				if _kfscrypt_encr in arg:
					chunksize=_megabyte
					outdir=cdir.joinpath(ticket+".EN")

				if _kfscrypt_decr in arg:
					chunksize=_megabyte_fe
					outdir=cdir.joinpath(ticket+".DE")

				if not outdir.exists():
					outdir.mkdir()

				opstat=""

				for tfile in filepaths:
					tfile_name=tfile.name
					outfile_pl=outdir.joinpath(tfile_name)

					data_link["e"]=""
					data_link["p"]=""
					data_link["f"]=tfile_name
					data_link["t"]=os.path.getsize(str(tfile))
					data_link["r"]=0
					data_link["w"]=0

					read=0
					proc=0

					time.sleep(1)

					print(str(tfile),"→",outfile_pl)
					try:
						if outfile_pl.exists():
							raise Exception("El archivo de salida ya existe")

						with open(str(tfile),"rb") as infile:
							while True:
								chunk=infile.read(chunksize)

								if len(chunk)>0:
									if _kfscrypt_encr in arg:
										data=key.encrypt(chunk)

									if _kfscrypt_decr in arg:
										data=key.decrypt(chunk)

									with open(str(outfile_pl),"ab") as outfile:
										outfile.write(data)

									read=read+len(chunk)
									proc=proc+len(data)

									data_link["r"]=read
									data_link["w"]=proc

									#time.sleep(1)

								else:
									break

					except Exception as e:
						data_link["e"]=str(e)
						if len(opstat)==0:
							opstat="<p>Se detectaron errores"

						print("ERROR:\n"+str(e))
						msglog=msglog+["<p>#Error al procesar el archivo <code>"+tfile_name+"\n<p>\t"+str(e)+"</code>"]

					else:
						data_link["e"]="OK"
						print("Completado")

					time.sleep(1)

				if len(opstat)==0:
					opstat="<p>Terminado sin errores"

				msglog=["<p>#Terminado\n<p>Salida: <code>"+get_path_show(outdir)+"</code>"]+[opstat]+msglog

			return msglog

################################################################################
# Async functions
################################################################################

# Wait before a heavy task
async def wait_global_queue(slug,qname,replyto,chat):

	print("waiting:",slug)

	mev=None

	msg_saved=""
	msg=""

	show=False

	wait=True
	while wait:

		pfff=False
		if qname=="INT":
			if slug==_gq_cpu[0] or len(_gq_cpu)==0:
				wait=False
			else:
				pfff=True

		if qname=="SUB":
			if slug==_gq_sub[0] or len(_gq_sub)==0:
				wait=False
			else:
				pfff=True

		if pfff:
			if not show:
				show=True
			await asyncio.sleep(1)

		if show:
			msg="<p>Usuarios en la cola global "+qname+":\n<p>"
			w=True
			index=0

			if qname=="INT":
				qqq=_gq_cpu

			if qname=="SUB":
				qqq=_gq_sub

			for s in qqq:
				if len(msg)<4000:
					msg=msg+"\n<p><code>"+str(s)+"</code>"
					if s==slug:
						msg=msg+" ← USTED ("+str(index)+")"

				else:
					if w:
						w=False

					if s==slug:
						break

				index=index+1

			msg=msg+"\n<p>"

			if not w:
				msg=msg+"\n<p>...\n<p>Posición "+str(index)

			if wait:
				end="\n<p>Por favor, espere..."
			else:
				end="\n<p>Ya es su turno"

			msg=msg+end

			if not msg==msg_saved:
				try:
					if not mev:
						mev=await replyto.reply(msg,parse_mode="html")
					else:
						await bot.edit_message(chat,mev,msg,parse_mode="html")

				except Exception as e:
					print("while waiting:",slug,":",e)

				else:
					msg_saved=msg

	print("doing this:",slug)

# subprocess shell run
async def shell_run(cmd):

	try:
		proc=await asyncio.create_subprocess_shell(cmd,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
		stdout_raw,stderr_raw=await proc.communicate()
		stdout=stdout_raw.decode()
		stderr=stderr_raw.decode()

	except Exception as e:
		stdout=""
		stderr="<p>Excepción grave:\n<p>"+str(e)

	return stdout,stderr

# Concatenator function (regular awaitable, put ntprog to work before this one)
async def concatenator(pathlist,thefilepath):
	funout=""
	try:
		async with aiofiles.open(thefilepath,"wb") as outfile:
			for fp in pathlist:
				print("fp =",fp)
				async with aiofiles.open(fp,"rb") as part:
					while True:
						chunk=await part.read(_megabyte)
						if chunk:
							await outfile.write(chunk)
						else:
							break

	except Exception as e:
		wutt=True
		funout=str(e)

	await asyncio.sleep(1)

	return funout

# Progress monitor for kfscrypt encryptions and decryptions
async def ntprog_kfscrypt(chat,repev,msg_head,data_link=None):
	try:
		sname=""
		msg_update=""
		while True:
			cname=data_link["f"]
			if len(cname)==0:
				await asyncio.sleep(0.2)

			if len(cname)>0:
				if not sname==cname:
					chain=None
					sname=cname
					read=data_link["r"]
					read_old=0
					wrote=data_link["w"]
					wrote_old=0
					rspeed=0
					wspeed=0
					total=data_link["t"]

				if sname==cname:
					read=data_link["r"]
					wrote=data_link["w"]

					read_txt="<p>Leído <code>"+hr_units(read)+"</code> de <code>"+hr_units(total)+"</code>\n"

					percent=round((read/total)*100,2)
					percent_txt="<p>P. Lectura <code>"+str(percent)+" %</code>\n"

					wrote_txt="<p>Escrito <code>"+hr_units(wrote)+"</code>\n"

					rspeed=read-read_old
					wspeed=wrote-wrote_old

					rspeed_txt="<p>V. Lectura <code>"+hr_units(rspeed)+"/seg</code>\n"
					wspeed_txt="<p>V. Escritura <code>"+hr_units(wspeed)+"/seg</code>\n"

					read_old=read
					wrote_old=wrote

					err=data_link["e"]
					if len(err)>0:
						err_txt="<p>Resultado: <code>"+err+"</code>"
					else:
						err_txt=""

					msg_update="<p>Nombre: <code>"+cname+"</code>\n"+read_txt+percent_txt+rspeed_txt+wrote_txt+wspeed_txt+err_txt

				try:
					if data_link["p"]==msg_update:
						raise Exception("same shit!")

					if chain:
						await bot.edit_message(chat,chain,msg_head+msg_update,parse_mode="html")

					else:
						chain=await repev.reply(msg_head+msg_update,parse_mode="html")

				except Exception as e:
					print("error at bot.edit_message() or repev.reply() at ntprog_kfscrypt()",e)

				else:
					data_link["p"]=msg_update

				await asyncio.sleep(1)

	except asyncio.CancelledError:
		raise

	except:
		raise

	finally:
		pass

# Download/Growth monitor
async def ntprog(chat,editev,fpath,tsize,mheader,filedata=None,backup=None,fname_from_path=True):
	try:
		if filedata:
			while True:
				print("waiting for conf...")
				await asyncio.sleep(0.2)
				conf=filedata["conf"]
				if conf:
					break

			fpath=filedata["fpath"]
			tsize=filedata["tsize"]

		if fname_from_path:
			fname=fpath.name

		csize=0
		psize=0
		um=""
		while True:
			print("waiting for file...")
			if fpath.exists():
				break

			else:
				await asyncio.sleep(0.2)

		keepon=True
		fcount=0
		aspeed=0
		while csize<tsize:
			print("filedata =",filedata)
			await asyncio.sleep(1)
			if fpath.exists():
				if fpath.is_file():
					csize=os.path.getsize(str(fpath))

				else:
					size=0

					try:
						for fse in list(fpath.rglob("*")):
							if fse.is_file():
								size=size+os.path.getsize(str(fse))

					except Exception as e:
						print("ntprog()",e)

					else:
						csize=size

				aspeed=csize-psize
				psize=csize
				percent=round((csize/tsize)*100,2)
				um="\n<p><code>"+hr_units(csize)+" / "+hr_units(tsize)+"\n<p>"+hr_units(aspeed)+"/seg\n<p>"+str(percent)+" %</code>"

				if filedata:
					if fname_from_path:
						um="\n<p><code>"+fname+um+"</code>"

				print(fname,"→",csize,"/",tsize)

				if csize==tsize:
					# um=um+"\n<p>OK"
					keepon=False

				#else:
				#	um=um+"\n<p>INTERRUMPIDO"

				if aspeed==0 and csize>0:
					fcount=fcount+1
					if fcount>30:
						keepon=False
						# um=um+"\n<p>???"
				else:
					fcount=0

			else:
				#status="<p>#archivo #interrumpido\n"
				#um=um+"\n<p>INTERRUMPIDO"
				keepon=False

			try:
				await bot.edit_message(chat,editev,mheader+um,parse_mode="html")

			except Exception as e:
				print("Download Monitor error: ",str(e))

			else:
				if filedata:
					filedata.update({"msg":um})
				else:
					backup.update({"msg":um})

			if not keepon:
				break

	except asyncio.CancelledError:
		raise

	except:
		raise

	finally:
		print("STOP MONITORING...")
		pass

class ProgressUnit:
	def __init__(self):
		self.start_time=time.time()
		self.time_between=1
		self.data=0
		self.log=""

	#def can_send(self):
	#	if time.time()>(self.start_time+self.time_between):
	#		self.start_time=time.time()
	#		return True
	#
	#	return False

	# Progress update (used for telegram transfers)
	async def progress_update(self,msghead,chat,msgev,variable,limit):
		if time.time()>(self.start_time+self.time_between):
			self.start_time=time.time()
			if variable<limit:
				aspeed=variable-self.data
				aspeed_txt="<p>"+hr_units(aspeed)+"/seg\n"

			else:
				aspeed_txt=""

			self.data=variable
			percent=round((variable/limit)*100,2)
			msgv="\n<p><code>"+hr_units(variable)+" / "+hr_units(limit)+"\n"+aspeed_txt+"<p>"+str(percent)+" %</code>"

			try:
				await bot.edit_message(chat,msgev,msghead+msgv,parse_mode="html")
			except Exception as e:
				print("Error at /upload in the progress_callback function: progress_tgupload():",e)
			else:
				print("ProgressUnit()",variable,"/",limit)
				self.log=msgv

# Telegram Download progress meter (progress_callback at download_media())
async def progress_tgdownload(punit,msghead,chat,msgev,recieved_bytes,total):
	if total>_megabyte or total==recieved_bytes:
		await punit.progress_update(msghead,chat,msgev,recieved_bytes,total)

# Telegram Upload progress meter (progress_callback at send_file())
async def progress_tgupload(punit,msghead,chat,msgev,sent_bytes,total):
	if total>_megabyte or total==sent_bytes:
		await punit.progress_update(msghead,chat,msgev,sent_bytes,total)

# Task admin
async def task_admin(the_task,q=None):
	while True:
		print("...")
		if q:
			kill=q.attrib["cancel"]
			if kill:
				the_task.cancel()
				print("TASK_CANCELLED")

		done=the_task.done()
		print("done =",done)
		if done:
			print("TASK_DONE")
			break

		else:
			await asyncio.sleep(1)

	print("OUTSIDE THE LOOP")

	if the_task.cancelled():
		print("Task got cancelled...")
		msg="Cancelado"

	else:
		print("Task had an error...")
		exc=the_task.exception()
		if exc:

			if q:
				q.attrib.update({"exc":exc})

			if len(str(exc))>0:
				msg=str(exc)
			else:
				msg="Error desconocido"

		else:
			msg="OK"

	print("Ending task_admin()...")
	return msg

# Downloads file from telegram to the bot
async def tgdownloader(punit,event_with_payload,filepath,tsize,msghead,the_chat,the_msgev):
	try:
		await event_with_payload.download_media(file=str(filepath),progress_callback=partial(progress_tgdownload,punit,msghead,the_chat,the_msgev))
		await asyncio.sleep(1)
		await punit.progress_update(msghead,the_chat,the_msgev,tsize,tsize)
		await asyncio.sleep(1)
	except asyncio.CancelledError:
		raise

	except:
		f="tgdownloader-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
		traceback.print_exc(file=open(f,"w"))
		raise

	finally:
		pass

# Uploads file from bot to telegram
async def tguploader(punit,filepath,tsize,msghead,the_chat,the_msgev):
	try:
		await bot.send_file(the_chat,file=str(filepath),force_document=True,progress_callback=partial(progress_tgupload,punit,msghead,the_chat,the_msgev))
		await asyncio.sleep(1)
		await punit.progress_update(msghead,the_chat,the_msgev,tsize,tsize)
		await asyncio.sleep(1)
	except asyncio.CancelledError:
		raise

	except:
		f="tguploader-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
		traceback.print_exc(file=open(f,"w"))
		raise

	finally:
		pass

# Web downloader
async def webdownloader(session,the_url,the_path,the_cookies=None,data_link=None):
	try:
		async with session.get(the_url,cookies=the_cookies) as response:
			httprs=str(response.status)
			assert httprs.startswith("2")
			if data_link:
				if not response.headers.get("content-disposition"):
					raise Exception("No se encontró el archivo")

				filename=response.content_disposition.filename
				total_size_raw=response.headers.get("content-length")
				total_size=int(total_size_raw)

				odir=data_link["outdir"]
				the_path=odir.joinpath(filename)
				if the_path.exists():
					raise Exception(_msg_error_exists)

				data_link["fpath"]=the_path
				data_link["tsize"]=total_size
				data_link["conf"]=True

			mode="b"
			if the_path.exists():
				mode="a"+mode

			else:
				mode="w"+mode

			async with aiofiles.open(str(the_path),mode) as outfile:
				while True:
					chunk=await response.content.read(_megabyte)
					if chunk:
						await outfile.write(chunk)

					else:
						break

	except asyncio.CancelledError:
		raise

	except:
		f="webdownloader-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
		traceback.print_exc(file=open(f,"w"))
		raise

	finally:
		pass

################################################################################
# THE Bot Event Handler
################################################################################

_the_channel=[None]

async def tge_handler_messages(event):
	global _devmode

	channel_obj=_the_channel[0]

	# Chat type filter
	if event.is_group:
		print("Cannot run event handler in a group")
		return

	try:
		the_user_id=str(event.peer_id.user_id)

	except:
		print("usser_id not found conventionally")
		return

	# Channel object getter
	if not channel_obj:
		wtf=False
		try:
			channel_val=int(_ev_channel)

		except:
			wtf=True

		if not wtf:
			channel_obj=await bot.get_entity(channel_val)
			print("channel_obj =",channel_obj.id)
			if not channel_obj:
				wtf=True

			else:
				if not channel_obj.has_link:
					wtf=True

				if not channel_obj.broadcast:
					wtf=True

		if wtf:
			print("ERROR: MAKE SURE THE ID IS VALID, EXISTS, BELONGS TO A PUBLIC CHANNEL AND THE BOT IS A MEMBER OF IT")
			return

		if not wtf:
			_the_channel[0]=channel_obj

	# Chat and user info gathering

	transfer_jobs=0
	success=False
	msg=""
	wutt=False
	user_is_ban=False
	user_is_vip=False
	user_is_admin=False

	# Message or file detection

	if event.file or len(event.raw_text)>0:

		if len(_banlist)>0:
			for uid in _banlist:
				if not user_is_ban:
					if uid==the_user_id:
						user_is_ban=True

		if user_is_ban:
			# For banned users, the bot will not even respond to ANYTHING they do
			print("Banned user",the_user_id,"attempted to use the bot")
			return

		if len(_viplist)>0:
			if the_user_id in _viplist:
				user_is_vip=True

		if user_is_vip:
			if the_user_id==_viplist[0]:
				user_is_admin=True

		if _devmode:
			if not user_is_admin:
				if event.file:
					return

				if len(event.raw_text)>0:
					await event.reply(_devmode_label)
					print("Regular user",uid,"attempted to use the bot")
					return

	################################################################################
	# User session handling
	################################################################################

	thischat = await event.get_chat()

	session_link=_sessions.get(the_user_id)

	print("session_link =",session_link)

	must_verify=False

	if session_link:
		new=False
		mark=session_link[0]
		if mark:
			if type(mark) is str:
				print("\t",the_user_id,"has not joined")
				must_verify=True
				new=True

			else:
				now=time.time()
				if now-mark>60:
					print("\t",the_user_id,"must be verified again")

				else:
					print("\t",the_user_id,"can continue")
					session_link[_sd_time]=now

		else:
			print("\t",the_user_id,"request already pending...")
			return

	else:
		print("\t",the_user_id,"must be verified before creating a session")
		new=True
		must_verify=True
		sd=[None]
		lim=_sdid+1
		while len(sd)<lim:
			sd=sd+sd

		_sessions.update({the_user_id:sd})

	if must_verify:

		if user_is_admin:
			is_channel_member=True
		else:
			is_channel_member=False

		if not is_channel_member:
			if the_user_id in _gq_req:
				return

			_gq_req.append(the_user_id)

			while True:
				if len(_gq_req)==0:
					break

				if _gq_req[0]==the_user_id:
					break

				else:
					print("waiting in line:",_gq_req)
					await asyncio.sleep(1)

			# https://api.telegram.org/bot{TOKEN}/

			vurl="https://bocv.up.railway.app/?user="+the_user_id
			print("vurl =",vurl)
			try:
				mytimeout=aiohttp.ClientTimeout(total=10)
				async with aiohttp.ClientSession(timeout=mytimeout) as session:
					async with session.get(vurl) as response:
						m=await response.text()
						print("\m =",m,"\n\nresponse.headers =",response.headers)
						assert response.status==200

			except Exception as e:
				f="verifying-"+the_user_id+"-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
				traceback.print_exc(file=open(f,"w"))
				with open(f,"at") as ff:
					ff.write("\nRESPONSE ="+m)

				print("While verifying",the_user_id,"→",e)
			else:
				is_channel_member=True

			try:
				_gq_req.pop(0)
			except:
				pass

		if not is_channel_member:
			await event.reply("<p>Únete a este canal para usar el bot:\n<p><a href=https://t.me/"+channel_obj.username+">"+channel_obj.title+"</a>",parse_mode="html")
			sd[_sd_time]="PENDING..."
			return

		if not new:
			return

		# Non Visible
		sd[_sd_saved]=""
		sd[_sd_time]=time.time()
		sd[_sd_exec_mv]=False
		sd[_sd_exec_rm]=False
		sd[_sd_hview]=False

		# Visible by other means
		sd[_sd_fkey]=""
		queuedict={"d":QueueForTGE("Cola de descarga de Telegram al bot"),"u":QueueForFiles("Cola de subida a Telegram"),"w":QueueForURLs("Cola de descarga general"),"g":QueueForURLs("Cola de Google Drive"),"m":QueueForURLs("Cola de descarga MEGA"),"y":QueueForURLs("Cola de descarga Youtube")}

		# Special queue in MEGA 
		queuedict["m"].attrib.update({"conf":False,"fpath":None,"tsize":0})
		queuedict["d"].attrib.update({"rec":False})

		if user_is_vip:
			queuedict.update({"c":QueueForURLs("Cola de Manga y Comics")})

		sd[_sd_que]=queuedict

		# Visible through /start
		sd[_sd_hproc]=""
		sd[_sd_autodl]=False
		sd[_sd_cwd]=Path(the_user_id)
		sd[_sd_netwquota]=0
		sd[_sd_ua]="r"
		sd[_sd_mega_session]=["",""]
		sd[_sd_shared]=""
		sd[_sd_shared_name]=""

		#if user_is_vip:
		#	sd[_sd_todus_atds3]=False
		#	sd[_sd_todus_dl]=_job_ready
		#	sd[_sd_todus_token]="..."
		#	sd[_sd_todus_token_last]=""

		if not os.path.exists(the_user_id):
			os.mkdir(the_user_id)

		if user_is_vip:
			msg_extra_vip="\n<p>\n<p>Usted es un miembro privilegiado, tiene acceso a comandos VIP"

		else:
			msg_extra_vip=""

		msg="<p><strong>"+_the_name_of_the_bot+"</strong>\n<p>\n<p>🔑 Sesión iniciada 🔑\n<p>\n<p>Ejecuta /help para aprender a usar el bot"+msg_extra_vip

		await event.reply(msg,parse_mode="html")

		session_link=_sessions.get(the_user_id)

		if len(admin_public_messages)>1:

			await asyncio.sleep(0.1)
			if len(admin_public_messages)==2:
				data=admin_public_messages[0].get_data()
				print(data)
				msg="⚠️ <strong>"+data[0]+"</strong> ⚠️\n<p>"+data[1]+"\n\nFuente: "+_ev_website_url+"news"

			else:
				msg="<p>⚠️ Atención ⚠️\n<p>\n<p>El administrador del bot ha dejado más de un mensaje en el sitio web: "+_ev_website_url+"news"

			await event.reply(msg,parse_mode="html")
			return

	################################################################################
	# Reception of files and messages
	################################################################################

	# Special case: Automatic album/file downloader and the "/download" command

	tgfiledl=False
	if event.file:
		autod=session_link[_sd_autodl]
		if autod:
			tgfiledl=True
			thepayload=event
			thyargs=["/download"]

	if not tgfiledl:
		if event.is_reply:
			thepayload=await event.get_reply_message()
			if thepayload.file and tg_cmd_chk(event.raw_text):
				raw_shit=event.raw_text
				thyargs=raw_shit.split(" ",1)
				if thyargs[0]=="/download":
					tgfiledl=True

	if tgfiledl:

		command=thyargs[0]

		if len(thyargs)>1:
			argname=thyargs[1]

		else:
			argname=""

		cwd=session_link[_sd_cwd]

		allow=False

		if thepayload.photo:

			if len(argname)>0:
				filename=argname

			else:
				autoname=False
				try:
					filename=thepayload.file.name

				except:
					autoname=True

				else:
					try:
						assert len(filename)>0

					except:
						autoname=True

				if autoname:
					filename=the_user_id+"-"+str(thepayload.id)

			filepath_full=cwd.joinpath(filename)

			try:
				realpath=await thepayload.download_media(file=filepath_full)

			except Exception as e:
				msg="<p>#Error al descargar: <code>"+str(e)+"</code>"

			else:
				filepath=get_path_show(filepath_full)
				msg="<p>#Descargado\n<p><code>"+filepath+"</code>"

			await thepayload.reply(msg,parse_mode="html")

		else:

			que=session_link[_sd_que]["d"]

			print("Adding",thepayload.id,"[BEFORE] que.queue =",que.queue)

			if que.get_size()>0:
				initiate=False

			else:
				initiate=True

			if que.attrib["rec"]:
				initiate=False

			else:
				que.attrib["rec"]=True

			if len(argname)>0:
				sug=argname
			else:
				sug=None

			value=[thepayload,sug,cwd]

			if que.check_value(value):
				obj_add=False

			else:
				obj_add=True

			if obj_add:
				qs=await thepayload.reply("Archivo agregado a la cola")
				que.add_value(value)

			else:
				await thepayload.reply("El archivo ya está en la cola")
				if initiate:
					initiate=False

			print("Adding",thepayload.id,"[AFTER] que.queue =",que.queue)

			if not initiate:
				wutt=True

			if not wutt:
				ntjobs=session_link[_sd_netwquota]
				if ntjobs==_sntl:
					await thepayload.reply("<p>#download #error\n<p><code>"+_msg_error_tquota+"</code>",parse_mode="html")
					wutt=True

			if not wutt:
				session_link[_sd_netwquota]=ntjobs+1

				iterate=True
				this=await qs.reply("#download")

				que.attrib["working"]=True

				while iterate:

					que.attrib["cancel"]=False
					element=que.get_value()
					print("element =",element)
					payload,fname,cwd=element

					while True:
						brake=que.attrib["brake"]
						if not brake:
							break

						else:
							await asyncio.sleep(1)

					msg_head1="<p>#archivo"
					msg_head2=que.show_value(element)

					cjob=await this.reply(msg_head1+msg_head2,parse_mode="html")

					await asyncio.sleep(0.5)

					if not fname:
						try:
							fname=payload.file.name
							assert len(fname)>0
						except:
							autoname=True
						else:
							autoname=False

						if autoname:
							fname=the_user_id+"-"+str(payload.id)

					fpath=cwd.joinpath(fname)

					if fpath.exists():
						msg_head1=msg_head1+" #error"
						await bot.edit_message(thischat,cjob,msg_head1+msg_head2+"<p>\n<p>El archivo ya existe\n<p><code>"+get_path_show(fpath)+"</code>",parse_mode="html")
						wutt=True

					if not wutt:

						loop=asyncio.get_event_loop()

						total_size=payload.file.size

						punit=ProgressUnit()
						tgdown=loop.create_task(tgdownloader(punit,payload,fpath,total_size,msg_head1+msg_head2,thischat,cjob))

						msg=await task_admin(tgdown,que)

						#if os.path.getsize(str(fpath))==total_size and total_size>_megabyte:
						#	await punit.progress_update(msg_head1+msg_head2,thischat,cjob,total_size,total_size)

						print("finished download task")

						await asyncio.sleep(0.5)
						try:
							await bot.edit_message(thischat,cjob,msg_head1+msg_head2+punit.log+"\n<p><code>"+msg+"</code>",parse_mode="html")
						except Exception as e:
							print(the_user_id,"/download last bot.edit_message() in the while loop:",e)

						del tgdown
						del punit

					que.del_index()
					if que.get_size()==0:
						iterate=False
						await this.reply("Ya no queda nada que procesar en la cola")

					else:
						await this.reply("Pasando al siguiente elemento en la cola")
						await asyncio.sleep(0.5)

					wutt=False

				que.attrib["working"]=False

				n=session_link[_sd_netwquota]
				if n>0:
					session_link[_sd_netwquota]=n-1

			que.attrib["rec"]=False

			return

	# Regular commands

	if tg_cmd_chk(event.raw_text):

		# Filter for the "/ok" command

		raw_shit=event.raw_text

		confirmed=False
		saved=session_link[_sd_saved]
		if len(saved)>0:
			print("saved =",saved)
			if raw_shit=="/ok" or raw_shit==saved:
				raw_shit=saved
				msg_ok="Confirmado"
				confirmed=True

			else:
				msg_ok="Cancelado"

			session_link[_sd_saved]=""

			await asyncio.sleep(0.2)
			await event.reply(msg_ok)
			await asyncio.sleep(0.2)

			print("new raw_shit =",raw_shit)

		command=raw_shit.split(" ")[0]
		command_found=False

		# Check if the command exists
		if command in cmdlist_all.keys():
			command_found=True

		# VIP commands do not exist for non-VIP users
		if command_found:
			if command in _clist_vip.keys():
				if not user_is_vip:
					command_found=False

		# Admin commands do not exist for non-admins
		if command_found:
			if command in _clist_dev.keys():
				if not user_is_admin:
					command_found=False

		if not command_found:
			await event.reply("Comando desconocido")
			return

		if command_found:

			arg_count=cmdlist_all.get(command)

			if arg_count==0:
				print(the_user_id,"executes",command)

			if arg_count>0:

				raw_split=raw_shit.split(" ",arg_count)[1:]

				args=[]
				for arg_raw in raw_split:
					args=args+[arg_raw.strip()]

				print(the_user_id,"executes",command,args)

			# Arguments are saved in the "args" list

			# Commands that work only as replies to other messages

			if event.is_reply:

				replied=await event.get_reply_message()

				replyto=event

				# ADMIN ONLY: posts a message at the news section
				if "/devpost" in command:
					if len(args)==1:
						title=args[0]

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						if replied.document or replied.video or replied.photo:
							wutt=True
							msg="Solo se aceptan mensajes"

						elif len(replied.raw_text)>0:
							text_raw=replied.raw_text

						else:
							wutt=True
							msg="???"

					if not wutt:
						admin_post_add(title,text_raw)
						info=await bot.get_me()
						await bot.send_message(channel_obj,"<p><strong>"+title+"</strong>\n<p>\n<p>"+text_raw+"\n<p>\n<p><a href=https://t.me/"+info.username+">"+info.first_name+"</a>",parse_mode="html")
						msg="Mensaje enviado al sitio web y al canal"

					await replyto.reply(msg)

					return

				# Telegram to bot
				if "/download" in command:
					if len(replied.message)>0:
						cwd=session_link[_sd_cwd]
						msg_error="<p>#Error al guardar mensaje\n"
						if len(args)==1:
							pass

						else:
							wutt=True
							msg=_msg_error_wargs

						if not wutt:
							the_arg=args[0]

							if check_correct_fse_name(the_arg):
								pass

							else:
								wutt=True
								msg=_msg_error_iarg

						if not wutt:
							filepathfull=Path(current_directory).joinpath(the_arg)

							# if os.path.exists(filepathfull):
							if filepathfull.exists():
								wutt=True
								msg=_msg_error_exists

						if not wutt:
							thetext=replied.message
							try:
								async with aiofiles.open(str(filepathfull),"wt") as txt:
									await txt.write(thetext)

							except Exception as e:
								wutt=True
								msg=str(e)

							else:
								msg="<p>Mensaje guardado en\n<p><code>"+get_path_show(filepathfull)+"</code>"

					else:
						wutt=True
						msg="???"

					if wutt:
						await replyto.reply(msg_error+"<p><code>"+msg+"</code>",parse_mode="html")

					else:
						await replyto.reply("<p>#Completo\n"+msg,parse_mode="html")

				# Dump Telegram info from a file
				if "/info" in command:
					msg_error="Error al mostrar la información\n"
					msg=""
					print("\nreplied =",replied)
					if replied.photo or replied.document or replied.video or replied.audio or replied.voice:
						fname=replied.file.name
						sfx=replied.file.ext

						if not fname:
							filename="Ninguno"

						else:
							filename="<code>"+fname+"</code>"

						if not sfx:
							suffix="Ninguno"

						else:
							suffix="<code>"+sfx+"</code>"

						mtype=replied.file.mime_type
						msg=msg+"<p><strong>Datos recogidos</strong>\n<p>\n<p>Nombre: "+filename+"\n<p>Sufijo: "+suffix+"\n<p>Tipo MIME: <code>"+mtype+"</code>\n"
						if replied.photo or replied.video:
							w=str(replied.file.width)
							h=str(replied.file.height)
							msg=msg+"<p>Dimensiones: <code>"+w+" x "+h+"</code>\n"

						size_show=hr_units(replied.file.size)
						msg=msg+"<p>Tamaño: <code>"+size_show+"</code>"
						dmessage=event

					else:
						wutt=True
						msg=msg+"No se detectó nada en el mensaje"

					if wutt:
						await event.reply(msg)

					else:
						await dmessage.reply(msg,parse_mode="html")

				# KFSCRYPT File Key Reader

				if "/crypt" in command:

					hproc=session_link[_sd_hproc]
					if len(hproc)>0:
						if hproc in command:
							await event.reply("Espere a que el otro proceso de crypt termine")
							return

					readfile=False
					fkey=session_link[_sd_fkey]

					if len(args)<3:
						if len(args)>0:
							if args[0]=="r":
								readfile=True

							else:
								wutt=True
								msg=_msg_error_iarg

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						if readfile:
							if len(fkey)>0:
								if len(args)>1:
									try:
										assert args[1]=="f"

									except:
										wutt=True
										msg=_msg_error_iarg

								else:
									wutt=True
									msg="Ya existe una clave. Ejecute con el argumento extra 'f' para forzar el cambio a la nueva clave."

					if not wutt:

						ticket=mkticket(the_user_id)
						dkey=ticket+".key"
						vmime="application/pgp-keys"

						try:
							assert replied.file.mime_type==vmime
							assert replied.file.size<100
							fname=replied.file.name
							assert fname.endswith(".fernet.key")

						except Exception as e:
							wutt=True
							msg="El archivo no es válido o no contiene una clave válida"
							print(the_user_id,"while using /crypt to load a key, caused an error:",e)

					if not wutt:
						print("dkey",dkey)
						try:
							await replied.download_media(file=dkey)

						except Exception as e:
							wutt=True
							msg="Fallo al descargar el archivo con la clave:\n<p><code>"+str(e)+"</code>"

					if not wutt:
						try:
							async with aiofiles.open(dkey) as tkey:
								thykey=await tkey.read()

							#if not type(thykey)==bytes:
							#	raise Exception("El contenido del archivo no es válido")

						except Exception as e:
							wutt=True
							msg="Fallo al leer el archivo con la clave:\n<p><code>"+str(e)+"</code>"

						else:
							Path(dkey).unlink()

					if not wutt:
						if readfile:
							session_link[_sd_fkey]=thykey
							msg="<p>Ha cambiado de clave a partir del archivo seleccionado:\n<p><code>"+str(thykey)+"</code>"

						else:
							if len(fkey)>0:
								fkey_str="<code>"+str(fkey)+"</code>"

							else:
								fkey_str="Ninguna"

							thykey_str="<code>"+str(thykey)+"</code>"
							msg="<p><strong>Comparación de claves</strong>\n<p>\n<p>Clave del archivo: "+thykey_str+"\n<p>Clave guardada: "+fkey_str

					if wutt:
						msg="<p>#Error\n<p>"+msg

					await event.reply(msg,parse_mode="html")

#				# Download files from toDus. Grab TXT from current directory
#				if "/tdl" in command:
#					msg_error="Error al iniciar el descargador de de toDus\n"
#					try:
#						assert replied.file.mime_type=="text/plain"
#
#					except:
#						wutt=True
#						msg=msg_error+"El archivo no es un TXT"
#
#					else:
#
#						transfer_jobs=session_link[_sd_netwquota]
#
#						tdjobstat=session_link[_sd_todus_dl]
#
#						if tdjobstat==_job_ready:
#							pass
#
#						else:
#							wutt=True
#							msg="Ocupado con otro TXT"
#
#					if not wutt:
#						if transfer_jobs<_sntl:
#							session_link[_sd_netwquota]=transfer_jobs+1
#
#							session_link[_sd_todus_dl]=_job_working
#
#							atds3_support=session_link[_sd_todus_atds3]
#							current_directory=session_link[_sd_cwd]
#
#							# ddir=path_gitgud(the_user_id+"/"+current_directory)
#							ddir=Path(the_user_dir).joinpath(current_directory)
#							txtfile_abspath=mkticket(the_user_id)+".txt"
#
#							await replied.download_media(file=txtfile_abspath)
#
#							lines=[]
#							try:
#								txtfile_openedup=open(txtfile_abspath,"r")
#								lines_read_raw=txtfile_openedup.readlines()
#								for line in lines_read_raw:
#									try:
#										splitme=line.split("\t")
#										url=splitme[0]
#										if url.startswith("https://s3.todus.cu/"):
#											#fullpath=path_gitgud(ddir+"/"+splitme[1].strip())
#											fname=splitme[1].strip()
#											fullpath=ddir.joinpath(fname)
#											lines=lines+[[url,str(fullpath)]]
#
#									except:
#										print("pfffff\n",line)
#
#								txtfile_openedup.close()
#								# os.path.remove(txtfile_abspath)
#
#							except Exception as e:
#								wutt=True
#								msgerr=str(e)
#
#							# The real deal starts here
#
#							if not wutt:
#								if len(lines)>0:
#
#									exitcode=0
#
#									# 0 = smooth than a mother fucker
#									# 1 = misc errors, SSL and shit, skip for now
#									# 2 = 404, skip and reduce life to zero
#									# 3 = auth error or limit error, request a new token
#									# 4 = token simply not valid, request a new token
#									# (exitcode>2 and no atds3_support) → cancel everything
#
#									async def check_cancellation(ecode):
#										if session_link[_sd_todus_dl]==_job_cancel and ecode<5:
#											ecode=5
#											await event.reply("#Cancelando")
#
#										return ecode
#
#									print("current_directory =",current_directory)
#
#									# cmdlink=await event.reply("#Inicio Descargador de toDus")
#
#									jobman=session_link[_sd_obj_jobman]
#
#									keepgoing=True
#
#									ttoken=""
#
#									halt=False
#
#									total_lines=len(lines)
#
#									while keepgoing:
#
#										# Check wether continue the loop or not based on the size of the "lines" list
#
#										progress=total_lines-len(lines)
#										msg_main_ct="#tdl #txt\n\nTotal "+str(total_lines)+"\nProcesados "+str(progress)
#										if total_lines==len(lines):
#											msg_main_ev=await event.reply(msg_main_ct)
#
#										else:
#											await bot.edit_message(thischat,msg_main_ev,msg_main_ct,parse_mode="html")
#
#										exitcode=0
#										finished=False
#
#										exitcode=await check_cancellation(exitcode)
#
#										if exitcode==5:
#											keepgoing=False
#
#										if len(lines)==0:
#											keepgoing=False
#
#										if keepgoing:
#											job=lines[0]
#											job_url,job_path=job
#											job_path_name=Path(job_path).name
#
#											tryagain=True
#											total_size=0
#
#											msg_part_log=""
#
#											pmsg=None
#
#											while tryagain:
#												exitcode=await check_cancellation(exitcode)
#
#												msg_part_ct="<p>#tdl #trabajo\n<p>\n<p>Salida: <code>"+current_directory+"</code>\n<p>URL: <code>"+job_url+"</code>\n<p>Archivo: <code>"+str(job_path_name)+"</code>\n"
#												if total_size>0:
#													msg_part_ct=msg_part_ct+"<p>Longitud: <code>"+hr_units(total_size)+"</code>\n"
#
#												if not exitcode==5:
#													# Retry due to misc error
#													if exitcode>0:
#														msg_part_log="<p>Reintentando...\n"
#
#														# Erase current token and get a new one (ATDS3 support only)
#														if exitcode>2 and len(ttoken)>0:
#															if session_link[_sd_todus_token_last]==ttoken:
#																session_link[_sd_todus_token_last]=""
#
#															ttoken=""
#															msg_part_log=msg_part_log+"<p>Buscando un nuevo token...\n"
#
#														else:
#															msg_part_log=msg_part_log+"<p>Usando el mismo token...\n"
#
#														exitcode=0
#
#													else:
#														msg_part_log="<p>Iniciando...\n"
#
#													if total_lines==len(lines):
#														msg_part_ev=await event.reply(msg_part_ct+msg_part_log,parse_mode="html")
#
#													else:
#														await bot.edit_message(thischat,msg_part_ev,msg_part_ct+msg_part_log,parse_mode="html")
#
#													await asyncio.sleep(1)
#
#												exitcode=await check_cancellation(exitcode)
#
#												if exitcode==0:
#													if len(ttoken)==0:
#														if atds3_support:
#
#															msg="<p>Esperando un token de AGTPP..."
#															await bot.edit_message(thischat,msg_part_ev,msg_part_ct+msg_part_log+msg,parse_mode="html")
#
#															loop=asyncio.get_event_loop()
#															task=loop.create_task(agtpp_fetch())
#
#															searching=True
#															while searching:
#																exitcode=await check_cancellation(exitcode)
#
#																if exitcode==5:
#																	task.cancel()
#
#																if task.done():
#																	searching=False
#																	ttoken=task.result()
#
#																if task.cancelled():
#																	searching=False
#
#																await asyncio.sleep(1)
#
#														else:
#															ttoken=session_link[_sd_todus_token]
#
#												exitcode=await check_cancellation(exitcode)
#
#												if exitcode==0:
#													try:
#														token_core=ttoken.split(" ")[1]
#														print("Token =",ttoken)
#														print("Token Core =",token_core)
#														print("")
#														assert len(ttoken)==168
#														assert len(token_core)==161
#														assert ttoken.startswith("Bearer ")
#
#													except:
#														exitcode=4
#														msg="<p>#Error El \"token\" dado no es válido"
#
#													else:
#														msg="<p>El token es válido. Firmando enlace..."
#
#													await bot.edit_message(thischat,msg_part_ev,msg_part_ct+msg_part_log+msg,parse_mode="html")
#
#												exitcode=await check_cancellation(exitcode)
#
#												if exitcode==0:
#
#													await asyncio.sleep(1)
#
#													print("REMEMBER THIS IS THE TOKEN USED:",ttoken)
#
#													print("Step 2. Token OK. Signing URL...")
#
#													loop = asyncio.get_event_loop()
#													signed_url=await loop.run_in_executor(None,get_signed_url,token_core,job_url)
#
#													print("signed_url =",signed_url)
#													print("job_url =",job_url)
#
#													try:
#														if signed_url==None:
#															raise Exception("Error desconocido")
#
#														elif "auth_err" in signed_url:
#															raise AuthError()
#															# raise Exception()
#
#														elif "limit_err" in signed_url:
#															raise LimitError()
#															# raise Exception()
#
#														else:
#															if signed_url.startswith(job_url):
#																print("URL Signed Correctly")
#
#															else:
#																raise Exception("Error desconocido")
#
#													except AuthError:
#														exitcode=3
#														msg="<p>#Error "+activity+"Autenticación"
#
#													except LimitError:
#														exitcode=3
#														msg="<p>#Error "+activity+"Cuota superada"
#
#													except Exception as e:
#														print("e =",e)
#														msg="<p>#Error "+activity+"(no registrado):\n<p><code>"+str(e)+"</code>"
#														exitcode=1
#
#													else:
#														msg="<p>URL Firmada correctamente"
#														if total_size==0:
#															msg=msg+". Obteniendo longitud del archivo..."
#
#													if not "#Error" in msg:
#														try:
#															assert session
#
#														except:
#															print("Creating new download session")
#															session=aiohttp.ClientSession()
#
#
#													await bot.edit_message(thischat,msg_part_ev,msg_part_ct+msg_part_log+msg,parse_mode="html")
#
#												exitcode=await check_cancellation(exitcode)
#
#												if exitcode==0:
#
#													await asyncio.sleep(1)
#
#													activity=" mientras se obtenía la longitud"
#													ready=False
#
#													session_link[_sd_todus_token_last]=ttoken
#
#													uagent={"user-agent":"ToDus 0.39.4 HTTP-Download","authorization":ttoken}
#
#													if total_size==0:
#														#try:
#														#	await mid.reply("Obteniendo longitud del archivo...")
#
#														#except:
#														#	print("Message not edited.... Obtainig file length")
#
#														#print("Step 3: Get content-length")
#
#														try:
#															async with session.get(signed_url,headers=uagent) as response:
#																print("response.status =",response.status)
#																rs=response.status
#																if rs==404:
#																	raise NotFoundError()
#
#																assert rs==200
#																total_size=int(response.headers.get('content-length'))
#																assert total_size>0
#
#														#			else:
#														#				raise Exception("Respuesta no satisfactoria: "+str(response.status))
#														#	async with aiohttp.ClientSession(headers=uagent) as session:
#														#		async with session.get(signed_url) as response:
#														#			print("response.status =",response.status)
#														#			if response.status==404:
#														#				exitcode=2
#														#				raise NotFoundError()
#
#														#			elif response.status==200:
#														#				total_size=int(response.headers.get('content-length'))
#
#														#			else:
#														#				raise Exception("Respuesta no satisfactoria: "+str(response.status))
#
#														except NotFoundError:
#															exitcode=2
#															msg="<p>#Error "+activity+": "+_msg_error_404
#
#														except Exception as e:
#															exitcode=1
#															msg=_msg_error_this+str(e)
#
#														else:
#															ready=True
#
#													if ready:
#														msg="<p>Descargando..."
#														msg_part_log=msg_part_log+"<p>Longitud del archivo: "+hr_units(total_size)+"\n"
#
#													await bot.edit_message(thischat,msg_part_ev,msg_part_ct+msg_part_log+msg,parse_mode="html")
#
#													#else:
#													#	total_size=int(response.headers.get('content-length'))
#
#													#if exitcode>0:
#													#	await mid.reply("Error al obtener longitud del archivo\n<p><code>"+emsg+"</code>",parse_mode="html")
#
#												exitcode=await check_cancellation(exitcode)
#
#												if exitcode==0:
#
#													await asyncio.sleep(1)
#
#													# File already exists
#													if os.path.exists(job_path):
#														current_size=os.path.getsize(job_path)
#														if current_size<total_size:
#															wmode="ab"
#
#													else:
#														current_size=0
#														wmode="wb"
#
#													# Write down the missing bytes
#													if current_size<total_size:
#
#														if pmsg:
#															await bot.edit_message(thischat,pmsg,"Empezando a descargar...")
#
#														else:
#															pmsg=await msg_part_ev.reply("Empezando a descargar...")
#
#														the_id=pmsg.id
#
#														print("Step 4: write 'em bytes")
#
#														msg_error_skel="<p>#Error mientras se descargaba:"
#														uagent_new=uagent.copy()
#														if current_size>0:
#															range_header="bytes="+str(current_size)+"-"+str(total_size)
#															uagent_new.update({"Range":range_header})
#
#														jobman.job_update(the_id,[job_path,total_size])
#
#														loop=asyncio.get_event_loop()
#														loop.create_task(ntprog(thischat,current_directory,jobman,the_id))
#
#														print("uagent_new =",uagent_new)
#														try:
#															print("Writing...")
#															tout=aiohttp.ClientTimeout(sock_read=10)
#															#async with aiohttp.ClientSession(headers=uagent_new) as session:
#															#	async with session.get(signed_url,timeout=uagent) as response:
#															async with session.get(signed_url,headers=uagent_new,timeout=tout) as response:
#																httprs=str(response.status)
#																print("httprs =",httprs)
#
#																if httprs=="404":
#																	raise NotFoundError
#
#																async with aiofiles.open(job_path,wmode) as outfile:
#																	while True:
#																		exitcode=await check_cancellation(exitcode)
#																		if exitcode==0:
#																			chunk=await response.content.read(_kilobyte)
#																			if chunk:
#																				await outfile.write(chunk)
#																			else:
#																				break
#
#																		else:
#																			break
#
#																if exitcode==5:
#																	raise asyncio.CancelledError
#
#														except asyncio.CancelledError:
#															msg=msg_error_skel+"<code>Cancelado por usted</code>"
#
#														except NotFoundError:
#															exitcode=2
#															msg=msg_error_skel+"<code>"+_msg_error_404+"</code>"
#
#														except Exception as e:
#															exitcode=1
#															msg=_msg_error_this+"<code>"+str(e)+"</code>"
#
#														else:
#															print("COMPLETE")
#
#														if exitcode>0 and exitcode<5:
#															pass
#															# await mid.reply("Fallo al descargar\n<p><code>"+emsg+"</code>",parse_mode="html")
#
#														jobman.job_expire(the_id)
#
#														del uagent_new
#
#													if os.path.exists(job_path):
#														current_size=os.path.getsize(job_path)
#
#													if exitcode<5:
#														# Compare sizes
#														if current_size==total_size:
#															print("FILE COMPLETED!")
#															await mid.reply("#DescargaCompleta")
#
#														else:
#															if exitcode==0:
#																exitcode==1
#
#															await mid.reply("#DescargaIncompleta")
#
#												exitcode=await check_cancellation(exitcode)
#
#												# Exit code analysis
#
#												if exitcode==0:
#													print("Exit code 0: No errors")
#													tryagain=False
#
#												if exitcode==1:
#													print("Exit code 1: Some undefined error")
#
#												if exitcode==2:
#													print("Exit code 2: Skip this line, it gave 404")
#													tryagain=False
#													# await mid.reply("Este trabajo no se puede volver a hacer (404)")
#
#												if exitcode==3:
#													print("Exit code 3: Request a new token")
#
#												if exitcode==4:
#													print("Exit code 4: Token was useless")
#
#												if exitcode<5:
#
#													if exitcode>2:
#														await session.close()
#														del session
#														if not atds3_support:
#															print("Manual token was used, and it sucks ass")
#															tryagain=False
#															keepgoing=False
#
#														else:
#															print("Changing token...")
#
#													if exitcode>0:
#														await asyncio.sleep(1)
#
#												if exitcode==5:
#													print("Exit code 5: Cancelation request accepted")
#													tryagain=False
#													keepgoing=False
#													# await cmdlink.reply("Se ha cancelado el descargador de toDus")
#
#											# Loop for this particular URL + FileName line ends here
#
#										# Previous loop continues here
#
#										lines.pop(0)
#										if len(lines)==0 or halt:
#											keepgoing=False
#
#									# TXT file loop ends here
#
#									await event.reply("#Final del descargador de toDus")
#
#								else:
#									wutt=True
#									msg=msg_error+"Fallo al leer el... \"TXT\"\n"+msgerr
#
#							transfer_jobs=session_link[_sd_netwquota]
#							if transfer_jobs>0:
#								session_link[_sd_netwquota]=transfer_jobs-1
#
#							session_link[_sd_todus_dl]=_job_ready
#
#						else:
#							wutt=True
#							msg=msg_error+_msg_error_tquota
#
#					if wutt:
#						await event.reply(msg)

#				# Grab toDus token from a replied message
#				if "/tt" in command:
#					msg_error="Error de lectura:\n"
#					if replied.document or replied.video or replied.photo:
#						msg=msg_error+"Solo se aceptan mensajes con texto"
#
#					else:
#						if len(replied.message)>0:
#							msg="Se ha guardado el mensaje como token de toDus"
#							session_link[_sd_todus_token]=replied.message
#
#						else:
#							msg=msg_error+"El mensaje está vacío..."
#
#					await event.reply(msg)

			# Commands that work only as normal messages

			if not event.is_reply:

				if "/bash" in command:
					if len(args)==1:
						output,errors=await shell_run(args[0])

						if len(output)>4000:
							async with aiofiles.open(_bash_out,"w") as out:
								await out.write(output)

							await bot.send_file(thischat,file=_bash_out)

						else:
							if len(output)>0:
								await event.reply("<code>"+output+"</code>",parse_mode="html")

						if len(errors)>4000:
							async with aiofiles.open(_bash_err,"w") as err:
								await err.write(errors)

							await bot.send_file(thischat,file=_bash_err)

						else:
							if len(errors)>0:
								await event.reply("<code>"+errors+"</code>",parse_mode="html")

					else:
						await event.reply("...")

				# Peek at qjobs
				if "/peek" in command:
					if len(args)==1:
						qjob=args[0]
						if qjob=="cpu" or qjob=="req" or qjob=="sub":
							print("qjob =",qjob)

						else:
							wutt=True

					else:
						wutt=True

					if not wutt:
						if qjob=="cpu":
							que=_gq_cpu

						if qjob=="req":
							que=_gq_req

						if qjob=="sub":
							que=_gq_sub

						msg=qjob+"\n"
						if len(que)==0:
							msg=msg+"EMPTY"

						else:
							for v in que:
								msg=msg+"\n"+str(v)

					if wutt:
						msg="pfffff"

					await event.reply(msg)

				# Clear stuff
				if "/fix" in command:
					if len(args)==0:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						thy_arg=args[0]
						try:
							user_int=int(thy_arg)
						except:
							ctype=None

						else:
							ctype="udata"

						if ctype=="udata":
							target_session=_sessions.get(str(user_int))
							if not target_session:
								wutt=True
								msg="no such session"

						else:
							if thy_arg=="cpu" or thy_arg=="req" or thy_arg=="sub":
								ctype=thy_arg

							else:
								wutt=True

						print("ctype =",ctype)

					if not wutt:
						qid=None
						reset=False
						if len(args)>1:
							if ctype=="udata":
								qid=args[1]

							else:
								wutt=True

							if qid and len(args)==3:
								reset=True

					if not wutt:

						msg=""
						if len(args)==2 and (not ctype=="udata"):
							print("NUKING",ctype)

						try:
							if ctype=="udata":
								if not qid:
									target_session[_sd_hview]=False
									target_session[_sd_hproc]=""

								if qid:
									if not qid in target_session[_sd_que]:
										raise Exception("user does not have that queue")

									else:
										que=target_session[_sd_que][qid]
										q=target_session[_sd_netwquota]
										if reset:
											que.reset()
											msg="\n[!]Queue reset\n"
											if q>0:
												q=q-1
												target_session[_sd_netwquota]=q

										msg=msg+"\nname: "+str(que.name)+"\nattrib: "+str(que.attrib)+"\n\ncontents:\n"+str(que.queue)

							if ctype=="cpu":
								if len(args)==2:
									print("Nuking CPU")
									msg="\nCleared CPU queue"
									_gq_cpu.clear()

								else:
									msg="\nPopped "+str(_gq_cpu[0])
									_gq_cpu.pop(0)

							if ctype=="sub":

								if len(args)==2:
									print("Nuking SUB")
									msg="\nCleared SUB queue"
									_gq_sub.clear()

								else:
									msg="\nPopped "+str(_gq_req[0])
									_gq_sub.pop(0)

							if ctype=="req":

								if len(args)==2:
									print("Nuking REQ")
									msg="\nCleared REQ queue"
									_gq_req.clear()

								else:
									msg="\nPopped "+str(_gq_req[0])
									_gq_req.pop(0)

						except Exception as e:
							wutt=True
							msg="damn..."+str(e)

					if wutt:
						msg="FUCK\n"+msg

					else:
						msg="OK"+msg

					if len(msg)<4000:
						await event.reply(msg)

					else:
						await event.reply("tldr bitch")

				# Developer mode
				if "/devmode" in command:
					if _devmode:
						_devmode=False
						await event.reply("Modo desarrollador desactivado")

					else:
						_devmode=True
						await event.reply("Modo desarrollador activado")

				# NOTES
				if "/notes" in command:
					await event.reply("https://www.mediafire.com/file/ss7ff3bu9icbbjw/Carbon_%2526_Silicon_1_por_Floyd_Wayne_y_Arsenio_Lup%25C3%25ADn.cbr/file\nhttps://www43.zippyshare.com/v/T0ybv7Xm/file.html")

				# AIO Runner
				if "/runner" in command:
					pass
					# executor runner

				# INFORMATION COMMANDS

				# Some info
				if "/about" in command:
					await event.reply("<p><strong>Acerca del bot</strong>\n<p>Bot programado y administrado por <a href=https://t.me/CarlosAGH>カルロサグ</a>\n<p>Sitio web del bot: "+_ev_website_url+"\n<p>\n<p>Si tiene dudas respecto a cómo usar el bot, lea primero la guía completa luego consulte la ayuda para buscar los comandos que necesita.",parse_mode="html")

#				# NOT IMPLEMENTED YET: androeed.ru downloader
#				if _c_androeed in command:
#					url=args[0]
#					coded=url.split("get_file?url=")[1]
#					decoded_a=base64_decode(coded)
#					url_real=str(base64.b64decode(t))[2:]

				# Get command reference
				if "/help" in command:
					await event.reply("Guía completa\nhttps://carlosagh96.github.io/boc/mfshell_g.html\n\nComandos\nhttps://carlosagh96.github.io/boc/mfshell_h.html")
					return

				# Get session data
				if "/start" in command:
					if session_link[_sd_autodl]:
						auto_download="Activada"

					else:
						auto_download="Desactivada"

					if len(session_link[_sd_shared])>0:
						shared_name=session_link[_sd_shared_name]
						shared_info="<a href='"+session_link[_sd_shared]+"'>"+shared_name+"</a>"

					else:
						shared_info="Ninguno"

					cwd=session_link[_sd_cwd]

					await event.reply("<p><strong>Datos de la sesión</strong>\n<p>\n<p>🤔 Ubicación actual:\n<p>\n<p><code>"+get_path_show(cwd)+"</code>\n<p>\n<p>🔃 Transferencias de red simultáneas: "+str(session_link[_sd_netwquota])+" de "+str(_sntl)+"\n<p>📝 Descargas encoladas (Ejecute /que)\n<p>📦 Proceso pesado: "+session_link[_sd_hproc]+"\n<p>⏬ Descarga automática: "+auto_download+"\n<p>🌐 Enlace para compartir: "+shared_info,parse_mode="html")

				# ???

				# Switch automatic downloads on/off
				if "/auto" in command:
					adswitch=session_link[_sd_autodl]
					if adswitch:
						adswitch=False
						msg="Descargas automáticas de Telegram al bot desactivadas\nEjecute /download para descargar manualmente"

					else:
						adswitch=True
						msg="Descargas automáticas de Telegram al bot activadas\nReenvíe archivos y álbumes a este chat para descargarlos automáticamente. Puede seguir usando /download para descargar manualmente si así lo desea."

					session_link[_sd_autodl]=adswitch
					
					await event.reply(msg)

				# Share session publically
				if "/share" in command:
					if session_link[_sd_shared].startswith(_ev_website_url):
						sharing=True

					else:
						sharing=False

					uid_mask=session_link[_sd_shared_name]
					if uid_mask=="":
						basename=random.choice(list(_uid_masks.keys()))
						print("basename =",basename)
						num=_uid_masks.get(basename)
						uid_mask=basename+"-"+str(num)
						session_link[_sd_shared_name]=uid_mask
						_uid_masks.update({basename:num+1})

					# share_dir=path_gitgud(_fse_root_path+"/"+uid_mask)
					share_dir=Path(_fse_root_path).joinpath(uid_mask)

					if not sharing:
						origin=Path(the_user_id).resolve()
						print("origin =",origin)
						link=share_dir.resolve()
						print("link =",link)
						link.symlink_to(origin)
						share_link_base=_ev_website_url+"/fse/"+uid_mask
						session_link[_sd_shared]=share_link_base
						await event.reply("Ha decidido compartir su sesión de forma pública\nTodos sus archivos serán accesibles desde el sitio web del bot\nEste es el enlace a sus archivos:\n\n"+share_link_base)

					else:
						share_dir.unlink()
						session_link[_sd_shared]=""
						await event.reply("Su sesión ha vuelto a ser privada")

				# FILE SYSTEM VISIBILITY, NAVIGATION AND MANIPULATION COMMANDS

				if ("/back" in command) or ("/cd" in command) or ("/ls" in command):

					viewing=session_link[_sd_hview]
					if viewing:
						return

					try:
						ranged=False

						if "/ls" in command:
							listonly=True

							if len(args)==1:
								try:
									index=int(args[0])

								except:
									ranged=True

								if ranged:
									jump=True
									range_args=get_args_range(args[0])
									if not range_args:
										wutt=True
										msg=_msg_error_iarg

							elif len(args)==0:
								index="f"

							else:
								wutt=True
								msg=_msg_error_wargs

						else:
							listonly=False

							if "/cd" in command:

								if len(args)==1:
									try:
										index=int(args[0])

									except:
										msg=_msg_error_iarg

								else:
									wutt=True
									msg=_msg_error_wargs

							else:
								index=-1

						if not wutt:
							cwd=session_link[_sd_cwd]

							if not ranged:
								if index=="f":
									cwd_new=cwd

								else:
									cwd_new=await aio_get_fsepath(cwd,index,1)
									if not cwd_new:
										wutt=True
										msg=_msg_error_notfound

								if not cwd_new:
									if index=="f":
										wutt=True
										if index<0:
											msg="No hay niveles superiores"

										else:
											msg="No se encuentró el elemento"

						if not wutt:

							if not listonly:
								headline="Ha cambiado de ubicación"

							else:
								headline=""

							# Display current directory

							session_link[_sd_hview]=True

							try:
								if ranged:
									await aio_display_ls(thischat,event,cwd,cwd,the_title=headline,crange=range_args)

								else:
									print("non-ranged")
									await aio_display_ls(thischat,event,cwd,cwd_new,the_title=headline)

							except Exception as e:
								print(the_user_id,"had an error while looking at the dir:",e)
								wutt=True
								msg=str(e)

							else:
								if not listonly:
									session_link[_sd_cwd]=cwd_new

							session_link[_sd_hview]=False

						if wutt:
							await event.reply("<p>#Error\n<p><code>"+msg+"</code>",parse_mode="html")

					except:
						pass

					session_link[_sd_hview]=False

				# Create directory
				if "/mkdir" in command:
					if len(args)==1:
						dname=args[0]

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						ok=check_correct_fse_name(dname)
						if not ok:
							wutt=True
							msg=_msg_error_iarg

					if not wutt:
						cwd=session_link[_sd_cwd]
						newdir=cwd.joinpath(dname)
						if newdir.exists():
							wutt=True
							msg=_msg_error_exists

					if not wutt:
						newdir.mkdir()

					if wutt:
						msg="<p>#mkdir #error\n<p>"+msg

					else:
						msg="<p>#mkdir #ok\n<p>Se creó el directorio\n<p><code>"+get_path_show(newdir)+"</code>"

					await event.reply(msg,parse_mode="html")

				# Move or rename file/directory
				if "/mv" in command:

					moving=session_link[_sd_exec_mv]
					if moving:
						return

					else:
						session_link[_sd_exec_mv]=True

					stype=_stype_s

					# First arg
					if len(args)==2:

						try:
							origin=int(args[0])
							assert (origin>-1)

						except:
							stype=_stype_r

						if _stype_r in stype:
							range_args=get_args_range(args[0])
							if not range_args:
								stype=_stype_f

						if _stype_f in stype:
							free_args=get_args_free(args[0])
							if not free_args:
								wutt=True
								msg=_msg_error_iarg

					else:
						wutt=True
						msg=_msg_error_wargs

					# Second arg
					if not wutt:

						justrename=False

						if _stype_s in stype:
							try:
								dest_index=int(args[1])

							except:
								justrename=True

							if justrename:
								newname=args[1]
								if not check_correct_fse_name(newname):
									wutt=True
									msg=_msg_error_iarg

						else:
							try:
								dest_index=int(args[1])

							except:
								wutt=True
								msg=_msg_error_iarg

					# Execution

					if not wutt:

						cwd=session_link[_sd_cwd]

						if justrename:

							opath=await aio_get_fsepath(cwd,origin)
							if not opath:
								wutt=True
								msg=_msg_error_notfound

							if not wutt:
								newpath=cwd.joinpath(newname)
								if newpath.exists():
									wutt=True
									msg=_msg_error_exists

							if not wutt:
								try:
									opath.rename(newpath)

								except Exception as e:
									wutt=True
									msg="Mientras se renombraba el recurso: <code>"+str(e)+"</code>"

								else:
									msg="<p>#mv #ok\n<p>Renombrado correctamente\n<p><code>"+get_path_show(opath)+"\n<p>"+get_path_show(newpath)+"</code>"

							if not wutt:
								await event.reply(msg,parse_mode="html")

						else:

							destdir=await aio_get_fsepath(cwd,dest_index,fsetype=1)
							if not destdir:
								wutt=True
								msg=_msg_error_nondir

							if not wutt:
								thepaths=[]
								if _stype_s in stype:
									origpath=await aio_get_fsepath(cwd,origin)
									if not origpath:
										wutt=True
										msg=_msg_error_notfound

									if not wutt:
										thepaths.append(origpath)

								if _stype_r in stype:
									thepaths=await aio_get_dircont_ranged(cwd,range_args)

								if _stype_f in stype:
									thepaths=await aio_get_dircont_free(cwd,free_args)

								if len(thepaths)==0:
									wutt=True
									msg="No hay nada que mover"

							if not wutt:
								fail_list=[]
								for fse in thepaths:
									namae=fse.name
									newpath=destdir.joinpath(namae)
									if newpath.exists():
										fail_list=fail_list+[get_path_show(fse)]

									else:
										try:
											fse.rename(newpath)

										except:
											fail_list=fail_list+[get_path_show(fse)]

								if len(fail_list)>0:
									msg="<p>#mv #errores\n<p>Hubo errores al mover\n<p><code>"
									msg_lst=[]
									count=1
									for e in fail_list:
										msg_add="\n<p>"+e
										if count==len(fail_list):
											msg_add=msg_add+"</code>"

										if len(msg+msg_add)<4000:
											msg=msg+msg_add

										else:
											msg_lst=msg_lst+[msg]
											msg=msg_add

										count=count+1

									chain=None
									for m in msg_lst:
										if not chain:
											rpl=event

										else:
											rpl=chain

										try:
											tryed=await rpl.reply(m,parse_mode="html")
											await asyncio.sleep(0.1)

										except Exception as e:
											print(the_user_id,"just had a problem while displaying THE /mv error message chained list:",str(e))

										else:
											chain=tryed

								else:
									await event.reply("#mv #ok\nSe movieron sin problemas los elementos seleccionados")

					if wutt:
						await event.reply("<p>#Error\n<p>"+msg,parse_mode="html")

					session_link[_sd_exec_mv]=False

				# Batch Renamer
				if "/bren" in command:
					initiate=False
					cwd=session_link[_sd_cwd]
					msg_head="<p>#bren"

					# Simple, Ranged, Free

					v=session_link[_sd_hview]
					if v:
						return

					else:
						session_link[_sd_hview]=True

					if len(args)==3:
						try:
							index=int(args[0])
							assert index>-1

						except:
							stype="RANGE"

						else:
							stype="SIMPLE"

						if stype=="RANGE":
							print("try if ranged")
							range_args=get_args_range(args[0])
							if not range_args:
								stype="FREE"

						if stype=="FREE":
							print("try if free.........")
							free_args=get_args_free(args[0])
							if not free_args:
								stype=None

						if not stype:
							wutt=True
							msg=_msg_error_iarg

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						job_raw=args[1].strip()
						if "R"==job_raw.capitalize() or "E"==job_raw.capitalize() or "A"==job_raw.capitalize():
							job_type=job_raw.capitalize()

						else:
							wutt=True
							msg=_msg_error_iarg

					if not wutt:
						subargs=args[2]
						try:
							if not "A"==job_raw.capitalize():
								if subargs.startswith("/"):
									raise Exception("LOL")

							if "/" in subargs:
								subargs_lst=subargs.split("/")

						except:
							wutt=True
							msg=_msg_error_iarg

					if not wutt:

						# 'R'(Remplazar). "TextoV/TextoN"
						# 'E'(Enumerar). "TextoNuevo/N/C"
						# 'A'(Agregar).Vía 1: "Prefijo/" ;Vía 2: "/Sufijo"

						print("subargs_lst =",subargs_lst)

						if "A" in job_type:
							# Add
							try:
								assert len(subargs_lst)==2
								assert subargs.startswith("/") or subargs.endswith("/")
								if subargs.startswith("/"):
									addstr=subargs_lst[1]
								if subargs.endswith("/"):
									addstr=subargs_lst[0]

							except:
								wutt=True
								msg=_msg_error_iarg

						if "R" in job_type:
							# Replace
							try:
								str_tgt=subargs_lst[0]
								if str_tgt.startswith("/"):
									raise Exception("LOL")

								str_new=subargs_lst[1]

							except:
								wutt=True
								msg=_msg_error_iarg

						if "E" in job_type:
							#Enumerate
							try:
								assert len(subargs_lst)<4
								newtext=subargs_lst[0]
								if newtext.startswith("/"):
									raise Exception("LOL")

								start_raw=subargs_lst[1]
								start=int(start_raw)

							except:
								wutt=True
								msg=_msg_error_iarg

							if not wutt:

								if len(subargs_lst)>2:
									figures_raw=subargs_lst[2].strip()
								else:
									figures_raw=""

								#if len(subargs_lst)==4:
								#	suffix=subargs.split("/")[3]
								#else:
								#	suffix=None

								try:
									if len(figures_raw)>0:
										figures=int(figures_raw)
										assert figures>0
									else:
										figures=len(str(len(fse_list)))

								except:
									wutt=True
									msg=_msg_error_iarg

					if not wutt:
						if stype=="RANGE":
							fse_list_raw=await aio_get_dircont_ranged(cwd,range_args)
							if len(fse_list_raw)==0:
								wutt=True
								msg=_msg_error_empty

							if not wutt:
								fse_list=[]
								for fse in fse_list_raw:
									if fse.is_file():
										fse_list=fse_list+[fse]

								if len(fse_list)<2:
									wutt=True
									if len(fse_list)==0:
										msg=_msg_error_empty
									else:
										msg=_msg_error_few

						if stype=="SIMPLE":
							selected_fse=await aio_get_fsepath(cwd,index)

							if selected_fse.is_dir():
								fse_list=await aio_get_dircont(selected_fse,fsetype=0)

								if len(fse_list)<2:
									wutt=True
									if len(fse_list)==0:
										msg=_msg_error_empty
									else:
										msg=_msg_error_few

							elif selected_fse.is_file():
								wutt=True
								msg=_msg_error_few

							else:
								wutt=True
								msg=_msg_error_unknown

						if stype=="FREE":
							fse_list=[]
							fse_list_raw=await aio_get_dircont_free(cwd,free_args)
							if len(fse_list_raw)>0:
								for fse in fse_list_raw:
									if fse.is_file():
										fse_list.append(fse)

							#for index in free_args:
							#	fse=await aio_get_fsepath(cwd,index,0)
							#	if fse:
							#		fse_list.append(fse)

							if len(fse_list)<2:
								wutt=True
								if len(fse_list)==0:
									msg=_msg_error_empty
								else:
									msg=_msg_error_few

					if not wutt:

						print("fse_list =",fse_list)

						print("detected names\nJob type:",job_type)
						ticket=str(time.strftime("%Y-%m-%d-%H-%M-%S"))

						if confirmed:
							sim=False
						else:
							sim=True
							session_link[_sd_saved]=raw_shit

						job_e="newtext+paddednumb(figures,count,dlen_as_figs=True)+fse_tmp.suffix"
						job_r="oname.replace(str_tgt,str_new,1)"
						job_ap="addstr+oname"
						job_as="oname+addstr"

						index=0

						if sim:
							msg_title="¿Es correcto?"
						else:
							msg_title="Ha confirmado"

						if "A" in job_type:
							if subargs.startswith("/"):
								job_a=job_as

							if subargs.endswith("/"):
								job_a=job_ap

						if "E" in job_type:
							count=start

						msg_total=msg_head+"\n<p>"+msg_title+"\n<p>"
						msg_chunks=[]

						print("LISTING FSEs")
						for fse in fse_list:
							print("\n",fse)
							oname=fse.name
							fse_tmp=fse
							if "E" in job_type:
								nn=eval(job_e)
								count=count+1

							if "R" in job_type:
								nn=eval(job_r)

							if "A" in job_type:
								nn=eval(job_a)

							msg_buff="\n<p>Original:\n<p><code>"+oname+"</code>\n<p>Nuevo:\n<p><code>"+nn+"</code>\n<p>"

							index=index+1
							msg_add=None
							if index==len(fse_list):
								if sim:
									msg_end="\n<p>Confirmar /ok"
								else:
									msg_end="\n<p>Ver /ls"

								msg_add=msg_total+msg_buff+msg_end

							else:
								if len(msg_total+msg_buff)>4000:
									msg_add=msg_total
									msg_total="<p>..."+msg_buff

								else:
									msg_total=msg_total+msg_buff

							if msg_add:
								msg_chunks.append(msg_add)

						if not sim:

							await asyncio.sleep(0.1)

							try:
								count=1
								fse_dict={}
								for fse in fse_list:
									tmpname=ticket+paddednumb(len(fse_list),count)+fse.suffix
									fse_tmp=cwd.joinpath(tmpname)
									fse.rename(fse_tmp)
									fse_dict.update({fse.name:fse_tmp})
									count=count+1

							except Exception as e:
								wutt=True
								msg="stp1:"+str(e)
							else:
								await asyncio.sleep(0.1)

							if not wutt:
								if "E" in job_type:
									count=start

								try:
									for fse in fse_dict:
										fse_tmp=fse_dict[fse]
										if "A" in job_type:
											oname=fse
											newname=eval(job_a)

										if "R" in job_type:
											oname=fse
											newname=eval(job_r)

										if "E" in job_type:
											newname=eval(job_e)
											count=count+1

										newpath=cwd.joinpath(newname)
										if not newpath.exists():
											fse_tmp.rename(newpath)

										else:
											fse_tmp.rename(fse)

								except Exception as e:
									msg="stp2:"+str(e)

						chain=None
						if not wutt:
							for m in msg_chunks:
								if not chain:
									replyme=event

								else:
									replyme=chain

								try:
									c=await replyme.reply(m,parse_mode="html")
									await asyncio.sleep(0.1)

								except Exception as e:
									print(the_user_id,"/bren msg_chunks[] error:",e)

								else:
									chain=c

					if wutt:
						await event.reply(msg_head+" #error\n<p><code>"+msg+"</code",parse_mode="html")

					session_link[_sd_hview]=False

				# Delete file or a directory. It does not ask for confirmation, be careful
				if "/rm" in command:
					if len(args)==1:
						print(the_user_id,"executes",command)

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						stype=_stype_s
						try:
							index=int(args[0])
						except:
							stype=_stype_r

						if _stype_r in stype:
							range_args=get_args_range(args[0])
							if not range_args:
								stype=_stype_f

						if _stype_f in stype:
							free_args=get_args_free(args[0])
							if not free_args:
								wutt=True
								msg=_msg_error_iarg

					if not wutt:
						cwd=session_link[_sd_cwd]
						if _stype_s in stype:
							deathlist=[]
							deathrow=await aio_get_fsepath(cwd,index)
							if deathrow:
								deathlist.append(deathrow)

						if _stype_r in stype:
							deathlist=await aio_get_dircont_ranged(cwd,range_args)

						if _stype_f in stype:
							deathlist=await aio_get_dircont_free(cwd,free_args)

						if len(deathlist)==0:
							wutt=True
							msg="No hay nada que borrar"

					if not wutt:
						shit_happened=False
						for tgt in deathlist:
							if tgt.is_file():
								try:
									tgt.unlink()
								except Exception as e:
									print(the_user_id,"/rm err del file:",str(tgt),"→",str(e))
									if not shit_happened:
										shit_happened=True

							if tgt.is_dir():
								lst=list(tgt.rglob("*"))
								if len(lst)>0:
									lst.reverse()
									for fse in lst:
										try:
											if fse.is_file():
												fse.unlink()

											if fse.is_dir():
												fse.rmdir()

										except Exception as e:
											print(the_user_id,"/rm del fse:",str(tgt),"→",str(e))
											if not shit_happened:
												shit_happened=True

									del lst

								try:
									tgt.rmdir()

								except Exception as e:
									print(the_user_id,"/rm del empty:",str(tgt),"→",str(e))
									if not shit_happened:
										shit_happened=True

					if wutt:
						msg="<p>#rm #error\n<p>"+msg

					else:
						if shit_happened:
							msg="<p>#rm #errores\n<p>Hubo errores al borrar"
						else:
							msg="<p>#rm #ok\n<p>Elemento(s) borrado(s) correctamente"

					await event.reply(msg,parse_mode="html")

				# NETWORK TRANSFERS

				# Google Drive
				if "/gddl" in command:

					initiate=False
					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					try:
						if len(args)==1:
							url_list_raw=args[0]

						else:
							wutt=True
							msg=_msg_error_wargs

						if not wutt:
							url_list=url_list_raw.split(" ")

							if len(url_list)==0:
								wutt=True
								msg="No se encontraron URLs"

						if not wutt:
							recursive=False
							if len(url_list)>1:
								le_val=url_list[-1]
								le_idx=len(url_list)-1
								if le_val=="r" or le_val=="R":
									recursive=True
									url_list.pop(le_idx)

								elif le_val.startswith("https://") or le_val.startswith("http://"):
									recursive=False

								else:
									wutt=True
									msg=_msg_error_iarg

						if not wutt:
							que=session_link[_sd_que]["g"]
							cwd=session_link[_sd_cwd]

							if que.get_size()==0:
								initiate=True

							added_at_least_one=False
							print("\n",the_user_id,"url_list:")

							chain=None

							msg_total="<p>#gddl\n<p>URLs detectadas:\n"
							msg_chunks=[]

							index=0
							for iurl in url_list:
								iurl=iurl.strip()
								print("\t",the_user_id,"iurl =",iurl)

								if iurl.startswith("https://") or iurl.startswith("http://"):
									if iurl.startswith("http://"):
										iurl.replace("http://","https://")

									yurl=yarl.URL(iurl)
									yurl_host=yurl.host

								else:
									wutt=True

								if not wutt:
									if ("drive.google.com" in yurl_host) or ("docs.google.com" in yurl_host):
										print(the_user_id,"/gddl allows",iurl)

									else:
										wutt=True

								if not wutt:
									ok=False

									if ("docs.google.com" in yurl_host):
										if yurl.path.startswith("/uc") and yurl.query.get("id"):
											ok=True

									if ("drive.google.com" in yurl_host):
										if yurl.path.startswith("/file/d") and len(yurl.parts)>2:
											if yurl.parts[2]=="d":
												iurl="https://drive.google.com/uc?id="+yurl.parts[3]+"&export=download"
												ok=True

										elif yurl.path=="/folderview":
											data_id=yurl.query.get("id")
											if data_id:
												iurl="https://drive.google.com/drive/folders/"+data_id
												ok=True

										elif yurl.path.startswith("/drive/mobile/folders/"):
											iurl="https://drive.google.com/drive/folders/"+yurl.parts[3]
											ok=True

										elif yurl.path.startswith("/drive/folders/"):
											if yurl.parts[2]=="folders":
												ok=True

										elif yurl.path=="/u/0/uc" and yurl.query.get("id"):
											iurl="https://drive.google.com/uc?id="+yurl.query.get("id")+"&export=download"
											ok=True

										elif yurl.path=="/uc" and yurl.query.get("id"):
											if yurl.query.get("amp;export")=="download" and yurl.query.get("amp;confirm")=="t":
												ok=True

											elif yurl.query.get("export")=="download":
												ok=True

											else:
												iurl="https://drive.google.com/uc?id="+yurl.query.get("id")+"&export=download"
												ok=True

										else:
											wutt=True

									if not ok:
										wutt=True

								val=[iurl,cwd]
								if recursive and iurl.startswith("https://drive.google.com/drive/folders"):
									val=val+["Recursivo"]

								print("val =",val)

								if not wutt:
									vexists=que.check_value_spc(val)

									if vexists:
										wutt=True

								if not wutt:
									que.add_value(val)
									prefix="<code>[OK]</code> "
									if not added_at_least_one:
										added_at_least_one=True

								if wutt:
									prefix="<code>[--]</code> "

								msg_tmp=que.show_value(val,prefix)

								index=index+1

								emit=None

								if index==len(url_list):
									emit=msg_total+msg_tmp

								else:
									if len(msg+msg_tmp)>4000:
										emit=msg_total
										msg_total="\n<p>..."+msg_tmp

									else:
										msg_total=msg_total+msg_tmp

								if emit:
									msg_chunks.append(emit)

								wutt=False
								if index==len(url_list):
									break

							for m in msg_chunks:
								if not chain:
									replyme=event

								else:
									replyme=chain

								try:
									c=await replyme.reply(m,parse_mode="html")
									await asyncio.sleep(0.1)

								except Exception as e:
									print(the_user_id,"/gddl urls list error(1):",e)

								else:
									chain=c

							if initiate:
								if not added_at_least_one:
									initiate=False

					except:
						pass

					session_link[_sd_hview]=False

					if not wutt:
						if not initiate:
							return

					if not wutt:
						transfer_jobs=session_link[_sd_netwquota]
						if transfer_jobs==_sntl:
							wutt=True
							msg=_msg_error_tquota

					if wutt:
						await event.reply("<p>#gddl #error\n<p><code>"+msg+"</code>",parse_mode="html")

					else:
						session_link[_sd_netwquota]=transfer_jobs+1
						uagent=random.choice(_ua_utd)
						uahead={"User-Agent":uagent}
						session=aiohttp.ClientSession(headers=uahead,timeout=_tout)
						replyto=chain
						iterate=True
						que.attrib["working"]=True

						# ENTER GDDL LOOP
						while iterate:
							# GDDL LOOP START

							wutt=False
							que.attrib["cancel"]=False
							cvalue=que.get_value()

							base_url=cvalue[0]
							outdir=cvalue[1]

							if len(cvalue)==3:
								recursive=True
							else:
								recursive=False

							msg_head="<p>#gddl"
							msg_body="\n<p>"+que.show_value(cvalue)+"\n<p>"
							msg_extra=""

							yurl=yarl.URL(base_url)

							msg_recursive=""

							if yurl.path=="/uc":
								filelink=True
								msg_type="Enlace a archivo"

							else:
								filelink=False
								msg_type="Enlace a carpeta"
								msg_recursive="\n<p>¿Recursivo? "
								if recursive:
									msg_recursive=msg_recursive+"Si"
								else:
									msg_recursive=msg_recursive+"No"

							msg_body=msg_body+"\n<p>Tipo: "+msg_type+msg_recursive

							wait=True
							while wait:
								try:
									cmev=await replyto.reply(msg_head+msg_body+"\n<p>Iniciando...",parse_mode="html")
								except:
									await asyncio.sleep(0.5)
								else:
									wait=False

							if filelink:

								await queue_brake_checker(que,cmev)

								# Download as regular file

								stay=True
								retry=False
								trying=False

								try:
									while stay:

										if retry:
											retry=False

										async with session.get(base_url) as response:
											status=response.status
											hascd=response.headers.get("content-disposition")
											cookies=response.cookies
											if hascd:
												print("Plan A")
												filename=response.content_disposition.filename
												total_size_raw=str(response.headers.get("content-length"))
												if not total_size_raw:
													raise Exception("No se obtuvo la longitud")

												total_size=int(total_size_raw)
												if total_size and filename:
													stay=False

											else:
												print("PLAN B")
												html_dump=await response.text()
												if "Google Drive - Quota exceeded" in html_dump:
													raise Exception("Cuota del archivo excedida")

												soup=BeautifulSoup(html_dump,"lxml")
												print("\nsoup =",soup)
												tag_a=soup.find("a",id="uc-download-link")

												if tag_a:
													tag_form=None

												else:
													tag_form=soup.find("form",id="downloadForm")

												if tag_a or tag_form:
													link=True

												else:
													link=False

												if link:
													if tag_a:
														url="https://drive.google.com"+tag_a.get("href")

													if tag_form:
														url=tag_form.get("action")
														stay=False

												else:
													# Try downloading without the export=download thing
													if str(status).startswith("4"):
														if not trying:
															yurl=yarl.URL(base_url)
															if base_url.endswith("&export=download") and yurl.path.startswith("/uc"):
																file_id=yurl.query.get("id")
																base_url="https://drive.google.com/uc?id="+file_id
																retry=True
																trying=True
																print("NEW Base URL =",base_url)

															del yurl

														else:
															trying=False

													if not trying:
														raise Exception("No se encuentra")

												if not retry:
													stay=False

								except Exception as e:
									wutt=True
									msg_head=msg_head+" #error"
									msg_extra="\n<p>Mientras se obtenía el tamaño y el nombre:\n<p><code>"+str(e)+"</code>"

								else:
									if hascd:
										url=base_url
										msg_body=msg_body+"\n<p>Nombre: <code>"+filename+"</code>\n<p>Tamaño: "+hr_units(total_size)

									msg_extra="\n<p>Descargando..."

								if not wutt:
									if hascd:
										filepath=outdir.joinpath(filename)
										if filepath.exists():
											wutt=True
											msg_head=msg_head+" #error"
											msg_extra="\n<p><code>"+_msg_error_exists+"</code>"

									else:
										filepath=None
										total_size=0

								if not wutt:
									loop=asyncio.get_event_loop()

									if hascd:
										data_link=None
										if total_size>_megabyte:
											pm=True
										else:
											pm=False

									else:
										pm=True

									if pm:
										progress_data={"msg":"","exc":None}
										if not hascd:
											progress_data.update({"conf":False,"outdir":outdir,"fpath":filepath,"tsize":total_size})
											data_link=progress_data

										if hascd:
											progress=loop.create_task(ntprog(thischat,cmev,filepath,total_size,msg_head+msg_body,backup=progress_data))
										else:
											progress=loop.create_task(ntprog(thischat,cmev,filepath,total_size,msg_head+msg_body,filedata=data_link))

									getdown=loop.create_task(webdownloader(session,url,filepath,cookies,data_link))

									msg=await task_admin(getdown,que)

									if pm:
										await asyncio.sleep(0.5)
										if not progress.done():
											print(the_user_id,command,"cancelling progress meter...")
											progress.cancel()
											while True:
												await asyncio.sleep(0.5)
												print(the_user_id,command,"waiting for progress meter to end...")
												if progress.done():
													break

									msg_extra="\n<p><code>"+msg+"</code>"
									if pm:
										msg_extra=progress_data["msg"]+msg_extra

									del cookies

								await asyncio.sleep(0.5)

								wait=True
								while wait:
									try:
										await bot.edit_message(thischat,cmev,msg_head+msg_body+msg_extra,parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

							else:

								# Populate the queue with the new links

								try:
									async with session.get(base_url) as response:
										html_dump=await response.text()

								except Exception as e:
									wutt=True
									msg=str(e)
									msg_head=msg_head+" #error"
									msg_extra="\n<p>Mientras se descargaba la página:\n<p><code>"+msg+"</code>"

								else:
									msg_extra="\n<p>Recogiendo información..."

								wait=True
								while wait:
									try:
										await bot.edit_message(thischat,cmev,msg_head+msg_body+msg_extra,parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

								if not wutt:

									parent_id=yurl.name

									soup=BeautifulSoup(html_dump,"lxml")
									try:
										folder_stuff=soup.find("div",attrs={"class":"g3Fmkb"}).find("div",attrs={"guidedhelpid":"main_container"}).find_all("c-wiz",attrs={"class":"pmHCK"})
										if len(folder_stuff)==0:
											raise Exception("¿Carpeta vacía?")

									except Exception as e:
										wutt=True
										msg=str(e)
										msg_head=msg_head+" #error"
										msg_extra="\n<p>Mientras se recogía información:\n<p><code>"+msg+"</code>"

								if wutt:
									wait=True
									while wait:
										try:
											await bot.edit_message(thischat,cmev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											wait=False

								if not wutt:
									index=0
									msg_chunks=[]
									msg_total=msg_head+"\n<p>URLs detectadas:"
									msg_buffer=""
									added=False
									chain=None

									for thing in folder_stuff:

										data_id=None
										data_target=None
										label_grid_cell=None

										try:
											thing_divs=thing.find_all("div")
											name=thing.find("div",attrs={"class":"Q5txwe"}).text

										except Exception as e:
											print(the_user_id,"fucked up:",e)

										else:
											for div in thing_divs:

												try:
													if not data_id:
														data_id=div.get("data-id")

													if not data_target:
														data_target=div.get("data-target")

													if not label_grid_cell:
														if div.get("role"):
															if div.get("role")=="gridcell":
																label_grid_cell=div.get("aria-label")

												except Exception as e:
													print(the_user_id,"had error at 'for div in thing_divs' loop",e)

												else:
													pass

										link=None
										if data_id and data_target and label_grid_cell:
											if label_grid_cell.endswith("Google Drive Folder"):
												if recursive:
													link="https://drive.google.com/drive/folders/"+data_id

											else:
												link="https://drive.google.com/uc?id="+data_id+"&export=download"

										if link:
											if recursive and link.startswith("https://drive.google.com/drive/folders/"):
												folder=True
												outpath=outdir.joinpath(name)
												if not outpath.exists():
													outpath.mkdir()

											else:
												folder=False
												outpath=outdir

											nvalue=[link,outpath]

											if folder and recursive:
												nvalue=nvalue+["Recursivo"]

											wutt=que.check_value_spc(nvalue)

											if not recursive:
												if not wutt:
													futurepath=outpath.joinpath(name)
													wutt=futurepath.exists()

											if not wutt:
												que.add_value(nvalue)
												prefix="<code>[OK]</code> "

											if wutt:
												prefix="<code>[--]</code> "

											wutt=False

											msg_buffer=que.show_value(nvalue,prefix)+"\n"

										index=index+1

										if link:
											if index==len(folder_stuff):
												msg_chunks.append(msg_total+msg_buffer)

											else:
												if len(msg_total+msg_buffer)>4000:
													msg_chunks.append(msg_total)
													msg_total="<p>..."+msg_buffer

												else:
													msg_total=msg_total+msg_buffer

										if index==len(folder_stuff):
											break

									session_link[_sd_hview]=True

									for m in msg_chunks:
										if not chain:
											replyme=cmev

										else:
											replyme=chain

										try:
											c=await replyme.reply(m,parse_mode="html")
											await asyncio.sleep(0.1)

										except Exception as e:
											print(the_user_id,"/gddl urls list error:",e)

										else:
											chain=c

									session_link[_sd_hview]=False

							que.del_index()
							if que.get_size()==0:
								iterate=False
								wait=True
								while wait:
									try:
										await replyto.reply("Ya no queda nada que procesar en la cola")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

							else:
								wait=True
								while wait:
									try:
										await replyto.reply("Pasando al siguiente elemento en la cola")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

							wutt=False

							# GDDL LOOP ENDS

						# EXIT GDDL LOOP

						que.attrib["working"]=False

						await session.close()

						del session

						n=session_link[_sd_netwquota]
						if n>0:
							session_link[_sd_netwquota]=n-1

				# Manga/Comic Gallery Downloader (VIP ONLY)
				if "/cdl" in command:

					if len(args)>0:
						url_list_raw=args[0]

					if len(args)==0:

						msg=""
						for m in _cdl_support:
							msg=msg+"\n<p><code>"+m+"</code>"

						msg=msg+"\n<p>\n<p>🌚🌚🌚"
						for m in _cdl_support_vip:
							msg=msg+"\n<p><code>"+m+"</code>"

						await event.reply("<p>Sitios soportados\n<p>"+msg,parse_mode="html")
						session_link[_sd_hview]=False
						return

					if not wutt:
						url_list=url_list_raw.split(" ")

						if len(url_list)==0:
							wutt=True
							msg="No se encontraron URLs"

					if not wutt:

						que=session_link[_sd_que]["c"]
						cwd=session_link[_sd_cwd]

						if que.get_size()==0:
							initiate=True

						added_at_least_one=False
						print("\n",the_user_id,"url_list:")

						chain=None

						msg_total="<p>#cdl\n<p>URLs detectadas:\n"
						msg_chunks=[]

						index=0
						while True:
							iurl=url_list[index]
							iurl=iurl.strip()
							print("\t",the_user_id,"iurl =",iurl)
							if iurl.startswith("https://") or iurl.startswith("http://"):
								yurl=yarl.URL(iurl)
								yurl_host=yurl.host

							else:
								wutt=True

							val=[iurl,cwd]

							if not supported_website(_cdl_support,iurl):
								wutt=True

							if wutt:
								if supported_website(_cdl_support_vip,iurl):
									if user_is_vip:
										wutt=False

							if not wutt:
								wutt=que.check_value_spc(val)

							if not wutt:
								que.add_value(val)
								prefix="<code>[OK]</code> "
								if not added_at_least_one:
									added_at_least_one=True

							if wutt:
								prefix="<code>[--]</code> "

							msg_tmp=que.show_value(val,prefix)+"\n"

							index=index+1

							emit=None

							if index==len(url_list):
								print("! emit last msg...")
								emit=msg_total+msg_tmp

							else:
								if len(msg_total+msg_tmp)>4000:
									print("! cut and add...")
									emit=msg_total
									msg_total="\n<p>..."+msg_tmp

								else:
									print("! keep gathering...")
									msg_total=msg_total+msg_tmp

							if emit:
								msg_chunks.append(emit)

							wutt=False
							if index==len(url_list):
								break

						for m in msg_chunks:
							if not chain:
								replyme=event

							else:
								replyme=chain

							try:
								c=await replyme.reply(m,parse_mode="html")
								await asyncio.sleep(0.1)

							except Exception as e:
								print(the_user_id,"/cdl urls list error:",e)

							else:
								chain=c

						if initiate:
							if not added_at_least_one:
								initiate=False

					session_link[_sd_hview]=False

					if not wutt:
						if not initiate:
							return

					if not wutt:
						transfer_jobs=session_link[_sd_netwquota]
						if transfer_jobs==_sntl:
							wutt=True
							msg=_msg_error_tquota

					if wutt:
						await event.reply("<p>#cdl #error\n<p><code>"+msg+"</code>",parse_mode="html")

					else:
						session_link[_sd_netwquota]=transfer_jobs+1

						##########

						working=True

						uagent=get_user_agent()
						ua_head={"User-Agent":uagent}
						session=aiohttp.ClientSession(headers=ua_head,timeout=_tout)

						ticket=mkticket(the_user_id)

						iterate=True

						que.attrib["working"]=True

						while iterate:

							##########

							wutt=False

							que.attrib["cancel"]=False

							value=que.get_value()
							url,outdir=value

							wsite=supported_website(_cdl_support,url)

							if not wsite:
								wsite=supported_website(_cdl_support_vip,url)

							msg_head="<p>#cdl"
							msg_body="\n<p>"+que.show_value(value)
							msg_extra="\n<p>"

							while True:
								try:
									hookev=await chain.reply(msg_head+msg_body+msg_extra+"Preparando...",parse_mode="html")
								except:
									await asyncio.sleep(0.5)
								else:
									break

							await queue_brake_checker(que,event)

							yurl=yarl.URL(url)
							yurl_home=yurl.scheme+"://"+yurl.host

							# URL Modding before the first connection
							if (_ws_xoxocm in wsite) or (_ws_mtemplo in wsite):
								yurl_path_org=Path(yurl.path)
								yurl_path_new=None

								if (_ws_xoxocm in wsite):
									if len(yurl_path_org.parts)==5:
										yurl_path_new=yurl_path_org.joinpath("all")

								if (_ws_mtemplo in wsite):
									if len(yurl_path_org.parts)==4:
										yurl_path_new=yurl_path_org

								if (_ws_lectortmo in wsite):
									if len(yurl_path_org.parts)==2:
										yurl_path_new=yurl_path_org.joinpath("cascade")

									if len(yurl_path_org.parts)==3 and (not yurl_path_org.name=="cascade"):
										yurl_path_new=yurl_path_org.parent.joinpath("cascade")

								if yurl_path_new:
									url=yurl_home+str(yurl_path_new)
									yurl=yarl.URL(url)

							session.headers.update({"Referer":yurl_home})

							if (_ws_nhentai in wsite) or (_ws_hentaifox in wsite) or (_ws_imhentai in wsite) or (_ws_tmohentai in wsite):
								wsite_type=1

							if (_ws_ehentai in wsite) or (_ws_mtemplo in wsite):
								wsite_type=2

							if (_ws_chochox in wsite) or (_ws_vmporno in wsite) or (_ws_tmonline in wsite) or (_ws_mangasin in wsite) or (_ws_leermanga in wsite) or (_ws_xoxocm in wsite) or (_ws_mangafox in wsite) or (_ws_mreadertv in wsite) or (_ws_lectortmo in wsite) or (_ws_hvmanga in wsite) or (_ws_mreadercc in wsite) or (_ws_freeco in wsite):
								wsite_type=3

							msg_act="Descargando la página"

							try:
								async with session.get(url) as response:
									print("response.headers =",response.headers)
									#print("\nresponse.history =",response.history)
									cookies=response.cookies
									html_dump=await response.text()

								session.headers.update({"Referer":url})

							except Exception as e:
								wutt=True
								msg_head=msg_head+" #error"
								msg_extra=msg_extra+"<code>"+msg_act+"\n<p>"+str(e)+"</code>"

							else:
								tags_all=BeautifulSoup(html_dump,"lxml")

							if not wutt:

								page_max=None

								try:
									msg_act="Buscando el título"

									if (_ws_nhentai in wsite) or (_ws_hentaifox in wsite) or (_ws_imhentai in wsite) or (_ws_chochox in wsite) or (_ws_tmonline in wsite) or (_ws_mangasin in wsite) or (_ws_leermanga in wsite) or (_ws_xoxocm in wsite) or (_ws_mangafox in wsite) or (_ws_mreadercc in wsite) or (_ws_freeco in wsite):
										title=tags_all.find("h1").text.strip()

									if (_ws_tmohentai in wsite):
										title=tags_all.find("h3").text.strip()

									if (_ws_ehentai in wsite):
										title=tags_all.find("h1",id="gn").text.strip()

									if (_ws_vmporno in wsite):
										title=tags_all.find("p").text.strip()

									if (_ws_mreadertv in wsite):
										title=tags_all.find("h1").text.split("\n")[0]+" "+yurl.name

									if (_ws_mtemplo in wsite):
										title=tags_all.find("title").text.strip().replace(" - Manga Templo","")

									if (_ws_lectortmo in wsite):
										tag_h1=tags_all.find("h1").text.strip()
										tag_h2=tags_all.find("h2").text.strip().split(" ")[1]
										title=tag_h1+" "+tag_h2

									if (_ws_hvmanga in wsite):
										title=tags_all.find("h2").text.strip()

									if wsite_type<3:

										msg_act="Buscando el número de páginas"

										if (_ws_nhentai in wsite):
											tags_tgt=tags_all.find_all("div",attrs={"tag-container field-name"})

										if (_ws_hentaifox in wsite):
											tags_tgt=tags_all.find_all("span",attrs={"class":"i_text pages"})

										if (_ws_imhentai in wsite):
											tags_tgt=tags_all.find_all("li",attrs={"class":"pages"})

										if (_ws_tmohentai in wsite):
											tags_tgt=tags_all.select("img[data-toggle]")
											page_max=len(tags_tgt)

										if (_ws_ehentai in wsite):
											tags_tgt=tags_all.find_all("td",attrs={"class":"gdt1"})

										if (not _ws_tmohentai in wsite) and (not _ws_mangasin in wsite) and (not _ws_mtemplo in wsite):

											for tag in tags_tgt:
												if ("e-hentai.org") in yurl.host:
													print("tag =",tag)
													if tag.text=="Length:":
														page_max_raw=tag.findNextSibling().text.split(" ")[0]
														try:
															page_max=int(page_max_raw)
														except:
															print("pfffff")

												else:
													if tag.text.find("Pages:")>-1:

														# [!] Get Page number

														if (_ws_nhentai in wsite):
															page_max_raw=tag.find("span").find("span").text

														if (_ws_hentaifox in wsite) or (_ws_imhentai in wsite):
															page_max_raw=tag.text.split(" ")[1]

														try:
															page_max=int(page_max_raw)
														except:
															print("pfffff")

												if type(page_max)==int:
													break

											if not (type(page_max)==int):
												raise Exception("No pages?????")

									if wsite_type==3:

										msg_act="Buscando el número de páginas y las URLs de las imágenes"

										url_list=[]
										if (_ws_tmonline in wsite) or (_ws_mangafox in wsite):
											tags_imgs=tags_all.find_all("div",attrs={"class":"page-break"})
											for tag in tags_imgs:
												data_img=tag.find("img").get("data-src").strip()
												if data_img.startswith("https://"):
													url_list.append(data_img)

										if (_ws_chochox in wsite):
											tags_imgs=tags_all.find_all("li",attrs={"class":"blocks-gallery-item"})
											for tag in tags_imgs:
												data_img=tag.find("img").get("src")
												if data_img.startswith("https://"):
													url_list.append(data_img)

											if len(url_list)==0:
												tags_imgs=tags_all.find_all("img",loading="lazy",attrs={"class":"alignnone"})
												for tag in tags_imgs:
													if tag.get("src"):
														data_img=tag.get("src")
														if data_img.startswith("https://"):
															url_list.append(data_img)

										if (_ws_vmporno in wsite):
											tags_p=tags_all.find("div",attrs={"class":"comicimg"}).find_all("p")
											for tag in tags_p:
												tag_img=tag.select("img[data-lazy-src]")
												if len(tag_img)>0:
													img_data=tag_img[0].get("data-lazy-src")
													if img_data.startswith(yurl_home):
														url_list.append(img_data)

										if (_ws_mangasin in wsite):
											tags_imgs=tags_all.find_all("img",attrs={"class":"img-responsive"})
											for tag in tags_imgs:
												img_data=tag.get("data-src")
												if img_data:
													if img_data.startswith("https://"):
														url_list.append(img_data)

										if (_ws_leermanga in wsite):
											tags_imgs=tags_all.find_all("img",attrs={"class":"img-fluid"})
											for tag in tags_imgs:
												if tag.get("data-src"):
													img_data=tag.get("data-src")
													if img_data.startswith("https://"):
														url_list.append(img_data)

										if (_ws_xoxocm in wsite):
											tags_imgs=tags_all.find_all("div",attrs={"class":"page-chapter"})
											for tag in tags_imgs:
												if tag.find("img"):
													if tag.find("img").get("data-original"):
														img_data=tag.find("img").get("data-original")
														if img_data.startswith("https://"):
															url_list.append(img_data)

										if (_ws_mreadertv in wsite):
											tags_imgs=tags_all.find_all("img",attrs={"class":"img-loading"})
											for tag in tags_imgs:
												if tag.get("data-src"):
													img_data=tag.get("data-src")
													if img_data.startswith("https://") or img_data.startswith("http://"):
														url_list.append(img_data)

										if (_ws_lectortmo in wsite):
											tags_imgs=tags_all.find_all("img",attrs={"viewer-img"})
											for tag in tags_imgs:
												if tag.get("data-src"):
													img_data=tag.get("data-src")
													if img_data.startswith("https://") or img_data.startswith("http://"):
														url_list.append(img_data)

										if (_ws_hvmanga in wsite):
											start=html_dump.find("var pUrl=[")
											if start>-1:
												start_real=start+9
												length=html_dump[start_real:].find("]")
												if length>-1:
													structure=eval(html_dump[start_real:start_real+length+1])
													for indict in structure:
														url_this=indict.get("imgURL")
														if url_this:
															if url_this.startswith("https://") or url_this.startswith("http://"):
																url_list.append(url_this.strip())

										if (_ws_mreadercc in wsite):
											data=tags_all.find("p",id="arraydata").text.split(",")
											for thing in data:
												if thing.startswith("https://") or thing.startswith("http://"):
													url_list.append(thing.strip())

										if (_ws_freeco in wsite):
											tags_imgs=tags_all.find_all("div",attrs={"class":"page-break"})
											for tag in tags_imgs:
												data_img=tag.find("img").get("src").strip()
												if data_img.startswith("https://"):
													url_list.append(data_img)

										page_max=len(url_list)
										if page_max==0:
											raise Exception("No se encontró el número de páginas")

									if wsite_type==2:

										msg_act="Buscando la primera página"

										if (_ws_ehentai in wsite):
											url_page=tags_all.find("div",attrs={"class":"gdtm"}).find("a").get("href")

										if (_ws_mtemplo in wsite):
											url_page=yurl_home+str(yurl_path_org.joinpath("1"))

								except Exception as e:
									wutt=True
									msg_head=msg_head+" #error"
									msg_extra=msg_extra+"<code>"+msg_act+"\n<p>"+str(e)+"</code>"

							if not wutt:

								if wsite_type==1:

									# [!] Get path format

									if (_ws_nhentai in wsite):
										base_path=Path(yurl.path)

									if (_ws_hentaifox in wsite):
										mod_path=yurl.path.replace("gallery","g")
										base_path=Path(mod_path)

									if (_ws_imhentai in wsite):
										mod_path=yurl.path.replace("gallery","view")
										base_path=Path(mod_path)

									if (_ws_tmohentai in wsite):
										mod_path=yurl.path.replace("contents","reader")
										base_path=Path(mod_path).joinpath("paginated")

								msg_act="Creando directorio de salida"

								try:
									if (_ws_mangasin in wsite) or (_ws_xoxocm in yurl.host) or (_ws_tmonline in wsite) or (_ws_mangafox in wsite):
										dirname=yurl.parts[2]+" "+yurl.parts[3]

									elif (_ws_chochox in wsite):
										dirname=yurl.parts[1]

									elif (_ws_leermanga in wsite) or (_ws_mreadercc in wsite):
										dirname=yurl.parts[2]

									else:
										dirname=title.replace("/","-")
										dirname=dirname.replace("|","-")
										dirname=dirname.replace("\\","-")
										dirname=dirname.strip()

								except Exception as e:
									wutt=True
									msg_head=msg_head+" #error"
									msg_extra=msg_extra+"<code>"+msg_act+"\n<p>"+str(e)+"</code>"


								else:
									outpath=outdir.joinpath(dirname)
									if not outpath.exists():
										outpath.mkdir()

									msg_extra=""
									msg_body=msg_body+"\n<p>Salida:\n<p><code>"+get_path_show(outpath)+"</code>"

							while True:
								try:
									await bot.edit_message(thischat,hookev,msg_head+msg_body+msg_extra,parse_mode="html")
								except:
									await asyncio.sleep(0.5)
								else:
									break

							if not wutt:
								page=0
								offset=1
								page_img=1

								stop=False

								errors=0

								info_file=paddednumb(page_max,0)+".nfo"
								info_file_path=outpath.joinpath(info_file)

								async with aiofiles.open(str(info_file_path),"wt") as nfo:
									await nfo.write(title+"\n"+url)

								await asyncio.sleep(0.5)

								stop=False

								while not stop:

									if page_max:
										page_max_str=str(page_max)
									else:
										page_max_str="???"

									msg_extra="\n<p>Página "+str(page_img)+" de "+page_max_str

									cont=True
									while cont:
										try:
											await bot.edit_message(thischat,hookev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											cont=False

									wutt=False

									if wsite_type==1:
										path_new=base_path.joinpath(mod)
										url_page=yurl_home+str(path_new)

									cancel_signal=que.attrib["cancel"]
									if cancel_signal:
										wutt=True
										stop=True
										msg="Cancelado"

									if not wutt:

										# [!] Obtain page content

										if not wsite_type==3:
											msg_act="Obteniendo contenido de "+url_page
											print("current page:",url_page)

											try:

												cancel_signal=que.attrib["cancel"]
												if cancel_signal:
													raise Exception("Cancelado")

												# HTML dump from this page
												async with session.get(url_page,cookies=cookies) as response:
													cookies=response.cookies
													html_dump_page=await response.text()

											except Exception as e:
												errors=errors+1
												wutt=True
												msg=str(e)
												if msg=="Cancelado":
													stop=True

											else:
												tags_page=BeautifulSoup(html_dump_page,"lxml")

											await asyncio.sleep(0.5)

									if not wutt:

										# [!] Obtain image URL

										msg_act="Obteniendo URL con la imagen"
										try:

											cancel_signal=que.attrib["cancel"]
											if cancel_signal:
												raise Exception("Cancelado")

											if wsite_type==3:
												url_img=url_list[page]

											if not wsite_type==3:
												if (_ws_nhentai in wsite):
													url_img=tags_page.find("section",id="image-container").find("img").get("src")

												if (_ws_hentaifox in wsite) or (_ws_imhentai in wsite):
													url_img=tags_page.find("img",id="gimg").get("data-src")

												if (_ws_tmohentai in wsite):
													path_img=tags_page.find("img",attrs={"class":"content-image lazy"}).get("data-original")
													url_img=yurl_home+path_img

												if (_ws_ehentai in wsite):
													url_img=tags_page.find("img",id="img").get("src")

												if (_ws_mtemplo in wsite):
													url_img=tags_page.find("img",attrs={"class":"img-fluid"}).get("src")

												if not url_img:
													raise Exception("URL no válida")

										except Exception as e:
											errors=errors+1
											wutt=True
											msg=str(e)
											if msg=="Cancelado":
												stop=True

									if not wutt:
										msg_act="Descargando la imagen de "+url_img

										try:

											cancel_signal=que.attrib["cancel"]
											if cancel_signal:
												raise Exception("Cancelado")

											yyy=yarl.URL(url_img)

											async with session.get(url_img,cookies=cookies) as r:
												cookies=response.cookies

												# TODO: fix serious problem with the fucking suffixes!

												suffix=""
												if response.headers.get("content-disposition"):
													filename_from_url=response.content_disposition.filename
													suffix=Path(filename_from_url).suffix

												if suffix=="":
													suffix=Path(yarl.URL(url_img).name).suffix

												if suffix=="":
													suffix=".jpeg"

												if page_max:
													limit=page_max
												else:
													limit=1000

												stem=paddednumb(limit,page_img)

												filename=stem+suffix
												filepath=outpath.joinpath(filename)

												async with aiofiles.open(str(filepath),"wb") as f:
													while True:
														chunk=await r.content.read(1024*1024)
														if chunk:
															await f.write(chunk)
														else:
															break

										except Exception as e:
											errors=errors+1
											wutt=True
											msg=str(e)
											if msg=="Cancelado":
												stop=True

										else:
											if filepath.exists():
												if os.path.getsize(str(filepath))==0:
													stop=True
													filepath.unlink()

									if not wutt:
										if wsite_type==2:

											# Determining the next page's URL

											url_page_ar=url_page
											session.headers.update({"Referer":url_page_ar})

											url_page=None

											if (_ws_ehentai in wsite):
												tag=tags_page.find("a",id="next")
												if tag:
													url_page=tag.get("href")

											if (_ws_mtemplo in wsite):
												tag=tags_page.find("a",attrs={"class":"btn-next"})
												if tag:
													npath=tag.get("href")
													if npath:
														url_page=yurl_home+npath

											if not url_page:
												stop=True

									if wutt:
										cont=True
										while cont:
											try:
												await hookev.reply("<p>Error en la página "+str(page_img)+":\n<p><code>"+msg_act+"\n<p>"+msg+"</code>",parse_mode="html")
											except:
												await asyncio.sleep(0.5)
											else:
												cont=False

									await asyncio.sleep(0.5)

									page_img=page_img+1
									page=page+1

									if page_max:
										if page_max>0:
											if page==page_max:
												stop=True

								if errors>0:
									msg_extra="\n<p>Hubo errores durante la descarga"
									msg_head=msg_head+" #error"
									while True:
										try:
											await bot.edit_message(thischat,hookev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											break

								if errors==0:

									# zip -0 -j path/to/archive.zip path/to/dir/*

									msg_extra="\n<p>Archivando en CBZ..."
									while True:
										try:
											await bot.edit_message(thischat,hookev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											break

									me=["/ekisdé",the_user_id]
									_gq_sub.append(me)

									while True:
										try:
											await wait_global_queue(me,"SUB",event,thischat)
										except:
											await asyncio.sleep(0.5)
										else:
											break

									cbzpath=outdir.joinpath(dirname+".cbz")
									if cbzpath.exists():
										frname=dirname+" "+mkticket(aspath=False)+".cbz"
										cbzpath=outdir.joinpath(frname)

									run_this="zip -0 -j \""+str(cbzpath)+"\" \""+str(outpath)+"\"/*"
									print("$",run_this)

									output,errors=await shell_run(run_this)

									await asyncio.sleep(0.5)

									try:
										_gq_sub.pop(0)
									except:
										pass

									msg_head=msg_head+" #ok"
									msg_extra="\n<p>Archivo CBZ creado:\n<p><code>"+get_path_show(cbzpath)+"</code>"

									while True:
										try:
											await bot.edit_message(thischat,hookev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											break

							que.del_index()
							if que.get_size()==0:
								iterate=False
								await event.reply("Ya no queda nada que procesar en la cola")

							else:
								await event.reply("Pasando al siguiente elemento en la cola")
								await asyncio.sleep(0.5)

							wutt=False

							##########

						##########

						que.attrib["working"]=False

						await session.close()
						del session

						n=session_link[_sd_netwquota]
						if n>0:
							session_link[_sd_netwquota]=n-1

					##########

				# MEGA.nz Credentials for the "/mega" command
				if "/megacreds" in command:
					msg_head="#megacreds"
					if len(args)>0 and len(args)<3:

						if args[0]=="-":
							mega_username=""
							mega_password=""

						else:
							mega_username=args[0]
							mega_password=args[1]

						session_link[_sd_mega_session]=[mega_username,mega_password]
						msg="Credenciales de MEGA actualizados"

					elif len(args)==0:
						msg="Usuario: <code>"+session_link[_sd_mega_session][0]+"</code>\n<p>Contraseña: <code>"+session_link[_sd_mega_session][1]+"</code>"

					else:
						wutt=True
						msg=_msg_error_wargs

					if wutt:
						msg_head=msg_head+" #error"

					await event.reply("<p>"+msg_head+"\n<p>"+msg,parse_mode="html")

				# MEGA.nz Downloader
				if "/megadl" in command:

					initiate=False
					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					if len(args)==1:
						url_list_raw=args[0]

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						url_list=url_list_raw.split(" ")

						if len(url_list)==0:
							wutt=True
							msg="No se encontraron URLs"

					if not wutt:

						que=session_link[_sd_que]["m"]
						cwd=session_link[_sd_cwd]

						if que.get_size()==0:
							initiate=True

						added_at_least_one=False
						print("\n",the_user_id,"url_list:")

						chain=None

						msg_total="<p>#megadl\n<p>URLs detectadas:\n"
						msg_chunks=[]

						index=0
						while True:
							iurl=url_list[index]
							iurl=iurl.strip()
							print("\t",the_user_id,"iurl =",iurl)

							if iurl.startswith("https://") or iurl.startswith("http://"):
								if iurl.startswith("http://"):
									iurl.replace("http://","https://")

								yurl=yarl.URL(iurl)
								yurl_host=yurl.host

							else:
								wutt=True

							if not wutt:
								if not ("mega.nz" in yurl_host):
									wutt=True

								print("yurl.path =",yurl.path)

								if yurl.path.startswith("/folder"):
									wutt=True

								elif yurl.path.startswith("/file"):
									print("ok")

								elif iurl.startswith("https://mega.nz/#!"):
									print("ok")

								else:
									wutt=True

							val=[iurl,cwd]

							if not wutt:
								vexists=que.check_value_spc(val)

								if vexists:
									wutt=True

							if not wutt:
								que.add_value(val)
								prefix="<code>[OK]</code> "
								if not added_at_least_one:
									added_at_least_one=True

							if wutt:
								prefix="<code>[--]</code> "

							msg_tmp=que.show_value(val,prefix)

							index=index+1

							emit=None

							if index==len(url_list):
								emit=msg_total+msg_tmp

							else:
								if len(msg_total+msg_tmp)>4000:
									emit=msg_total
									msg_total=msg_tmp

								else:
									msg_total=msg_total+msg_tmp

							if emit:
								msg_chunks.append(emit)

							wutt=False
							if index==len(url_list):
								break

						for m in msg_chunks:
							if not chain:
								replyme=event

							else:
								replyme=chain

							try:
								c=await replyme.reply(m,parse_mode="html")
								await asyncio.sleep(0.1)

							except Exception as e:
								print(the_user_id,"/megadl urls list error:",e)

							else:
								chain=c

						if initiate:
							if not added_at_least_one:
								initiate=False

					session_link[_sd_hview]=False

					if not wutt:
						if not initiate:
							return

					if not wutt:
						transfer_jobs=session_link[_sd_netwquota]
						if transfer_jobs==_sntl:
							wutt=True
							msg=_msg_error_tquota

					if wutt:
						await event.reply("<p>#megadl #error\n<p><code>"+msg+"</code>",parse_mode="html")

					else:
						tquota=session_link[_sd_netwquota]
						session_link[_sd_netwquota]=tquota+1

						email,password=session_link[_sd_mega_session]

						# Get stuff from session link

						msg_title="<p>#megadl\n<p>"

						mainmev=await event.reply(msg_title+"\n<p>Iniciando sesión...",parse_mode="html")

						loop=asyncio.get_event_loop()

						m=Mega()
						msg_login="<p>Sesión"
						
						try:
							assert len(email)>0
							assert len(password)>0
						
						except:
							msg_login_extra=" anónima"
                       
						else:
							msg_login_extra=" con los credenciales"
						
						loop=asyncio.get_event_loop()
						mlogin=loop.run_in_executor(None,mega_login,m,email,password)
						await mlogin
						
						msg_login=msg_login+msg_login_extra
						
						await asyncio.sleep(0.5)
						
						await bot.edit_message(thischat,mainmev,msg_title+msg_login,parse_mode="html")

						que.attrib["working"]=True

						iterate=True
						while iterate:

							value=que.get_value()
							this_url,outdir=value

							que.attrib.update({"conf":False,"fpath":None,"tsize":0,"cancel":False})

							await queue_brake_checker(que,mainmev)
							#await queue_brake_checker(que,chain)

							if not value:
								wutt=True

							msg_head="<p>#megadl"
							msg_curr=que.show_value(value)

							progmev=await mainmev.reply(msg_head+msg_curr+"\n<p>Descargando...",parse_mode="html")
							#progmev=await chain.reply(msg_head+msg_curr+"\n<p>Descargando...",parse_mode="html")

							await asyncio.sleep(0.5)

							hook=que.attrib

							loop=asyncio.get_event_loop()
							#mega_user,mega_pass=session_link[_sd_mega_session]

							progress=loop.create_task(ntprog(thischat,progmev,outdir,None,msg_head+msg_curr,hook))
							print("leaving ev to go to the executor...")
							download_from_mega=loop.run_in_executor(None,mega_downloader,outdir,this_url,m,hook)
							#download_from_mega=loop.run_in_executor(None,mega_downloader_new,outdir,this_url,hook,mega_user,mega_pass)
							await download_from_mega
							print("returning from the executor...")

							progress.cancel()

							while True:
								await asyncio.sleep(0.5)
								if progress.done():
									break

							msg_at_the_end=download_from_mega.result()

							if len(msg_at_the_end)>0:
								if "Cancelado" in msg_at_the_end:
									msg_head=msg_head+" #cancel"

								else:
									msg_head=msg_head+" #error"

								if que.attrib.get("kick"):
									msg_head=msg_head+" #kick"
									que.add_value(value)
									que.attrib.update({"kick":False})

									if que.queue[1]==value:
										await asyncio.sleep(2)

								msg_at_the_end="\n<p>"+msg_at_the_end

							else:
								#filepath=fdata["fpath"]
								filepath=que.attrib["fpath"]
								msg_at_the_end="\n<p>#terminado\n<p><code>"+get_path_show(filepath)+"</code>"

							await bot.edit_message(thischat,progmev,msg_head+msg_curr+msg_at_the_end,parse_mode="html")

							que.del_index()

							if que.get_size()>0:
								await event.reply("Pasando al siguiente elemento en la cola")
								await asyncio.sleep(0.5)

							else:
								iterate=False
								await event.reply("Ya no queda nada que procesar en la cola")

							wutt=False

						del m

						que.attrib["working"]=False

						# Remove quota usage

						n=session_link[_sd_netwquota]
						if n>0:
							session_link[_sd_netwquota]=n-1

				# Upload to Telegram
				if "/upload" in command:

					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					initiate=False
					cwd=session_link[_sd_cwd]

					if len(args)==1:
						stype=_stype_s
						try:
							index=int(args[0])
							assert index>-1

						except:
							stype=_stype_r

						if _stype_r in stype:
							range_args=get_args_range(args[0])
							if not range_args:
								stype=_stype_f

						if _stype_f in stype:
							free_args=get_args_free(args[0])
							if not free_args:
								wutt=True
								msg=_msg_error_iarg

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						if _stype_s in stype:
							selected_fse=await aio_get_fsepath(cwd,index)

							if selected_fse:
								if selected_fse.is_dir():
									fse_list=await aio_get_dircont(selected_fse,fsetype=0)
									if len(fse_list)==0:
										wutt=True
										msg=_msg_error_empty

								elif selected_fse.is_file():
									fse_list=[selected_fse]

								else:
									wutt=True
									msg=_msg_error_unknown

							else:
								wutt=True
								msg=_msg_error_notfound

						else:
							if _stype_r in stype:
								fse_list_raw=await aio_get_dircont_ranged(cwd,range_args)

							if _stype_f in stype:
								fse_list_raw=await aio_get_dircont_free(cwd,free_args)

							if len(fse_list_raw)==0:
								wutt=True
								msg=_msg_error_empty

							if not wutt:
								fse_list=[]
								for fse in fse_list_raw:
									if fse.is_file():
										fse_list=fse_list+[fse]

								if len(fse_list)==0:
									wutt=True
									msg=_msg_error_empty

					if not wutt:
						que=session_link[_sd_que]["u"]
						cwd=session_link[_sd_cwd]

						if que.get_size()==0:
							initiate=True

						msg_chunks=[]
						msg_total="<p>Archivos seleccionados\n<p><code>"
						index=0

						for fse in fse_list:
							wutt=que.check_value(fse)

							if not wutt:
								if os.path.getsize(str(fse))>2*_gigabyte:
									wutt=True

							if not wutt:
								if len(fse.name)>60:
									wutt=True

							msg_add=get_path_show(fse)

							if wutt:
								msg_add="[--] "+msg_add

							else:
								msg_add="[OK] "+msg_add
								que.add_value(fse)

							msg_add="\n<p><code>"+msg_add+"</code>"

							msg_put=None

							index=index+1
							if index==len(fse_list):
								msg_put=msg_total+msg_add

							else:
								if len(msg_total+msg_add)>4000:
									msg_put=msg_total
									msg_total=msg_add

								else:
									msg_total=msg_total+msg_add

							if msg_put:
								msg_chunks.append(msg_put)

							wutt=False

						chain=None
						for m in msg_chunks:
							if not chain:
								repl=event
							else:
								repl=chain

							try:
								chk=await repl.reply(m,parse_mode="html")
							except Exception as e:
								print(the_user_id,"/upload (showing upload list)",e)
							else:
								chain=chk

							await asyncio.sleep(0.1)

						if initiate:
							if que.get_size()==0:
								initiate=False

					session_link[_sd_hview]=False

					if not wutt:
						if not initiate:
							return

					if not wutt:
						transfer_jobs=session_link[_sd_netwquota]
						if transfer_jobs==_sntl:
							msg=_msg_error_tquota
							wutt=True

					if wutt:
						await event.reply(msg)

					else:
						session_link[_sd_netwquota]=transfer_jobs+1

						iterate=True
						this=await event.reply("#upload")

						que.attrib["working"]=True

						while iterate:

							que.attrib["cancel"]=False
							cancelled=False

							fpath=que.get_value()

							await queue_brake_checker(que,this)

							msg_head1="<p>#upload"
							msg_head2="\n<p><code>"+get_path_show(fpath)+"</code>"

							try:
								await bot.edit_message(thischat,this,msg_head1+msg_head2,parse_mode="html")
							except Exception as e:
								print(the_user_id,"/upload display error (A):",e)

							if not fpath.exists():
								wutt=True
								msg_head1=msg_head1+" #error"
								msg_extra="\n<p><code>"+_msg_error_notfound+"</code>"

							if not wutt:
								await asyncio.sleep(0.5)
								loop=asyncio.get_event_loop()

								punit=ProgressUnit()

								total_size=os.path.getsize(str(fpath))

								tgup=loop.create_task(tguploader(punit,fpath,total_size,msg_head1+msg_head2,thischat,this))

								msg=await task_admin(tgup,que)

								if que.attrib.get("exc"):
									wutt=True

								await asyncio.sleep(0.5)

								if wutt:
									msg_extra=punit.log+"\n<p><code>"+msg+"</code>"

							if wutt:
								await this.reply(msg_head1+msg_head2+msg_extra,parse_mode="html")

							await asyncio.sleep(0.5)

							que.del_index()
							if que.get_size()==0:
								iterate=False
							else:
								await asyncio.sleep(0.5)

							wutt=False

						que.attrib["working"]=False

						n=session_link[_sd_netwquota]
						if n>0:
							session_link[_sd_netwquota]=n-1

						try:
							await bot.edit_message(thischat,this,"#upload #terminado")
							await asyncio.sleep(0.5)
							await this.reply("Ya no queda nada que procesar en la cola")
						except Exception as e:
							print(the_user_id,"Error at the very end of /upload:",e)

				# User Agent selector
				if "/ua" in command:
					if len(args)==0:
						ua=session_link[_sd_ua]

						namae=_ua_dict[ua]

						msg="<p>#ua\n<p>Agentes de usuario disponibles:"
						for b in _ua_dict:
							n=_ua_dict[b]
							msg=msg+"\n<p>"+b+" - "+n

						msg=msg+"\n<p>\n<p>Agente de usuario actual:\n<p>"+ua+" - "+namae

						await event.reply(msg,parse_mode="html")
						return

					elif len(args)==1:
						ua=args[0]
						if ua in _ua_dict:
							session_link[_sd_ua]=ua
							namae=_ua_dict.get(ua)
							msg="\n<p>Agente de usuario seleccionado:\n<p>"+ua+" - "+namae

						else:
							wutt=True
							msg="Agente de usuario no conocido"

					else:
						wutt=True
						msg=_msg_error_wargs

					if wutt:
						msg="<p>#ua #error\n<p><code>"+msg+"</code>"

					else:
						msg="<p>#ua #ok"+msg

					await event.reply(msg,parse_mode="html")

				# General web downloader
				if ("/wget" in command) or ("/apkaward" in command):

					#if "/wget" in command:
					#	ctype=1

					#if "/apkaward" in command:
					#	ctype=2

					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					initiate=False

					if len(args)==1:
						url_list_raw=args[0]

					elif len(args)==0:
						msg="<code>"

						for ws in _wget_support:
							msg=msg+"\n<p>"+ws

						msg=msg+"</code>"

						await event.reply("<p>Sitios soportados\n<p>"+msg,parse_mode="html")
						session_link[_sd_hview]=False
						return

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						url_list=url_list_raw.split(" ")

						if len(url_list)==0:
							wutt=True
							msg="No se encontraron URLs"

					if not wutt:

						que=session_link[_sd_que]["w"]
						cwd=session_link[_sd_cwd]

						if que.get_size()==0:
							initiate=True

						added_at_least_one=False
						print("\n",the_user_id,"url_list:")

						chain=None

						msg_total="<p>#wget\n<p>URLs detectadas:\n"
						msg_chunks=[]

						index=0
						while True:
							iurl=url_list[index]
							iurl=iurl.strip()
							print("\t",the_user_id,"iurl =",iurl)
							if iurl.startswith("https://") or iurl.startswith("http://"):
								yurl=yarl.URL(iurl)
								yurl_host=yurl.host

							else:
								wutt=True

							if not wutt:
								if ("mega.nz" in yurl_host):
									wutt=True

							val=[iurl,cwd]

							if not wutt:
								vexists=que.check_value_spc(val)

								if vexists:
									wutt=True

							if not wutt:
								que.add_value(val)
								prefix="<code>[OK]</code> "
								if not added_at_least_one:
									added_at_least_one=True

							if wutt:
								prefix="<code>[--]</code> "

							msg_tmp=que.show_value(val,prefix)+"\n"

							index=index+1

							emit=None

							if index==len(url_list):
								emit=msg_total+msg_tmp

							else:
								if len(msg_total+msg_tmp)>4000:
									emit=msg_total
									msg_total="\n<p>..."+msg_tmp

								else:
									msg_total=msg_total+msg_tmp

							if emit:
								msg_chunks.append(emit)

							wutt=False
							if index==len(url_list):
								break

						for m in msg_chunks:
							if not chain:
								replyme=event

							else:
								replyme=chain

							try:
								c=await replyme.reply(m,parse_mode="html")
								await asyncio.sleep(0.1)

							except Exception as e:
								print(the_user_id,"/wget urls list error:",e)

							else:
								chain=c

						if initiate:
							if not added_at_least_one:
								initiate=False

					session_link[_sd_hview]=False

					if not wutt:
						if not initiate:
							return

					if not wutt:
						transfer_jobs=session_link[_sd_netwquota]
						if transfer_jobs==_sntl:
							wutt=True
							msg=_msg_error_tquota

					if wutt:
						await event.reply("<p>#wget #error\n<p><code>"+msg+"</code>",parse_mode="html")

					else:

						# wget START

						session_link[_sd_netwquota]=transfer_jobs+1

						sel_ua=session_link[_sd_ua]

						uagent=get_user_agent(sel_ua)
						msg_ua="\n<p>Agente de usuario:\n<p>"+sel_ua+" - "+_ua_dict[sel_ua]+"\n<p><code>"+uagent+"</code>"

						uahead={"User-Agent":uagent}
						session=aiohttp.ClientSession(headers=uahead,timeout=_tout)

						replyto=await event.reply("<p>#wget"+msg_ua,parse_mode="html")

						iterate=True

						que.attrib["working"]=True

						the_urls={}

						# ENTER A LOOP

						while iterate:

							# wget STARTS LOOP

							que.attrib["cancel"]=False

							reservoir=False

							cvalue=que.get_value()
							ourl,cwd=cvalue

							yurl=yarl.URL(ourl)
							yurl_host=yurl.host

							# Check if URL is supported
							supported=supported_website(_wget_support,ourl)

							# VIP only
							if user_is_vip and not supported:
								supported=supported_website(_wget_support_vip,ourl)

							msg_head1="<p>#wget"
							msg_head2="\n<p>"+que.show_value(cvalue)+"\n<p>"
							msg_extra=""

							currmev=await replyto.reply(msg_head1+msg_head2+"\n<p>Iniciando...",parse_mode="html")

							await queue_brake_checker(que,currmev)

							cookies=None

							ourl_host=yurl.scheme+"://"+yurl_host

							# Supported sites (scrapers, etc...)
							if supported:
								if not wutt:
									await asyncio.sleep(0.5)

									try:
										async with session.get(ourl) as response:
											cookies=response.cookies
											html_dump=await response.text()
											print("response.status =",response.status)

									except Exception as e:
										wutt=True
										msg_head1=msg_head1+" #error"
										msg_extra="\n<p>Mientras se descargaba la página:\n<p><code>"+str(e)+"</code>"

									else:
										msg_extra="\n<p>Buscando información en la página..."

									finally:
										await bot.edit_message(thischat,currmev,msg_head1+msg_head2+msg_extra,parse_mode="html")

								if not wutt:
									await asyncio.sleep(0.5)

									session.headers.update({"Referer":ourl_host})
									print("session.headers =",session.headers)

									just_add=False

									try:
										# AndroEED
										if _ws_androeed in supported:
											tags_all=BeautifulSoup(html_dump,"lxml")
											tags_script=tags_all.find_all("script")

											#NOTES
											#url=args[0]
											#coded=url.split("get_file?url=")[1]
											#decoded_a=base64_decode(coded)
											#url_real=str(base64.b64decode(t))[2:]

											s_selected=None
											pattern="function send_speed_alert(a){show_mainloader()"
											for s in tags_script:
												s_current=s.text
												if pattern in s_current:
													s_selected=s_current
													break

											if not s_selected:
												raise Exception("checkpoint no. 1")

											i=0
											i_start=-1
											while i<len(s_selected):
												if s_selected[i]=="h":
													if s_selected[i:i+5]=="href=":
														i_start=i+5
														break

												i=i+1

											if not i_start>-1:
												raise Exception("checkpoint no. 2")


											s_selected=s_selected[i_start:]

											i=0
											i_end=-1
											while i<len(s_selected):
												if s_selected[i]==" ":
													i_end=i
													break

												i=i+1

											if not i_end>-1:
												raise Exception("checkpoint no. 3")

											url_button=eval(s_selected[:i_end])
											coded=url_button.split("get_file.php?url=")[1]
											dec_a=base64.b64decode(coded)

											i=-1
											i_sel=-1
											dec_a_str=dec_a.decode("utf-8")
											for c in dec_a_str:
												i=i+1
												if c=="|":
													i_sel=i
													break

											if not i_sel>-1:
												raise Exception("checkpoint no. 4")

											dec_a_core=dec_a_str[:i].encode("utf-8")
											dec_b=base64.b64decode(dec_a_core)
											real_url=dec_b.decode("utf-8")
											fname=Path(real_url).name

											the_urls.update({real_url:fname})

										# APKAWard
										if _ws_apkaward in supported:
											tags_all=BeautifulSoup(html_dump,"lxml")
											# buttons=alltags.find("div",id="DAPK").find("div",attrs={"class":"like-apk-file"}).find_all("a")
											buttons=tags_all.find("div",id="DAPK").find_all("a")

											if len(buttons)==0:
												raise Exception("checkpoint no. 1")

											for btn_raw in buttons:
												btn_onclick=btn_raw.get("onclick")
												btn_txt=eval(btn_onclick.replace("apk_mod(this,","("))
												if btn_txt.startswith("https://"):
													fname=Path(btn_txt).name
													the_urls.update({btn_txt:fname})

											if len(the_urls)==0:
												raise Exception("checkpoint no. 2")

										# APKMirror
										#if _ws_apkmirror in supported:
										#	tags_all=BeautifulSoup(html_dump,"lxml")
										#	fname=tags_all.find("span",style="word-break: break-all; font-style: italic;").text
										#	session.headers.update({"Referer":ourl})
										#	real_url="https://www.apkmirror.com/wp-content/themes/APKMirror/download.php?id="+shortlink

										# CDROMance
										#if "cdromance.com" in supported:
										#	"""
										#	<script>
										#	(function($) {
										#	  $(".acf-get-content-button").click(function(e) {
										#		e.preventDefault();
										#				
										#		var $contentWrapper = $("#acf-content-wrapper");
										#		var buttonId = $(this).attr("id");
										#		
										#		var postId = $contentWrapper.data("id");
										#		var fileName = $(this).data("filename");
										#		var serverId = $(this).data("server");
										#
										#		$.ajax({
										#			url: "/wp-content/plugins/cdromance/public/direct.php",
										#			type: "POST",
										#			data: {
										#			  "post_id": postId,
										#			  "file_name": fileName,
										#			  "server_id": serverId
										#			},
										#		  })
										#		  .done(function(data) {
										#
										#			$contentWrapper.html("");
										#			$contentWrapper.append(data);
										#			$("#" + buttonId).replaceWith("Download Requested...");
										#		  });
										#	  });
										#	})
										#	(jQuery);
										#	</script>
										#	"""

										# Mediafire
										if _ws_mf in supported:
											tags_all=BeautifulSoup(html_dump,"lxml")
											real_url=tags_all.find("a",id="downloadButton").get("href")
											fname_tag=tags_all.find("div",attrs={"class":"filename"})
											if fname_tag:
												fname=fname_tag.text
											else:
												fname=Path(real_url).name

											the_urls.update({real_url:fname})

										# OpenSubtitles1
										if _ws_osubt1 in supported:
											the_urls={}
											site_lang=yurl.parts[1]

											level=0

											if len(site_lang)==2 and yurl.parts[2]=="subtitles":
												level=1

											if len(site_lang)==2 and yurl.parts[3].startswith("sublanguageid-"):
												if yurl.parts[2]=="search":
													level=2

												if yurl.parts[2]=="ssearch":
													level=3

											if level==0:
												raise Exception("URL no válida...")

											if level==1:
												sub_id=yurl.parts[3]
												if int(sub_id):
													real_url=ourl_host+"/"+site_lang+"/subtitleserve/sub/"+sub_id
													the_urls.update({real_url:None})

												if len(the_urls)==0:
													raise Exception("???")

											if level>1:

												just_add=True
												added=0

												tags_all=BeautifulSoup(html_dump,"lxml")

												if level==2:
													tags_a=tags_all.find_all("a",attrs={"class":"bnone"})

												if level==3:
													tags_a=tags_all.find_all("a",itemprop="url")

												idx=0
												tags_a_len=0

												if level==2:
													scan_bool=[False]

												if level==3:
													scan_bool=[True,False]

												for scan in [True,False]:
													for tag in tags_a:
														ok=False
														npath=tag.get("href")
														print("npath =",npath)

														if level==2:
															if ("/subtitles/" in npath):
																if scan:
																	tags_a_len=tags_a_len+1
																else:
																	ok=True

														if level==3:
															if ("/sublanguageid-" in npath) and ("/pimdbid-" in npath) and ("Season" in tag.text):
																if scan:
																	tags_a_len=tags_a_len+1
																else:
																	idx=idx+1

															if not scan:
																if ("/sublanguageid-" in npath) and ("/imdbid-" in npath):
																	ok=True

														if not scan:
															if ok:
																new_url=ourl_host+npath

																if level==2:
																	new_value=[new_url,cwd]

																if level==3:
																	season=yurl.name+" S"+paddednumb(tags_a_len,idx)
																	season_path=cwd.joinpath(season)
																	if not season_path.exists():
																		season_path.mkdir()

																	new_value=[new_url,season_path]

																pfff=que.check_value_spc(new_value)
																if not pfff:
																	que.add_value(new_value)
																	added=added+1

										# Solidfiles
										if _ws_sf in supported:
											tags_all=BeautifulSoup(html_dump,"lxml")
											tags_script=tags_all.find_all("script")

											pos=0
											selected=-1
											for idx in tags_script:
												if "downloadUrl" in str(idx):
													selected=pos
													break
												pos=pos+1

											if not selected>-1:
												raise Exception("checkpoint no. 1")

											selected_tag=str(tags_script[selected])

											pos=0
											bracket1=-1
											bracket2=-1
											for c in selected_tag:
												if bracket1<0:
													if c=="{":
														bracket1=pos

												if bracket2<0:
													if c=="}":
														bracket2=pos

												if (bracket1>-1) and (bracket2>-1):
													break

												pos=pos+1

											if bracket1>-1 and bracket2>-1:
												pass

											else:
												raise Exception("checkpoint no. 2")

											dict_str=selected_tag[bracket1:bracket2+1]
											dict_real=json.loads(dict_str)
											real_url=dict_real["downloadUrl"]
											fname=dict_real["nodeName"]
											the_urls.update({real_url:fname})

										# Subscene
										if _ws_subscene in supported:
											tags_all=BeautifulSoup(html_dump,"lxml")
											tag_a=tags_all.find("a",id="downloadButton")
											if tag_a:
												npath=tag_a.get("href")
												real_url=ourl_host+npath
												the_urls={real_url:None}

											else:
												raise Exception("URL no válida...")

										# TokyVideo
										if _ws_tokyvideo in supported:
											alltags=BeautifulSoup(html_dump,"lxml")
											real_url=alltags.find("source").get("src")
											real_url_yarl=yarl.URL(real_url)
											suffix=Path(real_url_yarl.name).suffix
											fname=yurl.name+suffix
											the_urls.update({real_url:fname})

										# TuSubtitulo
										if _ws_tusubtitulo in supported:
											tags_all=BeautifulSoup(html_dump,"lxml")

											level=0
											if yurl.path.startswith("/episodes"):
												level=1

											if yurl.path.startswith("/season") or yurl.path.startswith("/show"):
												level=2
												if yurl.path.startswith("/show"):
													if len(yurl.parts)==3:
														level=3

													if len(yurl.parts)==4 and yurl.parts[-1]=="":
														level=3

											if level==0:
												raise Exception("URL no válida...")

											# Get all in this episode
											if level==1:
												tags_vlinks=tags_all.find_all("a",attrs={"class":"bt_descarga"})

												the_urls={}

												for tag in tags_vlinks:
													rel_raw=tag.get("rel")[0]
													rel_split=rel_raw.split(",")
													new_url=ourl_host
													if len(rel_split)==2:
														new_url=new_url+"/original/"+rel_split[0]+"/"+rel_split[1]

													else:
														new_url=new_url+"/updated/"+rel_split[0]+"/"+rel_split[1]+"/"+rel_split[2]

													print("added:",new_url)
													the_urls.update({new_url:None})

											# Get all episodes in a season
											if level==2:
												tags_a=tags_all.find_all("a")
												added=0
												just_add=True
												pattern=ourl_host+"/episodes/"
												for tag in tags_a:
													pfff=False
													href_this=tag.get("href")
													if href_this:
														if href_this.startswith(pattern):
															new_value=[href_this,cwd]
															pfff=que.check_value_spc(new_value)
															if not pfff:
																que.add_value(new_value)
																added=added+1

											# Get all seasons
											if level==3:
												tags_a=tags_all.select("a[data-season]")

												tag_p=tags_all.find("p",attrs={"class":"titulo"})
												if tag_p:
													the_title=tag_p.text
												else:
													the_title=yurl.parts[2]

												added=0
												just_add=True

												tags_a_len=len(tags_a)

												for tag in tags_a:
													npath=tag.get("href")
													nurl=ourl_host+npath

													idx_raw=tag.get("data-season")
													idx=int(idx_raw)
													season=the_title+" S"+paddednumb(tags_a_len,idx)
													path_season=cwd.joinpath(season)
													if not path_season.exists():
														path_season.mkdir()

													new_value=[nurl,path_season]
													pfff=que.check_value_spc(new_value)
													if not pfff:
														que.add_value(new_value)
														added=added+1
										# Vimm's Lair
										if _ws_vimm in supported:

											if not yurl.path.startswith("/vault/"):
												raise Exception("Solo hay soporte para bajar de la bóveda, es decir, las ROMs")

											tags_all=BeautifulSoup(html_dump,"lxml")
											tag_fname_stem=tags_all.find("span",id="data-good-title")

											fname=None
											url_base=None
											input_value=None

											if yurl.path.startswith("/vault/"):
												if tag_fname_stem:
													fname=tag_fname_stem.findParent("td").text

												tag_form=tags_all.find("form",id="download_form")
												if tag_form:
													url_base=tag_form.get("action")
													input_value=tag_form.find("input").get("value")

												if not tag_form:
													tag_form=tags_all.find("form",id="ird-form")
													url_base=tag_form.get("action")
													input_value=tag_form.find("input").get("value")

											if url_base and input_value:
												real_url="https:"+url_base+"?mediaId="+input_value
											else:
												raise Exception("¿Quééééé?")

											the_urls.update({real_url:fname})
											print("the_urls =",the_urls)

										# YIFY Subtitles
										if _ws_yifysubs in supported:

											tags_all=BeautifulSoup(html_dump,"lxml")
											the_urls={}

											if yurl.path.startswith("/subtitles/"):
												tag_a=tags_all.find("a",attrs={"class":"btn-icon download-subtitle"})

												if tag_a:
													new_url=ourl_host+tag_a.get("href")
													fname=tag_a.get("href").replace("/subtitle/","")
													the_urls.update({new_url:fname})

												else:
													raise Exception("???")

											elif yurl.path.startswith("/movie-imdb/"):
												tags_a=tags_all.find_all("a")
												added=0
												just_add=True
												for tag in tags_a:
													npath=tag.get("href")
													if npath.startswith("/subtitles/"):
														new_url=ourl_host+npath
														new_value=[new_url,cwd]
														pfff=que.check_value_spc(new_value)
														if not pfff:
															que.add_value(new_value)
															added=added+1

											else:
												raise Exception("URL no válida")

										# Zippyshare
										if _ws_zippy in supported:
											subdomain,file_id=re.match('http[s]?://(\w+)\.zippyshare\.com/v/(\w+)/file.html',ourl).groups()
											alltags=BeautifulSoup(html_dump,"lxml")
											script_tags=alltags.find_all("script")

											selected=None
											for s in script_tags:
												if "document.getElementById(" in s.text:
													if ").href" in s.text:
														if "dlbutton" in s.text:
															selected=s.text
															break

											if not selected:
												raise Exception("checkpoint no. 1")

											page_parser=re.match('\s*document\.getElementById\(\'dlbutton\'\)\.href = "/([p]?d)/\w+/" \+ \((.*?)\) \+ "/(.*)";',selected).groups()
											url_subfolder=page_parser[0].replace('pd','d')
											modulo_string=eval(page_parser[1])
											file_url=page_parser[2]
											fname=urllib.parse.unquote(file_url)
											real_url=f'https://{subdomain}.zippyshare.com/{url_subfolder}/{file_id}/{modulo_string}/{file_url}'
											the_urls.update({real_url:fname})

										print("the_urls =",the_urls)

									except Exception as e:
										f="wget-scrapper-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
										traceback.print_exc(file=open(f,"w"))
										wutt=True
										msg_head1=msg_head1+" #error"
										msg_extra="\n<p>Mientras se obtenía información:\n<p><code>"+str(e)+"</code>"

									else:
										if len(the_urls)>0:
											session.headers.update({"Referer":ourl})

										if len(the_urls)>1:
											msg_extra="\n<p>Descargando múltiples archivos..."

										elif len(the_urls)==1:
											msg_extra="\n<p>Obteniendo longitud del archivo..."

										else:
											msg_extra="\n<p>No hay más que hacer en esta URL"

											# Skip URL downloading, all work is done
											if just_add:
												wutt=True
												msg_head1=msg_head1+" #skip"
												msg_extra=msg_extra+"\n<p>Se agregaron "+str(added)+" URLs a la cola"

										# print("REAL_URL =",real_url)
										# print("FILENAME =",filename)
										# await currmev.reply("<p><code>["+real_url+"</code>,<code>"+filename+"]</code>",parse_mode="html")

									await bot.edit_message(thischat,currmev,msg_head1+msg_head2+msg_extra,parse_mode="html")

							# Unsupported sites
							if not supported:
								if not wutt:
									session.headers.update({"Referer":ourl_host})
									the_urls.update({ourl:None})

							if not wutt:

								if len(the_urls)>1:
									one=False
								else:
									one=True

								# Enter URL dict

								for target_url in the_urls:

									que.attrib["cancel"]=False

									# Inside URL dict
									wutt=False

									if not one:
										msg_single1="<p>#wget"

									smol=False
									if supported:
										if (_ws_tusubtitulo in supported) or (_ws_osubt1 in supported) or (_ws_yifysubs in supported):
											smol=True

									try:
										print("target_url =",target_url)
										print("session.headers =",session.headers)
										async with session.get(target_url,cookies=cookies) as response:
											if not cookies:
												cookies=response.cookies

											httprs=str(response.status)
											# assert httprs.startswith("2")
											print("response.headers =",response.headers)

											total_size_raw=response.headers.get("content-length")
											print("total_size_raw",total_size_raw)
											print("type(total_size_raw)",type(total_size_raw))

											if not total_size_raw:
												if smol:
													total_size_raw="1"

											if not total_size_raw:
												raise Exception("Fallo al obtener el tamaño del archivo")

											if total_size_raw:
												total_size=int(total_size_raw)

											print("Getting filename")
											filename=the_urls.get(target_url)
											print("filename =",filename)
											if not filename:
												if response.content_disposition:
													filename=response.content_disposition.filename

													# Filename Workarounds
													if supported and filename:
														if _ws_tusubtitulo in supported:
															yyy=yarl.URL(target_url)
															if yyy.path.startswith("/original"):
																name_mod=yyy.parts[1]+"-"+yyy.name
															elif yyy.path.startswith("/updated"):
																name_mod=yyy.parts[1]+"-"+yyy.parts[2]+"-"+yyy.name
															else:
																name_mod=str(time.strftime("%Y-%m-%d-%H-%M-%S"))

															filename_new=Path(filename).stem+" "+name_mod+Path(filename).suffix
															filename=filename_new

											if not filename:
												filename=response.request_info.url.name

											# last resource: give it a very fucking random name
											if not filename:
												filename=mkticket(aspath=False)

											if response.headers.get("accept-ranges")=="bytes":
												tries=10

											else:
												tries=1

											if response.headers.get("content-type")=="text/html":
												async with aiofiles.open("FUCK.html","wb") as f:
													shit=await response.content.read(_megabyte)
													await f.write(shit)

									except Exception as e:
										wutt=True
										msg="\n<p>Mientras se obtenían datos:\n<p><code>"+str(e)+"</code>"

										if one:
											msg_head1=msg_head1+" #error"
											msg_extra=msg

										else:
											msg_single1=msg_single1+" #error"
											msg_single2=msg
											msg_single3=""

									else:
										total_size_nice=hr_units(total_size)

										if smol:
											total_size_msg=""

										else:
											total_size_msg="\n<p>Tamaño: <code>"+total_size_nice+"</code>"

										msg="\n<p>Nombre: <code>"+filename+"</code>"+total_size_msg+"\n<p>"
										msgx="\n<p>Comprobando ruta..."

										if one:
											msg_head2=msg_head2+msg
											msg_extra=msgx

										else:
											msg_single2=msg
											msg_single3=msgx

									await asyncio.sleep(0.5)

									if one:
										await bot.edit_message(thischat,currmev,msg_head1+msg_head2+msg_extra,parse_mode="html")

									else:
										thismev=await currmev.reply(msg_single1+msg_single2+msg_single3,parse_mode="html")

									if not wutt:
										job_path=cwd.joinpath(filename)

										if job_path.exists():
											wutt=True
											msg="\n<p><code>"+_msg_error_exists+"</code>"

											if one:
												msg_head1=msg_head1+" #error"
												msg_extra=msg_extra+msg
											else:
												msg_single1=msg_single1+" #error"
												msg_single2=msg_single2+msg


										else:
											msg="\n<p>Salida: <code>"+get_path_show(cwd)+"</code>\n<p>"
											msgx="\n<p>Descargando..."

											if one:
												msg_head2=msg_head2+msg
												msg_extra=msgx
											else:
												msg_single2=msg_single2+msg
												msg_single3=msgx

										if one:
											msgedit=msg_head1+msg_head2+msg_extra
											thismev=currmev

										else:
											msgedit=msg_single1+msg_single2+msg_single3

										await asyncio.sleep(0.5)

										await bot.edit_message(thischat,thismev,msgedit,parse_mode="html")

									if not wutt:

										loop=asyncio.get_event_loop()

										# Entering loop for retrying download

										while tries>0:

											if job_path.exists():

												current_size=os.path.getsize(str(job_path))
												range_value="bytes="+str(current_size)+"-"+str(total_size)
												session.headers.update({"Range":range_value})

											progress_data={"msg":""}

											if total_size>_megabyte:
												await asyncio.sleep(0.5)

												if one:
													msgedit=msg_head1+msg_head2

												else:
													msgedit=msg_single1+msg_single2

												msgedit=msgedit+"\n<p>Reintentos: "+str(tries-1)

												progress=loop.create_task(ntprog(thischat,thismev,job_path,total_size,msgedit,backup=progress_data))

											webdown=loop.create_task(webdownloader(session,target_url,job_path,cookies))

											msg=await task_admin(webdown,que)

											if total_size>_megabyte:
												await asyncio.sleep(0.5)
												if not progress.done():
													print(the_user_id,command,"cancelling progress meter...")
													progress.cancel()
													while True:
														await asyncio.sleep(0.5)
														print(the_user_id,command,"waiting for progress meter to end...")
														if progress.done():
															break

											print("after progress.cancel()...")

											msgx="\n<p><code>"+msg+"</code>"
											if one:
												msg_extra=msgx
												msg_extra=progress_data["msg"]+msg_extra
												msgedit=msg_head1+msg_head2+str(msg_extra)

											else:
												msg_single3=msgx
												msg_single3=progress_data["msg"]+msg_single3
												msgedit=msg_single1+msg_single2+msg_single3

											if que.attrib.get("exc"):
												exc=que.attrib.get("exc")
												if exc=="" or "Timeout" in str(exc):
													tries=tries-1

												else:
													tries=0

												que.attrib.pop("exc")

											else:
												tries=0

											if tries>0:
												msg_retry="\n<p>Reintentando..."

											else:
												msg_retry=""

											await bot.edit_message(thischat,thismev,msgedit+msg_retry,parse_mode="html")
											await asyncio.sleep(0.5)

										# Exiting retry loop

									#if supported==_ws_tusubtitulo:
									#	await asyncio.sleep(0.5)

									# End of URL dict

								# Outside URL dict

								if not one:
									await bot.edit_message(thischat,currmev,msg_head1+" #terminado"+msg_head2,parse_mode="html")
									await asyncio.sleep(0.5)

							que.del_index()
							if que.get_size()==0:
								iterate=False
								await replyto.reply("Ya no queda nada que procesar en la cola")

							else:
								await replyto.reply("Pasando al siguiente elemento en la cola")
								await asyncio.sleep(0.5)

							wutt=False

							if session.headers.get("Range"):
								session.headers.pop("Range")

							if session.headers.get("Host"):
								session.headers.pop("Host")

							del cookies

							the_urls.clear()

							# wget ENDS LOOP

						# LOOP EXIT

						que.attrib["working"]=False

						await session.close()

						del session

						n=session_link[_sd_netwquota]
						if n>0:
							session_link[_sd_netwquota]=n-1

						# wget END

				# Youtube Download 

				if "/ytdl" in command:

					initiate=False
					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					if len(args)==1:
						url_list_raw=args[0]

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						url_list=url_list_raw.split(" ")

						if len(url_list)==0:
							wutt=True
							msg="No se encontraron URLs"

					if not wutt:
						opt="720p"
						le_val=url_list[-1].strip()
						le_idx=len(url_list)-1
						if not (le_val.startswith("https://") or le_val.startswith("http://")):
							if le_val in _ytdlf:
								opt=le_val
								url_list.pop(le_idx)

							else:
								wutt=True
								msg=_msg_error_iarg

					if not wutt:
						que=session_link[_sd_que]["y"]
						cwd=session_link[_sd_cwd]

						if que.get_size()==0:
							initiate=True

						added_at_least_one=False
						print("\n",the_user_id,"url_list:")

						chain=None

						msg_total="<p>#ytdl\n<p>URLs detectadas:\n"
						msg_chunks=[]

						index=0
						for iurl in url_list:
							iurl=iurl.strip()

							if iurl.startswith("https://") or iurl.startswith("http://"):

								if iurl.startswith("http://"):
									iurl.replace("http://","https://")

								yurl=yarl.URL(iurl)
								yurl_host=yurl.host

							else:
								wutt=True

							if not wutt:
								if not ("youtube.com" in yurl_host or "youtu.be" in yurl_host):
									wutt=True

							if not wutt:
								res,wutt=youtube_determ(iurl)
								if res:
									iurl=res

							val=[iurl,cwd,opt]

							if not wutt:
								vexists=que.check_value_spc(val)

								if vexists:
									wutt=True

							if not wutt:
								que.add_value(val)
								prefix="<code>[OK]</code> "
								if not added_at_least_one:
									added_at_least_one=True

							if wutt:
								prefix="<code>[--]</code> "

							msg_tmp=que.show_value(val,prefix)

							index=index+1

							emit=None

							if index==len(url_list):
								emit=msg_total+msg_tmp

							else:
								if len(msg_total+msg_tmp)>4000:
									emit=msg_total
									msg_total="\n<p>..."+msg_tmp

								else:
									msg_total=msg_total+msg_tmp

							if emit:
								msg_chunks.append(emit)

							wutt=False

						for m in msg_chunks:
							if not chain:
								replyme=event

							else:
								replyme=chain

							try:
								c=await replyme.reply(m,parse_mode="html")
								await asyncio.sleep(0.1)

							except Exception as e:
								print(the_user_id,"/ytdl urls list error:",e)

							else:
								chain=c

						del msg_chunks
						del url_list

						if initiate:
							if not added_at_least_one:
								initiate=False

					session_link[_sd_hview]=False

					if not wutt:
						if not initiate:
							return

					if not wutt:
						tjs=session_link[_sd_netwquota]
						if tjs==_sntl:
							wutt=True
							msg=msg_error+_msg_error_tquota

					if wutt:
						await event.reply("<p>#ytdl #error\n<p><code>"+msg+"</code>",parse_mode="html")

					else:
						session_link[_sd_netwquota]=tjs+1
						iterate=True
						que.attrib["working"]=True

						while iterate:
							que.attrib["cancel"]=False
							val=que.get_value()

							url=val[0]
							outdir=val[1]

							if len(val)==3:
								specs=val[2]

							else:
								specs="720p"

							yurl=yarl.URL(url)

							if "youtube.com" in yurl.host:
								pl=True

							else:
								pl=False

							msg_head="<p>#ytdl"
							msg_body="\n<p>"+que.show_value(val)

							me=[command,the_user_id]

							_gq_cpu.append(me)

							await wait_global_queue(me,"INT",event,thischat)

							loop=asyncio.get_event_loop()

							if pl:
								msg_body="\n<p>Lista de reproducción detectada"
								msg_extra=""

								while True:
									try:
										thismev=await chain.reply(msg_head+msg_body+"\n<p>Reuniendo información...",parse_mode="html")
										await asyncio.sleep(1)
									except:
										print("WTF")
									else:
										break

								getter=loop.run_in_executor(None,youtube_getter_from_pl,url,outdir)
								await getter

								asyncio.sleep(1)

								try:
									_gq_cpu.pop(0)
								except Exception as e:
									print(me,"had problems leaving the cpu queue:",e)
								else:
									print(me,"leaves the cpu queue")

								msg_out,msg_errors,plinfo,url_list=getter.result()

								try:
									if len(msg_errors)>0:
										errorfile="errors-ytdl-playlist-"+the_user_id+"-"+time.strftime("%Y-%m-%d-%H-%M-%S")+".log"
										async with aiofiles.open(errorfile,"w") as f:
											await f.write(msg_errors)

										await bot.send_file(thischat,file=errorfile)
										await asyncio.sleep(0.5)

								except Exception as e:
									f="ytdl-pl-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
									traceback.print_exc(file=open(f,"w"))
									pass

								if len(url_list)==0:
									wutt=True
									msg_head=msg_head+" #error"
									msg_body=msg_body+msg_out

								else:

									title=plinfo[0]
									title=title.replace("*","-")
									title=title.replace("|","-")
									title=title.replace("/","-")
									title=title.replace("\\","-")

									title=title+" "+plinfo[1]

									msg_total=msg_head+"\n<p>"+plinfo[0]+"\n<p>URLs detectadas:"
									msg_buffer=""
									msg_chunks=[]

									subchain=None
									outdir_pl=outdir.joinpath(title)

									if not outdir_pl.exists():
										outdir_pl.mkdir()

									index=0
									session_link[_sd_hview]=True

									for vurl in url_list:
										nvalue=[vurl,outdir_pl,specs]

										wutt=que.check_value_spc(nvalue)

										if not wutt:
											que.add_value(nvalue)
											prefix="<code>[OK]</code> "

										if wutt:
											prefix="<code>[--]</code> "

										msg_buffer=que.show_value(nvalue,prefix)

										index=index+1

										msg_add=None

										if index==len(url_list):
											msg_add=msg_total+msg_buffer

										else:
											if len(msg_total+msg_buffer)>4000:
												msg_add=msg_total
												msg_total="<p>..."+msg_buffer

											else:
												msg_total=msg_total+msg_buffer

										if msg_add:
											msg_chunks.append(msg_add)

									session_link[_sd_hview]=True

									for m in msg_chunks:
										if not subchain:
											replyme=thismev

										else:
											replyme=subchain

										try:
											c=await replyme.reply(m,parse_mode="html")
											await asyncio.sleep(0.1)

										except Exception as e:
											print(the_user_id,"/ytdl urls list error:",e)

										else:
											subchain=c

									del url_list
									del msg_chunks

									wutt=False
									session_link[_sd_hview]=False

									msg_head=msg_head+" #ok"
									msg_extra=msg_extra+msg_out

								wait=True
								while wait:
									try:
										await bot.edit_message(thischat,thismev,msg_head+msg_body+msg_extra,parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

							if not pl:

								await queue_brake_checker(que,chain)

								if specs in _ytdlf_vres:
									msg_extra="\n<p>Buscando video en "+specs+"..."

								else:
									# exa
									msg_extra="\n<p>Buscando audio..."

								wait=True
								while wait:
									try:
										thismev=await chain.reply(msg_head+msg_body+"\n<p>Reuniendo información...",parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

								getter=loop.run_in_executor(None,youtube_getter,url,specs)
								await getter
								getter_result=getter.result()

								await asyncio.sleep(1)

								try:
									_gq_cpu.pop(0)
								except Exception as e:
									print(me,"had problems leaving the cpu queue:",e)
								else:
									print(me,"leaves the cpu queue")

								print("getter_result =",getter_result)

								if getter_result:
									if type(getter_result) is str:
										wutt=True
										msg=getter_result

									else:
										msg_extra="\n<p>Agarrando datos..."

								else:
									wutt=True
									msg="No se encontró nada"

								if wutt:
									msg_head=msg_head+" #error"
									msg_extra="\n<p>Mientras se reunía información:\n<p><code>"+msg+"</code>"

								wait=True
								while wait:
									try:
										await bot.edit_message(thischat,thismev,msg_head+msg_body+msg_extra,parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

								if not wutt:
									await asyncio.sleep(0.5)

									title,big_dump=getter_result

									title=title.replace("*","-")
									title=title.replace("|","-")
									title=title.replace("/","-")
									title=title.replace("\\","-")

									suffix="."+big_dump["ext"]
									filename=title+suffix

									filepath=outdir.joinpath(filename)

									if filepath.exists():
										wutt=True
										wait=True
										while wait:
											try:
												await bot.edit_message(thischat,thismev,msg_head+" #error"+msg_body+"\n<p><code>"+_msg_error_exists+"<code>",parse_mode="html")
											except:
												await asyncio.sleep(0.5)
											else:
												wait=False

								if not wutt:

									ua=big_dump["http_headers"]

									print("ua =",ua)
									target_url=big_dump["url"]
									print("target_url =",target_url)

									total_size=None

									try:
										total_size=big_dump["filesize"]
										if not total_size:
											raise Exception("NO SIZE")

									except:
										print("pffffffffffffff")

									session=aiohttp.ClientSession(headers=ua,timeout=_tout)

									if not total_size:
										try:
											async with session.get(target_url) as response:
												total_size_raw=str(response.headers.get("content-length"))

											if total_size_raw:
												total_size=int(total_size_raw)

											else:
												raise Exception("No se encontró la longitud")

										except Exception as e:
											wutt=True
											msg=str(e)

									if total_size:
										if specs in _ytdlf_vres:
											found=big_dump["format_note"]

											msg_vres="\n<p>Resolución "+found

											if not (specs in found):
												msg_vres=msg_vres+" (inferior a lo solicitado: "+specs+")"

										else:
											msg_vres=""

										msg_body=msg_body+"\n<p>Nombre: <code>"+filename+"</code>\n<p>Tamaño: <code>"+hr_units(total_size)+"</code>"+msg_vres
										msg_extra="\n<p>Descargando..."

									else:
										msg_head=msg_head+" #error"
										msg_extra="\n<p><code>"+msg+"</code>"

									wait=True
									while wait:
										try:
											await bot.edit_message(thischat,thismev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											wait=False

								if not wutt:
									await asyncio.sleep(0.5)
									progress_data={"msg":""}
									if total_size>_megabyte:
										progress=loop.create_task(ntprog(thischat,thismev,filepath,total_size,msg_head+msg_body,backup=progress_data))

									aioytdl=loop.create_task(webdownloader(session,target_url,filepath))

									msg=await task_admin(aioytdl,que)

									if total_size>_megabyte:
										await asyncio.sleep(0.5)
										if not progress.done():
											print(the_user_id,command,"cancelling progress meter...")
											progress.cancel()
											while True:
												await asyncio.sleep(0.5)
												print(the_user_id,command,"waiting for progress meter to end...")
												if progress.done():
													break

									msg_extra=progress_data["msg"]+"\n<p><code>"+msg+"</code>"

									
									while wait:
										try:
											await bot.edit_message(thischat,thismev,msg_head+msg_body+msg_extra,parse_mode="html")
										except:
											await asyncio.sleep(0.5)
										else:
											wait=False

									await session.close()

									del session
									del big_dump

							wutt=False

							que.del_index()
							if que.get_size()==0:
								iterate=False
								await chain.reply("Ya no queda nada que procesar en la cola")

							else:
								await chain.reply("Pasando al siguiente elemento en la cola")
								await asyncio.sleep(0.5)

						que.attrib["working"]=False
						n=session_link[_sd_netwquota]
						if n>0:
							session_link[_sd_netwquota]=n-1


				# QUEUE COMMANDS

				# Cancellation
				if "/cancel" in command:

					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					if len(args)==1:
						sq=args[0]
						try:
							assert sq in session_link[_sd_que]
						except:
							wutt=True
							msg=_msg_error_iarg
						else:
							que=session_link[_sd_que][sq]

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						working=que.attrib["working"]
						if not working:
							wutt=True
							msg="La cola seleccionada no está en marcha:\n"+que.name

					if wutt:
						await event.reply("<p>#cancel #error\n<p></code>"+msg+"</code>",parse_mode="html")

					else:
						cancel=que.attrib["cancel"]
						if cancel:
							msg="La órden de cancelación ya existe en:\n"+que.name

						else:
							que.attrib["cancel"]=True
							msg="Orden de cancelación enviada a:\n"+que.name

						await event.reply("<p>#cancel #ok\n<p>"+msg,parse_mode="html")

					session_link[_sd_hview]=False

				# Queue Brake
				if "/brake" in command:

					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					if len(args)==1:
						sq=args[0]
						try:
							assert sq in session_link[_sd_que]
						except:
							wutt=True
							msg=_msg_error_iarg
						else:
							que=session_link[_sd_que][sq]

					else:
						wutt=True
						msg=_msg_error_wargs

					if wutt:
						await event.reply("<p>#brake #error\n<p></code>"+msg+"</code>",parse_mode="html")

					else:
						status_brake=que.attrib["brake"]
						if status_brake:
							que.attrib["brake"]=False
							msg="Se ha liberado el freno de la cola:\n"+que.name

						else:
							que.attrib["brake"]=True
							msg="Se ha frenado la cola: "+que.name

						await event.reply("<p>#brake #ok\n<p>"+msg,parse_mode="html")

					session_link[_sd_hview]=False

				# Queue Viewer and admin
				if "/que" in command:

					viewing=session_link[_sd_hview]
					if viewing:
						return

					else:
						session_link[_sd_hview]=True

					# 2 max args only
					if len(args)>2:
						wutt=True
						msg=_msg_error_wargs

					# arg 1: get all or single
					if not wutt:
						if len(args)==0:
							get_all=True
							# get all queues
							qlist=[]
							for q in session_link[_sd_que].values():
								qlist=qlist+[q]

						else:
							get_all=False
							#show single queue
							sq=args[0]

							#print("session_link[_sd_que]",session_link[_sd_que])

							try:
								assert sq in session_link[_sd_que]
							except:
								wutt=True
								msg=_msg_error_iarg
							else:
								#print(session_link[_sd_que][sq])
								qlist=[session_link[_sd_que][sq]]

					# arg 2: wether to delete or not
					if not wutt:
						if len(args)==2:
							the_arg=args[1]
							try:
								target=int(the_arg)
							except:
								target=-1
								ranged=True
							else:
								if target>0:
									ranged=False

								else:
									ranged=True
									the_arg="0-0"

							if ranged:
								target_range=get_args_range(the_arg)
								if not target_range:
									wutt=True
									msg=_msg_error_iarg

							if not wutt:
								removal=True

						else:
							ranged=False
							removal=False

					if wutt:
						await event.reply("<p>#que error\n"+msg,parse_mode="html")

					else:
						if not ranged:
							if not get_all:
								que=session_link[_sd_que][sq]
								qlist=[que]

						chained=None
						# Show queue list
						for que in qlist:
							#print("Queue name:",que.name)
							#print("Queue contents:",que.queue)
							pieces=que.get_chunked()
							#print("pieces =",pieces)
							for p in pieces:
								if not chained:
									rpl=event
								else:
									rpl=chained

								try:
									chained=await rpl.reply(p,parse_mode="html")
								except Exception as e:
									print("user",the_user_id,"just shit itself while showing queue, this happened →",e)
								finally:
									await asyncio.sleep(0.2)

						# do something depending on the number of queues
						if get_all:
							# message indicating the code of the queues
							if not chained:
								rpl=event
							else:
								rpl=chained

							msg="<p>Colas\n<p>"
							qdict=session_link[_sd_que]
							for k in qdict:
								que=qdict.get(k)
								msg=msg+"\n<p><code>"+k+"</code> - "+que.name

							await rpl.reply(msg,parse_mode="html")

						else:
							# removal of a value
							if removal:
								if not chained:
									rpl=event
								else:
									rpl=chained

								if ranged:
									#print("DELETION")
									#ranged removal
									deleted,offset=que.del_index_range(target_range)

									#print("deleted")
									#for d in deleted:
									#	print(d)

									if len(deleted)==0:
										try:
											await rpl.reply("No hay nada que borrar")
										except Exception as e:
											print(the_user_id,"in /que, had an error while saying \"there's nothing to delete\", this happened →",e)

									else:

										if target==-1:
											t="Borrados de la cola:"

										else:
											t="Borrando todos menos el primero:"

										parts=que.get_chunked(vlist=deleted,title=t,offset=offset)
										for p in parts:
											if not chained:
												rpl=event
											else:
												rpl=chained

											try:
												chained=await rpl.reply(p,parse_mode="html")
											except Exception as e:
												print("user",the_user_id,"just shit itself while showing deleted elements, this happened →",e)
											finally:
												await asyncio.sleep(0.1)

								else:
									#single removal
									val=que.get_value(target)
									if not val:
										msg="<p>No hay nada que borrar"

									else:
										pfx=str(target)+"|"
										val_show=que.show_value(val,prefix=pfx)
										que.del_index(target)
										msg="<p>Borrado de la cola:\n<p>"+val_show

									await rpl.reply(msg,parse_mode="html")

					session_link[_sd_hview]=False

				# OTHER CUSTOM FILE COMMANDS

				# FFmpeg cloud transcoder

				if "/ffmpeg" in command:

					if len(args)>4 or len(args)==0:
						wutt=True
						msg=_msg_error_wargs

					# 1rst arg

					if not wutt:

						job=arg[0]
						if job=="conf" and len(args)<5:
							pass

						elif job=="exec" and len(args)==1:
							pass

						elif job=="cancel" and len(args)==1:
							pass

						else:
							wutt=True
							msg=_msg_error_iarg

					# Jobs

					if not wutt:
						if job=="conf":
							pass

						if job=="exec":
							pass

						if job=="cancel":
							pass

					# DESSIGN

					# View all configs
					# /ffmpeg conf
					#
					# Select a config
					# /ffmpeg conf CONF_INDEX
					#
					# View config on items
					# /ffmpeg conf CONF_INDEX ITEMS
					#
					# Set config on items
					# /ffmpeg conf CONF_INDEX ITEMS set
					#
					# Modifies config
					# /ffmpeg conf mod
					#
					# Deletes config
					# /ffmpeg conf clear
					#
					# Upload to free server
					# /ffmpeg exec
					#
					# Cancel job
					# /ffmpeg cancel






					session=aiohttp.ClientSession(headers={"User-Agent":"BoC-IF"})




					# Step 1: Check which server is NOT busy
					# GET http://server.net/?
					# TODO: Recieve answer: WTFAY (Who The Fuck Are You)

					# Step 2: Upload files to THAT server
					# ffmpeg/upload/*
					# for each uploaded file, get notified with a 200 or a 4xx in case of failure (retry)

					# Step 3: Notify the server to start working on the files
					# GET http://server.net/?

					# Step 4: Wait for the server to send a GET request to us

					await session.close()

				# Fernet-spec Encrypter/Decrypter:

				if "/crypt" in command:

					sharing=session_link[_sd_shared]
					print("sharing =",sharing)

					if len(sharing)>0:
						await event.reply("Desactive a /share mientras trabaje con el cifrado")
						return

					hproc=session_link[_sd_hproc]
					if len(hproc)>0:
						return

					else:
						session_link[_sd_hproc]=command

					fkey=session_link[_sd_fkey]

					if len(args)<3:

						if len(args)>0:

							if args[0]=="c":
								job=_kfscrypt_mkey

							elif args[0]=="e":
								job=_kfscrypt_encr

							elif args[0]=="d":
								job=_kfscrypt_decr

							else:
								wutt=True
								msg=_msg_error_iarg

						else:
							job=None

					else:
						wutt=True
						msg=_msg_error_wargs

					if wutt:
						await event.reply("<p>#crypt #error\n"+msg,parse_mode="html")

					if not wutt:

						# Show download links for KFSCrypt

						if not job:

							if len(fkey)>0:
								keyhere="<code>"+str(fkey)+"</code>"

							else:
								keyhere="Ninguna"

							bin_win32="https://github.com/carlosagh96/cuban-python-scripts/raw/main/multi/kfscrypt/kfscrypt-windows-i386.tar"
							bin_lin64="https://github.com/carlosagh96/cuban-python-scripts/raw/main/multi/kfscrypt/kfscrypt-linux-amd64.tar"

							await event.reply("<p><strong>Utilidad de cifrado de archivos</strong>\n<p>\n<p>Clave guardada:\n<p>"+keyhere+"\n<p>\n<p>KFSCrypt:\n<p><a href="+bin_win32+">Descargar para Windows (32 bits)</a>\n<p><a href="+bin_lin64+">Descargar para Linux (64 bits)</a>\n",parse_mode="html")

							session_link[_sd_hproc]=""

							return

						loop=asyncio.get_event_loop()

						me=[command,the_user_id]

						_gq_cpu.append(me)

						await wait_global_queue(me,"INT",event,thischat)

						# Make Fernet key,save it and upload it as a file
						if _kfscrypt_mkey in job:

							if len(fkey)>0:
								if len(args)>1:
									try:
										assert args[1]=="f"

									except:
										wutt=True
										msg=_msg_error_iarg

								else:
									wutt=True
									msg="Ya existe una clave, ejecute con el argumento extra 'f' para forzar"

							if not wutt:
								mkey=loop.run_in_executor(None,kfscrypt,the_user_id,job)
								await mkey
								mkey_result=mkey.result()

								session_link[_sd_fkey]=mkey_result

								ticket=mkticket(the_user_id)
								keyfile=ticket+".fernet.key"

								print("keyfile =",keyfile)

								try:
									async with aiofiles.open(keyfile,"wb") as k:
										await k.write(mkey_result)

									await bot.send_file(thischat,file=keyfile,force_document=True)

								except Exception as e:
									wutt=True
									msg="Mientras se subía el archivo con la clave\n<p><code>"+str(e)+"</code>"

								else:
									Path(keyfile).unlink()

								session_link[_sd_hproc]=""

								try:
									_gq_cpu.pop(0)
								except Exception as e:
									pass

								return

						# Encrypt or Decrypt
						if (_kfscrypt_decr in job) or (_kfscrypt_encr in job):

							cwd=session_link[_sd_cwd]

							tgtpath=None

							if len(fkey)==0:
								wutt=True
								msg="No hay una clave presente"

							if len(args)>2:
								wutt=True
								msg=_msg_error_wargs

							if not wutt:
								stype=_stype_s
								if len(args)==1:
									tgtpath=cwd

								else:
									try:
										fse_index=int(args[1])
										assert fse_index>-1

									except:
										stype=_stype_r

									if _stype_s in stype:
										tgtpath=await aio_get_fsepath(cwd,fse_index)
										if not tgtpath:
											wutt=True
											msg=_msg_error_notfound

									if _stype_r in stype:
										range_select=get_args_range(args[1])
										if not range_select:
											stype=_stype_f

									if _stype_f in stype:
										free_select=get_args_free(args[1])
										if not free_select:
											wutt=True
											msg=_msg_error_iarg

							if not wutt:

								pathcont=[]

								if _stype_s in stype:
									if tgtpath.is_dir():
										pathcont=await aio_get_dircont(tgtpath,fsetype=0)

									else:
										pathcont=[tgtpath]

								else:
									if _stype_r in stype:
										pathcont_raw=await aio_get_dircont_ranged(cwd,range_select)

									if _stype_f in stype:
										pathcont_raw=await aio_get_dircont_free(cwd,free_select)

									for path in pathcont_raw:
										if path.is_file():
											pathcont.append(path)

								if len(pathcont)==0:
									wutt=True
									msg=_msg_error_notfound

							if wutt:
								await event.reply("<p>#crypt #error\n"+msg,parse_mode="html")

							else:
								if job==_kfscrypt_encr:
									j="#crypt #cifrado"

								if job==_kfscrypt_decr:
									j="#crypt #descifrado"

								data_link={"e":"","p":"","f":"","t":0,"r":0,"w":0}
								repev=await event.reply(j)

								progress=loop.create_task(ntprog_kfscrypt(thischat,repev,"<p>"+j+"\n",data_link))

								cryptjob=loop.run_in_executor(None,kfscrypt,the_user_id,job,cwd,fkey,pathcont,data_link)
								await cryptjob
								mlog=cryptjob.result()

								chained=None
								for m in mlog:
									if not chained:
										rt=event

									else:
										rt=chained

									chained=await rt.reply(m,parse_mode="html")
									await asyncio.sleep(0.1)

								await asyncio.sleep(1)

								progress.cancel()
								while True:
									await asyncio.sleep(0.5)
									if progress.done():
										break

						try:
							_gq_cpu.pop(0)
						except Exception as e:
							pass

					session_link[_sd_hproc]=""

				# Archive extractor
				if "/ext" in command:

					# NOTES

					# tar -xf PATH/file.tar.gz -C PATH/

					# 7z x -o"PATH" "PATH/file.7z"
					# 7z x -o"PATH" "PATH/file.7z.001"

					heavyproc=session_link[_sd_hproc]
					if len(heavyproc)>0:
						await event.reply("Espere a que termine "+heavyproc)
						return

					else:
						session_link[_sd_hproc]=command

					msg_error="#ext #error"
					if len(args)==0 or len(args)>2:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						try:
							selected=int(args[0])
							assert selected>-1

						except:
							wutt=True
							msg=_msg_error_iarg

					if not wutt:
						cwd=session_link[_sd_cwd]
						filepath=await aio_get_fsepath(cwd,selected,fsetype=0)
						if not filepath:
							wutt=True
							msg=_msg_error_notfound

					if not wutt:
						if len(args)==2:
							password=args[1]
						else:
							password=""

					if wutt:
						await event.reply("#ext #error\n"+msg)

					if not wutt:

						me=[command,the_user_id]

						_gq_cpu.append(me)
						await wait_global_queue(me,"INT",event,thischat)

						_gq_sub.append(me)
						await wait_global_queue(me,"SUB",event,thischat)

						while True:
							try:
								stdev=await event.reply("#ext\nTrabajando...")
							except:
								await asyncio.sleep(0.5)
							else:
								break

						shell_in="./ext.sh \""+str(cwd)+"\" \""+str(filepath)+"\" \""+str(password)+"\""
						print(the_user_id,"executes:\n$",shell_in)
						# shell_in be like → $ ./ext "PATH/" "PATH/FILE" "PASSWORD"
						output,errors=await shell_run(shell_in)

						try:
							_gq_cpu.pop(0)
							_gq_sub.pop(0)
						except:
							pass

						ticket=mkticket(the_user_id,False)

						asyncio.sleep(0.5)
						if len(output)>4000:
							outfile="ext-out-"+ticket+".log"
							async with aiofiles.open(outfile,"w") as out:
								await out.write(output)

							while True:
								try:
									await bot.send_file(thischat,file=outfile)
								except:
									await asyncio.sleep(0.5)
								else:
									break

						else:
							if len(output)>0:
								while True:
									try:
										await bot.edit_message(thischat,stdev,"<p>#ext\n<p>SAL.EST.\n<p><code>"+output+"</code>",parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										break

						asyncio.sleep(0.5)
						if len(errors)>4000:
							errfile="ext-err-"+ticket+".log"
							async with aiofiles.open(errfile,"w") as err:
								await err.write(errors)

							while True:
								try:
									await bot.send_file(thischat,file=errfile)
								except:
									await asyncio.sleep(0.5)
								else:
									break

						else:
							if len(errors)>0:
								while True:
									try:
										await stdev.reply("<p>#ext\n<p>SAL.ERR.\n<p><code>"+errors+"</code>",parse_mode="html")
									except:
										await asyncio.sleep(0.5)
									else:
										break

					session_link[_sd_hproc]=""

				# unfinished ?
				if "/join" in command:
					await event.reply("EN DESARROLLO (TODAVIA)")
					return

					hproc=session_link[_sd_hproc]
					if len(hproc)>0:
						await event.reply("Espere a que termine "+hproc[1:])
						return

					else:
						session_link[_sd_hproc]=command

					if len(args)==1:
						ranged=False
						try:
							index=int(args[0])
							assert fse_index>-1

						except:
							ranged=True

						if ranged:
							range_select=get_args_range(args[0])
							if not range_select:
								wutt=True
								msg=_msg_error_iarg

					else:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						cwd=session_link[_sd_cwd]
						if ranged:
							selfpaths_raw=await aio_get_dircont_ranged(cwd,range_select)
							if not selfpaths:
								wutt=True
								msg=_msg_error_notfound

							selfpaths=[]
							for fse in selfpaths_raw:
								if fse.is_file():
									selfpaths=selfpaths+[fse]

							del selfpaths_raw

						else:
							dirpath=await aio_get_fsepath(cwd,index,fsetype=1)
							if not dirpath:
								wutt=True
								msg=_msg_error_notfound

							if not wutt:
								selfpaths=await aio_get_dircont(dirpath,fsetype=0)

					if not wutt:
						if len(selfpaths)==0:
							wutt=True
							msg=_msg_error_empty

					if not wutt:
						total_size=0
						for fse in selfpaths:
							total_size=toal_size+os.path.getsize(str(fse))

						ticket=mkticket(aspath=False)
						firstone=selfpaths[0]
						firstone.parent

						if total_size>_megabyte:
							catmsgev=await event.reply("Concatenando...")

							loop=asyncio.get_event_loop()
							# TODO: UNFINISHED
							progress=loop.create_task(ntprog(thischat,catmsgev,))

					session_link[_sd_hproc]=""

				# Mediainfo

				if "/mediainfo" in command:

					if len(args)==0:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						try:
							fse_index=int(args[0])
							assert fse_index>-1

						except:
							wutt=True
							msg=_msg_error_iarg

					if not wutt:
						cwd=session_link[_sd_cwd]
						fse=await aio_get_fsepath(cwd,fse_index)
						if not fse:
							wutt=True
							msg=_msg_error_notfound

					if not wutt:
						if not fse.is_file():
							wutt=True
							msg=_msg_error_nonfile

					if wutt:
						await event.reply("#mediainfo #error\n"+msg)


					else:
						me=[command,the_user_id]

						_gq_sub.append(me)

						await wait_global_queue(me,"SUB",event,thischat)

						outfile=cwd.joinpath(fse.name+".txt")
						run_this="mediainfo \""+str(fse)+"\" > \""+str(outfile)+"\""
						print(the_user_id,"is running this command\n\t$",run_this)
						shell_output,shell_errors=await shell_run(run_this)
						print(shell_output)

						try:
							_gq_sub.pop(0)
						except:
							pass

						msg="Los resultados están en el archivo\n<p><code>"+get_path_show(outfile)+"</code>"

						try:
							await bot.send_file(thischat,file=str(outfile))

						except Exception as e:
							msg=msg+"\n<p>No se pudo subir el archivo a Telegram:\n<p><code>"+str(e)+"</code>"
							msg_head="<p>#mediainfo #error\n"

						else:
							msg_head="<p>#mediainfo #ok\n"

						msg_text=msg_head+msg

						await event.reply(msg_text,parse_mode="html")

				# Set toDus token
				#if "/tt" in command:
				#	msg_error="Error\n"
				#	if len(args)==1:
				#		session_link[_sd_todus_token]=args[0]
				#		msg="Se ha guardado el mensaje como token de toDus"
				#
				#	else:
				#		msg=msg_error+_msg_error_wargs
				#
				#	await event.reply(msg)

				# Other
				if "/esubs" in command:
					the_host="https://txt.erai-raws.org/"
					if len(args)==0 or len(args)>2:
						wutt=True
						msg=_msg_error_warg

					if not wutt:
						input_url=args[0]
						try:
							assert input_url.startswith(the_host+"?dir=Sub")
						except:
							msg=_msg_error_iarg

					if not wutt:
						if len(args)==1:
							params=None

						if len(args)==2:
							params_raw=args[1]
							params=params_raw.split(" ")

					if wutt:
						await event.reply(msg)

					if not wutt:
						ua=get_user_agent()

						session=aiohttp.ClientSession()
						session.headers.update({"User-Agent":ua,"Referer":the_host})

						list_all=[input_url]
						list_ready=[]

						msg_base="Dándole 😏😏😏"
						msg_mid=""
						msg_extra=""

						wait=True
						while wait:
							try:
								chain=await event.reply(msg_base)
							except:
								await asyncio.sleep(0.5)
							else:
								wait=False

						time_mark=time.time()

						index=0
						nextone=True
						purl=None
						cookies=None
						while nextone:
							curl=list_all[index]
							yurl=yarl.URL(curl)

							print("curl",index,"of",len(list_all)-1," =",yurl.path)

							if len(yurl.path)>1:
								print("\tadding to list_ready...")

								add=False
								if not params:
									add=True

								if params:
									if "spa" in params:
										if yurl.name.endswith("spa.ass") or yurl.name.endswith("spa.ssa"):
											add=True
									if "eng" in params:
										if yurl.name.endswith("eng.ass") or yurl.name.endswith("eng.ssa"):
											add=True
									if "7z" in params:
										if yurl.name.endswith(".7z"):
											add=True

								if add:
									print("...added")
									list_ready.append(curl)

							else:
								print("\tobtaining URLs...")
								await asyncio.sleep(0.5)
								if index==1:
									session.headers.update({"Referer":input_url})

								try:
									async with session.get(curl,cookies=cookies) as response:
										cookies=response.cookies
										# print(the_user_id,command,"response.headers =",response.headers)
										html_dump=await response.text()

									tags_all=BeautifulSoup(html_dump,"lxml")
									tags_a=tags_all.find("ul",id="file-list").find_all("li")[1].find_all("a")
									for a in tags_a:
										path=a.get("href")
										nurl=the_host+path
										print("\t",path)
										list_all.append(nurl)
								except Exception as e:
									print(the_user_id,command,"at scrape loop:",e)

							index_max=len(list_all)-1
							time_now=time.time()
							if time_now-time_mark>1 or index==index_max:
								print("!")
								msg_mid="Enlaces procesados "+str(index)+" de "+str(index_max)
								try:
									await bot.edit_message(thischat,chain,msg_base+"\n"+msg_mid)
								except Exception as e:
									print("pFFFF",e)
								else:
									time_mark=time_now

							index=index+1
							if index==len(list_all):
								nextone=False

						await session.close()

						del list_all
						del cookies
						del session

						print(the_user_id,command,"Displaying...")

						if len(list_ready)==0:
							wutt=True
							msg_extra="No hay URLs"

						if len(list_ready)>0:
							msg_extra="Mostrando URLs encontradas"

						wait=True
						while wait:
							try:
								await bot.edit_message(thischat,chain,msg_mid+"\n"+msg_extra)
							except:
								await asyncio.sleep(0.5)
							else:
								wait=False

						if wutt:
							return

						if not wutt:
							msg_chunks=[]
							msg_total=""
							index=0
							for url in list_ready:
								msg_this=url

								index=index+1
								msg_add=None
								if index==len(list_ready):
									msg_add=msg_total+msg_this

								else:
									msg_this=msg_this+" "
									if len(msg_total+msg_this)>4000:
										msg_add=msg_total
										msg_total=msg_this

									else:
										msg_total=msg_total+msg_this

								if msg_add:
									msg_chunks.append(msg_add)

							for m in msg_chunks:
								await asyncio.sleep(0.1)
								wait=True
								while wait:
									try:
										if not chain:
											mev=event
										else:
											mev=chain

										chain=await mev.reply(m)
									except:
										await asyncio.sleep(0.5)
									else:
										wait=False

				# VIP Users List
				if "/vipinfo" in command:
					return

					v=session_link[_sd_hview]
					if v:
						return
					else:
						session_link[_sd_hview]=True

					msg="<p><strong>Usuarios VIP</strong>\n<p>"
					editme=await event.reply("Un momento...")
					failed=[]
					for uid in _viplist:
						# msg=msg+"\n<p><a href=tg://user?id="+uid+">"+uid+"</a>"
						keepsearching=True
						while keepsearching:
							try:
								full_info = await bot.get_entity(int(uid))

							except TimeoutError:
								if retry:
									retry=False

								else:
									uname=str(uid)+" (Fallo de búsqueda 2 veces)"
									keepsearching=False
									failed=failed+[uname]

							except Exception as e:
								print("Fallo de búsqueda",e)
								uname=uid
								keepsearching=False
								failed=failed+[uname]

							else:
								uname=""
								uname=full_info.first_name
								if not full_info.last_name==None:
									uname=uname+" "+full_info.last_name

								keepsearching=False

								print("uinfo =",uname)

								msg=msg+"\n<p><a href=tg://user?id="+uid+">Usuario</a> → "+str(uname)

						try:
							await bot.edit_message(thischat,editme,msg,parse_mode="html")

						except:
							print("pfffff")

					if len(failed)>0:
						msg=msg+"\n<p>\n<p>Fallos de búsqueda\n<p>"
						for f in failed:
							msg=msg+"\n<p><a href=tg://user?id="+f+">"+f+"</a>"

					msg=msg+"\n<p>\n<p>⚠️ Respete la privacidad de otros, no escriba sin avisar a personas que no conozca."

					await bot.edit_message(thischat,editme,msg,parse_mode="html")

					session_link[_sd_hview]=False

				# 7Zip archiver

				if "/seven" in command:
					hproc=session_link[_sd_hproc]
					if len(hproc)>0:
						return

					else:
						session_link[_sd_hproc]=command

					hashtag="#seven"

					if len(args)==0 or len(args)>3:
						wutt=True
						msg=_msg_error_wargs

					if not wutt:
						try:
							target=int(args[0])
							assert target>-1

						except:
							wutt=True
							msg=_msg_error_iarg

					if not wutt:
						partsize=0
						if len(args)==2 or len(args)>2:
							try:
								partsize=int(args[1])
								assert partsize>-1

							except:
								wutt=True
								msg=_msg_error_iarg

					if not wutt:
						if len(args)==3:
							password=args[2]

						else:
							password=None

						cwd=session_link[_sd_cwd]
						tgtpath=await aio_get_fsepath(cwd,target)
						if not tgtpath:
							wutt=True
							msg=_msg_error_notfound

					if not wutt:
						if partsize>0:
							size=0
							try:
								if tgtpath.is_dir():
									for fse in list(tgtpath.rglob("*")):
										if fse.is_file():
											size=size+os.path.getsize(str(fse))
								else:
									size=os.path.getsize(str(tgtpath))

							except Exception as e:
								print("Error at OS Walking before archiving:\n",str(e))
								wutt=True
								msg=str(e)

							else:
								tsize=float(size/_megabyte)
								tsize_int=int(tsize)
								if tsize_int==0:
									tsize_int=tsize_int+1

								if partsize>tsize_int:
									partsize=0

					if wutt:
						wait=True
						while wait:
							try:
								await event.reply("<p>"+hashtag+" #error\n<p><code>"+msg+"</code>",parse_mode="html")
							except:
								await asyncio.sleep(0.5)
							else:
								wait=False

					else:

						if partsize==0:
							msg=hashtag+"\nArchivando..."

						else:
							msg="#split\nArchivando en partes de "+str(partsize)+" MB..."

						me=[command,the_user_id]

						_gq_cpu.append(me)

						await wait_global_queue(me,"INT",event,thischat)

						wait=True
						while wait:
							try:
								this=await event.reply(msg)
							except:
								await asyncio.sleep(0.5)
							else:
								wait=False

						loop=asyncio.get_event_loop()
						arcjob=loop.run_in_executor(None,sevenzipper,tgtpath,partsize,password)
						await arcjob
						arcjobr=arcjob.result()

						await asyncio.sleep(0.5)

						try:
							_gq_cpu.pop(0)
						except Exception as e:
							pass

						try:
							if len(arcjobr)>0:
								wutt=True

							if wutt:
								msg="<p>"+hashtag+" #error\n<p><code>"+arcjobr+"</code>"

							else:
								msg="<p>"+hashtag+" #ok\n<p>Archivado correctamente\n<p><code>"+get_path_show(tgtpath)+"</code>"

							await bot.edit_message(thischat,this,msg,parse_mode="html")

						except:
							f="cmd_seven-"+str(time.strftime("%Y-%m-%d-%H-%M-%S"))+".log"
							traceback.print_exc(file=open(f,"w"))
							await asyncio.sleep(1)
							await bot.edit_message(thischat,this,"Terminado...",parse_mode="html")

					session_link[_sd_hproc]=""

################################################################################
# AIOHTTP Server Event Handlers
################################################################################

# Handler for the home page
async def http_handler_home(request):
	text = await request.text()
	print(request.remote,"asks for the homepage")
	info=await bot.get_me()
	
	htmldump=_piece_html_start+_piece_html_title+"\n<style>"+_piece_css_default+"</style>\n</head>\n<body style='text-align:center;'>\n<p><h1>Bienvenid@</h1>\n<p><h3>Este es el sitio web asociado al bot <a href=https://t.me/"+info.username+">"+info.first_name+"</a>\n<p>¿Qué se puede hacer aquí?\n<p>Desde aquí puede ver y descargar archivos compartidos por otros usuarios\n<p>También puede ver las noticias y avisos emitidos por el administrador</h3>\n<p><h2><a href=/fse>Ver los archivos</a></h2>\n<p><h2><a href=/news>Ver las noticias</a></h2>"+_piece_html_end
	return web.Response(body=htmldump,content_type="text/html",charset="utf-8")
"""
# handler for communicating with the FFmpeg Server
async def http_handler_ffmpeg(request):
	yurl=yarl.URL(request.url)
	sid=int(yurl.query.get("sid"))

	# Give the amount of files
	if sid==0:
		msg=len(list(_path_ffmpeg.glob("*")))
		return web.Response(body=htmldump,content_type="text/html",charset="utf-8")

	# requested a file from this bot
	if sid==1:
		fid=int(yurl.query.get("fid"))
		the_fse=await aio_get_fsepath(_path_ffmpeg,sid)

		the_file_name=the_fse.name
		content_disposition="attachment;filename=\""+the_file_name+"\""
		return web.FileResponse(path=str(the_fse),headers={"content-disposition":content_disposition},chunk_size=1024)

	# Recieved success notice from FFmpeg
	if sid==2:
		pass

	# Recieved error notice from FFmpeg
	if sid==3:
		pass
"""
# Handler for everything else
async def http_handler_main(request):
	peer=str(request.remote)
	print("http_handler_main triggered by",peer)
	print("\t→ request.host =",request.host)
	print("\t→ request.url =",request.url)
	print("\t→ asks for request.rel_url =",request.rel_url)
	
	requested_path_raw=str(request.rel_url)
	requested_path_parsed=urllib.parse.unquote(requested_path_raw)
	requested_path=Path(requested_path_parsed)

	# Return a file or a directory
	if requested_path_raw.startswith("/fse"):
		
		print("\t→",peer,"requested a file or dir")

		virtual_path=requested_path.relative_to("/fse")
		real_path=Path(_fse_root).joinpath(virtual_path)
		server_side_path=get_serverside_path(real_path)
		print("\t\t→ vpath =,",virtual_path)
		print("\t\t→ rpath =,",real_path)
		print("\t\t→ sspath =,",server_side_path)

		# The path is real on the server-side
		if server_side_path:

			# Bring up the File System Explorer if the path's a directory, if not, download the file... It's a file right?
			if server_side_path.is_dir():
				display_path=get_path_show(real_path)
				htmldump=_piece_html_start+_piece_html_title+"\n<style>"+_piece_css_default+"</style>\n</head>\n<body>\n<p><h1>Ubicación actual</h1>\n<p><h2><code>"+display_path+"</code></h2>"

				# Wether to show or not the link to the upper level, also show a link to the home page

				homepage=" <a href=/>Página de inicio</a>"

				if display_path=="/":
					htmldump=htmldump+"\n<p>Directorio raiz"+homepage+"\n<p>"

				else:
					upperlevel_path=str(Path("/fse").joinpath(virtual_path.parent))
					upperlevel_link=urllib.parse.quote(upperlevel_path)
					htmldump=htmldump+"\n<p><a href="+upperlevel_link+">Subir un nivel</a>"+homepage+"\n<p>"

				# Show subdirectories and files of current location

				ls_data,ls_dirs,ls_files=await aio_get_dircont(real_path,get_pop=True)

				htmldump=htmldump+"\n<p><h2>Directorios</h2>\n<p>"
				if ls_dirs>0:
					cp=0
					htmldump=htmldump+"\n<p><table cellpadding=8 width=100%>\n<tr>\n<th align=left>Nombre</th>\n<tr>"
					for fse in ls_data:
						if fse.is_dir():
							fse_path=Path("/fse").joinpath(virtual_path).joinpath(fse.name)
							fse_link=urllib.parse.quote(str(fse_path))

							htmldump=htmldump+"\n<tr style=\"background-color:"+_cc[cp]+";\">\n<td>📂 <a href="+fse_link+"><code>"+fse.name+"</code></a></td>\n<tr>"
							cp=cp+1
							if cp>1:
								cp=0

					htmldump=htmldump+"\n</table>"

				else:
					htmldump=htmldump+"\n<p>No hay nada\n<p>"

				htmldump=htmldump+"\n<p><h2>Archivos</h2>\n<p>"
				if ls_files>0:
					cp=0
					htmldump=htmldump+"\n<table cellpadding=8 width=100%>\n<tr>\n<th align=left>Nombre</th>\n<th align=left width=128>Tamaño</th>\n<tr>"
					for fse in ls_data:
						if fse.is_file():
							fse_path=Path("/fse").joinpath(virtual_path).joinpath(fse.name)
							fse_path_real=real_path.joinpath(fse.name)
							fse_link=urllib.parse.quote(str(fse_path))

							fse_filesize=os.path.getsize(str(fse_path_real))
							fse_filesize_hr=hr_units(fse_filesize)

							htmldump=htmldump+"\n<tr style='background-color:"+_cc[cp]+";'>\n<td>📄 <a href="+fse_link+"><code>"+fse.name+"</code></a></td>\n<td><code style='font-weight:bold;'>"+fse_filesize_hr+"</code></td>\n<tr>"
							cp=cp+1
							if cp>1:
								cp=0

					htmldump=htmldump+"\n</table>"

				else:
					htmldump=htmldump+"\n<p>No hay nada\n<p>"

				# Actions

				actions=False

				# File dependant actions

				if ls_files>1:

					if not actions:
						actions=True
						htmldump=htmldump+"\n<p><h2>Acciones</h2>\n<p>"

					fse_path=str(Path("/act/txtdl").joinpath(virtual_path))
					fse_link=urllib.parse.quote(fse_path)

					# The URL list maker
					fse_path=str(Path("/act/txtdl").joinpath(virtual_path))
					fse_link=urllib.parse.quote(fse_path)
					htmldump=htmldump+"\n<p><a href="+fse_link+">Lista de URLs de archivos (URL por línea)</a>\n<p>"

					fse_path=str(Path("/act/txtdl-idm").joinpath(virtual_path))
					fse_link=urllib.parse.quote(fse_path)
					htmldump=htmldump+"\n<p><a href="+fse_link+">Lista de URLs de archivos (URL + Nombre por línea)</a>\n<p>"

					# The M3U Playlist maker
					ls_files_f=list_filter_suffix(ls_data,_avsuffixes)

					if len(ls_files_f)>1:
						fse_path=str(Path("/act/mkm3u").joinpath(virtual_path))
						fse_link=urllib.parse.quote(fse_path)
						htmldump=htmldump+"\n<p><a href="+fse_link+">Lista de reproducción M3U</a>\n<p>"

					# The album viewer
					#ls_files_f=list_filter_suffix(ls_data,_imsuffixes)
					#
					#if len(ls_files_f)>1:
					#	fse_link=path_gitgud("/act/iview"+fse_link_raw+"/0-"+_iview_args[0])
					#	htmldump=htmldump+"\n<p><a href="+fse_link+">Visor de imágenes</a>\n<p>"

				htmldump=htmldump+_piece_html_end

				return web.Response(body=htmldump,content_type="text/html",charset="utf-8")

			elif server_side_path.is_file():

				# Send the file to the client

				the_file_name=server_side_path.name
				content_disposition="attachment; filename=\""+the_file_name+"\""
				the_file_size=os.path.getsize(server_side_path)
				content_length=str(the_file_size)

				the_headers={"content-disposition":content_disposition,"content-length":content_length}
				# the_headers={"content-length":content_length}

				return web.FileResponse(path=server_side_path,headers=the_headers,chunk_size=_kilobyte)

			else:
				err=403
				show_error=html_error_page(error,"El recurso no es ni archivo ni directorio. (¿Qué?)")
				return web.Response(body=show_error,content_type="text/html",charset="utf-8",status=err)

		else:
			err=404
			show_error=html_error_page(err,"La ubicación no existe")
			return web.Response(body=show_error,content_type="text/html",charset="utf-8",status=err)

	# Action to perform over a file or a directory. Mostly directories
	if requested_path_raw.startswith("/act/"):
		estatus=0
		ula=requested_path.parts[2]

		# First check if the command is valid
		if ula in _url_actions:
			cmd_valid=True
		else:
			cmd_valid=False

		if not cmd_valid:
			estatus=400
			show_error=html_error_page(estatus,"Acción no válida")

		# The command is valid. Now check if the requested path exists in the server side.
		if estatus==0:
			discard_path=Path("/act/"+ula)
			virtual_path=requested_path.relative_to(discard_path)
			real_path=Path(_fse_root).joinpath(virtual_path)
			server_side_path=get_serverside_path(real_path)

			if not server_side_path:
				estatus=404
				show_error=html_error_page(estatus,"La ubicación no existe")

		# Checking if the path is a directory
		if estatus==0:
			try:
				assert server_side_path.is_dir()

			except:
				estatus=406
				show_error=html_error_page(estatus,"La ubicación no es un directorio")

		# The server side path is a directory. List it and check if there's more than one file (the TXTDL runs)
		if estatus==0:
			ok_to_run=[]
			#ls_dump=get_ls_data(sside_path,return_dirs=False)
			ls_dump,ls_files=await aio_get_dircont(real_path,fsetype=0,get_pop=True)
			try:
				assert ls_files>1

			except:
				estatus=406
				show_error=html_error_page(estatus,"Hay menos de dos archivos en total")

		# Check if the other actions are OK to run
		if estatus==0:

			requested_url=str(request.url)
			wsite=requested_url.replace(requested_path_raw,"")
			base_path=Path("/fse").joinpath(virtual_path)
			the_file_name=virtual_path.name

			# URL files list
			if "txtdl" in ula:

				ticket=mkticket(peer)
				ticket_path=Path(_app_cwd).joinpath(ticket)

				async with aiofiles.open(ticket_path,"wt") as tmp:
					for fse in ls_dump:
						fse_path=base_path.joinpath(fse.name)
						fse_link=urllib.parse.quote(str(fse_path))
						if "txtdl-idm" in ula:
							await tmp.write(wsite+fse_link+"\t"+fse.name+"\n")
						else:
							   await tmp.write(wsite+fse_link+"\n")

				the_file_name=the_file_name+".txt"
				content_disposition="attachment;filename=\""+the_file_name+"\""
				return web.FileResponse(path=str(ticket_path),headers={"content-disposition":content_disposition},chunk_size=_kilobyte)

			# M3U Playlist Maker
			elif "mkm3u" in ula:

				# There's more than one file here. Make another list of compatible files and see if it's still worth it
				if estatus==0:
					ls_files_f=list_filter_suffix(ls_dump,_avsuffixes)

					try:
						assert len(ls_files_f)>1

					except:
						estatus=406
						show_error=html_error_page(estatus,"Hay menos de dos archivos compatibles.")

				# Create the M3U playlist
				if estatus==0:

					ticket=mkticket(peer)
					ticket_path=Path(_app_cwd).joinpath(ticket)

					base_path=Path("/fse").joinpath(virtual_path)

					async with aiofiles.open(ticket_path,"wt") as tmp:
						for fse in ls_files_f:
							fse_path=base_path.joinpath(fse.name)
							fse_link=urllib.parse.quote(str(fse_path))
							await tmp.write(wsite+fse_link+"\n")

					the_file_name=the_file_name+".m3u"
					content_disposition="attachment;filename=\""+the_file_name+"\""
					return web.FileResponse(path=str(ticket_path),headers={"content-disposition":content_disposition},chunk_size=_kilobyte)

			# TODO: FIX THE IMAGE VIEWER

			# Image viewer
#			elif "iview" in command:

#				args=cside_path_pl.name
#				args_list=args.split("-")
#				try:
#					dir_index=int(args_list[0])

#				except:
#					estatus=406
#					show_error=html_error_page(estatus,"La petición no es válida")

#				# Check if the arg after the dir index is legit
#				if estatus==0:
#					try:
#						iview_arg=args_list[1]
#						arg_is_valid=False
#						for a in _iview_args:
#							if iview_arg==a:
#								arg_is_valid=True

#					except:
#						estatus=406
#						show_error=html_error_page(estatus,"La petición no es válida")

				# Check for compatible files
#				if estatus==0:
#					ls_files_f=list_filter_suffix(ls_files_o,_imsuffixes)
#					try:
#						assert len(ls_files_f)>1

#					except:
#						estatus=406
#						show_error=html_error_page(estatus,"Hay menos de dos archivos compatibles")

				# The image viewer interface
#				if estatus==0:
#					# Get CSS piece of code
#					print("iview_arg",iview_arg)
#					css_code=str(_css_iview.get(iview_arg))

#					file_max=len(ls_files_f)-1
#					file_name=ls_files_f[dir_index]
#					file_link_raw=path_gitgud("/fse"+cside_path_this+"/"+file_name)
#					file_link=urllib.parse.quote(file_link_raw)

#					# Links above the image for navigating and changing the fit

#					link_common_part="/act/iview"+cside_path_this+"/"
#					link_base_raw=path_gitgud(link_common_part)
#					link_base=urllib.parse.quote(link_base_raw)

#					# Link to previous page
#					if dir_index>0:
#						idx_back=dir_index-1
#						link_back_html="<a href='"+link_base+"/"+str(idx_back)+"-"+iview_arg+"'>Anterior</a>"
 
#					else:
#						link_back_html="Primera pág."

#					# Return to the explorer
#					link_dir_raw=path_gitgud("/fse"+cside_path_this)
#					link_dir=urllib.parse.quote(link_dir_raw)
#					link_dir_html="<a href='"+link_dir+"'>Volver</a>"

#					# Link to the next page
#					if dir_index<file_max:
#						idx_next=dir_index+1
#						link_next_html="<a href='"+link_base+"/"+str(idx_next)+"-"+iview_arg+"'>Siguiente</a>"

#					else:
#						link_next_html="Última pág."

#					# Links to change the image fit

#					# Width fit
#					if iview_arg==_iview_args[0]:
#						image_fit_w="Ajustado al ancho"

#					else:
#						image_fit_w="<a href='"+link_base+"/"+str(dir_index)+"-"+_iview_args[0]+"'>Ajustar al ancho</a>"

#					# Height fit
#					if iview_arg==_iview_args[1]:
#						image_fit_h="Ajustado al alto"

#					else:
#						image_fit_h="<a href='"+link_base+"/"+str(dir_index)+"-"+_iview_args[1]+"'>Ajustar al alto</a>"

#					# Write down the HTML body and send it

#					html_init=htmldump=_piece_html_start+_piece_html_title+"\n<style>"+_piece_css_default+"</style>\n<script>"+_piece_js_iview+"</script>\n</head>\n<body"+_piece_html_body_iview+">\n"

#					iview_controls="<tr><th width=20%>"+link_back_html+"</th><th>Viendo imágenes en <code>"+cside_path_this+"</code> ["+link_dir_html+"] Ajuste ["+image_fit_w+"]["+image_fit_h+"]</th><th width=20%>"+link_next_html+"</th></tr>\n"

#					# iview_controls_nav="<tr></tr>\n"

#					iview_image="<div id='ic' style='overflow:auto;'><img src='"+file_link+"' style='"+css_code+"'></div>\n"

#					htmldump=html_init+"<div id='mc'>\n<div id='cc'>\n<p><table width=100% layout='fixed'>\n"+iview_controls+"</table>\n</div>\n"+iview_image+"</div>"+_piece_html_end

#					return web.Response(body=htmldump,content_type="text/html",charset="utf-8",status=estatus)

			# Not implemented
			else:
				estatus=501
				show_error=html_error_page(estatus,"Acción no implementada :V")

		if estatus>0:
			return web.Response(body=show_error,content_type="text/html",charset="utf-8",status=estatus)

	# Take a look at the news
	if requested_path_raw.startswith("/news"):
		htmldump=_piece_html_start+_piece_html_title+"\n<style>"+_piece_css_default+"\ndiv{margin:4;padding-left:16;padding-right:16;padding-top:2;padding-bottom:2;background-color:"+_cgray1+"}"+"</style>\n</head>\n<body>\n<p><h1>Noticias y avisos</h1>\n<p><a href='/'>Volver a la página de inicio</a>\n"
		if len(admin_public_messages)>0:
			if len(admin_public_messages)>1:
				count=1
				htmldump=htmldump+"<p><h2>Índice</h2>\n"
				for post in admin_public_messages:
					title=post.get_data()[0]
					htmldump=htmldump+"<p><a href='#p"+str(count)+"'>"+title+"</a>\n"
					count=count+1

				htmldump=htmldump+"<p><h2>Mensajes</h2>\n"

			count=1
			#htmldump=htmldump+""
			for post in admin_public_messages:
				data=post.get_data()
				age_raw=post.get_age()

				sec_float=float(age_raw/3600.0)
				sec_int=int(age_raw/3600)

				sed_diff=sec_float-sec_int

				if sec_int==0:
					if sed_diff<0.3:
						time_difference="Unos minutos"

					elif sed_diff>=0.3 and sed_diff<0.6:
						time_difference="Media hora"

					elif sed_diff>=0.6:
						time_difference="Casi una hora"

				elif sec_int==1:
					if sed_diff<0.3:
						time_difference="Una hora"

					elif sed_diff>=0.3 and sed_diff<0.6:
						time_difference="Hora y media"

					elif sed_diff>=0.6:
						time_difference="Casi 2 horas"

				else:
					if sed_diff<0.3:
						time_difference=str(sec_int)+" horas"

					elif sed_diff>=0.3 and sed_diff<0.6:
						time_difference=str(sec_int)+" horas y media"

					elif sed_diff>=0.6:
						time_difference="Casi "+str(sec_int+1)+" horas"

				title=data[0]
				content=data[1]
				htmldump=htmldump+"<p>\n<a name='p"+str(count)+"'><p></a><div><h3>"+title+"</h3>\n"+content+"<p>\n<p>Publicado hace: "+time_difference+"</div>\n"
				count=count+1

			#htmldump=htmldump+"</div>"

		htmldump=htmldump+_piece_html_end

		return web.Response(body=htmldump,content_type="text/html",charset="utf-8")

################################################################################
# Build the web server
################################################################################

# Build this mother f***er
async def build_app():
	app=web.Application()
	# web.get("/ffmpeg",http_handler_ffmpeg),
	app.add_routes([web.get("/",http_handler_home),web.get("/fse",http_handler_main),web.get("/fse/{p:.*}",http_handler_main),web.get("/act/{p:.*}",http_handler_main),web.get("/news",http_handler_main)])
	return app

# Run this mother f***er
# web.run_app(build_app(),port=_server_port)

#################################################################################
# Run this freak
#################################################################################

admin_post_add("Bot iniciado","Este mensaje es automático")

loop=asyncio.get_event_loop()

# loop.create_task(agtpp_service())

# loop.create_task(heavy_jobs())

loop.create_task(admin_posts_supervisor())

bot.add_event_handler(tge_handler_messages,events.NewMessage())

web.run_app(build_app(),port=_ev_port)
