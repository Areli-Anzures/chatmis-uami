from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pandas as pd

import re
import time

def guradaCSV(pregunta, respuesta):
    data = [[pregunta,respuesta]]
    df = pd.DataFrame(data)
    df.to_csv('Preguntas_de_usuarios.csv', mode = "a", index = None, header = False)

def CorrectorOrtografico(cadena):
    cadena = cadena.lower() #convierte en minusculas
    #elimina acentos
    cadena = cadena.replace("á", "a")
    cadena = cadena.replace("é", "e")
    cadena = cadena.replace("í", "i")
    cadena = cadena.replace("ó", "o")
    cadena = cadena.replace("ú", "u")
    cadena = cadena.strip() #elimina espacios de más
    return cadena

class ActionDarInfoAdicional(Action):
    def name(self) -> Text:
        return "action_dar_info_general"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entidades = tracker.latest_message['entities'] #extrae entidad
        mensaje = tracker.latest_message['text'] #mensaje dado por el usuario
        pregunta = mensaje
        inicio = time.time()
        if len(entidades) != 0:
            print(entidades)
            entidad_corregida = ""
            for e in entidades: # hay mas de una entidad identificada
                entidad = e.pop('value') #extraccion de la lista y diccionario
                entidad = CorrectorOrtografico(entidad) #se quitan mayusculas y acentos
                entidad_corregida = entidad_corregida + entidad + " "
            entidad_corregida = entidad_corregida.strip()
            Resultado_titulo = []
            Resultado_link = []
            info = pd.read_csv('links_visitados.csv')
            tamaño = len(info)
            for i in range(tamaño):
                titulo = info.loc[i].iat[1]
                titulo = str(titulo)
                titulo_corregido = CorrectorOrtografico(titulo)
                #print("titulo corregido es: ", entidad_corregida, "  y ", titulo_corregido)
                if titulo_corregido.find(entidad_corregida) != -1 and titulo_corregido.find("izt.uam") == -1: #si la lista no esta vacia la imprime, encontro algo
                    link = info.loc[i].iat[2]
                    if titulo not in Resultado_titulo and link not in Resultado_link:
                        Resultado_titulo.append(titulo)
                        Resultado_link.append(link)
            if len(Resultado_titulo) != 0: # si encontro resultados
                if len(Resultado_titulo) <= 5: #Tratar de no pressentar mas de 5 resultados 
                    c = 0
                    for resultado in Resultado_titulo:
                        dispatcher.utter_message(text= "Info sobre " + resultado.strip() + " ver en " + Resultado_link[c])
                        c += 1
                        respuesta = "Obtuve respuesta de BD"
                else:
                    for i in range(0,5):
                        dispatcher.utter_message(text= "Info sobre " + Resultado_titulo[i].strip() + " ver en " + Resultado_link[i])
                    dispatcher.utter_message(text= "Por el momento te presento 5 resultados, espera la mejora para obtener más resultados")
                    respuesta = "Obtuve respuesta de BD"
            else:
                dispatcher.utter_message(text="No encontre información en la web sobre " + entidad)
                respuesta = "No encontre nada en BD"
            fin = time.time()
            print("Di resultados en un tiempo de ", fin - inicio)
            guradaCSV(pregunta, respuesta)
            return []
        else:
            dispatcher.utter_message(text="Lo siento, no logro entender lo que dices, tu mensaje fue: '" + mensaje + "'")
            dispatcher.utter_message(text="Recuerda que aún no estoy preparada para para responder cualquier pregunta. Únicamente lo encontrado en las páginas de la UAMI.")
            respuesta = "No entendí la entidad, no di respuesta"
            guradaCSV(pregunta, respuesta)
            return []
