# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
Tecla de atalho:
   ESC - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import cv2
import numpy as np
import sys
import os
import glob
import math
import datetime
import time
import mysql.connector
from datetime import date
from datetime import datetime
import Adafruit_CharLCD as LCD
import socket
import RPi.GPIO as GPIO
from time import sleep
import datetime as dt


#variaveis do banco de dados

host1 = '' #IP local utilizado
database1 = 'relatorio'
user1 = 'root'
password1 = '' #senha inserida pelo autor
qtd_erro = 0
qtd_obj = 0
qtd_ok = 0
status = 1
data = 1
data_atual = date.today()
hora_atual = datetime.now().strftime('%H:%M:%S')
time_shape = datetime.now().strftime('%H:%M:%S')
time_defect = datetime.now().strftime('%H:%M:%S')
inicio = time.time()

#inicializando banco de dados

con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)

if __name__ == '__main__':
    import sys
    print(__doc__)

    try:
        fn = sys.argv[1]
    except:
        fn = 1
    try:

        cap = cv2.VideoCapture(0)
    except:
        print("capture error")

    def processing(im):
        # primeiramente se converte para escala de cinza
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # divide a imagem entre as cores
        r, g, b = cv2.split(im)
        # aplica-se o threshold para binarização
        (thresh, bb) = cv2.threshold(b, 110, 255, cv2.THRESH_BINARY)
        #cv2.imshow('b', bb)
    
        mask = cleanup(bb)
        #imshow utilizado para a versão de testes no comparativo com a captura original
        #cv2.imshow('mask', mask) 
        
        return mask

    def cleanup(im):
        kernel = np.ones((3, 3), np.uint8)
        imr = cv2.resize(
            im,
            None,
            fx=0.5,
            fy=0.5,
            interpolation=cv2.INTER_CUBIC)
        op = cv2.morphologyEx(imr, cv2.MORPH_OPEN, kernel)
        cl = cv2.morphologyEx(op, cv2.MORPH_CLOSE, kernel)
        mask = cv2.resize(
            cl,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC)
            
        mask = cv2.bitwise_and(im, mask, mask=mask)
        return mask
        
        
        
    def detect(c):
        
		#detecta três situações:  conforme, inconforme, alerta
        
        # Identificando o formato de acordo com os vertices
        shape = "unidentified"
        peri = cv2.arcLength(c, True)   #dado em px
        print(peri)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        if peri > 300 and peri < 1000:
            if len(approx) == 4:
                shape = "conforme"
            else:
                shape = "inconforme"
        else:
            shape = "alerta"
                			
			
        return shape      

    def inspect(imd):
        inconformes = []
        conformes = []
        alerta = []
        mask = np.zeros((480, 640), np.uint8)
        # Procura os contornos e retorna para a função
        try:
            _, contours, hierarchy = cv2.findContours(
                imd.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                for component in zip(contours, hierarchy):
                    currentContour = component[0]
                    currentHierarchy = component[1]
                    areaC = cv2.contourArea(currentContour)
                    
                    if areaC > 2000:
                        shape = detect(currentContour)
                    
                    if shape == 'conforme':
                        conformes.append(currentContour)
                    elif shape == 'inconforme':
                        inconformes.append(currentContour)
                    elif shape == 'alerta':
                        alerta.append(currentContour)
                    
        except:
            pass
        conformes = [sorted(conformes, key = cv2.contourArea, reverse = True)[0]] if len(conformes) else conformes
        return conformes, inconformes, alerta
        
        
    count = 0
    cont_erro = 0
    cont_ok = 0
    last_inspect = 0
    flagStatus = 1      #0 - máquina desligada, 1 - maquina operando, 2 - maquina parada (devido ao alerta)
    
    #Configuração dos pinos do Display        
	# Pinos LCD x Raspberry (GPIO)
    lcd_rs        = 18
    lcd_en        = 23
    lcd_d4        = 12
    lcd_d5        = 16
    lcd_d6        = 20
    lcd_d7        = 21
    lcd_backlight = 4
    lcd_colunas = 16
    lcd_linhas  = 2
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5,
                               lcd_d6, lcd_d7, lcd_colunas, lcd_linhas,
                               lcd_backlight)
	
	#Configuração do Buzzer
    triggerPIN = 24
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(triggerPIN, GPIO.OUT)
    buzzer = GPIO.PWM(triggerPIN, 523)	
	
	#Realiza a conexão com o BD
    con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
    if con.is_connected():
        cursor = con.cursor()
        hora_atual = datetime.now().strftime('%H:%M:%S')
        sql = " INSERT INTO tempo (data, tempo_desligado, tempo_ligado, tempo_parado) VALUES (%s, %s, %s, %s)"
        val = (data_atual, 0, hora_atual, 0)
        cursor.execute(sql,val) 
        con.commit()
        cursor.close()	
        
    if con.is_connected():
        cursor = con.cursor()				
        sql = "   UPDATE flag SET flag = 1"
        cursor.execute(sql)
                       
        con.commit()
        cursor.close()
	
    
    while True:
        e1 = time.time()

        ret, frame = cap.read()
        cnt_style = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        frame = cv2.resize(frame, (640, 480))
        total_shapes = 0
        total_defects = 0
        
        
        if flagStatus == 2:
            con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
            cursor = con.cursor()
            query = "SELECT * FROM flag"			
            cursor.execute(query)
            row = cursor.fetchone()
            for row in cursor:
                print(row)
            #print(row[0])
            if row[0] != 2:
                flagStatus = 1
            cursor.close()
        
        '''MEAN TRIGGER - DETECTA O OBJETO NO CENTRO DA FRAME'''
        roi = frame[245:315, 250:320]
        mean = cv2.mean(roi)
        trigger = frame.copy()
        trigger[235:275, 190:430] = 0
        
        #ṕrevenindo multiplas inspecoes com delay
        
        t = (e1 - last_inspect)
        
        #ajustar de acordo com a esteira utilizada

        if mean[0] > 100 and t > 1.4:

            # PRE PROCESSAMENTO
            pre = processing(frame)
            # INSPEÇÃO
            conformes, inconformes, alerta = inspect(pre)
            
            
            if len(alerta) > 0 and flagStatus == 1:
                flagStatus = 2
                buzzer.start(10)
                time.sleep(1)
                buzzer.stop(10)
                
                print("ALERTA!!")
                
                #setando a flag para 2
                if con.is_connected():
                    cursor = con.cursor()				
                    sql = "   UPDATE flag SET flag = 2"
                    cursor.execute(sql)
                                   
                    con.commit()
                    cursor.close()
                else:
                    
                    con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
                    cursor = con.cursor()				
                    sql = "   UPDATE flag SET flag = 2"
                    cursor.execute(sql)
                                   
                    con.commit()
                    cursor.close()
                
                #iniciando a contagem de tempo parado
                if con.is_connected():
                    cursor = con.cursor()
                    hora_atual = datetime.now().strftime('%H:%M:%S')
                    sql = " INSERT INTO tempo (data, tempo_desligado, tempo_ligado, tempo_parado) VALUES (%s, %s, %s, %s)"
                    val = (data_atual, 0, 0, hora_atual)
                    cursor.execute(sql,val) 
                    con.commit()
                    cursor.close()	
                else:
                    con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
                    cursor = con.cursor()
                    hora_atual = datetime.now().strftime('%H:%M:%S')
                    sql = " INSERT INTO tempo (data, tempo_desligado, tempo_ligado, tempo_parado) VALUES (%s, %s, %s, %s)"
                    val = (data_atual, 0, 0, hora_atual)
                    cursor.execute(sql,val) 
                    con.commit()
                    cursor.close()
                
                lcd.clear()
                lcd.message('\n')    
                lcd.message('    ALERTA!!    ') 


            
                
            if flagStatus == 1:
            
                # RESULT
                total_conformes = len(conformes)
                qtd_ok = qtd_ok + total_conformes
                time_now = datetime.now().strftime('%H:%M:%S')
                
                if total_conformes > 0:# and time_now != time_shape:
                    if con.is_connected():
                        cursor = con.cursor()
                        hora_atual = datetime.now().strftime('%H:%M:%S')
                        sql = " INSERT INTO valores (qtd_ok, qtd_erro, data, horario, flag) VALUES (%s, %s, %s, %s, %s)"
                        val = (1, 0, data_atual, hora_atual, 0)
                        cursor.execute(sql,val)
                        ultimo = cursor.lastrowid
                        
                                                                   
                                           
                        con.commit()
                        cursor.close()

                    else:
                        con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
                        
                        if con.is_connected():
                            cursor = con.cursor()
                            hora_atual = datetime.now().strftime('%H:%M:%S')
                            sql = " INSERT INTO valores (qtd_ok, qtd_erro, data, horario, flag) VALUES (%s, %s, %s, %s, %s)"
                            val = (1, 0, data_atual, hora_atual, 0)
                            cursor.execute(sql,val)
                            ultimo = cursor.lastrowid
                                                
                                               
                            con.commit()
                            cursor.close()
                        else:
                            print("BD não conectou!")
                        
                    time_shape = datetime.now().strftime('%H:%M:%S')
                
                total_inconformes = len(inconformes)
                qtd_erro = qtd_erro + total_inconformes
                time_now = datetime.now().strftime('%H:%M:%S')
                
                
                if total_inconformes > 0:
                    
                    if con.is_connected():
                        cursor = con.cursor()
                        hora_atual = datetime.now().strftime('%H:%M:%S')
                        sql = " INSERT INTO valores (qtd_ok, qtd_erro, data, horario, flag) VALUES (%s, %s, %s, %s, %s)"
                        val = (0, 1, data_atual, hora_atual, 1)
                        cursor.execute(sql,val)
                        ultimo = cursor.lastrowid
                                           
                        
                        con.commit()
                        cursor.close()
                        con.close()
                    
                    else:
                        con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
                        if con.is_connected():
                            cursor = con.cursor()
                            hora_atual = datetime.now().strftime('%H:%M:%S')
                            sql = " INSERT INTO valores (qtd_ok, qtd_erro, data, horario, flag) VALUES (%s, %s, %s, %s, %s)"
                            val = (0, 1, data_atual, hora_atual, 1)
                            cursor.execute(sql,val)
                            ultimo = cursor.lastrowid
                                               
                            
                            con.commit()
                            cursor.close()
                            con.close()
                            
                        else:
                            print("BD não conectou!")
                        
                    time_defect = datetime.now().strftime('%H:%M:%S')
                last_inspect = time.time()
                    

                lcd.clear()
                # Linha disponivel para codigo de erro
                lcd.message('\n')
                # Mostra os acertos e erros
                ok = qtd_ok
                erro = qtd_erro

                lcd.message('OK %s Erro %s\n' %(ok,erro))
                

        # Dados para impressão da tela de "frame"
        # Opcional utilizado para testes, se aplicado sem interface gráfica,
        # pode ser removido
        e2 = time.time()
        t = (e2 - e1) / cv2.getTickFrequency()
        fps = str("%.2d" % (1 / t))
        msg = "fps: " + str(fps)
        t = str("%.3f" % t)
        msg = "time (s): " + str(t)
        cv2.rectangle(frame, (0, 0), (90, 14), (0, 0, 0), -1)

        cv2.putText(frame, t + 's ' + fps + 'fps', (1, 10),
                    cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 250, 0), 1)
        text = "ok:[" + \
            str(total_shapes) + "] error:[" + str(total_defects) + "]"
        cv2.putText(frame, text, (90, 10), font, .4, (0, 250, 0), 1)

        cv2.imshow('frame', frame)
        

        # execução pode ser finalizada utilizando a tecla ESC como botão de segurança 
        # e botão de "desliga"
        ch = 0xFF & cv2.waitKey(1)
        if ch == 27:
            
            buzzer.start(10)
            time.sleep(1)
            
            if con.is_connected():
                cursor = con.cursor()				
                sql = "   UPDATE flag SET flag = 0"
                cursor.execute(sql)
                               
                con.commit()
                cursor.close()
            else:
                con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
                cursor = con.cursor()				
                sql = "   UPDATE flag SET flag = 0"
                cursor.execute(sql)
                               
                con.commit()
                cursor.close()
            
            #iniciando a contagem de tempo desligado
                if con.is_connected():
                    cursor = con.cursor()
                    hora_atual = datetime.now().strftime('%H:%M:%S')
                    sql = " INSERT INTO tempo (data, tempo_desligado, tempo_ligado, tempo_parado) VALUES (%s, %s, %s, %s)"
                    val = (data_atual, hora_atual, 0, 0)
                    cursor.execute(sql,val) 
                    con.commit()
                    cursor.close()	
                else:
                    con = mysql.connector.connect(host=host1,database=database1,user=user1,password=password1)
                    cursor = con.cursor()
                    hora_atual = datetime.now().strftime('%H:%M:%S')
                    sql = " INSERT INTO tempo (data, tempo_desligado, tempo_ligado, tempo_parado) VALUES (%s, %s, %s, %s)"
                    val = (data_atual, hora_atual, 0, 0)
                    cursor.execute(sql,val) 
                    con.commit()
                    cursor.close()
            
            if con.is_connected():    
                                
                cursor = con.cursor()
                
                
                sql = """   UPDATE valores
                            SET flag = %s
                            WHERE id = %s """
                sql_data = (1, ultimo)
                cursor.execute(sql,sql_data)
                
                
                con.commit()
                cursor.close()
                con.close()
        
            break
            
                
            cv2.destroyAllWindows()
            
    if con.is_connected(): 
        con.commit()
        cursor.close()
        con.close()  
