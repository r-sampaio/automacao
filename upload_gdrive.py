#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Date: 08/04/2021
# Author: r-sampaio
# Github: https://github.com/r-sampaio
# Python version: 3.x

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import sleep
import smtplib
import os
from folder import folder_gdrive

# Authentication
gauth = GoogleAuth()
# gauth.LocalWebserverAuth() # Authentication in browser
# gauth.SaveCredentialsFile("mycreds.txt") # Save credentials
gauth.LoadCredentialsFile('mycreds.txt') # Load credentials
drive = GoogleDrive(gauth)

while True:
    text_status         = ''
    text_status_erro    = ''
    text_status_success = ''
    
    # Read dictionary
    for folder, data in folder_gdrive().items():
        print ('Pasta', folder)
        for path_local,id_folder_gdrive in data.items():
            path = path_local
            id_folder = id_folder_gdrive
            for filename in os.listdir(path):
                try:
                    # Search file in folder
                    file_list = drive.ListFile({'q':  f"title contains '{filename}' and '{id_folder}' in parents and trashed=false"}).GetList()
                    text_erro = (f"{file_list[0]['title']} \033[31mArquivo existe\033[m")
                    print(text_erro)
                    text_status_erro += (f'Pasta {folder}: {text_erro}')
                except:
                    # Send new file
                    file = drive.CreateFile({'title': filename, 'parents': [{'id': f'{id_folder}'}]})
                    file.SetContentFile(os.path.join(path, filename))
                    file.Upload()
                    
                    # Search file uploaded
                    file_list = drive.ListFile({'q': f"title contains '{filename}' and trashed=false"}).GetList()
                    text_success = (f"{file_list[0]['title']} \033[34mUpload completo!\033[m")
                    print(text_success)
                    text_status_success += (f'Pasta {folder}: {text_success}')

    if text_status_success != '':
        # Credentials
        cred_email_to = open('email_to.txt', 'r')
        to_addr = cred_email_to.readlines()
        cred_email_from = open('email_from.txt', 'r')
        auth = cred_email_from.readlines()
        from_addr = (auth[0]).strip()
        password = auth[1].strip()
        smtp='smtp.gmail.com'
        
        # Login
        print('Login email')
        send = smtplib.SMTP(smtp, 587) 
        send.starttls() 
        send.login(from_addr, password)
        
        for i in range(len(to_addr)):
            # Constructing messenge
            print(f'Criando mensagem para {(to_addr[i]).strip()}.')
            email_msg = MIMEMultipart()
            email_msg['Subject'] = 'Status Backup'
            email_msg['From'] = (from_addr).strip()
            email_msg['To'] = (to_addr[i]).strip()
            message = text_status_success
            email_msg.attach(MIMEText(message, 'plain'))
            
            # Send Email
            send.sendmail(from_addr, to_addr[i], email_msg.as_string())
            print(f'Email enviado para {(to_addr[i]).strip()}.')
        print('Logout email')
        send.quit()
    print()
    print('Waiting...\n')
    sleep(6) # waiting seconds
